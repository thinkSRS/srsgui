
import os
import sys

import logging
import logging.handlers

from pathlib import Path

from .qt import QT_BINDER, PYSIDE6, QT_BINDER_VERSION
from .qt.QtCore import QTimer, QSettings
from .qt.QtWidgets import QMainWindow, QApplication, QTextBrowser,\
                                QVBoxLayout, QMessageBox, \
                                QInputDialog, QFileDialog, \
                                QMenu, QAction

from .ui_taskmain import Ui_TaskMain

from .connectdlg import ConnectDlg

from .inputpanel import InputPanel
from .signalhandler import SignalHandler

from .stdout import StdOut
from .qtloghandler import QtLogHandler
from .deviceinfohandler import DeviceInfoHandler

from .dockhandler import DockHandler

from srsgui.task.config import Config
from srsgui.task.sessionhandler import SessionHandler
from srsgui.task.task import Task, Bold

from srsgui import __version__

logger = logging.getLogger(__name__)


class TaskMain(QMainWindow, Ui_TaskMain):
    """
    The main window of the SRSGUI application
    """

    DefaultConfigFile = str(Path(__file__).parent.parent /
        "examples/oscilloscope example/oscilloscope example project.taskconfig")

    OrganizationName = 'srsinst'
    ApplicationName = 'srsgui'

    LogoImageFile = 'srslogo.jpg'
    LogoFile = str(Path(__file__).parent / LogoImageFile)

    def __init__(self, parent=None):
        super(TaskMain, self).__init__(parent)
        self.setupUi(self)
        # self.taskResult.setFontFamily('monospace')

        QApplication.setOrganizationName(self.OrganizationName)
        QApplication.setApplicationName(self.ApplicationName)
        self.settings = QSettings()

        # The dict holds subclass of Task
        self.task_dict = {}
        self.task_menus = []
        self.current_task_action = None
        self.task = None
        self.task_method = None

        self.question_result = None
        self.question_result_value = None

        # data_dict hold data shared among task. It will inject to a task when run
        self.data_dict = {}

        # self.inst_dict holds instances of subclass of Instrument
        self.inst_dict = {}
        self.inst_info_handler = DeviceInfoHandler(self)

        self.dock_handler = DockHandler(self)
        self.command_handler = self.dock_handler.terminal_command_handler
        self.console = self.dock_handler.console
        self.terminal_widget = self.dock_handler.terminal_widget
        self.plotDockWidget = self.dock_handler.get_dock()

        # Make the terminal not blocking for log query

        self.geometry_dict = {}
        try:
            default_config_file = self.DefaultConfigFile
            self.config = Config()
            self.base_data_dir = self.config.base_data_dir
            self.base_log_file_name = self.config.base_log_file_name

            self.taskParameter = QTextBrowser()
            layout = QVBoxLayout()
            layout.addWidget(self.taskParameter)
            self.taskParameterFrame.setLayout(layout)

            # Load task configuration after init
            self.initial_load = True
            QTimer.singleShot(0, self.load_tasks)

        except Exception as e:
            logger.error(e)

        # Setup toolbar buttons
        self.actionRun.setEnabled(True)
        self.actionStop.setEnabled(False)

        # busy flag is used to tell if a task is running
        self._busy_flag = False
        self.is_selection_running = False

        self.qt_log_handler = QtLogHandler(self.console)
        self.qt_log_handler.setLevel(logging.INFO)

        log_file = self.base_log_file_name

        self.file_log_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=100000, backupCount=10)

        logging.basicConfig(handlers=[self.qt_log_handler, self.file_log_handler],
                            format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
                            level=logging.DEBUG)

        # Session handler for TaskResult output
        self.session_handler = None

        # self.load_settings()
        QTimer.singleShot(0, self.load_settings)
        self.default_config_file = self.settings.value("ConfigFile", "", type=str)
        if not self.default_config_file:
            self.default_config_file = default_config_file

        self.statusbar.showMessage('Waiting for task selection')
        self.stdout = StdOut(self.print_redirect)

        self.about = QAction(self)
        self.about.setText('About')
        self.menu_Help.addAction(self.about)
        self.about.triggered.connect(self.onAbout)

        self.menu_Tasks.triggered.connect(self.onTaskSelect)
        self.menu_Instruments.triggered.connect(self.onInstrumentSelect)

    def load_tasks(self):
        try:
            # Clear console and result display
            self.console.clear()
            self.taskResult.clear()
            self.terminal_widget.tbCommand.clear()

            if self.initial_load:
                logger.info('Python started from "{}"'.format(sys.exec_prefix))
                logger.info('srsgui started from "{}"'.format(Path(__file__).parent.parent))
            # Disconnect previously used instruments
            prev_inst_dict = self.inst_dict
            try:
                for key in prev_inst_dict:
                    instr = prev_inst_dict[key]
                    if hasattr(instr, 'disconnect'):
                        instr.disconnect()
            except Exception as e:
                logger.error(e)

            # Check if argument is given in the command line
            if self.initial_load and len(sys.argv) == 2 and sys.argv[1].split('.')[-1].lower() == 'taskconfig':
                self.default_config_file = sys.argv[1]
                self.initial_load = False
            else:
                popped_path = sys.path.pop()
                logger.debug('"{}" removed from sys.path'.format(popped_path))

            current_dir = str(Path(self.default_config_file).parent)
            sys.path.insert(0, current_dir)
            os.chdir(current_dir)
            logger.debug('Set the current directory to "{}"'.format(current_dir))
            self.config.load(self.default_config_file)
            logger.debug('TaskConfig file: "{}"  loading done'.format(self.default_config_file))

            for instr in prev_inst_dict:
                del instr
            self.inst_dict = self.config.inst_dict

            self.dock_handler.reset_inst_docks()

            self.inst_info_handler.update_tabs()
            for inst_name in self.inst_dict:
                self.inst_info_handler.update_info(inst_name)

            self.task_dict = self.config.task_dict

            self.setWindowTitle(self.config.task_dict_name)
            self.dock_handler.display_image(self.get_logo_file())

            self.session_handler = SessionHandler(True, False, False)
            self.session_handler.set_data_directory(self.config.base_data_dir, self.config.task_dict_name)
            self.session_handler.open_session(0, False)

        except Exception as e:
            logger.error('{}: {}'.format(e.__class__.__name__, e))

        try:
            actions = self.menu_Instruments.actions()
            for action in actions:
                self.menu_Instruments.removeAction(action)
            for item in self.inst_dict:
                action_inst = QAction(self)
                action_inst.setText(item)
                self.menu_Instruments.addAction(action_inst)
            logger.debug('Added new actions to Instruments menu')
            # Remove previous actions from Task menu
            actions = self.menu_Tasks.actions()
            for action in actions:
                self.menu_Tasks.removeAction(action)

            # Add new actions to Task menu
            for name in self.task_dict:
                m = self.menu_Tasks

                # set up submenu structure
                p = self.config.task_path_dict[name]
                if p:
                    tokens = p.split('/')
                    for token in tokens:
                        exists = False
                        na = None
                        if type(m) == QAction:
                            ma = m.menu()
                            if ma:
                                m = ma
                            else:
                                continue
                        for action in m.actions():
                            if token == action.text():
                                na = action
                                exists = True
                                break
                        if not exists:
                            na = m.addMenu(QMenu(token, m))
                        m = na
                    if type(m) == QAction:
                        ma = m.menu()
                        if ma:
                            m = ma
                        else:
                            continue
                action_task = QAction(self)
                action_task.setText(name)
                m.addAction(action_task)
        except Exception as e:
            logger.error('Error adding to Task menu Task:{}  Error: {}'.format(name, e))

    def get_logo_file(self):
        return self.LogoFile

    def print_redirect(self, text):
        """
        Handles text output for stdout, stderr and various text output
        from :class:`srsgui.task.task.Task`
        """
        try:
            if len(text) < 2:
                return
            if text[0] != Task.EscapeForResult[0]:
                if len(text) > 4:
                    self.console.append(text)
                    # sb = self.console.verticalScrollBar()
                    # sb.setValue(sb.maximum())
                return

            msg = text.split(Task.EscapeForResult[0], 2)
            if len(msg) != 3:
                return

            if text.startswith(Task.EscapeForResult):
                if msg[2] == 'cls':
                    self.taskResult.clear()
                else:
                    self.taskResult.append(msg[2])
                    sb = self.taskResult.verticalScrollBar()
                    sb.setValue(sb.maximum())

            elif text.startswith(Task.EscapeForDevice):
                # Check if the message starts with an inst name
                message = msg[2]
                inst_name = None
                sub_msgs = message.split(':', 1)
                if len(sub_msgs) == 2 and sub_msgs[0] in self.inst_dict:
                    inst_name = sub_msgs[0]
                    self.inst_info_handler.select_browser(inst_name)
                    message = sub_msgs[1]
                if message == 'cls':
                    self.deviceInfo.clear()
                elif inst_name and message == 'update':
                    self.inst_info_handler.update_info(inst_name)
                else:
                    self.deviceInfo.append(message)

            elif text.startswith(Task.EscapeForStatus):
                self.statusbar.showMessage(msg[2])
            elif text.startswith(Task.EscapeForStart):
                # self.taskInfo.append(text)
                pass
            elif text.startswith(Task.EscapeForStop):
                # self.taskInfo.append(text)
                # self.clear_busy()
                pass
            else:
                raise ValueError("Invalid escape string")
        except Exception as e:
            logger.error(e)

    def onTaskStarted(self):
        # setup toolbar buttons
        self.actionRun.setEnabled(False)
        self.actionStop.setEnabled(True)

        self.taskResult.clear()

        self._busy_flag = True
        self.dock_handler.show_toolbar(True)
        self.session_handler.create_file(self.task.__class__.__name__)

    def onTaskFinished(self):
        try:
            logger.debug('onTaskFinished started')
            # Setup toolbar buttons
            self.actionRun.setEnabled(True)
            self.actionStop.setEnabled(False)
            self.setWindowTitle(self.config.task_dict_name)
            self._busy_flag = False

            # PySide2 needs to refresh matplotlib display before starting a new task
            # for live update. Hide and show toolbar does the trick.
            self.dock_handler.show_toolbar(False)
            self.session_handler.close_file()
            # try:
            #     self.task.deleteLater()
            # except Exception as e:
            #     logger.error('Error with deleteLater in onTaskFinished: {}'.format(e))
            self.task = None

            for inst in self.inst_dict:
                self.inst_info_handler.update_info(inst)
            logger.debug('onTaskFinished finished')
        except Exception as e:
            logger.error('Error onTaskFinished: {}'.format(e))

    def is_task_running(self):
        return self._busy_flag

    def update_figure(self, figure):
        self.dock_handler.update_figure(figure)

    def onTaskSelect(self, action):
        try:
            if self.is_task_running():  # Another task is running
                return

            if self.task_method:
                old_task_name = self.task_method.__name__
            else:
                old_task_name = 'Default'
            self.geometry_dict[old_task_name] = (self.saveGeometry(),
                                                 self.saveState(),
                                                 self.centralwidget.width())

            self.current_task_action = action
            current_action_name = action.text()
            logger.info('Task {} is selected.'.format(Bold.format(current_action_name)))

            taskClassChosen = self.task_dict[current_action_name]
            if not issubclass(taskClassChosen, Task):
                title = 'Error'
                msg = 'The task chosen "{}" does not have a valid Task subclass'.format(current_action_name)
                self.display_question(msg, None)
                raise TypeError(msg)

            self.task_method = taskClassChosen
            self.statusbar.showMessage('Press Run button to start the task selected')
            if QT_BINDER == PYSIDE6:  # To bypass PySide6 docstring bug
                task = self.task_method()
                doc = task.__doc__
                del task
            else:
                doc = self.task_method.__doc__
            self.taskResult.setText(doc)
            self.taskParameterFrame.layout().removeWidget(self.taskParameter)
            self.taskParameter.deleteLater()
            self.taskParameter = InputPanel(self.task_method, self)
            self.taskParameterFrame.layout().addWidget(self.taskParameter)
            self.label_task_params.setText('Parameters in  {}'.format(current_action_name))
            self.label_task_params.setWordWrap(True)

            self.dock_handler.reset_figures(self.task_method.additional_figure_names)

            self.dock_handler.show_toolbar(False)
            self.handle_initial_image(self.task_method)

            new_task_name = self.task_method.__name__
            if new_task_name in self.geometry_dict:
                geo, state, width = self.geometry_dict[new_task_name]
                self.restoreState(state)
                self.restoreGeometry(geo)
                self.centralwidget.resize(width, self.centralwidget.height())

        except Exception as e:
            logger.error(e)

    def onRun(self):
        try:
            if self.is_task_running():
                self.display_question('Another task is running', None)
                return
            if self.task_method is None:
                raise TypeError("No Task selected")
            if not issubclass(self.task_method, Task):
                raise TypeError("{} is not a subclass of Task".format(self.task_method.__name__))

            self.task = self.task_method(self)
            self.task.name = self.current_task_action.text()
            self.setWindowTitle("{}  -  {}".format(self.config.task_dict_name, self.task.name))
            self.task.set_figure_dict(self.dock_handler.get_figure_dict())
            self.task.set_inst_dict(self.inst_dict)
            self.task.set_data_dict(self.data_dict)
            self.task.set_session_handler(self.session_handler)
            signal_handler = SignalHandler(self)
            self.task.set_callback_handler(signal_handler)
            self.onTaskStarted()
            self.task.start()
        except Exception as e:
            logger.error(e)

    def onStop(self):
        if self.task is not None:
            logger.info('{} stopping'.format(self.task.name))
            self.task.stop()

    def onOpen(self):
        try:
            logger.info('Opening a TaskConfig file..')
            file_name, _ = QFileDialog.getOpenFileName(self, "Select a .taskconfig file", ".",
                                                       "TaskConfig files (*.taskconfig)")
            if file_name:
                self.default_config_file = file_name
                self.load_tasks()
                logger.info('File opened: {}'.format(file_name))
        except Exception as e:
            logger.error(e)

    def onInstrumentSelect(self, inst_action):
        try:
            name = inst_action.text()
            self.inst_info_handler.select_browser(name)
            if self.inst_dict[name].is_connected():
                try:
                    self.inst_info_handler.update_info(name)
                except:
                    pass
                self.onDisconnect(name)
            else:
                self.onConnect(name)
        except Exception as e:
            logger.error(e)

    def onConnect(self, inst_name):
        if inst_name not in self.inst_dict:
            raise KeyError('Invalid instrument name: {}'.format(inst_name))

        logger.info('Connecting to {}...'.format(inst_name))
        try:
            inst = self.inst_dict[inst_name]
            form = ConnectDlg(inst)
            # form = CommConnectDlg(inst)
            form.exec_()

            if inst.is_connected():
                self.inst_info_handler.update_info(inst_name)
                logger.info('{} is connected'.format(inst_name))
            else:
                logger.info('Connection to {} aborted'.format(inst_name))
        except Exception as e:
            logger.error(e)

    def onDisconnect(self, inst_name):
        try:
            if not (inst_name in self.inst_dict and hasattr(self.inst_dict[inst_name], "is_connected")):
                raise KeyError('Invalid instrument: {}'.format(inst_name))

            inst = self.inst_dict[inst_name]
            if not self.inst_dict[inst_name].is_connected():
                logger.error('{} is not connected'.format(inst_name))
                return
            self.display_question("Do you want to disconnect '{}'?".format(inst_name))
            if self.question_result_value:
                inst.disconnect()
                self.inst_info_handler.update_info(inst_name)
                logger.info('{} is disconnected'.format(inst_name))
        except Exception as e:
            logger.error(e)

    def okToContinue(self):
        if self.task and self.task.is_running():
            self.display_question("Do you want to quit while a task is running?")
            if not self.question_result_value:
                return False
        return True

    def display_question(self, question, return_type=bool):
        try:
            self.question_result = None
            self.question_result_value = None
            # text = '<font size=12>{}</font>'.format(question)
            text = question
            title = self.task.name if self.task is not None else ""

            if return_type is None:
                msg_box = QMessageBox()
                msg_box.setText(text)
                msg_box.setWindowTitle(title)
                reply = msg_box.exec_()
                self.question_result = True

            elif return_type is bool:
                msg_box = QMessageBox()
                msg_box.setText(text)
                msg_box.setWindowTitle(title)
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
                msg_box.setDefaultButton(QMessageBox.Yes)
                reply = msg_box.exec()
                if reply == QMessageBox.Yes:
                    self.question_result = True
                    self.question_result_value = True
                elif reply == QMessageBox.No:
                    self.question_result = True
                    self.question_result_value = False
                else:
                    # if reply is not yes or no, return None
                    self.question_result = False
                    self.question_result_value = None

            elif return_type is str:
                self.question_result_value, self.question_result = \
                    QInputDialog.getText(self, title, text)
                if not self.question_result:
                    # If cancelled, return None
                    self.question_result_value = None

            else:
                raise TypeError('Not supported type {}'.format(return_type))
        except Exception as e:
            logger.error('display_question error: {}'.format(e))

    def closeEvent(self, event):
        if self.okToContinue():
            # Save settings
            self.save_settings()

            self.dock_handler.stop_command_handlers()

            # Close instruments
            inst_dict = self.inst_dict
            for key in inst_dict:
                if hasattr(inst_dict[key], "disconnect"):
                    inst_dict[key].disconnect()
        else:
            event.ignore()

    def handle_initial_image(self, task_class):
        try:
            self.dock_handler.clear_figures()
            attr = 'InitialImage'
            image_file = self.get_logo_file()
            if hasattr(task_class, attr):
                i_file = getattr(task_class, attr)
                if i_file:
                    image_file = i_file
            self.dock_handler.display_image(image_file)
            return
        except Exception as e:
            logger.error(f"Error in handle_initial_image: {e}")

    def onAbout(self,checked):
        msg = ''
        for name in self.inst_dict:
            inst = self.inst_dict[name]
            msg += '{} version: {}\n'.format(inst.__class__.__name__, inst.__version__)
        msg += '\nSrsgui version: {}\n'.format(__version__)
        msg += '\n{} version: {}\n'.format(QT_BINDER, QT_BINDER_VERSION)
        msg += 'Python version: {}\n'.format(sys.version)
        self.display_question(msg, None)

    def load_settings(self):
        try:
            self.default_config_file = self.settings.value("ConfigFile", "")
            sizes = self.settings.value("MainWindow/Splitter1", [100, 200, 200])
            self.splitter.setSizes([int(i) for i in sizes])
            sizes = self.settings.value("MainWindow/Splitter2", [150, 500])
            self.splitter_2.setSizes([int(i) for i in sizes])
            geo = self.settings.value("MainWindow/Geometry")
            state = self.settings.value("MainWindow/State")
            if geo and state:
                self.restoreGeometry(geo)
                self.restoreState(state)
        except Exception as e:
            logger.error('During load_setting, {}'.format(e))

    def save_settings(self):
        self.settings.setValue("ConfigFile", self.default_config_file)
        self.settings.setValue("MainWindow/Splitter1", self.splitter.sizes())
        self.settings.setValue("MainWindow/Splitter2", self.splitter_2.sizes())

        self.settings.setValue("MainWindow/Geometry", self.saveGeometry())
        self.settings.setValue("MainWindow/State", self.saveState())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = TaskMain()
    mw.show()
    sys.exit(app.exec_())
