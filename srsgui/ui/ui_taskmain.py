# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'taskmain.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

from .qt import QtCore, QtGui, QtWidgets


class Ui_TaskMain(object):
    def setupUi(self, TaskMain):
        TaskMain.setObjectName("TaskMain")
        TaskMain.resize(1140, 688)
        options = QtWidgets.QMainWindow.AllowNestedDocks|QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks
        TaskMain.setDockOptions(options)
        self.centralwidget = QtWidgets.QWidget(TaskMain)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(300, 500))
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.deviceInfoTabWidget = QtWidgets.QTabWidget(self.layoutWidget)
        self.deviceInfoTabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.deviceInfoTabWidget.setObjectName("deviceInfoTabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.deviceInfo = QtWidgets.QTextBrowser(self.tab)
        self.deviceInfo.setObjectName("deviceInfo")
        self.horizontalLayout_3.addWidget(self.deviceInfo)
        self.deviceInfoTabWidget.addTab(self.tab, "")
        self.verticalLayout_2.addWidget(self.deviceInfoTabWidget)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_task_params = QtWidgets.QLabel(self.layoutWidget1)
        self.label_task_params.setObjectName("label_task_params")
        self.verticalLayout_3.addWidget(self.label_task_params)
        self.taskParameterFrame = QtWidgets.QFrame(self.layoutWidget1)
        self.taskParameterFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.taskParameterFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.taskParameterFrame.setObjectName("taskParameterFrame")
        self.verticalLayout_3.addWidget(self.taskParameterFrame)
        self.layoutWidget2 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.taskResult = QtWidgets.QTextBrowser(self.layoutWidget2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.taskResult.setFont(font)
        self.taskResult.setObjectName("taskResult")
        self.verticalLayout_4.addWidget(self.taskResult)
        self.horizontalLayout_2.addWidget(self.splitter_2)
        TaskMain.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(TaskMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1140, 29))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.menubar.setFont(font)
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Control = QtWidgets.QMenu(self.menubar)
        self.menu_Control.setObjectName("menu_Control")
        self.menu_Docks = QtWidgets.QMenu(self.menubar)
        self.menu_Docks.setObjectName("menu_Docks")
        self.menu_Help = QtWidgets.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        self.menu_Tasks = QtWidgets.QMenu(self.menubar)
        self.menu_Tasks.setObjectName("menu_Tasks")
        self.menu_Instruments = QtWidgets.QMenu(self.menubar)
        self.menu_Instruments.setObjectName("menu_Instruments")
        self.menu_Plot = QtWidgets.QMenu(self.menubar)
        self.menu_Plot.setObjectName("menu_Plot")
        TaskMain.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(TaskMain)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.statusbar.setFont(font)
        self.statusbar.setObjectName("statusbar")
        TaskMain.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(TaskMain)
        self.toolBar.setObjectName("toolBar")
        TaskMain.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_New = QtWidgets.QAction(TaskMain)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/filenew.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_New.setIcon(icon)
        self.action_New.setObjectName("action_New")
        self.action_Open = QtWidgets.QAction(TaskMain)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/fileopen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Open.setIcon(icon1)
        self.action_Open.setObjectName("action_Open")
        self.action_Save = QtWidgets.QAction(TaskMain)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/filesave.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Save.setIcon(icon2)
        self.action_Save.setObjectName("action_Save")
        self.actionE_xit = QtWidgets.QAction(TaskMain)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icons/x.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionE_xit.setIcon(icon3)
        self.actionE_xit.setObjectName("actionE_xit")
        self.actionConsole = QtWidgets.QAction(TaskMain)
        self.actionConsole.setCheckable(True)
        self.actionConsole.setChecked(False)
        self.actionConsole.setObjectName("actionConsole")
        self.actionQuit = QtWidgets.QAction(TaskMain)
        self.actionQuit.setObjectName("actionQuit")
        self.actionRun = QtWidgets.QAction(TaskMain)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/run.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRun.setIcon(icon4)
        self.actionRun.setObjectName("actionRun")
        self.actionStop = QtWidgets.QAction(TaskMain)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStop.setIcon(icon5)
        self.actionStop.setObjectName("actionStop")
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionQuit)
        self.menu_Control.addAction(self.actionRun)
        self.menu_Control.addAction(self.actionStop)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Control.menuAction())
        self.menubar.addAction(self.menu_Instruments.menuAction())
        self.menubar.addAction(self.menu_Tasks.menuAction())
        self.menubar.addAction(self.menu_Docks.menuAction())
        self.menubar.addAction(self.menu_Plot.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.toolBar.addAction(self.action_Open)
        self.toolBar.addAction(self.actionRun)
        self.toolBar.addAction(self.actionStop)
        self.label_4.setBuddy(self.taskResult)

        self.retranslateUi(TaskMain)
        self.deviceInfoTabWidget.setCurrentIndex(0)
        self.action_Open.triggered.connect(TaskMain.onOpen)
        self.actionE_xit.triggered.connect(TaskMain.close)
        self.actionRun.triggered.connect(TaskMain.onRun)
        self.actionStop.triggered.connect(TaskMain.onStop)
        self.actionQuit.triggered.connect(TaskMain.close)
        QtCore.QMetaObject.connectSlotsByName(TaskMain)

    def retranslateUi(self, TaskMain):
        _translate = QtCore.QCoreApplication.translate
        TaskMain.setWindowTitle(_translate("TaskMain", "srsgui"))
        self.label_2.setText(_translate("TaskMain", "Instrument Info"))
        self.deviceInfoTabWidget.setTabText(self.deviceInfoTabWidget.indexOf(self.tab), _translate("TaskMain", "Instrument"))
        self.label_task_params.setText(_translate("TaskMain", "Task Parameters"))
        self.label_4.setText(_translate("TaskMain", "Task Result"))
        self.menu_File.setTitle(_translate("TaskMain", "&File"))
        self.menu_Control.setTitle(_translate("TaskMain", "&Control"))
        self.menu_Docks.setTitle(_translate("TaskMain", "&Docks"))
        self.menu_Help.setTitle(_translate("TaskMain", "&Help"))
        self.menu_Tasks.setTitle(_translate("TaskMain", "&Tasks"))
        self.menu_Instruments.setTitle(_translate("TaskMain", "&Instruments"))
        self.menu_Plot.setTitle(_translate("TaskMain", "&Plot"))
        self.toolBar.setWindowTitle(_translate("TaskMain", "toolBar"))
        self.action_New.setText(_translate("TaskMain", "&New"))
        self.action_Open.setText(_translate("TaskMain", "&Open Config"))
        self.action_Save.setText(_translate("TaskMain", "&Save"))
        self.actionE_xit.setText(_translate("TaskMain", "E&xit"))
        self.actionConsole.setText(_translate("TaskMain", "Console"))
        self.actionQuit.setText(_translate("TaskMain", "Quit"))
        self.actionRun.setText(_translate("TaskMain", "Run"))
        self.actionRun.setToolTip(_translate("TaskMain", "Start the selected test"))
        self.actionRun.setShortcut(_translate("TaskMain", "Alt+R"))
        self.actionStop.setText(_translate("TaskMain", "Stop"))
        self.actionStop.setToolTip(_translate("TaskMain", "Abort the current test"))
import srsgui.ui.resource_rc
