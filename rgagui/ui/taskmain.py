import os
import sys

import webbrowser

import logging
import logging.handlers

from pathlib import Path

from PyQt5.QtCore import Qt, QEvent, QTimer, QSettings, QItemSelectionModel, QByteArray
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QTextBrowser,\
                            QVBoxLayout, QMessageBox, QDockWidget, \
                            QInputDialog, QFileDialog, \
                            QAbstractItemView, QAction

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .commConnectDlg import CommConnectDlg

from .ui_taskmain import Ui_TaskMain

from .inputpanel import InputPanel
from .commandTerminal import CommandTerminal
from .config import Config
from .stdout import StdOut
from .qtloghandler import QtLogHandler
from .sessionhandler import SessionHandler
from .deviceinfohandler import DeviceInfoHandler
from .dockhandler import DockHandler

from rgagui.base import Task, Bold
from rga.base import Instrument

SuccessSound = str(Path(__file__).parent / 'sounds/successSound.wav')
FailSound = str(Path(__file__).parent / 'sounds/errorSound.wav')

logger = logging.getLogger(__name__)


class TaskMain(QMainWindow, Ui_TaskMain):

    def __init__(self, parent=None):
        super(TaskMain, self).__init__(parent)
        self.setupUi(self)
        # self.taskResult.setFontFamily('monospace')

        QApplication.setOrganizationName("SRS")
        QApplication.setApplicationName('rgagui')
        self.settings = QSettings()

        # The dict holds subclass of Task
        self.task_dict = {}
        self.current_task_action = None
        self.task = None
        self.task_method = None

        self.question_result = None
        self.question_result_value = None

        # self.inst_dict holds instances of subclass of Instrument
        self.inst_dict = {}
        self.inst_info_handler = DeviceInfoHandler(self)

        # self.dock_dict holds all the QDeckWidget instances
        self.dock_dict = {}
        self.dock_handler = DockHandler(self)
        self.figure = self.dock_handler.get_figure()
        self.plotDockWidget = self.dock_handler.get_dock()
        self.terminal_widget = self.dock_handler.get_terminal()

        try:
            self.default_config_file = 'rga120tasks/rga120.taskconfig'
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
        self.actionRun_2.setEnabled(True)
        self.actionStop_2.setEnabled(False)

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

        self.load_settings()

        self.statusbar.showMessage('Waiting for selection')
        self.stdout = StdOut(self.print_redirect)

    def load_tasks(self):

        try:
            # Clear console and result display
            self.console.clear()
            self.taskResult.clear()
            self.terminal_widget.tbCommand.clear()

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
                sys.path.pop()

            current_dir = str(Path(self.default_config_file).parent)
            sys.path.insert(0, current_dir)
            os.chdir(current_dir)
            self.config.load(self.default_config_file)
            logger.debug('Taskconfig file: "{}"  loading done'.format(self.default_config_file))

            for instr in prev_inst_dict:
                del instr
            self.inst_dict = self.config.inst_dict

            self.inst_info_handler.update_tabs()
            for inst_name in self.inst_dict:
                inst = self.get_inst(inst_name)
                self.inst_info_handler.update_info(inst_name)

            self.dut_sn_prefix = '0'  # self.config.dut_sn_prefix
            self.task_dict = self.config.task_dict

            self.setWindowTitle(self.config.task_dict_name)
            self.display_image(self.config.get_logo_file())

            self.session_handler = SessionHandler(self.config, True, False, False)
            self.session_handler.open_session(0)

        except Exception as e:
            logger.error(e)

        try:
            try:
                # Disconnect with none connected causes an exception
                self.menu_Instruments.triggered.disconnect()
            except:
                pass
            actions = self.menu_Instruments.actions()
            for action in actions:
                self.menu_Instruments.removeAction(action)

            for item in self.inst_dict:
                action_inst = QAction(self)
                action_inst.setText(item)
                self.menu_Instruments.addAction(action_inst)

                # action_inst.setCheckable(True)
                # if hasattr(self.inst_dict[item], 'is_connected') and self.inst_dict[item].is_connected():
                #    action_inst.setChecked(True)
            self.menu_Instruments.triggered.connect(self.onInstrumentSelect)

            try:
                self.menu_Tasks.triggered.disconnect()
            except:
                pass

            actions = self.menu_Tasks.actions()
            for action in actions:
                self.menu_Tasks.removeAction(action)

            for item in self.task_dict:
                action_task = QAction(self)
                action_task.setText(item)
                self.menu_Tasks.addAction(action_task)
            self.menu_Tasks.triggered.connect(self.onTaskSelect)
        except Exception as e:
            print(e)

    def onInstrumentSelect(self, inst_action):
        try:
            name = inst_action.text()
            self.inst_info_handler.select_browser(name)
            if self.inst_dict[name].is_connected():
                self.onDisconnect(name)
            else:
                self.onConnect(name)
        except Exception as e:
            logger.error(e)

    def print_redirect(self, text):
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
            if len(msg) != 3: return
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
        self.actionRun_2.setEnabled(False)
        self.actionStop_2.setEnabled(True)

        self._busy_flag = True

        self.session_handler.create_file(self.task.__class__.__name__)

    def onTaskFinished(self):
        try:
            logger.debug('onTaskFinished run started')
            # Setup toolbar buttons
            self.actionRun.setEnabled(True)
            self.actionStop.setEnabled(False)
            self.actionRun_2.setEnabled(True)
            self.actionStop_2.setEnabled(False)

            self._busy_flag = False

            self.create_task_result_in_session(self.task)

            # try:
            #     self.task.deleteLater()
            # except Exception as e:
            #     logger.error('Error with deleteLater in onTaskFinished: {}'.format(e))

            if self.task.is_error_raised():  # No more task runs with error raised
                self.onStop()
                return

            self.task = None

        except Exception as e:
            logger.error('Error onTaskFinished: {}'.format(e))

    def is_task_running(self):
        return self._busy_flag

    def get_inst(self, inst):
        if inst in self.inst_dict:
            return self.inst_dict[inst]
        else:
            return None

    def onTaskSelect(self, action):
        try:
            if self.is_task_running():  # Another task is running
                return

            self.plotDockWidget.toolbar.hide()

            self.current_task_action = action
            current_action_name = action.text()
            logger.info('Task {} is selected.'.format(Bold.format(current_action_name)))
            taskClassChosen = self.task_dict[current_action_name]
            if not issubclass(taskClassChosen, Task):
                title = 'Error'
                msg = 'The task chosen "{}" does not have a valid Task subclass'.format(current_action_name)
                self.show_message(msg, title)
                raise TypeError(msg)

            self.task_method = taskClassChosen
            self.handle_initial_image(self.task_method)

            self.statusbar.showMessage('Press Run button to start the task selected')

            self.taskResult.setText(self.task_method.__doc__)
            self.taskParameterFrame.layout().removeWidget(self.taskParameter)
            self.taskParameter.deleteLater()
            self.taskParameter = InputPanel(self.task_method, self)
            self.taskParameterFrame.layout().addWidget(self.taskParameter)
        except Exception as e:
            logger.error(e)

    def onRun(self):
        try:
            if self.is_task_running():
                self.show_message('Another task is running', 'Error')
                return
            if self.task_method is None:
                raise TypeError("No Task selected")
            if not issubclass(self.task_method, Task):
                raise TypeError("{} is not a subclass of Task".format(self.task_method.__name__))

            self.task = self.task_method(self)
            self.task.name = self.current_task_action.text()
            self.task.set_figure(self.figure)
            self.task.set_inst_dict(self.inst_dict)
            self.task.set_session_handler(self.session_handler)
            self.task.text_written_available.connect(self.print_redirect)
            self.task.data_available.connect(self.task.update)
            self.task.scan_started.connect(self.task.update_on_scan_started)
            self.task.scan_finished.connect(self.task.update_on_scan_finished)
            self.task.parameter_changed.connect(self.taskParameter.update)
            self.task.finished.connect(self.onTaskFinished)
            self.task.new_question.connect(self.display_question)
            self.taskResult.clear()

            # logger.info('{} starting'.format(type(self.task)))
            self.onTaskStarted()
            self.plotDockWidget.toolbar.show()
            self.task.start()
        except Exception as e:
            logger.error(e)

    def onStop(self):
        if self.task is not None:
            logger.info('{} stopped'.format(self.task.name))
            self.task.stop()

    def onNew(self):
        logger.info('Creating a file..')

    def onOpen(self):
        try:
            logger.info('Opening a taskconfig file..')
            file_name, _ = QFileDialog.getOpenFileName(self, "Select a taskconfig file", ".",
                                                       "TaskConfig files (*.taskconfig)")
            if file_name:
                self.default_config_file = file_name
                self.load_tasks()
                logger.info('file opened: {}'.format(file_name))
        except Exception as e:
            logger.error(e)

    def onSave(self):
        logger.info('Saving a file..')

    def onConnect(self, inst_name):
        logger.info('Connecting to {}...'.format(inst_name))
        try:
            inst = self.get_inst(inst_name)
            form = CommConnectDlg(inst)
            form.exec_()

            # self.display_image(self.config.get_logo_file())
            # self.console.clear()

            if inst.is_connected():
                self.inst_info_handler.update_info(inst_name)
                logger.info('{} is connected'.format(inst_name))
            else:
                logger.info('Connection to {} aborted'.format(inst_name))
        except Exception as e:
            logger.error(e)

    def onDisconnect(self, inst_name):
        inst = self.get_inst(inst_name)
        if inst.is_connected():
            msg_box = QMessageBox()
            msg_box.setText("Do you want disconnect '{}' ?".format(inst_name))
            msg_box.setWindowTitle('Disconnect')
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            reply = msg_box.exec()
            if reply == QMessageBox.Yes:
                inst.disconnect()
                self.inst_info_handler.update_info(inst_name)
                logger.info('{} is disconnected'.format(inst_name))

    def okToContinue(self):
        return True

    def create_task_result_in_session(self, task):
        if not self.session_handler.is_open():
            logger.error('No session is open when the task is finished')
            return
        self.session_handler.create_new_task_result(task.result)
        self.session_handler.close_file()
        logger.debug('A task result for DUT is created')

    @staticmethod
    def show_message(msg, title=''):
        logger.error(msg)
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setWindowTitle(title)
        msg_box.exec_()

    def display_question(self, question, return_type=bool):
        try:
            self.question_result = None
            self.question_result_value = None
            text = '<font size=12>{}</font>'.format(question)
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

            # Close instruments
            inst_dict = self.inst_dict
            for key in inst_dict:
                if issubclass(type(inst_dict[key]), Instrument):
                    inst_dict[key].disconnect()
        else:
            event.ignore()

    def display_image(self, image_file):
        self.dock_handler.display_image(image_file)

    def handle_initial_image(self, task_class):
        attr = 'InitialImage'
        if not hasattr(task_class, attr):
            self.display_image(self.config.get_logo_file())
            return

        image_file = getattr(task_class, attr)
        if image_file is None:
            self.display_image(self.config.get_logo_file())
            return

        try:
            self.figure.clear()
            img = mpimg.imread(image_file)
            ax = self.figure.subplots()
            ax.imshow(img)
            ax.axis('off')

            attr = 'InitialLimits'
            if hasattr(task_class, attr):
                limits = getattr(task_class, attr)
                if limits is not None:
                    ax.set_xlim(limits[0])
                    ax.set_ylim(limits[1])

            attr = 'InitialMarkers'
            if hasattr(task_class, attr):
                markers = getattr(task_class, attr)
                if markers is not None:
                    for marker in markers:
                        ax.plot(marker[0], marker[1], **marker[2])

            self.figure.canvas.draw_idle()
        except Exception as e:
            logger.error(f"Error in handle_initial_image: {e}")

    def load_settings(self):
        self.default_config_file = self.settings.value("ConfigFile", "", type=str)
        sizes = self.settings.value("MainWindow/Splitter1", [100, 200, 200])
        self.splitter.setSizes([int(i) for i in sizes])
        sizes = self.settings.value("MainWindow/Splitter2", [150, 500])
        self.splitter_2.setSizes([int(i) for i in sizes])
        # self.splitter.setSizes(self.settings.value("MainWindow/Splitter1", [100, 200, 200]))  #, type=int))
        # self.splitter_2.setSizes(self.settings.value("MainWindow/Splitter2", [150, 500]))  #, type=int))

        self.restoreGeometry(self.settings.value("MainWindow/Geometry", type=QByteArray))
        self.restoreState(self.settings.value("MainWindow/State", type=QByteArray))

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
