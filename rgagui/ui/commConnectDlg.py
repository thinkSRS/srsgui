
import sys
import logging

from .qt.QtCore import QSettings
from .qt.QtWidgets import QDialog, QMessageBox, QApplication

from rgagui.inst.serial_ports import serial_ports
from rgagui.inst.communications import Interface, SerialInterface, TcpipInterface
from .ui_commConnectDlg import Ui_CommConnectDlg

logger = logging.getLogger(__name__)


class CommConnectDlg(QDialog, Ui_CommConnectDlg):
    def __init__(self, dut, parent=None):
        try:
            super(CommConnectDlg, self).__init__(parent)
            self.setModal(True)
            self.setupUi(self)

            self.settings = QSettings()
            self.setWindowTitle('Connect using {}'.format(type(dut)))

            self.serialPortComboBox.addItems(serial_ports())
            self.ipAddressLineEdit.setInputMask('000.000.000.000;_')
            # Alternate way of doing input masking
            # An octet in IP address expressed in RE
            # '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
            #   (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

            self.ipAddressLineEdit.selectAll()
            self.passwordLineEdit.setEchoMode(self.passwordLineEdit.Password)
            self.loginCB.stateChanged.connect(self.onStateChanged)

            self.load_settings()

            self.dut = dut
            if hasattr(self.dut, 'comm'):
                self.comm = dut.comm
                info = self.comm.get_info()
                if type(self.dut.comm) is TcpipInterface:
                    self.commTabWidget.setCurrentIndex(1)
                    self.ipAddressLineEdit.setText(info['ip_address'])
                    self.userNameLineEdit.setText(self.dut.comm._userid)
                    self.passwordLineEdit.setText(self.dut.comm._password)
                    self.portNumberSB.setValue(info['port'])
                elif type(self.dut.comm) is SerialInterface:
                    self.commTabWidget.setCurrentIndex(0)

            else:
                raise TypeError('Invalid Instrument class to connect : {}'.format(type(dut)))
        except Exception as e:
            logger.error(e)
            QMessageBox.warning(self, 'Error', str(e))

    def onStateChanged(self):
        if self.loginCB.isChecked():
            self.userNameLineEdit.setEnabled(True)
            self.passwordLineEdit.setEnabled(True)
            self.portNumberSB.setValue(self.dut.comm.RGA_PORT)
        else:
            self.userNameLineEdit.setEnabled(False)
            self.passwordLineEdit.setEnabled(False)
            self.portNumberSB.setValue(self.dut.comm.TELNET_PORT)
    
    def accept(self):
        if self.dut.comm.is_connected():
            self.dut.comm.disconnect()
        if self.commTabWidget.currentIndex() == 1:  # Tcpip Tab
            try:
                if self.loginCB.isChecked():
                    # print(self.ipAddressLineEdit.text())
                    self.dut.connect(Interface.TCPIP,
                                     self.ipAddressLineEdit.text(),
                                     self.userNameLineEdit.text(),
                                     self.passwordLineEdit.text(),
                                     self.portNumberSB.value())
                else:
                    self.dut.connect(Interface.TCPIP,
                                  self.ipAddressLineEdit.text(),
                                  self.portNumberSB.value())            

            except Exception as e:
                err_string = 'Error connecting to {0}\n {1}'\
                             .format(self.ipAddressLineEdit.text(), e)
                logger.error(err_string)
                QMessageBox.warning(self, 'Error', err_string)

            else:
                logger.info('Connected to IP: {}'.format(
                    self.ipAddressLineEdit.text()))

        elif self.commTabWidget.currentIndex() == 0:  # Serial Tab
            try:            
                # self.dut.comm = SerialInterface()
                self.dut.connect(
                              Interface.SERIAL,
                              self.serialPortComboBox.currentText(),
                              int(self.baudRateComboBox.currentText()))
                self.dut.comm.port = self.serialPortComboBox.currentText()
                self.dut.comm.baud = int(self.baudRateComboBox.currentText())
            except Exception as e:
                err_string = 'Error connecting to {0}\n {1}'\
                             .format(self.serialPortComboBox.currentText, e)
                logger.error(err_string)
                QMessageBox.warning(self, 'Error', err_string)
            else:
                logger.info('Connected to port {}'.format(
                    self.serialPortComboBox.currentText()))

        if self.dut.is_connected():
            try:
                self.dut.check_id()  # clear the comm buffer
                if self.dut.check_id()[0] is None:  # make sure it is a correct DUT
                    self.dut.disconnect()
                    err_string = 'Disconnected from an Invalid instrument'
                    logger.error(err_string)
                    QMessageBox.warning(self, 'Error', err_string)

            except Exception as e:
                err_string = 'Disconnected with error during ID checking: {}'.format(e)
                logger.error(err_string)
                QMessageBox.warning(self, 'Error', err_string)
                try:
                    self.dut.disconnect()
                except:
                    pass
            else:
                self.save_settings()
        QDialog.accept(self)  # This ends the dialog box.

    def load_settings(self):
        try:
            last_ip = self.settings.value("ConnectDlg/IP", "", type=str)
            last_id = self.settings.value("ConnectDlg/ID", "", type=str)
            last_pwd = self.settings.value("ConnectDlg/PWD", "", type=str)

            self.ipAddressLineEdit.setText(last_ip)
            self.userNameLineEdit.setText(last_id)
            self.passwordLineEdit.setText(last_pwd)

            port = self.settings.value("ConnectDlg/ComPort", "", type=str)
            baud = str(self.settings.value("ConnectDlg/BaudRate", 115200, type=int))
            index = self.serialPortComboBox.findText(port)
            if index > -1:
                self.serialPortComboBox.setCurrentIndex(index)

            index = self.baudRateComboBox.findText(baud)
            if index > -1:
                self.baudRateComboBox.setCurrentIndex(index)
        except Exception as e:
            logger.error("Error in load_settings: {}".format(e))

    def save_settings(self):
        try:
            if self.dut.is_connected():
                if self.dut.comm.type == 'serial':
                    self.settings.setValue("ConnectDlg/ComPort", self.dut.comm.port)
                    self.settings.setValue("ConnectDlg/BaudRate", self.dut.comm.baud)
                elif self.dut.comm.type == 'tcpip':
                    self.settings.setValue("ConnectDlg/IP", self.dut.comm._ip_address)
                    self.settings.setValue("ConnectDlg/ID", self.dut.comm._userid)
                    self.settings.setValue("ConnectDlg/PWD", self.dut.comm._password)
        except Exception as e:
            logger.error("Error in save_settings: {}".format(e))


if __name__ == "__main__":    
    app = QApplication(sys.argv)
    form = CommConnectDlg()    
    form.show()
    app.exec_()
