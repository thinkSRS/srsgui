# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'commConnectDlg.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CommConnectDlg(object):
    def setupUi(self, CommConnectDlg):
        CommConnectDlg.setObjectName("CommConnectDlg")
        CommConnectDlg.resize(376, 252)
        self.verticalLayout = QtWidgets.QVBoxLayout(CommConnectDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.commTabWidget = QtWidgets.QTabWidget(CommConnectDlg)
        self.commTabWidget.setObjectName("commTabWidget")
        self.serialTtab = QtWidgets.QWidget()
        self.serialTtab.setObjectName("serialTtab")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.serialTtab)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.serialTtab)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.serialPortComboBox = QtWidgets.QComboBox(self.serialTtab)
        self.serialPortComboBox.setObjectName("serialPortComboBox")
        self.horizontalLayout.addWidget(self.serialPortComboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.serialTtab)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.baudRateComboBox = QtWidgets.QComboBox(self.serialTtab)
        self.baudRateComboBox.setObjectName("baudRateComboBox")
        self.baudRateComboBox.addItem("")
        self.baudRateComboBox.addItem("")
        self.baudRateComboBox.addItem("")
        self.baudRateComboBox.addItem("")
        self.horizontalLayout_2.addWidget(self.baudRateComboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.commTabWidget.addTab(self.serialTtab, "")
        self.tcpipTab = QtWidgets.QWidget()
        self.tcpipTab.setObjectName("tcpipTab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tcpipTab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.ipAddressLabel = QtWidgets.QLabel(self.tcpipTab)
        self.ipAddressLabel.setObjectName("ipAddressLabel")
        self.gridLayout.addWidget(self.ipAddressLabel, 0, 0, 1, 1)
        self.ipAddressLineEdit = QtWidgets.QLineEdit(self.tcpipTab)
        self.ipAddressLineEdit.setObjectName("ipAddressLineEdit")
        self.gridLayout.addWidget(self.ipAddressLineEdit, 0, 1, 1, 1)
        self.userNameLabel = QtWidgets.QLabel(self.tcpipTab)
        self.userNameLabel.setObjectName("userNameLabel")
        self.gridLayout.addWidget(self.userNameLabel, 3, 0, 1, 1)
        self.userNameLineEdit = QtWidgets.QLineEdit(self.tcpipTab)
        self.userNameLineEdit.setObjectName("userNameLineEdit")
        self.gridLayout.addWidget(self.userNameLineEdit, 3, 1, 1, 1)
        self.PasswordLabel = QtWidgets.QLabel(self.tcpipTab)
        self.PasswordLabel.setObjectName("PasswordLabel")
        self.gridLayout.addWidget(self.PasswordLabel, 4, 0, 1, 1)
        self.passwordLineEdit = QtWidgets.QLineEdit(self.tcpipTab)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.gridLayout.addWidget(self.passwordLineEdit, 4, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 7, 1, 1, 1)
        self.portNumberLabel = QtWidgets.QLabel(self.tcpipTab)
        self.portNumberLabel.setObjectName("portNumberLabel")
        self.gridLayout.addWidget(self.portNumberLabel, 1, 0, 1, 1)
        self.portNumberSB = QtWidgets.QSpinBox(self.tcpipTab)
        self.portNumberSB.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.portNumberSB.setMaximum(65535)
        self.portNumberSB.setProperty("value", 818)
        self.portNumberSB.setObjectName("portNumberSB")
        self.gridLayout.addWidget(self.portNumberSB, 1, 1, 1, 1)
        self.loginCB = QtWidgets.QCheckBox(self.tcpipTab)
        self.loginCB.setChecked(True)
        self.loginCB.setObjectName("loginCB")
        self.gridLayout.addWidget(self.loginCB, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.commTabWidget.addTab(self.tcpipTab, "")
        self.verticalLayout.addWidget(self.commTabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(CommConnectDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.serialPortComboBox)
        self.label_2.setBuddy(self.baudRateComboBox)
        self.ipAddressLabel.setBuddy(self.ipAddressLineEdit)
        self.userNameLabel.setBuddy(self.userNameLineEdit)
        self.PasswordLabel.setBuddy(self.passwordLineEdit)

        self.retranslateUi(CommConnectDlg)
        self.commTabWidget.setCurrentIndex(1)
        self.baudRateComboBox.setCurrentIndex(3)
        self.buttonBox.accepted.connect(CommConnectDlg.accept)
        self.buttonBox.rejected.connect(CommConnectDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(CommConnectDlg)
        CommConnectDlg.setTabOrder(self.ipAddressLineEdit, self.userNameLineEdit)
        CommConnectDlg.setTabOrder(self.userNameLineEdit, self.passwordLineEdit)

    def retranslateUi(self, CommConnectDlg):
        _translate = QtCore.QCoreApplication.translate
        CommConnectDlg.setWindowTitle(_translate("CommConnectDlg", "Comm Connection"))
        self.label.setText(_translate("CommConnectDlg", "Serial port"))
        self.label_2.setText(_translate("CommConnectDlg", "Baud rate"))
        self.baudRateComboBox.setItemText(0, _translate("CommConnectDlg", "9600"))
        self.baudRateComboBox.setItemText(1, _translate("CommConnectDlg", "28800"))
        self.baudRateComboBox.setItemText(2, _translate("CommConnectDlg", "38400"))
        self.baudRateComboBox.setItemText(3, _translate("CommConnectDlg", "115200"))
        self.commTabWidget.setTabText(self.commTabWidget.indexOf(self.serialTtab), _translate("CommConnectDlg", "Serial"))
        self.ipAddressLabel.setText(_translate("CommConnectDlg", "&IP Address"))
        self.userNameLabel.setText(_translate("CommConnectDlg", "&User Name"))
        self.PasswordLabel.setText(_translate("CommConnectDlg", "&Password"))
        self.portNumberLabel.setText(_translate("CommConnectDlg", "Port"))
        self.loginCB.setText(_translate("CommConnectDlg", "Log in required"))
        self.commTabWidget.setTabText(self.commTabWidget.indexOf(self.tcpipTab), _translate("CommConnectDlg", "TCP/IP"))
