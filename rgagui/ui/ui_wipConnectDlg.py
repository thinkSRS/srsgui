# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wipConnectDlg.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_WipConnectDlg(object):
    def setupUi(self, WipConnectDlg):
        if not WipConnectDlg.objectName():
            WipConnectDlg.setObjectName(u"WipConnectDlg")
        WipConnectDlg.resize(361, 272)
        self.verticalLayout = QVBoxLayout(WipConnectDlg)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(WipConnectDlg)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.wipServerUrlLineEdit = QLineEdit(WipConnectDlg)
        self.wipServerUrlLineEdit.setObjectName(u"wipServerUrlLineEdit")

        self.verticalLayout.addWidget(self.wipServerUrlLineEdit)

        self.label_4 = QLabel(WipConnectDlg)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.wipTestStationUrlLineEdit = QLineEdit(WipConnectDlg)
        self.wipTestStationUrlLineEdit.setObjectName(u"wipTestStationUrlLineEdit")

        self.verticalLayout.addWidget(self.wipTestStationUrlLineEdit)

        self.label_5 = QLabel(WipConnectDlg)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)

        self.wipTestTypeUrlLineEdit = QLineEdit(WipConnectDlg)
        self.wipTestTypeUrlLineEdit.setObjectName(u"wipTestTypeUrlLineEdit")

        self.verticalLayout.addWidget(self.wipTestTypeUrlLineEdit)

        self.label_2 = QLabel(WipConnectDlg)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.userNameLineEdit = QLineEdit(WipConnectDlg)
        self.userNameLineEdit.setObjectName(u"userNameLineEdit")

        self.verticalLayout.addWidget(self.userNameLineEdit)

        self.label_3 = QLabel(WipConnectDlg)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.passwordLineEdit = QLineEdit(WipConnectDlg)
        self.passwordLineEdit.setObjectName(u"passwordLineEdit")

        self.verticalLayout.addWidget(self.passwordLineEdit)

        self.verticalSpacer = QSpacerItem(20, 18, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(WipConnectDlg)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.wipServerUrlLineEdit)
        self.label_4.setBuddy(self.wipServerUrlLineEdit)
        self.label_5.setBuddy(self.wipServerUrlLineEdit)
        self.label_2.setBuddy(self.wipServerUrlLineEdit)
        self.label_3.setBuddy(self.passwordLineEdit)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(WipConnectDlg)
        self.buttonBox.accepted.connect(WipConnectDlg.accept)
        self.buttonBox.rejected.connect(WipConnectDlg.reject)

        QMetaObject.connectSlotsByName(WipConnectDlg)
    # setupUi

    def retranslateUi(self, WipConnectDlg):
        WipConnectDlg.setWindowTitle(QCoreApplication.translate("WipConnectDlg", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("WipConnectDlg", u"WIP server URL", None))
        self.label_4.setText(QCoreApplication.translate("WipConnectDlg", u"WIP test station URL", None))
        self.label_5.setText(QCoreApplication.translate("WipConnectDlg", u"WIP test type URL", None))
        self.label_2.setText(QCoreApplication.translate("WipConnectDlg", u"User Name", None))
        self.label_3.setText(QCoreApplication.translate("WipConnectDlg", u"Password", None))
    # retranslateUi

