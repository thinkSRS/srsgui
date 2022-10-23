
import sys
import logging
from PyQt5.QtCore import QSettings

from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication

from srs_insts.baseinsts.serial_ports import serial_ports
from srs_insts.baseinsts.communications import Interface, SerialInterface, TcpipInterface
from .ui_commConnectDlg import Ui_CommConnectDlg

logger = logging.getLogger(__name__)


class CommConnectDlg(QDialog, Ui_CommConnectDlg):
    def __init__(self, dut, parent=None):
        try:
            super(CommConnectDlg, self).__init__(parent)
            self.setModal(True)
            self.setupUi(self)
            self.settings = QSettings()

            # self.ipAddressLineEdit.setText('192.025.128.015')

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
                if type(self.dut.comm) is TcpipInterface:
                    self.commTabWidget.setCurrentIndex(1)
                    self.ipAddressLineEdit.setText(self.dut.comm.ip_address)
                    self.userNameLineEdit.setText(self.dut.comm.userid)
                    self.passwordLineEdit.setText(self.dut.comm.password)
                elif type(self.dut.comm) is SerialInterface:
                    self.commTabWidget.setCurrentIndex(0)
            else:
                raise TypeError('Instrument class does not have communications class')
        except Exception as e:
            logger.error(e)
            QMessageBox.warning(self, 'Error', str(e))

    def onStateChanged(self):
        if self.loginCB.isChecked():
            self.userNameLineEdit.setEnabled(True)
            self.passwordLineEdit.setEnabled(True)
            self.portNumberSB.setValue(818)
        else:
            self.userNameLineEdit.setEnabled(False)
            self.passwordLineEdit.setEnabled(False)
            self.portNumberSB.setValue(23)
    
    def accept(self):
        if self.dut.comm.is_connected():
            self.dut.comm.disconnect()
        if self.commTabWidget.currentIndex() == 1:  # Tcpip Tab
            try:
                if self.loginCB.isChecked():
                    # print(self.ipAddressLineEdit.text())
                    self.dut.open(Interface.TCPIP,
                                  self.ipAddressLineEdit.text(),
                                  self.userNameLineEdit.text(),
                                  self.passwordLineEdit.text(),
                                  self.portNumberSB.value())
                    self.dut.comm.ip_address = self.ipAddressLineEdit.text()
                    self.dut.comm.userid = self.userNameLineEdit.text()
                    self.dut.comm.password = self.passwordLineEdit.text()
                    self.dut.comm.tcp_port = self.portNumberSB.value()
                else:
                    self.dut.open(Interface.TCPIP,
                                  self.ipAddressLineEdit.text(),
                                  self.portNumberSB.value())            
                    self.dut.comm.ip_address = self.ipAddressLineEdit.text()
                    self.dut.comm.userid = ''
                    self.dut.comm.password = ''
                    self.dut.comm.tcp_port = self.portNumberSB.value()
                self.dut.interface_type = 'tcpip'

            except Exception as e:
                err_string = 'Error connecting to {0}\n {1}'\
                             .format(self.ipAddressLineEdit.text(), e)
                logger.error(err_string)
                QMessageBox.warning(self, 'Error', err_string)

            else:
                logger.info('Connected to IP: {}'.format(
                    self.ipAddressLineEdit.text()))

        elif self.commTabWidget.currentIndex() == 0: #Serial Tab
            try:            
                #self.dut.comm = SerialInterface()
                self.dut.open(
                              Interface.SERIAL,
                              self.serialPortComboBox.currentText(),
                              int(self.baudRateComboBox.currentText()))
                self.dut.interface_type = 'serial'
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
                if self.dut.check_id()[0] is None:  # make sure it is a correct DUT
                    self.dut.close()
                    err_string = 'Disconnected from an Invalid instrument'
                    logger.error(err_string)
                    QMessageBox.warning(self, 'Error', err_string)

            except Exception as e:
                self.dut.close()
                err_string = 'Disconnected with error during ID checking: {}'.format(e)
                logger.error(err_string)
                QMessageBox.warning(self, 'Error', err_string)

            else:
                self.save_settings()
        QDialog.accept(self)  # This ends the dialog box.

    def load_settings(self):
        port = self.settings.value("ConnectDlg/ComPort", "", type=str)
        baud = str(self.settings.value("ConnectDlg/BaudRate", 115200, type=int))
        index = self.serialPortComboBox.findText(port)
        if index > -1:
            self.serialPortComboBox.setCurrentIndex(index)

        index = self.baudRateComboBox.findText(baud)
        if index > -1:
            self.baudRateComboBox.setCurrentIndex(index)

    def save_settings(self):
        if self.dut.is_connected():
            if self.dut.interface_type == 'serial':
                self.settings.setValue("ConnectDlg/ComPort", self.dut.comm.port)
                self.settings.setValue("ConnectDlg/BaudRate", self.dut.comm.baud)

if __name__ == "__main__":    
    app = QApplication(sys.argv)
    form = CommConnectDlg()    
    form.show()
    app.exec_()
