
import time

# import sys
# from pathlib import Path
# from datetime import datetime

from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot

import sys
import traceback
import logging

from .inputs import FloatInput
from .taskresult import TaskResult, ResultLogHandler

from rga.baseinst import Instrument as BaseInst

# HTML formatter for QTextBrowser
Bold = '<font color="black"><b>{}</b></font>'
GreenBold = '<font color="green"><b>{}</b></font>'
GreenNormal = '<font color="green">{}</font>'
RedBold = '<font color="red"><b>{}</b></font>'
RedNormal = '<font color="red">{}</font>'


def round_float(number, fmt='{:.4e}'):
    return float(fmt.format(number))


class Task(QThread):
    """ Base class for all task classes
    """

    class TaskException(Exception): pass
    class TaskSetupFailed(TaskException): pass
    class TaskRunFailed(TaskException): pass

    # Data directory is handled by SessionHandler now
    # DefaultDirectory = str(Path.home() / "tcal-results")
    # DataDirectory = 'data_dir'  # directory to hold all data files

    # When parent is not None, parent should have these attributes.
    InstrumentDict = 'inst_dict'  # all instruments to use in a task
    DeviceUnderTest = 'dut'      # dict key for main test device
    MatplotlibFigure = 'figure'  # to display plots
    SessionHandler = 'session_handler'

    # Escape string use in stdout redirection to GUI
    EscapeForResult = '@RESULT@'
    EscapeForDevice = '@DEVICE@'
    EscapeForStatus = '@STATUS@'
    EscapeForStart = '@START@'
    EscapeForStop = '@STOP@'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        # Example float parameter
        "Define variables before use!!": FloatInput(10.0, " Hz", 1.0, 1000.0, 1.0),
        "Constant value": FloatInput(1.0)
    }

    _is_running = False  # class wide flag to tell if any task is running
    _is_optional = False  # result status will set as success initially if a task class is optional

    # Multiple scans is run during a task
    scan_started = Signal()
    scan_finished = Signal()

    # signal for text output to UI
    text_written_available = Signal(str)

    # emit when you need UI update for newly available data
    data_available = Signal(dict)

    # emit to change UI input panel values for new parameters
    parameter_changed = Signal()

    # signal used to get an answer for a question from UI
    new_question = Signal(str, object)

    # Image information for parent to display instead of the default logo image before instantiated
    InitialImage = None  # None for default image
    InitialLimits = None
    InitialMarkers = None

    def __init__(self, parent=None):
        """ parent should have instrument dict,
        """
        super().__init__()
        self.parent = parent

        self._keep_running = False
        self._aborted = False
        self._error_raised = False
        self._task_passed = False
        self._log_error_detail = False  # Enables logging traceback information

        self.name = 'Base Task'
        self.logger_prefix = ''  # used for logger name for multi-threaded tasks
        self.logger = None
        self.result = None
        self.result_log_handler = None
        self.session_handler = None

        # inst_dict holds all the instrument to use in task
        self.inst_dict = {}

        self.data_dict = {}
        self.first_data = True

        # figure is expected to be Matplotlib figure object.
        self.figure = None

    def setup(self):
        """
        Subclass needs  to override this method.
        Put all preparation for a task in the overridden method.
        """
        raise NotImplementedError("No setup implemented!!")

    def test(self):
        """
        Subclass has to override this method.
        Check if is_running() is true to continue.
        Add data using in add_details, create_table, and add_data_to_table.
        """
        raise NotImplementedError("We need a real task!!")

    def cleanup(self):
        """
        Subclass has to override this method
        Put any cleanup after task in the overridden method
        """
        raise NotImplementedError("No cleanup implemented!!")

    def get_logger(self, name):
        if self.logger_prefix:
            n = f'{self.logger_prefix}.{name}'
        else:
            n = name
        logger = logging.getLogger(n)
        if self.result_log_handler is not None:
            logger.addHandler(self.result_log_handler)
        return logger

    def basic_setup(self):
        self.logger = self.get_logger(__name__)
        figure = getattr(self, self.MatplotlibFigure)
        if figure is None or not hasattr(figure, 'canvas'):
            raise AttributeError('Invalid figure')
        inst_dict = getattr(self, self.InstrumentDict)

        if (inst_dict is None) or (self.DeviceUnderTest not in inst_dict):
            raise AttributeError('inst_dict has no DUT')

        # We want Exception to be handled in run()
        Task._is_running = True
        self._keep_running = True
        self._error_raised = False

        # We want to create self.result after self.name is assigned
        self.result = TaskResult(self.name)
        self.result.set_start_time_now()

        log_format = '%(asctime)s-%(levelname)s-%(message)s'
        formatter = logging.Formatter(log_format)

        self.result_log_handler = ResultLogHandler(self.result)
        self.result_log_handler.setLevel(logging.INFO)
        self.result_log_handler.setFormatter(formatter)
        self.logger.addHandler(self.result_log_handler)

        msg = '{} STARTED'.format(self.name)
        self.display_result(msg)
        self.update_status(msg)
        self.logger.info(GreenBold.format(msg))

        self.__notify_start()
        self.clear_figure()

    def basic_cleanup(self):
        try:
            Task._is_running = False
            self._keep_running = False
            self.__notify_finish()
            self.result.set_stop_time_now()
            if self._aborted:
                msg = '{} ABORTED'.format(self.name)
                self.display_result(msg)
                self.update_status(msg)
                msg = '<font color="red"><b>' + msg + '</b></font>'
                self.logger.info(msg)
                self.result.set_aborted()
            elif self._task_passed:
                msg = '{} PASSED'.format(self.name)
                self.display_result(msg)
                self.update_status(msg)
                self.logger.info(GreenBold.format(msg))
                self.result.set_passed(True)
            else:
                msg = '{} FAILED'.format(self.name)
                self.display_result(msg)
                self.update_status(msg)
                self.logger.info(RedBold.format(msg))
                self.result.set_passed(False)

        except Exception as e:
            self.logger.error('Error during basic_cleanup: {}'.format(e))
        finally:
            # self.logger.removeHandler(self.file_log_handler)
            self.logger.removeHandler(self.result_log_handler)

    def run(self):
        try:
            self.basic_setup()
            if self._keep_running:
                self.logger.debug("{} run started".format(self.name))
            try:
                self.setup()  # setup from the subclass
                try:
                    self.logger.debug("{} task started".format(self.name))
                    self.test()
                    self.logger.debug("{} task completed".format(self.name))
                except Exception as e:
                    self._error_raised = True
                    self.log_exception(e)
                self.cleanup()  # cleanup from a subclass
            except Exception as e:
                self._error_raised = True  # We raise error for errors in setup or cleanup for now.
                self.log_exception(e)
            self.logger.debug("{} run completed".format(self.name))
            self.basic_cleanup()
        except Exception as e:
            self.log_exception(e)

    # Override for QThread start
    def start(self, priority=QThread.InheritPriority):
        # if Task._is_running: # Disable for multiple tasks running
        #     raise RuntimeError('Another task is running')

        self._keep_running = True
        self._aborted = False
        super().start(priority)
        # self.logger.debug("{} start completed".format(self.name))

    def stop(self):
        if self._keep_running:
            self._aborted = True
            self._keep_running = False

    def set_session_handler(self, session_handler):
        self.session_handler = session_handler

    def set_inst_dict(self, inst_dict):
        if self.DeviceUnderTest not in inst_dict:
            raise AttributeError('Inst_dict has no DUT')
        if not issubclass(type(inst_dict[self.DeviceUnderTest]), BaseInst):
            raise AttributeError('DUT is not a subclass of BaseInst.')
        setattr(self, self.InstrumentDict, inst_dict)

    def set_figure(self, figure=None):
        """
        If parent does  not have a figure, a MatplotLib figure object,
        you can provide a task with  one with this method.
        """
        if figure is not None and not hasattr(figure, 'canvas'):
            raise AttributeError('A Matplotlib figure should have canvas')
        else:
            self.figure = figure

        if hasattr(figure, 'canvas'):
            self.clear_figure()

    def clear_figure(self):
        """
        Clear figure
        """
        if self.figure is not None and hasattr(self.figure, 'canvas'):
            self.figure.clear()
            self.figure.canvas.draw_idle()

    def is_running(self):
        return self._keep_running

    @classmethod
    def is_optional(cls):
        return cls._is_optional

    def is_task_passed(self):
        return self._task_passed

    def set_task_passed(self, status):
        if status:
            self._aborted = False
        self._task_passed = status
        self.result.set_passed(status)

    def is_error_raised(self):
        return self._error_raised

    # Set to stop the task selection from running further
    def set_error_raised(self):
        self._error_raised = True

    # Wrapper for TaskResult.add_details
    def add_details(self, msg: str, key='summary'):
        self.result.add_details(msg, key)

    # Wrapper for TaskResult.create_table
    def create_table(self, name: str, *args):
        self.result.create_table(name, *args)

    # Wrapper for TaskResult.add_data_to_table
    def add_data_to_table(self, name: str, *args, ):
        self.result.add_data_to_table(name, *args)

    # The file for raw data is created by SessionHandler automatically.
    # You can sequentially add data to the table until you create another new table.
    # TaskResult is attached to the file in the last before closed.

    def create_table_in_file(self, name, *args):
        if self.session_handler is None:
            raise AttributeError("No session handler available")
        self.session_handler.create_table_in_file(name, *args)

    def add_to_table_in_file(self, *args, format_list=None):
        if self.session_handler is None:
            raise AttributeError("No session handler available")
        self.session_handler.add_to_table_in_file(*args, format_list=format_list)

    def save_result(self, msg):
        self.logger.error('Do not use save_result. Use add_to_table_in_file, or result.add_details, instead.')
        # raise NotImplementedError()

    # Following methods will be used with stdout redirection
    def update_status(self, message):
        self.write_text(self.EscapeForStatus + message)

    def display_device_info(self, message):
        """output for device info window
        """
        self.write_text(self.EscapeForDevice + message)

    def display_result(self, message):
        """ output for result window
        """
        self.write_text(self.EscapeForResult + message)

    def __notify_start(self):
        self.write_text(self.EscapeForStart + self.name)
        self.update_status(self.name + ' running')

    def __notify_finish(self):
        self.write_text(self.EscapeForStop + self.name)
        self.update_status(self.name + ' stopped')

    # output text to UI
    def write_text(self, text):
        self.text_written_available.emit(str(text))

    def get_input_parameter(self, name):
        if name in self.__class__.input_parameters:
            value = self.__class__.input_parameters[name].value
            self.add_details(str(value), name)
            return value
        else:
            raise KeyError('{} not in input_parameters'.format(name))

    @classmethod
    def set_input_parameter(cls, name, value):
        if name in cls.input_parameters:
            if type(cls.input_parameters[name].value) == type(value):
                cls.input_parameters[name].value = value
            else:
                 raise TypeError('Type for input_parameter {} does not match with type of {}'
                                 .format(name, value))
        else:
            raise KeyError('{} not in input_parameters'.format(name))


    # Notify UI to input_parameters for display update
    def notify_parameter_changed(self):
        self.parameter_changed.emit()

    # It needs a matching update() as a slot to run from UI
    def notify_data_available(self, data_dict={}):
        self.data_available.emit(data_dict)

    # These callbacks are used to update display for streaming data from another class or thread
    # Signals are wrapped as a callback functions 

    def data_available_callback(self, data_dict={}, *args):
        self.data_available.emit(data_dict)

    @Slot(dict)
    def update(self, data: dict):
        """
        when data_available signal emits, this method handles new data.
        By default, it only updates the matplotlib figure.
        """
        self.figure.canvas.draw_idle()
        # self.logger.error("Derive update() to use data_available signal")
        # raise NotImplementedError("Derive update() to use data_available signal")

    def scan_started_callback(self, *args):
        self.scan_started.emit()

    @Slot()
    def update_on_scan_started(self):
        """
        This method handles scan_started signal.
        """
        self.logger.error("Derive update_on_scan_started to use scan_started signal")
        # raise NotImplementedError("Derive update_on_scan_started to use scan_started signal")

    def scan_finished_callback(self, *args):
        self.scan_finished.emit()

    @Slot()
    def update_on_scan_finished(self):
        """
        This method handles scan_finished signal.
        """
        self.logger.error("Derive update_on_scan_finished() to use scan_finished signal")
        # raise NotImplementedError("Derive update_on_scan_finished() to use scan_finished signal")

    def get_instrument(self, name):
        """Get an instrument from parent's inst_dict and check its validity"""

        inst_dict = getattr(self, Task.InstrumentDict)
        if name not in inst_dict:
            self.logger.error("{} is not in Instrument dict.".format(name))
            # self.stop()
            return None

        inst = inst_dict[name]
        if not isinstance(inst, BaseInst):
            self.logger.error('{} is not an instance of {}.'
                         .format(type(inst), BaseInst.__class__.__name__))

        if not inst.is_connected():
            raise Task.TaskSetupFailed('{} is not connected'.format(name))
            return None

        model, sn, version = inst.check_id()
        self.logger.info('{} Device model: {} Version: {} S/N: {}'.format(name, model, version, sn))
        return inst

    def ask_question(self, question, return_type=bool, timeout=300.0):
        """This method display message with an OK button with return_type set to None,
        it asks a yes/no question when with return_type set to bool, and
        it asks for a string when with return_type set to str.
        This method returns True/False for a yes/no question, and
        it returns a string for the return type of str.
        it returns None if the question is aborted"""

        self.current_question = question
        self.question_return_type = return_type
        self.question_timeout = timeout
        self.parent.question_result = None
        self.parent.question_result_value = None

        self.new_question.emit(question, return_type)

        start_time = time.time()
        while time.time() - start_time < self.question_timeout:
            if not self.is_running():
                break
            if self.parent.question_result is not None:
                # if a yes/no question
                if self.question_return_type is None:
                    return True
                if self.question_return_type is bool:
                    return self.parent.question_result_value
                else:
                    # if a question asked for a value
                    return self.parent.question_result_value
            else:
                self.question_background_update()
        raise Task.TaskRunFailed("Timeout at '{}'".format(self.current_question))

    def question_background_update(self):
        time.sleep(0.1)

    def set_log_error_detail(self, state=False):
        self._log_error_detail = state

    def log_exception(self, err):
        # Capture the error
        self.logger.error(err)

        if self._log_error_detail:
            # And the stack trace
            tb_lines = traceback.format_exception(err.__class__, err, sys.exc_info()[2])
            self.logger.error(''.join(tb_lines))
