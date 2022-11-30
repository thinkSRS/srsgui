

from datetime import datetime

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def timestamp_now():
    return datetime.now().isoformat()


def strip_tags(message):
    """Removes HTML tags"""
    tag_enabled = False
    mod = ''
    for i in message:
        if i == '<':
            tag_enabled = True
            continue
        elif i == '>':
            tag_enabled = False
            continue
        if not tag_enabled:
            mod += i
    return mod


class ResultLogHandler(logging.Handler):
    def __init__(self, task_result):
        if not hasattr(task_result, 'log'):
            logging.error("ResultLogHandler needs a 'log' attribute")
            raise AttributeError

        super().__init__()
        self.task_result = task_result
        self.task_result.log = ""
        if hasattr(self, 'error'):
            delattr(self, 'error')

    def emit(self, record):
        try:
            msg = self.format(record)
            mod = strip_tags(msg).strip()

            if mod:
                self.task_result.log += mod + '\n'

                if record.levelno >= logging.ERROR:
                    if not hasattr(self.task_result, 'error'):
                        self.task_result.error = record.message + '\n'
                    else:
                        self.task_result.error += record.message + '\n'

        except Exception as e:
            print('Logging error: {}'.format(e))


class TaskResult:
    """An object that stores relevant test result data

    Any data stored in attributes of this object will
    end up saved in the database

    Be sure to store only json-serializable objects in
    the attributes of this class (i.e. only python primitives
    like dict, list, str, int) or it will throw an error
    when it tries to store it in a database
    """
    reserved = {}

    def __init__(self, task_class_name, task_id=None):
        # these will reflect the values configured in your test classes
        self.task_class_name = task_class_name

        # No idea what to do with task_id
        # self.task_id = task_id

        # these are automatically filled in by the test runner mechanism
        self.start_time = None
        self.stop_time = None
        self.passed = None
        self.log = ""
        TaskResult.reserved = list(self.__dict__.keys())

        logger.debug('Reserved for TestResults: {}'.format(self.reserved))

    def clear(self):
        self.start_time = None
        self.stop_time = None
        self.passed = None
        self.log = ""
        if hasattr(self, 'error'):
            delattr(self, 'error')

    def set_start_time_now(self):
        self.start_time = timestamp_now()

    def set_stop_time_now(self):
        self.stop_time = timestamp_now()

    def set_aborted(self, state=True):
        if state:
            self.passed = None

    def set_passed(self, state=True):
        self.passed = state

    def append_error(self, msg):
        if not hasattr(self, 'error'):
            setattr(self, 'error', msg)
        else:
            self.error += msg

    def add_details(self, msg: str, key='summary'):
        if key in TaskResult.reserved:
            msg = '{} is reserved'.format(key)
            logger.error(msg)
            raise AttributeError(msg)

        if not hasattr(self, key):
            setattr(self, key, msg)
        else:
            setattr(self, key, getattr(self, key) + ' {}'.format(msg))

    def create_table(self, name: str, *args):
        setattr(self, name, [args])
        logger.debug('table {} is created as {}'.format(name, getattr(self, name)))

    def add_data_to_table(self, name: str, *args):
        if type(getattr(self, name)) is not list:
            raise TypeError('Attr {} is not a list'.format(name))
        if len(getattr(self, name)[0]) != len(args):
            raise ValueError('Data length does not match with the header')
        getattr(self, name).append(args)
