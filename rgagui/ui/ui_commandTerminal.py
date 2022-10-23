# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'commandTerminal.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_CommandTerminal(object):
    def setupUi(self, CommandTerminal):
        if not CommandTerminal.objectName():
            CommandTerminal.setObjectName(u"CommandTerminal")
        CommandTerminal.resize(338, 406)
        self.verticalLayout = QVBoxLayout(CommandTerminal)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tbCommand = QTextBrowser(CommandTerminal)
        self.tbCommand.setObjectName(u"tbCommand")

        self.verticalLayout.addWidget(self.tbCommand)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pbClear = QPushButton(CommandTerminal)
        self.pbClear.setObjectName(u"pbClear")

        self.horizontalLayout.addWidget(self.pbClear)

        self.leCommand = QLineEdit(CommandTerminal)
        self.leCommand.setObjectName(u"leCommand")

        self.horizontalLayout.addWidget(self.leCommand)

        self.pbSend = QPushButton(CommandTerminal)
        self.pbSend.setObjectName(u"pbSend")

        self.horizontalLayout.addWidget(self.pbSend)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(CommandTerminal)

        QMetaObject.connectSlotsByName(CommandTerminal)
    # setupUi

    def retranslateUi(self, CommandTerminal):
        CommandTerminal.setWindowTitle(QCoreApplication.translate("CommandTerminal", u"Form", None))
        self.pbClear.setText(QCoreApplication.translate("CommandTerminal", u"Clear", None))
        self.pbSend.setText(QCoreApplication.translate("CommandTerminal", u"Send", None))
    # retranslateUi

