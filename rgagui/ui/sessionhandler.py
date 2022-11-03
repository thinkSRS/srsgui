
import json
import logging
from pathlib import Path
from datetime import datetime

# from wip.local_results import LocalClient
# from wip.wip_api import DutNotRegisteredError

from rgagui.base.taskresult import TaskResult

RedBold = '<font color="red"><b>{}</b></font>'
logger = logging.getLogger(__name__)

logging.getLogger('urllib3').setLevel(logging.WARNING)


class SessionHandler(object):
    def __init__(self, config, use_file=False, use_db=False, use_api=False):
        self.config = None
        self.use_file = False
        self.use_db = False
        self.use_api = False
        self._is_session_open = False
        self.serial_number = None

        self.path = None
        self.output_file = None
        self.is_file_open = False
        self.no_of_columns = 0

        if use_file or use_db:
            if not hasattr(config, 'base_data_dir'):
                raise AttributeError('Parent has no base_data_dir')
            if not hasattr(config, 'task_dict_name'):
                raise AttributeError('Parent has no task_dict_name')

        self.config = config

        self.use_file = use_file
        self.use_db = use_db
        self.use_api = use_api
        self.data_dir = self.config.base_data_dir
        self.current_session = None
        self.local_db_name = self.config.local_db_name

        if self.use_api:
            self.client = self.config.get_WIP_client()

        elif self.use_db:
            self.client = LocalClient(self.local_db_name)
            self.client.connect()

    def is_open(self):
        return self._is_session_open

    def open_session(self, sn, reuse_last_session=True):
        self.serial_number = sn
        if self.use_file:
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

        if self.use_api:
            self.client.create_new_test_result(self.current_session, result)
            logger.debug('Task result added to API session')
        elif self.use_db:
            logger.debug('Task result added to the local DB')
            self.client.create_new_test_result(self.current_session, result)

    def upload_local_results(self, serial_number):
        if self.use_api:
            try:
                self.client.api.get_built_part(serial_number)
                logger.info(f'S/N {serial_number} registered with API server')
                sessions = self.client.search_test_sessions(uploaded=False,
                                                            serial_number=serial_number,
                                                            sessions_only=None,
                                                            results_only=None)
                if len(sessions) > 0:
                    ids = [s['rowid'] for s in sessions]
                    self.client.upload_local_results(ids)
                    logger.info(f'rowid {ids} uploaded')
            except DutNotRegisteredError:
                logger.error(RedBold.format(f'S/N: {serial_number} not registered with API server'))
            except Exception as e:
                logger.error(e)

    def get_session_status(self):
        """ extract pass states of test result in the current session"""

        task_status_dict = {}
        results = self.client.get_test_session_results(self.current_session['id'])
        if self.use_api:
            results.reverse()
        for result in results:
            task_status_dict[result.task_class_name] = True if result.passed else False
        return task_status_dict

    def create_file(self, task_name):
        self.path = Path(self.data_dir)
        if not self.path.exists():
            self.path.mkdir(parents=True)
        # file_name = task_name + '-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.txt'
        file_name = '{}-{}.txt'.format(task_name, datetime.now().strftime('%Y%m%d-%H%M%S'))
        logger.debug('Output file opened as {}\\{}'.format(self.path, file_name))
        self.output_file = open(self.path / file_name, 'w')
        self.is_file_open = True

    def add_dict_to_file(self, name, data_dict):
        if not self.is_file_open:
            raise IOError('File is not open')
        self.output_file.write(':::DICT-{}:::\n'.format(name))
        json.dump(data_dict, self.output_file)

    def create_table_in_file(self, name, *args):
        """argv: list of header string"""
        self.no_of_columns = len(args)
        self.output_file.write(':::TABLE-{}:::\n'.format(name))
        self.output_file.write(', '.join(map(str, args)) + '\n')

    def add_to_table_in_file(self, *args, format_list=None):
        if len(args) != self.no_of_columns:
            raise ValueError('Length of data doe not match with header')

        if format_list:
            self.output_file.write(', '.join(format_list).format(*args) + '\n')
        else:
            self.output_file.write(', '.join(['{}'] * self.no_of_columns).format(*args) + '\n')

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
        task_data_dir = self.config.base_data_dir + '/' + self.config.task_dict_name

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
