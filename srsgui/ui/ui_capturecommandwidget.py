# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'capturecommandwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from .qt.QtCore import *
from .qt.QtGui import *
from .qt.QtWidgets import *


class Ui_CaptureCommandWidget(object):
    def setupUi(self, CaptureCommandWidget):
        if not CaptureCommandWidget.objectName():
            CaptureCommandWidget.setObjectName(u"CaptureCommandWidget")
        CaptureCommandWidget.resize(398, 523)
        self.verticalLayout_3 = QVBoxLayout(CaptureCommandWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.query_only_checkbox = QCheckBox(CaptureCommandWidget)
        self.query_only_checkbox.setObjectName(u"query_only_checkbox")

        self.verticalLayout.addWidget(self.query_only_checkbox)

        self.set_only_checkbox = QCheckBox(CaptureCommandWidget)
        self.set_only_checkbox.setObjectName(u"set_only_checkbox")

        self.verticalLayout.addWidget(self.set_only_checkbox)

        self.excluded_checkbox = QCheckBox(CaptureCommandWidget)
        self.excluded_checkbox.setObjectName(u"excluded_checkbox")

        self.verticalLayout.addWidget(self.excluded_checkbox)

        self.method_checkbox = QCheckBox(CaptureCommandWidget)
        self.method_checkbox.setObjectName(u"method_checkbox")

        self.verticalLayout.addWidget(self.method_checkbox)

        self.raw_command_checkbox = QCheckBox(CaptureCommandWidget)
        self.raw_command_checkbox.setObjectName(u"raw_command_checkbox")

        self.verticalLayout.addWidget(self.raw_command_checkbox)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.capture_button = QPushButton(CaptureCommandWidget)
        self.capture_button.setObjectName(u"capture_button")

        self.verticalLayout_2.addWidget(self.capture_button)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.expand_button = QPushButton(CaptureCommandWidget)
        self.expand_button.setObjectName(u"expand_button")

        self.verticalLayout_2.addWidget(self.expand_button)

        self.collapse_button = QPushButton(CaptureCommandWidget)
        self.collapse_button.setObjectName(u"collapse_button")

        self.verticalLayout_2.addWidget(self.collapse_button)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.tree_view = QTreeView(CaptureCommandWidget)
        self.tree_view.setObjectName(u"tree_view")

        self.verticalLayout_3.addWidget(self.tree_view)


        self.retranslateUi(CaptureCommandWidget)

        QMetaObject.connectSlotsByName(CaptureCommandWidget)
    # setupUi

    def retranslateUi(self, CaptureCommandWidget):
        CaptureCommandWidget.setWindowTitle(QCoreApplication.translate("CaptureCommandWidget", u"Form", None))
        self.query_only_checkbox.setText(QCoreApplication.translate("CaptureCommandWidget", u"Include query-only cmds", None))
        self.set_only_checkbox.setText(QCoreApplication.translate("CaptureCommandWidget", u"Show set-only cmds", None))
        self.excluded_checkbox.setText(QCoreApplication.translate("CaptureCommandWidget", u"Show excluded cmds", None))
        self.method_checkbox.setText(QCoreApplication.translate("CaptureCommandWidget", u"Show methods", None))
        self.raw_command_checkbox.setText(QCoreApplication.translate("CaptureCommandWidget", u"Show raw cmds", None))
        self.capture_button.setText(QCoreApplication.translate("CaptureCommandWidget", u"Capture", None))
        self.expand_button.setText(QCoreApplication.translate("CaptureCommandWidget", u"Expand all", None))
        self.collapse_button.setText(QCoreApplication.translate("CaptureCommandWidget", u"Collapse all", None))
    # retranslateUi

