import sys
import os
import logging
from pathlib import Path
from importlib import import_module, reload, invalidate_caches

from rgagui.base import Task, GreenNormal, RedNormal

# from srs_insts.baseinsts import BaseInst
from rga.base import Instrument

logger = logging.getLogger(__name__)


class Config(object):
    ResultDirectory = 'task-results'
    LogoImageFile = 'images/srslogo.jpg'
    DataRootDirectory = str(Path.home() / ResultDirectory)
    LogoFile = str(Path(__file__).parent / LogoImageFile)
    LocalModulePath = ['tasks', 'instruments']

    def __init__(self):
        self.inst_dict = {}
        self.task_dict = {}
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
        task_key, task_module_name, task_class_name = v.split(',', 2)
        task_key = task_key.strip()
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
        self.task_dict[task_key] = task_class

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
            logger.debug('Instrument class {} for "{}" loaded'.format(inst_class_name, inst_key))
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
            parameter_string = items[3]
            success = self.set_default_connect_parameters(self.inst_dict[inst_key],
                                                          parameter_string)
            if success:
                try:
                    self.connect_with_default_parameters(self.inst_dict[inst_key])
                    # logger.debug('check_id returns: {}, {}, {}'.format(
                    # self.inst_dict[inst_key].check_id()))
                    logger.info(GreenNormal.format(
                        '{} is connected with default parameters: {}'.format(
                            inst_key, parameter_string)))

                except Exception as e:
                    logger.error(e)
                    logger.error(RedNormal.format(
                        '{} failed to connect with default parameters {}'.format(
                            inst_key, items[3])))

    def get_logo_file(self):
        return self.LogoFile

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

    def set_default_connect_parameters(self, inst, parameter_string):
        inst.default_connect_parameters = []
        params = parameter_string.split(':')
        num = len(params)
        interface_type = params[0].strip().lower()
        if interface_type == Instrument.SERIAL:
            if num > 4:
                return False # too many parameters
            if num > 1:
                inst.default_connect_parameters.append(interface_type)  # 'serial'
                inst.default_connect_parameters.append(params[1])  # port name
            if num > 2:
                inst.default_connect_parameters.append(int(params[2]))  # baud rate
            if num > 3:
                inst.default_connect_parameters.append(params[3].upper == 'TRUE')  # hardware flow control
            return True

        elif interface_type == Instrument.TCPIP:
            if num > 5:
                return False
            inst.default_connect_parameters.append(interface_type)  # 'tcpip'
            if num == 2:
                inst.default_connect_parameters.append(params[1])  # ip address
                return True
            if num == 3:
                inst.default_connect_parameters.append(params[1])  # ip address
                inst.default_connect_parameters.append(int(params[2]))  # port number
                return True
            if num == 4:
                inst.default_connect_parameters.append(params[1])  # ip address
                inst.default_connect_parameters.append(params[2])  # user name
                inst.default_connect_parameters.append(params[3])  # password
                return True
            if num == 5:
                inst.default_connect_parameters.append(params[1])  # ip address
                inst.default_connect_parameters.append(params[2])  # user name
                inst.default_connect_parameters.append(params[3])  # password
                inst.default_connect_parameters.append(int(params[4]))  # port number
                return True
        inst.default_connect_parameters.clear()
        print("Invalid connect parameters", params)
        return False

    def connect_with_default_parameters(self, inst):
        inst.connect(*inst.default_connect_parameters)
