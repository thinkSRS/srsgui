# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'commConnectDlg.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_CommConnectDlg(object):
    def setupUi(self, CommConnectDlg):
        if not CommConnectDlg.objectName():
            CommConnectDlg.setObjectName(u"CommConnectDlg")
        CommConnectDlg.resize(340, 274)
        self.verticalLayout = QVBoxLayout(CommConnectDlg)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.commTabWidget = QTabWidget(CommConnectDlg)
        self.commTabWidget.setObjectName(u"commTabWidget")
        self.serialTtab = QWidget()
        self.serialTtab.setObjectName(u"serialTtab")
        self.horizontalLayout_3 = QHBoxLayout(self.serialTtab)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.serialTtab)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.serialPortComboBox = QComboBox(self.serialTtab)
        self.serialPortComboBox.setObjectName(u"serialPortComboBox")

        self.horizontalLayout.addWidget(self.serialPortComboBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.serialTtab)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.baudRateComboBox = QComboBox(self.serialTtab)
        self.baudRateComboBox.addItem("")
        self.baudRateComboBox.addItem("")
        self.baudRateComboBox.addItem("")
        self.baudRateComboBox.addItem("")
        self.baudRateComboBox.setObjectName(u"baudRateComboBox")

        self.horizontalLayout_2.addWidget(self.baudRateComboBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.commTabWidget.addTab(self.serialTtab, "")
        self.tcpipTab = QWidget()
        self.tcpipTab.setObjectName(u"tcpipTab")
        self.gridLayout_3 = QGridLayout(self.tcpipTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.ipAddressLabel = QLabel(self.tcpipTab)
        self.ipAddressLabel.setObjectName(u"ipAddressLabel")

        self.gridLayout.addWidget(self.ipAddressLabel, 0, 0, 1, 1)

        self.ipAddressLineEdit = QLineEdit(self.tcpipTab)
        self.ipAddressLineEdit.setObjectName(u"ipAddressLineEdit")

        self.gridLayout.addWidget(self.ipAddressLineEdit, 0, 1, 1, 1)

        self.userNameLabel = QLabel(self.tcpipTab)
        self.userNameLabel.setObjectName(u"userNameLabel")

        self.gridLayout.addWidget(self.userNameLabel, 3, 0, 1, 1)

        self.userNameLineEdit = QLineEdit(self.tcpipTab)
        self.userNameLineEdit.setObjectName(u"userNameLineEdit")

        self.gridLayout.addWidget(self.userNameLineEdit, 3, 1, 1, 1)

        self.PasswordLabel = QLabel(self.tcpipTab)
        self.PasswordLabel.setObjectName(u"PasswordLabel")

        self.gridLayout.addWidget(self.PasswordLabel, 4, 0, 1, 1)

        self.passwordLineEdit = QLineEdit(self.tcpipTab)
        self.passwordLineEdit.setObjectName(u"passwordLineEdit")

        self.gridLayout.addWidget(self.passwordLineEdit, 4, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 7, 1, 1, 1)

        self.portNumberLabel = QLabel(self.tcpipTab)
        self.portNumberLabel.setObjectName(u"portNumberLabel")

        self.gridLayout.addWidget(self.portNumberLabel, 1, 0, 1, 1)

        self.portNumberSB = QSpinBox(self.tcpipTab)
        self.portNumberSB.setObjectName(u"portNumberSB")
        self.portNumberSB.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.portNumberSB.setMaximum(65535)
        self.portNumberSB.setValue(818)

        self.gridLayout.addWidget(self.portNumberSB, 1, 1, 1, 1)

        self.loginCB = QCheckBox(self.tcpipTab)
        self.loginCB.setObjectName(u"loginCB")
        self.loginCB.setChecked(True)

        self.gridLayout.addWidget(self.loginCB, 2, 1, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.commTabWidget.addTab(self.tcpipTab, "")

        self.verticalLayout.addWidget(self.commTabWidget)

        self.buttonBox = QDialogButtonBox(CommConnectDlg)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.serialPortComboBox)
        self.label_2.setBuddy(self.baudRateComboBox)
        self.ipAddressLabel.setBuddy(self.ipAddressLineEdit)
        self.userNameLabel.setBuddy(self.userNameLineEdit)
        self.PasswordLabel.setBuddy(self.passwordLineEdit)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.ipAddressLineEdit, self.userNameLineEdit)
        QWidget.setTabOrder(self.userNameLineEdit, self.passwordLineEdit)

        self.retranslateUi(CommConnectDlg)
        self.buttonBox.accepted.connect(CommConnectDlg.accept)
        self.buttonBox.rejected.connect(CommConnectDlg.reject)

        self.commTabWidget.setCurrentIndex(1)
        self.baudRateComboBox.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(CommConnectDlg)
    # setupUi

    def retranslateUi(self, CommConnectDlg):
        CommConnectDlg.setWindowTitle(QCoreApplication.translate("CommConnectDlg", u"Comm Connection", None))
        self.label.setText(QCoreApplication.translate("CommConnectDlg", u"Serial port", None))
        self.label_2.setText(QCoreApplication.translate("CommConnectDlg", u"Baud rate", None))
        self.baudRateComboBox.setItemText(0, QCoreApplication.translate("CommConnectDlg", u"9600", None))
        self.baudRateComboBox.setItemText(1, QCoreApplication.translate("CommConnectDlg", u"28800", None))
        self.baudRateComboBox.setItemText(2, QCoreApplication.translate("CommConnectDlg", u"38400", None))
        self.baudRateComboBox.setItemText(3, QCoreApplication.translate("CommConnectDlg", u"115200", None))

        self.commTabWidget.setTabText(self.commTabWidget.indexOf(self.serialTtab), QCoreApplication.translate("CommConnectDlg", u"Serial", None))
        self.ipAddressLabel.setText(QCoreApplication.translate("CommConnectDlg", u"&IP Address", None))
        self.userNameLabel.setText(QCoreApplication.translate("CommConnectDlg", u"&User Name", None))
        self.PasswordLabel.setText(QCoreApplication.translate("CommConnectDlg", u"&Password", None))
        self.portNumberLabel.setText(QCoreApplication.translate("CommConnectDlg", u"Port", None))
        self.loginCB.setText(QCoreApplication.translate("CommConnectDlg", u"Log in required", None))
        self.commTabWidget.setTabText(self.commTabWidget.indexOf(self.tcpipTab), QCoreApplication.translate("CommConnectDlg", u"TCP/IP", None))
    # retranslateUi

