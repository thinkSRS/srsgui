# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'deviceinfowidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from .qt.QtCore import *
from .qt.QtGui import *
from .qt.QtWidgets import *


class Ui_DeviceInfoWidget(object):
    def setupUi(self, DeviceInfoWidget):
        if not DeviceInfoWidget.objectName():
            DeviceInfoWidget.setObjectName(u"DeviceInfoWidget")
        DeviceInfoWidget.resize(374, 551)
        self.verticalLayout_2 = QVBoxLayout(DeviceInfoWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(DeviceInfoWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.text_browser = QTextBrowser(self.splitter)
        self.text_browser.setObjectName(u"text_browser")
        self.splitter.addWidget(self.text_browser)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.update_button = QPushButton(self.widget)
        self.update_button.setObjectName(u"update_button")

        self.horizontalLayout.addWidget(self.update_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.capture_button = QPushButton(self.widget)
        self.capture_button.setObjectName(u"capture_button")

        self.horizontalLayout.addWidget(self.capture_button)

        self.include_checkbox = QCheckBox(self.widget)
        self.include_checkbox.setObjectName(u"include_checkbox")

        self.horizontalLayout.addWidget(self.include_checkbox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.tree_view = QTreeView(self.widget)
        self.tree_view.setObjectName(u"tree_view")

        self.verticalLayout.addWidget(self.tree_view)

        self.splitter.addWidget(self.widget)

        self.verticalLayout_2.addWidget(self.splitter)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.tree_view)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(DeviceInfoWidget)

        QMetaObject.connectSlotsByName(DeviceInfoWidget)
    # setupUi

    def retranslateUi(self, DeviceInfoWidget):
        DeviceInfoWidget.setWindowTitle(QCoreApplication.translate("DeviceInfoWidget", u"Form", None))
        self.update_button.setText(QCoreApplication.translate("DeviceInfoWidget", u"Update", None))
        self.capture_button.setText(QCoreApplication.translate("DeviceInfoWidget", u"Capture", None))
        self.include_checkbox.setText(QCoreApplication.translate("DeviceInfoWidget", u"include \n"
"query-only", None))
        self.label.setText(QCoreApplication.translate("DeviceInfoWidget", u"Command capture", None))
    # retranslateUi

