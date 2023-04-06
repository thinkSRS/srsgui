import sys
import os
import logging
from pathlib import Path
from importlib import import_module, reload, invalidate_caches

from srsgui.task import GreenNormal, RedNormal
from srsgui.task.task import Task

# from srs_insts.baseinsts import BaseInst
from srsgui.inst.instrument import Instrument

logger = logging.getLogger(__name__)


class Config(object):
    ResultDirectory = 'task-results'
    DataRootDirectory = str(Path.home() / ResultDirectory)
    LocalModulePath = ['tasks', 'instruments', 'plots']

    def __init__(self):
        self.inst_dict = {}
        self.task_dict = {}
        self.task_path_dict = {}
        self.task_dict_name = 'No tasks loaded'
        self.local_db_name = None
        self.base_data_dir = self.DataRootDirectory
        p = Path(self.base_data_dir)
        if not p.exists():
            p.mkdir(parents=True)
        self.base_log_file_name = self.get_base_log_file_name()

    def _remove_modules(self):
        for root in self.LocalModulePath:
            if root in sys.modules:
                sys.modules.pop(root)

            keys = list(sys.modules.keys())
            for mod in keys:
                if mod.startswith(root + '.'):
                    sys.modules.pop(mod)

    def load(self, file_name):
        current_line = ""
        try:
            self._remove_modules()

            with open(file_name, "r") as f:
                invalidate_caches()
                self.inst_dict = {}
                self.task_dict = {}

                for line in f:
                    current_line = line.strip()
                    if current_line.startswith('#'):
                        continue
                    if ':' in current_line:
                        k, v = current_line.split(':', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        if k == 'task':
                            self.load_task_from_line(v)

                        elif k == 'inst':
                            self.load_inst_from_line(v)

                        elif k == 'name':
                            self.task_dict_name = v
                        else:
                            raise KeyError('Invalid key: {}'.format(k))

            logger.info('TaskConfig file "{}" loaded'.format(file_name))

            # Local DB file name for SessionHandler
            self.data_dir = self.base_data_dir + '/' + self.task_dict_name
            p = Path(self.data_dir)
            if not p.exists():
                p.mkdir(parents=True)

        except FileNotFoundError:
            logger.error('File "{}" not found'.format(file_name))
            raise FileNotFoundError

        except Exception as e:
            logger.error("load_config_error: {}".format(e))
            logger.error("Error in line: {}".format(current_line))
            raise e.__class__

    def load_task_from_line(self, v):
        task_name, task_module_name, task_class_name = v.split(',', 2)
        tokens = task_name.strip().split('/')
        task_tokens = [token.strip() for token in tokens]
        if len(task_tokens) == 1:
            task_key = task_tokens[-1]
            task_path = ''
        else:
            task_key = task_tokens[-1]
            task_path = '/'.join(task_tokens[:-1])

        task_module = task_module_name.strip()

        if task_module in sys.modules:
            reload(sys.modules[task_module])
            mod = sys.modules[task_module]
        else:
            mod = import_module(task_module)
            logger.debug('Task module {} for "{}" loaded '.format(mod.__file__, task_key))

        task_class_name = task_class_name.strip()
        if hasattr(mod, task_class_name):
            task_class = getattr(mod, task_class_name)
            logger.debug('Task class {} for "{}" loaded'.format(task_class_name, task_key))
        else:
            logger.error('No task class: {} in module: {}'.format(task_class_name, task_module))
            return
        if not issubclass(task_class, Task):
            logger.error('{} is NOT a Task subclass'.format(task_class_name))
            return
        if task_key in self.task_dict:
            logger.error('"{}" already used in task_dict')
            return
        self.task_dict[task_key] = task_class
        self.task_path_dict[task_key] = task_path

    def load_inst_from_line(self, v):
        items = v.split(',')
        if len(items) < 3 or len(items) > 4:
            logger.error('invalid inst line: {}'.format(v))
            return

        inst_key = items[0].strip()
        inst_module_name = items[1].strip()
        inst_class_name = items[2].strip()
        mod = import_module(inst_module_name)
        logger.debug('Instrument module {} for "{}" loaded'.format(mod.__file__, inst_key))
        inst_class_name = inst_class_name

        if hasattr(mod, inst_class_name):
            inst_class = getattr(mod, inst_class_name)
            inst_class.__version = None
            if hasattr(mod, '__version__'):
                inst_class.__version__ = getattr(mod, "__version__")
            logger.debug('Instrument class {} from "{}" loaded'.format(inst_class_name, inst_key))
        else:
            logger.error('No inst class "{}" in module "{}"'.format(inst_class_name, inst_module_name))
            return

        if not issubclass(inst_class, Instrument):
            logger.error('Not a Instrument subclass')
            return

        self.inst_dict[inst_key] = inst_class()
        self.inst_dict[inst_key].set_name(inst_key)
        num = len(items)
        if num == 4:
            try:
                parameter_string = items[3]
                inst = self.inst_dict[inst_key]
                inst.connect_with_parameter_string(parameter_string)
            except Exception as e:
                logger.error(e)

    def get_base_log_file_name(self):
        max_file_number = 20
        return_value = None
        file_name_format = self.base_data_dir + '/mainlog-{:02d}.txt'
        for i in range(max_file_number):
            try:
                file_name = file_name_format.format(i)
                if os.path.exists(file_name):
                    os.remove(file_name)
                return_value = file_name
                break
            except:
                pass
        return return_value
