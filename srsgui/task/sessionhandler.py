
import json
import logging
from pathlib import Path
from datetime import datetime

from srsgui.task.taskresult import TaskResult

RedBold = '<font color="red"><b>{}</b></font>'
logger = logging.getLogger(__name__)


class SessionHandler(object):
    def __init__(self, use_file=False, use_db=False, use_api=False):
        self.use_file = False
        self.use_db = False
        self.use_api = False
        self._is_session_open = False
        self.serial_number = None

        self.path = None
        self.output_file = None
        self.is_file_open = False
        self.table_info = {}

        self.use_file = use_file
        self.use_db = use_db
        self.use_api = use_api
        self.current_session = None

        self.base_data_dir = None
        self.task_dict_name = None
        self.data_dir = None

        if self.use_api:
            pass

        elif self.use_db:
            pass

    def is_open(self):
        return self._is_session_open

    def set_data_directory(self, base_dir, task_dict_name):
        self.base_data_dir = base_dir
        self.task_dict_name = task_dict_name

    def open_session(self, sn, reuse_last_session=True):
        self.serial_number = sn
        if self.use_file:
            if not (self.base_data_dir and self.task_dict_name):
                logger.error('Data directory is not set: use set_data_directory()')
                self._is_session_open = False
                return

            self.data_dir = self.get_data_dir(sn, reuse_last_session)
            logger.info(f'Session directory is set to {self.data_dir}.')
            self._is_session_open = True
        self.current_session = None  # reset the current session

        return self._is_session_open

    def close_session(self, is_passed=False):
        if not self._is_session_open:
            logger.error("Error in close_session: No session opened")
            return

        self._is_session_open = False
        self.serial_number = None
        if self.use_file:
            self.close_data_dir()

        self.current_session = None
        logger.info('Current session is closed as {}.'.format('PASS' if is_passed else 'FAIL'))

    def create_new_task_result(self, result: TaskResult):
        if self.use_file:
            # Make sure output_file open
            self.add_dict_to_file('TaskResult', result.__dict__)
            logger.debug('Task result Saved')

    def create_file(self, task_name):
        self.path = Path(self.data_dir)
        if not self.path.exists():
            self.path.mkdir(parents=True)
        # file_name = task_name + '-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.txt'
        file_name = '{}-{}.txt'.format(task_name, datetime.now().strftime('%Y%m%d-%H%M%S'))
        logger.debug('Output file opened as {}\\{}'.format(self.path, file_name))
        self.output_file = open(self.path / file_name, 'w', 1)
        self.is_file_open = True
        self.table_info = {}

    def add_dict_to_file(self, name, data_dict):
        if not self.is_file_open:
            raise IOError('File is not open')
        self.output_file.write('\n:::JSON-{}:::\n'.format(name))
        json.dump(data_dict, self.output_file)
        self.output_file.write('\n:::JSONEND-{}:::\n'.format(name))

    def create_table_in_file(self, name, *args):
        """args: list of header string"""
        if name in self.table_info:
            raise KeyError('Table "{}" already exists'.format(name))

        self.table_info[name] = {'index': len(self.table_info),
                                 'size': len(args)}
        # Write the table name
        self.output_file.write('\nTN:{}, {}\n'.format(self.table_info[name]['index'], name))
        # Write the table header
        self.output_file.write('TH:{}, '.format(self.table_info[name]['index']))
        self.output_file.write(', '.join(map(str, args)) + '\n')

    def add_to_table_in_file(self, name, *args, format_list=None):
        no_of_cols = len(args)
        if name not in self.table_info:
            raise KeyError('Invalid table name: {}'.format(name))
        if no_of_cols != self.table_info[name]['size']:
            raise ValueError('Length of data does not match with header in "{}"'.format(name))
        # Write a table row
        self.output_file.write('TD:{}, '.format(self.table_info[name]['index']))
        if format_list:
            self.output_file.write(', '.join(format_list).format(*args) + '\n')
        else:
            self.output_file.write(', '.join(['{}'] * no_of_cols).format(*args) + '\n')

    def close_file(self):
        self.output_file.close()
        self.is_file_open = False
        logger.debug('Output file closed')

    def close_data_dir(self):
        self.create_file('DirClosed-')
        self.close_file()

    def is_data_dir_closed(self, directory):
        for f in Path(directory).iterdir():
            if f.name.startswith('DirClosed'):
                logger.debug(f'{self.data_dir} is a closed session.')
                return True
        return False

    def get_data_dir(self, serial_number, reuse_last_run_number=True):
        # Dir for task_dict
        task_data_dir = self.base_data_dir + '/' + self.task_dict_name

        # Dir for connected DUT
        unit_data_dir = task_data_dir  # No SN + '/SN' + str(serial_number).strip()
        unit_path = Path(unit_data_dir)
        if not unit_path.exists():
            unit_path.mkdir(parents=True)

        run_number = self.get_last_run_number(unit_data_dir)
        if reuse_last_run_number and run_number > 0:
            run_dir = unit_data_dir + '/RN' + '{:03d}'.format(run_number)
            if self.is_data_dir_closed(run_dir):
                run_number += 1
            else:
                return run_dir
        else:
            run_number += 1

        run_dir = unit_data_dir + '/RN' + '{:03d}'.format(run_number)
        logger.debug("Session directory set to {}".format(run_dir))
        return run_dir

    @staticmethod
    def get_last_run_number(unit_data_dir):
        run_number_limit = 1000
        p = Path(unit_data_dir)
        run_dir_list = [x.parts[-1] for x in p.iterdir() if x.is_dir() and x.parts[-1][:2] == 'RN']
        if len(run_dir_list) == 0:
            return 0
        max_rn = 1
        for i in run_dir_list:
            try:
                rn = int(i[2:])
                if (rn > max_rn) and (rn < run_number_limit):
                    max_rn = rn
            except ValueError:
                continue
        return max_rn
