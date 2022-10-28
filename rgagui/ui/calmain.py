import os
import sys

import webbrowser

import logging
import logging.handlers

from playsound import playsound
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

from .ui_calmain import Ui_CalMain
from .inputpanel import InputPanel
from .commandTerminal import CommandTerminal
from .config import Config
from .stdout import StdOut
from .qtloghandler import QtLogHandler
from .sessionhandler import SessionHandler

from rgagui.basetask import Task, Bold
from rga.baseinst import Instrument as BaseInst

SuccessSound = str(Path(__file__).parent / 'sounds/successSound.wav')
FailSound = str(Path(__file__).parent / 'sounds/errorSound.wav')

logger = logging.getLogger(__name__)


class CalMain(QMainWindow, Ui_CalMain):

    def __init__(self, parent=None):
        super(CalMain, self).__init__(parent)
        self.setupUi(self)
        # self.testResult.setFontFamily('monospace')

        QApplication.setOrganizationName("SRS")
        QApplication.setApplicationName('rgagui')
        self.settings = QSettings()

        # The dict holds subclass of BaseTest
        self.test_dict = {}
        self.current_action = None
        self.test = None
        self.question_result = None
        self.question_result_value = None

        # Get Instrument dict name from BaseTest
        # the dict holds instances of subclass of BaseInst
        self.InstDict = Task.InstrumentDict
        self.Dut = Task.DeviceUnderTest

        self.inst_dict = {
            self.Dut: BaseInst()
        }

        try:
            self.default_config_file = 'rga120tasks/rga120.taskconfig'
            self.config = Config()
            self.base_data_dir = self.config.base_data_dir

            self.success_icon = QIcon(str(Path(__file__).parent / 'icons/o.png'))
            self.fail_icon = QIcon(str(Path(__file__).parent / 'icons/x.png'))

            self.testParameter = QTextBrowser()
            layout = QVBoxLayout()
            layout.addWidget(self.testParameter)
            self.testParameterFrame.setLayout(layout)

            # Load test configuration after init
            QTimer.singleShot(0, self.load_tests)

        except Exception as e:
            logger.error(e)

        # Setup toolbar buttons
        self.actionRun.setEnabled(True)
        self.actionStop.setEnabled(False)
        # busy flag is used to tell if a test is running
        self._busy_flag = False
        self.is_selection_running = False

        self.testmethod = None

        self.init_plot()
        self.figure = self.plotDockWidget.figure

        self.init_terminal()

        log_file = self.base_data_dir + '/calmainlog.txt'
        self.qt_log_handler = QtLogHandler(self.console)
        self.qt_log_handler.setLevel(logging.INFO)

        self.file_log_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=100000, backupCount=10)
        logging.basicConfig(handlers=[self.qt_log_handler, self.file_log_handler],
                            format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
                            level=logging.DEBUG)

        # Session handler for TestResult output
        self.session_handler = None

        self.load_settings()

        self.statusbar.showMessage('Waiting for selection')
        self.stdout = StdOut(self.print_redirect)

    def load_tests(self):
        try:
            # Clear console and result display
            self.console.clear()
            self.testResult.clear()

            # Disconnect previously used instruments
            try:
                prev_inst_dict = self.inst_dict
                for key in prev_inst_dict:
                    instr = prev_inst_dict[key]
                    if hasattr(instr, 'disconnect'):
                        if key == self.Dut:
                            self.onDisconnect()
                        else:
                            instr.disconnect()
            except Exception as e:
                logger.error(e)

            if len(sys.argv) == 2 and sys.argv[1].split('.')[-1].lower() == 'taskconfig':
                self.default_config_file = sys.argv[1]
                
            current_dir = str(Path(self.default_config_file).parent)
            sys.path.insert(0, current_dir)
            os.chdir(current_dir)

            self.config.load(self.default_config_file)
            logger.info('Taskconfig file: "{}"  loading done'.format(self.default_config_file))

            self.inst_dict = self.config.inst_dict

            self.dut_sn_prefix = self.config.dut_sn_prefix
            self.test_dict = self.config.test_dict

            self.setWindowTitle(self.config.test_dict_name)
            self.display_image(self.config.get_logo_file())

            self.session_handler = SessionHandler(self.config, True, False, False)
            sn = self.get_current_serial_number()
            self.session_handler.open_session(sn)

        except Exception as e:
            logger.error(str(e))

        try:
            try:
                # diconnect with none connected causes an exception
                self.menu_Tasks.triggered.disconnect()
            except:
                pass

            actions = self.menu_Tasks.actions()
            for action in actions:
                self.menu_Tasks.removeAction(action)

            for item in self.test_dict:
                action_measure = QAction(self)
                action_measure.setText(item)
                self.menu_Tasks.addAction(action_measure)
            self.menu_Tasks.triggered.connect(self.onMenuSelect)
        except Exception as e:
            print(e)

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
                self.testResult.append(msg[2])
                sb = self.testResult.verticalScrollBar()
                sb.setValue(sb.maximum())
            elif text.startswith(Task.EscapeForDevice):
                self.deviceInfo.append(msg[2])
            elif text.startswith(Task.EscapeForStatus):
                self.statusbar.showMessage(msg[2])
            elif text.startswith(Task.EscapeForStart):
                # self.testInfo.append(text)
                pass
            elif text.startswith(Task.EscapeForStop):
                # self.testInfo.append(text)
                # self.clear_busy()
                pass
            else:
                raise ValueError("Invalid escape string")
        except Exception as e:
            logger.error(e)

    def onTestStarted(self):
        # setup toolbar buttons
        self.actionRun.setEnabled(False)
        self.actionStop.setEnabled(True)
        self._busy_flag = True

        self.session_handler.create_file(self.test.__class__.__name__)

    def onTestFinished(self):
        try:
            logger.debug('onTestFinished run started')
            # Setup toolbar buttons
            self.actionRun.setEnabled(True)
            self.actionStop.setEnabled(False)
            self._busy_flag = False

            self.create_test_result_in_session(self.test)

            if self.test.is_test_passed():
                # self.change_test_status(self.test.name, True)
                playsound(SuccessSound, block=False)
            else:
                # self.change_test_status(self.test.name, False)
                playsound(FailSound, block=False)

            # try:
            #     self.test.deleteLater()
            # except Exception as e:
            #     logger.error('Error with deleteLater in onTestFinished: {}'.format(e))

            if self.test.is_error_raised():  # No more test runs with error raised
                self.onStop()
                return

            self.test = None

        except Exception as e:
            logger.error('Error onTestFinished: {}'.format(e))

    def is_test_running(self):
        return self._busy_flag

    def get_dut(self):
        return self.inst_dict[self.Dut]

    def onMenuSelect(self, action):
        try:
            if self.is_test_running():  # Another test is running
                return

            self.plotDockWidget.toolbar.hide()

            self.current_action = action
            current_action_name = action.text()
            logger.info('Task {} is selected.'.format(Bold.format(current_action_name)))
            testClassChosen = self.test_dict[current_action_name]
            if not issubclass(testClassChosen, Task):
                title = 'Error'
                msg = 'The task chosen "{}" does not have a valid Task subclass'.format(current_action_name)
                self.show_message(msg, title)
                raise TypeError(msg)

            self.testmethod = testClassChosen
            self.handle_initial_image(self.testmethod)

            self.statusbar.showMessage('Press Run button to start the test selected')

            self.testResult.setText(self.testmethod.__doc__)
            self.testParameterFrame.layout().removeWidget(self.testParameter)
            self.testParameter.deleteLater()
            self.testParameter = InputPanel(self.testmethod)
            self.testParameterFrame.layout().addWidget(self.testParameter)
        except Exception as e:
            logger.error(e)

    def onRun(self):
        try:
            if self.is_test_running():
                self.show_message('Another test is running', 'Error')
                return
            if self.testmethod is None:
                raise TypeError("No Task selected")
            if not issubclass(self.testmethod, Task):
                raise TypeError("{} is not a subclass of BaseTest".format(self.testmethod.__name__))

            self.test = self.testmethod(self)
            self.test.name = self.current_action.text()
            self.test.set_figure(self.figure)
            self.test.set_inst_dict(self.inst_dict)
            self.test.set_session_handler(self.session_handler)
            self.test.text_written_available.connect(self.print_redirect)
            self.test.data_available.connect(self.test.update)
            self.test.scan_started.connect(self.test.update_on_scan_started)
            self.test.scan_finished.connect(self.test.update_on_scan_finished)
            self.test.parameter_changed.connect(self.testParameter.update)
            self.test.finished.connect(self.onTestFinished)
            self.test.new_question.connect(self.display_question)
            self.testResult.clear()

            # logger.info('{} starting'.format(type(self.test)))
            self.onTestStarted()
            self.plotDockWidget.toolbar.show()
            self.test.start()
        except Exception as e:
            logger.error(e)

    def onStop(self):
        if self.test is not None:
            logger.info('{} stopped'.format(self.test.name))
            self.test.stop()

    def onNew(self):
        logger.info('Creating a file..')

    def onOpen(self):
        try:
            logger.info('Opening a taskconfig file..')
            file_name, _ = QFileDialog.getOpenFileName(self, "Select a taskconfig file", ".",
                                                       "TaskConfig files (*.taskconfig)")
            if file_name:
                self.default_config_file = file_name
                self.load_tests()
                logger.info('file opened: {}'.format(file_name))
        except Exception as e:
            logger.error(e)

    def onSave(self):
        logger.info('Saving a file..')

    def onConnect(self):
        logger.info('Connecting to DUT...')
        try:
            dut = self.get_dut()
            logger.debug(dut.__class__.__name__)
            form = CommConnectDlg(dut)
            form.exec_()

            self.display_image(self.config.get_logo_file())
            self.console.clear()

            if dut.is_connected():
                msg = ''  # Name: {} \n S/N: {} \n F/W version: {} \n\n'.format(*dut.check_id())
                msg += ' Info: {} \n\n\n'.format(dut.get_info())
                msg += ' Status: {} \n'.format(dut.get_status())
                logger.debug(msg.replace('\n', ''))
                self.deviceInfo.clear()
                self.deviceInfo.append(msg)

                # if API server is available, upload.
                sn = self.get_current_serial_number()

                self.session_handler.open_session(sn)
            else:
                logger.info('Connection aborted')
        except Exception as e:
            logger.error(e)

    def onDisconnect(self):
        dut = self.get_dut()
        if dut.is_connected():

            dut.disconnect()
            self.deviceInfo.clear()
            msg = "Disconnected"
            self.deviceInfo.append(msg)
            self.sub_assemblies = {}
            logger.info('DUT is disconnected')

            self.session_handler.close_session(True)
    def okToContinue(self):
        return True

    def create_test_result_in_session(self, test):
        if not self.session_handler.is_open():
            logger.error('No session is open when the test is finished')
            return
        self.session_handler.create_new_test_result(test.result)
        self.session_handler.close_file()
        logger.debug('A test result for DUT is created')

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
            title = self.test.name if self.test is not None else ""

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
                if issubclass(type(inst_dict[key]), BaseInst):
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
        api_sn = '999' + DefaultSN

        if self.dut_sn_prefix:
            api_prefix = self.dut_sn_prefix
        else:
            api_prefix = '999'

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

    def handle_initial_image(self, test_class):
        attr = 'InitialImage'
        if not hasattr(test_class, attr):
            self.display_image(self.config.get_logo_file())
            return

        image_file = getattr(test_class, attr)
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
            if hasattr(test_class, attr):
                limits = getattr(test_class, attr)
                if limits is not None:
                    ax.set_xlim(limits[0])
                    ax.set_ylim(limits[1])

            attr = 'InitialMarkers'
            if hasattr(test_class, attr):
                markers = getattr(test_class, attr)
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
    mw = CalMain()
    mw.show()
    sys.exit(app.exec_())
