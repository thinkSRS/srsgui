
import sys


from PyQt5.QtWidgets import QDialog, QApplication

from .ui_wipConnectDlg import Ui_WipConnectDlg

from rgagui.wip.wip_api import HybridClient


class WipConnectDlg(QDialog, Ui_WipConnectDlg):
    def __init__(self, parent=None):
        super().__init__()
        self.setModal(True)
        self.setupUi(self)

        self.parent = parent
        self.passwordLineEdit.setEchoMode(self.passwordLineEdit.Password)

        if not hasattr(parent, parent.WIPRootAttr):
            self.wipServerUrlLineEdit.setText('No WIP attribute available')
            return

        self.wip = getattr(parent, parent.WIPRootAttr)
        if parent.WIPRootUrl in self.wip:
            self.wipServerUrlLineEdit.setText(self.wip[parent.WIPRootUrl])
        if parent.WIPTestStationUrl in self.wip:
            self.wipTestStationUrlLineEdit.setText(self.wip[parent.WIPTestStationUrl])
        if parent.WIPTestTypeUrl in self.wip:
            self.wipTestTypeUrlLineEdit.setText(self.wip[parent.WIPTestTypeUrl])

    def accept(self):
        try:
            client = HybridClient(
                self.wipServerUrlLineEdit.text(),
                self.userNameLineEdit.text(),
                self.passwordLineEdit.text(),
                self.wipTestStationUrlLineEdit.text(),
                self.wipTestTypeUrlLineEdit.text(),
                self.parent.local_db_name
                )
            self.wip['client'] = client
            self.wip['client'].connect()
            print('WIP server connected')

        except Exception as e:
            print('WIP server connection failed with error {}'.format(e))
        else:
            QDialog.accept(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = WipConnectDlg()
    form.show()
    app.exec_()
