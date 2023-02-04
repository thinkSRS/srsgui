
import sys
import traceback
import logging
import time

try:
    from matplotlib.figure import Figure
except (ImportError, ModuleNotFoundError):
    msg = "\n\nPython package 'Matplotlib' is required to use Task class." \
          "\nTry again after installing 'Matplotlib' with" \
          "\n\npip install matplotlib" \
          "\n\nOr your system may have a different way to install it."
    raise ModuleNotFoundError(msg)

from .inputs import FloatInput, InstrumentInput, StringInput
from .taskresult import TaskResult, ResultLogHandler
from .callbacks import Callbacks

from srsgui.inst.instrument import Instrument

try:
    from srsgui.ui.qt.QtCore import QThread
    thread_class = QThread
except (ImportError, ModuleNotFoundError):
    from threading import Thread
    thread_class = Thread

# HTML formatter for QTextBrowser
Bold = '<font color="black"><b>{}</b></font>'
GreenBold = '<font color="green"><b>{}</b></font>'
GreenNormal = '<font color="green">{}</font>'
RedBold = '<font color="red"><b>{}</b></font>'
RedNormal = '<font color="red">{}</font>'


class Task(thread_class):
    """
    Base class for derived Task subclasses.

    The parent process starts a task instance
    as a separate thread. Before starting the task thread, the parent process injects resources
    the task thread dependent on (instruements, figures, session handler), and connects
    callback functions to handle the requests from the task. The task uses
    the resources and send requests without knowing much about how they are handled by the parent
    process. It makes easy to write a derived task as a simple Python script starting from
    the base class.
    """

    class TaskException(Exception): pass
    class TaskSetupFailed(TaskException): pass
    class TaskRunFailed(TaskException): pass
    """
    Exceptions for Task
    """

    EscapeForResult = '@RESULT@'
    EscapeForDevice = '@DEVICE@'
    EscapeForStatus = '@STATUS@'
    EscapeForStart = '@START@'
    EscapeForStop = '@STOP@'
    """
    Escape strings used in stdout redirection to GUI
    """

    input_parameters = {
        # Example float parameter
            "define parameters": FloatInput(10.0, " Hz", 1.0, 1000.0, 1.0),
            "before use!! ": StringInput(" or empty input_parameters.")
    }
    """
    Class variable to define parameters used in the task.
    values in input_parameters can be changed interactively from GUI before the task runs    
    IntegerInput, FloatInput, StringInput, ListInput and InstrumentInput can be used 
    as dictionary values.     
    """

    additional_figure_names = []  # e.g., ['Scan Plots','Temperature Plots']
    """
    Names for extra Matplotlib figures added to use in the task
    If empty, only one figure named 'plot' is available as a default.
    """

    _is_running = False  # class wide flag to tell if any instance is running

    InitialImage = None  # None for default image
    """
    Image file for parent to display instead of the default logo image when the task is selected.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self._keep_running = False
        self._aborted = False
        self._error_raised = False
        self._task_passed = True
        self._log_error_detail = False  # Enables logging traceback information

        self.name = 'Base Task'
        self.logger_prefix = ''  # used for logger name for multi-threaded tasks
        self.logger = None

        self.result = None
        self.result_log_handler = None
        self.session_handler = None
        self.callbacks = None

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
        self.logger.info("Task.setup() is not overridden.")

    def test(self):
        """
        Subclass must override this method.
        Check if is_running() is true to continue.
        Add data using in add_details, create_table, and add_data_to_table.
        """
        raise NotImplementedError("We need a real test() implemented!")

    def cleanup(self):
        """
        Subclass need to override this method
        Put any cleanup after task in the overridden method
        """
        self.logger.info('Task.cleanup() is not overridden.')

    def get_logger(self, name):
        """
        Get a logger with its handler available from the parent
        """

        if self.logger_prefix:
            n = f'{self.logger_prefix}.{name}'
        else:
            n = name
        logger = logging.getLogger(n)
        if self.result_log_handler is not None:
            logger.addHandler(self.result_log_handler)
        return logger

    def basic_setup(self):
        """
        basic_setup() runs before task-specific setup()
        """

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
        self.clear_figures()

    def basic_cleanup(self):
        """
        basic_cleanup runs after task-specific cleanup()
        """

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
                msg = '{} FINISHED'.format(self.name)
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
            self.logger.removeHandler(self.result_log_handler)

    def run(self):
        """
        Overrides Thread run() method. task-speciic test() runs inside this method.
        """
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

    def start(self):
        """
        Overrides Thread start() method.
        """

        self._keep_running = True
        self._aborted = False
        super().start()


    def stop(self):
        """
        Make is_running() returns False. A task should check is_running()
        frequently. Stop if it returns False.
        """

        if self._keep_running:
            self._aborted = True
            self._keep_running = False

    def set_session_handler(self, session_handler):
        """
        Parent should set a session handler for Task to use file output.
        """
        self.session_handler = session_handler

    def set_callback_handler(self, callback_handler: Callbacks):
        """
        Parent should set a callback handler to handle events from Task.
        """
        self.callbacks = callback_handler

    @staticmethod
    def _check_dict_items(item_dict, item_class):
        if type(item_dict) is not dict:
            return False
        for value in item_dict.values():
            if not issubclass(type(value), item_class):
                return False
        return True

    def set_inst_dict(self, inst_dict):
        """
        Parent should set inst_dict for Task to use instruments available from the parent.
        """

        if not self._check_dict_items(inst_dict, Instrument):
            raise AttributeError('invalid inst_dict for Task class')
        self.inst_dict = inst_dict

    def set_data_dict(self, data_dict):
        """
        A dictionary injected when the task run. It is a way to share data among different tasks
        Do not reset the whole dictionary unless you know what you are doing.
        """
        self.data_dict = data_dict

    def set_figure_dict(self, figure_dict):
        """
        Parent should set figure_dict for Task to use Matplotlib figures available from the parent.
        """

        if not self._check_dict_items(figure_dict, Figure):
            raise AttributeError('invalid figure_dict for Task class')
        self.figure_dict = figure_dict
        if figure_dict:
            self.figure = list(figure_dict.values())[0]
        else:
            self.figure = None
            raise ValueError('No figure in figure_dict to set as default')

    def get_figure(self, name=None) -> Figure:
        """
        Get a Matplotlib figure from figure_dict.
        if name is None, it will reutrn the first figure in figure_dict as the defualt
        """

        if name is None:
            name = list(self.figure_dict.keys())[0]
        if name in self.figure_dict:
            return self.figure_dict[name]
        raise KeyError('Invalid figure name: {}'.format(name))

    def clear_figures(self):
        """
        Clear all the figures in figure_dict
        """
        for fig in self.figure_dict.values():
            if hasattr(fig, 'canvas'):
                fig.clear()
                self.request_figure_update()

    def is_running(self):
        """
        Task should check is_running() is True.
        If it returns False, Task should stop ASAP.
        """
        return self._keep_running

    def is_task_passed(self):
        return self._task_passed

    def set_task_passed(self, status):
        if status:
            self._aborted = False
        self._task_passed = status
        self.result.set_passed(status)

    def is_error_raised(self):
        """
        Check if Task stopped with an error
        """
        return self._error_raised

    def set_error_raised(self):
        """
        Mark Task is stopped with an error
        """
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
            value = param.get_value()
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
        self.request_figure_update(figure)

    # It needs a matching update() as a slot to run from UI
    def notify_data_available(self, data={}):
        self.callbacks.data_available(data)

    # These callbacks are used to update display for streaming data from another class or thread
    # Signals are wrapped as a callback functions 

    def data_available_callback(self, data={}, *args):
        self.callbacks.data_available(data)

    def update(self, data: dict):
        """
        when data_available signal emits, this method handles display update.
        By default, it does no data handling, but figure update request.
        GUI related data processing needs to be done here to be handled
        in proper order by the GUI event loop handler.
        """
        self.request_figure_update()

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
        """Set True To log exception traceback for debugging
        """
        self._log_error_detail = state

    def log_exception(self, err):
        """With set_log_error_detail(True), an error is looged with traceback information
        """
        self.logger.error(f'{err.__class__.__name__}: {err}')

        if self._log_error_detail:
            # And the stack trace
            tb_lines = traceback.format_exception(err.__class__, err, sys.exc_info()[2])
            self.logger.error(''.join(tb_lines))
