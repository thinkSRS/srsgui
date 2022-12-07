
import sys
import traceback
import logging
import time

# from threading import Thread
from rgagui.ui.qt.QtCore import QThread

from matplotlib.figure import Figure

from .inputs import FloatInput, InstrumentInput
from .taskresult import TaskResult, ResultLogHandler
from .callbacks import Callbacks

from rgagui.inst.instrument import Instrument

# HTML formatter for QTextBrowser
Bold = '<font color="black"><b>{}</b></font>'
GreenBold = '<font color="green"><b>{}</b></font>'
GreenNormal = '<font color="green">{}</font>'
RedBold = '<font color="red"><b>{}</b></font>'
RedNormal = '<font color="red">{}</font>'


class Task(QThread):
    """ Base class for all task classes
    """

    class TaskException(Exception): pass
    class TaskSetupFailed(TaskException): pass
    class TaskRunFailed(TaskException): pass

    # When parent is not None, parent should have these attributes.
    InstrumentDictName = 'inst_dict'  # all instruments to use in a task
    FigureDictName = 'figure_dict'  # all Matplotlib figures to use in a task
    SessionHandlerName = 'session_handler'

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

    # Names for multiple  Matplotlib figures you will use in this task
    # If empty, you will have one figure named 'Figure' as a default
    additional_figure_names = []  # e.g., ['Scan Plots','Temperature Plots']

    _is_running = False  # class wide flag to tell if any instance is running
    _is_optional = False  # result status will set as success initially if a task class is optional

    # Image information for parent to display instead of the default logo image before instantiated
    InitialImage = None  # None for default image

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
        self.callbacks = Callbacks()

        # inst_dict holds all the instrument to use in task
        self.inst_dict = {}
        self.data_dict = {}

        # figure is expected to be Matplotlib figure object.
        self.figure_dict = {}
        self.figure = None

        self.round_float_resolution = 4

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
        if self.figure is None or not hasattr(self.figure, 'canvas'):
            raise AttributeError('Invalid figure')

        if not self._check_dict_items(self.inst_dict, Instrument):
            raise AttributeError('Invalid inst_dict detected during basic setup')

        self.callbacks.started()

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

        self._notify_start()
        self.clear()

    def basic_cleanup(self):
        try:
            Task._is_running = False
            self._keep_running = False
            self._notify_finish()
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
            self.callbacks.finished()
        except Exception as e:
            self.log_exception(e)

    # Override for QThread start
    def start(self):
        # if Task._is_running: # Disable for multiple tasks running
        #     raise RuntimeError('Another task is running')

        self._keep_running = True
        self._aborted = False
        super().start()
        # self.logger.debug("{} start completed".format(self.name))

    def stop(self):
        if self._keep_running:
            self._aborted = True
            self._keep_running = False

    def set_session_handler(self, session_handler):
        self.session_handler = session_handler

    def set_signal_handler(self, signal_handler: Callbacks):
        self.callbacks = signal_handler

    @staticmethod
    def _check_dict_items(item_dict, item_class):
        if type(item_dict) is not dict:
            return False
        for value in item_dict.values():
            if not issubclass(type(value), item_class):
                return False
        return True

    def set_inst_dict(self, inst_dict):
        if not self._check_dict_items(inst_dict, Instrument):
            raise AttributeError('invalid inst_dict for Task class')
        self.inst_dict = inst_dict

    def set_figure_dict(self, figure_dict):
        if not self._check_dict_items(figure_dict, Figure):
            raise AttributeError('invalid figure_dict for Task class')
        self.figure_dict = figure_dict
        if figure_dict:
            self.figure = list(figure_dict.values())[0]
        else:
            self.logger.error('No figure to set as default')
            self.figure = None

    def get_figure(self, name=None) -> Figure:
        if name is None:
            name = list(self.figure_dict.keys())[0]
        if name in self.figure_dict:
            return self.figure_dict[name]
        raise KeyError('Invalid figure name: {}'.format(name))

    def clear(self):
        """
        Clear figures
        """
        for fig in self.figure_dict.values():
            if hasattr(fig, 'canvas'):
                fig.clear()
                fig.canvas.draw_idle()

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
        self.display_result('{}: {}'.format(key, msg))

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

    def round_float(self, number):
        # set the resolution of the number with self.round_float_resolution
        fmt = '{{:.{}e}}'.format(self.round_float_resolution)
        return float(fmt.format(number))

    # Following methods will be used with stdout redirection
    def update_status(self, message):
        self.write_text(self.EscapeForStatus + message)

    def display_device_info(self, message='', device_name=None, update=False,  clear=False):
        """output to device info windows
        """
        if update:
            if device_name:
                self.write_text('{}{}:update'.format(self.EscapeForDevice, device_name))
            else:
                name = list(self.inst_dict.keys())[0]
                self.write_text('{}{}:update'.format(self.EscapeForDevice, name))
            return

        if clear:
            if device_name:
                self.write_text('{}{}:cls'.format(self.EscapeForDevice, device_name))
            else:
                self.write_text('{}cls'.format(self.EscapeForDevice))

        if device_name:
            self.write_text('{}{}:{}'.format(self.EscapeForDevice, device_name, message))
        else:
            self.write_text('{}{}'.format(self.EscapeForDevice, message))

    def display_result(self, message, clear=False):
        """ output to the result window
        """
        if clear:
            self.write_text('{}cls'.format(self.EscapeForResult))
        self.write_text('{}{}'.format(self.EscapeForResult, message))

    def _notify_start(self):
        self.write_text(self.EscapeForStart + self.name)
        self.update_status(self.name + ' running')

    def _notify_finish(self):
        self.write_text(self.EscapeForStop + self.name)
        self.update_status(self.name + ' stopped')

    # output text to UI
    def write_text(self, text):
        self.callbacks.text_available(str(text))

    def get_input_parameter(self, name):
        if name in self.__class__.input_parameters:
            param = self.__class__.input_parameters[name]
            if type(param) == InstrumentInput:
                value = self.__class__.input_parameters[name].text
            else:
                value = self.__class__.input_parameters[name].value
            if not hasattr(self.result, name):
                self.add_details(str(value), name)
            return value
        else:
            raise KeyError('{} not in input_parameters'.format(name))

    def get_all_input_parameters(self):
        d = {}
        for name in self.__class__.input_parameters:
            value = self.get_input_parameter(name)
            d[name] = value
        return d

    @classmethod
    def set_input_parameter(cls, name, value):
        if name in cls.input_parameters:
            param = cls.input_parameters[name]
            if type(param) == InstrumentInput:
                if type(cls.input_parameters[name].text) == type(value):
                    cls.input_parameters[name].text = value
                else:
                    raise TypeError('Type for input_parameter "{}" is {}'
                                    .format(name, type(value)))
            elif type(cls.input_parameters[name].value) == type(value):
                cls.input_parameters[name].value = value
            else:
                raise TypeError('Type for input_parameter "{}" is {}'
                                .format(name, type(value)))
        else:
            raise KeyError('{} not in input_parameters'.format(name))

    # Notify UI to input_parameters for display update
    def notify_parameter_changed(self):
        self.callbacks.parameter_changed()

    def request_figure_update(self, figure=None):
        if type(figure) is not Figure:
            figure = self.figure
        self.callbacks.figure_update_requested(figure)

    def update_figure(self, figure: Figure):
        if type(figure) is not Figure:
            raise TypeError('{} is not  a Figure'.format(type(figure)))
        figure.canvas.draw_idle()

    # It needs a matching update() as a slot to run from UI
    def notify_data_available(self, data_dict={}):
        self.callbacks.data_available(data_dict)

    # These callbacks are used to update display for streaming data from another class or thread
    # Signals are wrapped as a callback functions 

    def data_available_callback(self, data_dict={}, *args):
        self.callbacks.data_available(data_dict)

    def update(self, data: dict):
        """
        when data_available signal emits, this method handles new data.
        By default, it only updates the matplotlib figure.
        """
        self.figure.canvas.draw_idle()
        # self.logger.error("Derive update() to use data_available signal")
        # raise NotImplementedError("Derive update() to use data_available signal")

    def get_instrument(self, name):
        """Get an instrument from parent's inst_dict and check its validity"""

        if name not in self.inst_dict:
            self.logger.error("{} is not in Instrument dict.".format(name))
            return None

        inst = self.inst_dict[name]
        if not isinstance(inst, Instrument):
            self.logger.error('{} is not an instance of {}.'
                              .format(type(inst), Instrument.__class__.__name__))

        if not inst.is_connected():
            raise Task.TaskSetupFailed('{} is not connected'.format(name))

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

        self.callbacks.new_question(question, return_type)

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
