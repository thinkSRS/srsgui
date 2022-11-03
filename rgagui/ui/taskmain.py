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
        self.current_action = None
        self.task = None
        self.question_result = None
        self.question_result_value = None

        # Get Instrument dict name from Task
        # the dict holds instances of subclass of Instrument
        self.InstDictName = Task.InstrumentDictName

        self.inst_dict = {}

        try:
            self.default_config_file = 'rga120tasks/rga120.taskconfig'
            self.config = Config()
            self.base_data_dir = self.config.base_data_dir
            self.base_log_file_name = self.config.base_log_file_name

            self.success_icon = QIcon(str(Path(__file__).parent / 'icons/o.png'))
            self.fail_icon = QIcon(str(Path(__file__).parent / 'icons/x.png'))

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

        self.taskmethod = None

        self.init_plot()
        self.figure = self.plotDockWidget.figure

        self.init_terminal()

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

            # Disconnect previously used instruments
            try:
                prev_inst_dict = self.inst_dict
                for key in prev_inst_dict:
                    instr = prev_inst_dict[key]
                    if hasattr(instr, 'disconnect'):
                        self.onDisconnect(key)
            except Exception as e:
                logger.error(e)

            # Check if argument is given in the command line
            if self.initial_load and len(sys.argv) == 2 and sys.argv[1].split('.')[-1].lower() == 'taskconfig':
                self.default_config_file = sys.argv[1]
                self.initial_load = False
                
            current_dir = str(Path(self.default_config_file).parent)
            sys.path.insert(0, current_dir)
            os.chdir(current_dir)

            self.config.load(self.default_config_file)
            logger.info('Taskconfig file: "{}"  loading done'.format(self.default_config_file))

            self.inst_dict = self.config.inst_dict

            self.dut_sn_prefix = '0'  # self.config.dut_sn_prefix
            self.task_dict = self.config.task_dict

            self.setWindowTitle(self.config.task_dict_name)
            self.display_image(self.config.get_logo_file())

            self.session_handler = SessionHandler(self.config, True, False, False)
            sn = self.get_current_serial_number()
            self.session_handler.open_session(sn)

        except Exception as e:
            logger.error(str(e))

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
                self.taskResult.append(msg[2])
                sb = self.taskResult.verticalScrollBar()
                sb.setValue(sb.maximum())
            elif text.startswith(Task.EscapeForDevice):
                self.deviceInfo.append(msg[2])
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
        self._busy_flag = True

        self.session_handler.create_file(self.task.__class__.__name__)

    def onTaskFinished(self):
        try:
            logger.debug('onTaskFinished run started')
            # Setup toolbar buttons
            self.actionRun.setEnabled(True)
            self.actionStop.setEnabled(False)
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

            self.current_action = action
            current_action_name = action.text()
            logger.info('Task {} is selected.'.format(Bold.format(current_action_name)))
            taskClassChosen = self.task_dict[current_action_name]
            if not issubclass(taskClassChosen, Task):
                title = 'Error'
                msg = 'The task chosen "{}" does not have a valid Task subclass'.format(current_action_name)
                self.show_message(msg, title)
                raise TypeError(msg)

            self.taskmethod = taskClassChosen
            self.handle_initial_image(self.taskmethod)

            self.statusbar.showMessage('Press Run button to start the task selected')

            self.taskResult.setText(self.taskmethod.__doc__)
            self.taskParameterFrame.layout().removeWidget(self.taskParameter)
            self.taskParameter.deleteLater()
            self.taskParameter = InputPanel(self.taskmethod)
            self.taskParameterFrame.layout().addWidget(self.taskParameter)
        except Exception as e:
            logger.error(e)

    def onRun(self):
        try:
            if self.is_task_running():
                self.show_message('Another task is running', 'Error')
                return
            if self.taskmethod is None:
                raise TypeError("No Task selected")
            if not issubclass(self.taskmethod, Task):
                raise TypeError("{} is not a subclass of Task".format(self.taskmethod.__name__))

            self.task = self.taskmethod(self)
            self.task.name = self.current_action.text()
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

            self.display_image(self.config.get_logo_file())
            self.console.clear()

            if inst.is_connected():
                msg = ''  # Name: {} \n S/N: {} \n F/W version: {} \n\n'.format(*inst.check_id())
                msg += ' Info: {} \n\n\n'.format(inst.get_info())
                msg += ' Status: {} \n'.format(inst.get_status())
                logger.debug(msg.replace('\n', ''))
                self.deviceInfo.clear()
                self.deviceInfo.append(msg)

                # if API server is available, upload.
                sn = self.get_current_serial_number()

                self.session_handler.open_session(sn)
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
                self.deviceInfo.clear()
                msg = "Disconnected"
                self.deviceInfo.append(msg)
                logger.info('{} is disconnected'.format(inst_name))
                self.session_handler.close_session(True)

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

    def onConsole(self):
        widget = self.loggingDockWidget
        if widget.isVisible():
            widget.setVisible(False)
            self.menu_View.actions()[0].setChecked(False)
        else:
            widget.setVisible(True)
            self.menu_View.actions()[0].setChecked(True)

    def get_current_serial_number(self):
        DefaultSN = '99999'


        if self.dut_sn_prefix:
            api_prefix = self.dut_sn_prefix
        else:
            api_prefix = '999'

        api_sn = '999' + DefaultSN
        serial_number = None
        try:
            dut = self.get_dut()
            _, serial_number, _ = dut.check_id()
            if serial_number is None:
                api_sn = api_prefix + DefaultSN
            elif len(serial_number) <= 5:
                api_sn = api_prefix + '0' * (5 - len(serial_number)) + serial_number
            else:
                api_sn = serial_number
        finally:
            logger.debug('Current DUT SN: {}'.format(api_sn))
            return api_sn

    @staticmethod
    def setup_figure_canvas(widget):
        widget.figure = plt.figure()
        widget.canvas = FigureCanvas(widget.figure)
        widget.toolbar = NavigationToolbar(widget.canvas, widget)
        layout = QVBoxLayout()
        layout.addWidget(widget.canvas)
        layout.addWidget(widget.toolbar)

        # use setWidget to put inside DockWidget
        # setLayout works for putting into QFrame
        child = QWidget()
        child.setLayout(layout)
        widget.setWidget(child)

    def init_plot(self):
        try:
            self.plotDockWidget = QDockWidget(self)
            self.plotDockWidget.setFloating(False)
            self.plotDockWidget.setObjectName("plotDockWidget")
            self.plotDockWidget.setWindowTitle("Plot")
            self.addDockWidget(Qt.RightDockWidgetArea, self.plotDockWidget)

            self.setup_figure_canvas(self.plotDockWidget)
            self.plotDockWidget.toolbar.hide()

            self.actionplot = QAction(self)
            self.actionplot.setCheckable(True)
            self.actionplot.setObjectName("actionplot")
            self.actionplot.setText("plot")
            self.actionplot.triggered.connect(self.onPlot)
            self.menu_View.addAction(self.actionplot)

            self.plotDockWidget.menu = self.menu_View
            self.plotDockWidget.menu_index = len(self.menu_View.actions()) - 1

        except Exception as e:
            logger.error(e)

    def onPlot(self):
        widget = self.plotDockWidget
        action = widget.menu.actions()[widget.menu_index]
        if widget.isVisible():
            widget.setVisible(False)
            action.setChecked(False)
        else:
            widget.setVisible(True)
            action.setChecked(True)

    def display_image(self, image_file):
        try:
            self.figure.clear()
            img = mpimg.imread(image_file)
            ax = self.figure.subplots()
            ax.imshow(img)
            ax.axis('off')
            self.figure.canvas.draw_idle()
        except Exception as e:
            logger.error(f"Error in display_image: {e}")

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

    def init_terminal(self):
        try:
            self.terminalDockWidget = QDockWidget(self)
            self.terminalDockWidget.setFloating(False)
            self.terminalDockWidget.setObjectName("terminalDockWidget")
            self.terminalDockWidget.setWindowTitle("Command Terminal")

            self.terminal_widget = CommandTerminal(self)
            self.terminalDockWidget.setWidget(self.terminal_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.terminalDockWidget)

            self.actionTerminal = QAction(self)
            self.actionTerminal.setCheckable(True)
            self.actionTerminal.setObjectName("actionTerminal")
            self.actionTerminal.setText("Terminal")
            self.actionTerminal.triggered.connect(self.onTerminal)
            self.menu_View.addAction(self.actionTerminal)

            self.terminalDockWidget.menu = self.menu_View
            self.terminalDockWidget.menu_index = len(self.menu_View.actions()) - 1
        except Exception as e:
            logger.error(e)

    def onTerminal(self):
        try:
            widget = self.terminalDockWidget
            action = widget.menu.actions()[widget.menu_index]
            if widget.isVisible():
                widget.setVisible(False)
                action.setChecked(False)
            else:
                widget.setVisible(True)
                action.setChecked(True)
        except Exception as e:
            logger.error(e)

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
