
import logging
from .jsonmodel import JsonModel

from srsgui.ui.qt.QtCore import Qt
from srsgui.ui.qt.QtWidgets import QWidget
from .ui_commandcapturewidget import Ui_CommandCaptureWidget

logger = logging.getLogger(__name__)


class CommandCaptureWidget(QWidget, Ui_CommandCaptureWidget):
    def __init__(self, parent=None):
        super(CommandCaptureWidget, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        #self.splitter.setStretchFactor(0, 1)
        #self.splitter.setStretchFactor(1, 2)

        self.inst = None
        self.name = None
        self.query_only_included = False
        self.set_only_included = False
        self.excluded_included = False
        self.method_included = False
        self.show_raw_command = False

        self.model = JsonModel()
        self.model._headers = ["   Command  ", "   Value  "]
        self.tree_view.setModel(self.model)

        self.query_only_checkbox.stateChanged.connect(self.on_query_only_changed)
        self.set_only_checkbox.stateChanged.connect(self.on_set_only_changed)
        self.excluded_checkbox.stateChanged.connect(self.on_excluded_changed)
        self.method_checkbox.stateChanged.connect(self.on_method_changed)
        self.raw_command_checkbox.stateChanged.connect(self.on_raw_command_changed)

        # self.update_button.clicked.connect(self.on_update_clicked)
        self.capture_button.clicked.connect(self.on_capture_clicked)
        self.expand_button.clicked.connect(self.on_expand_clicked)
        self.collapse_button.clicked.connect(self.on_collapse_clicked)

    def set_inst(self, name, inst):
        self.inst = inst
        self.name = name

    def on_query_only_changed(self, state):
        self.query_only_included = state != Qt.Unchecked

    def on_set_only_changed(self, state):
        self.set_only_included = state != Qt.Unchecked

    def on_excluded_changed(self, state):
        self.excluded_included = state != Qt.Unchecked

    def on_method_changed(self, state):
        self.method_included = state != Qt.Unchecked

    def on_raw_command_changed(self, state):
        self.show_raw_command = state != Qt.Unchecked

    def on_capture_clicked(self):
        if self.inst is not None and self.inst.is_connected():
            capture = self.inst.capture_commands(
                self.query_only_included, self.set_only_included, self.excluded_included,
                self.method_included, self.show_raw_command
            )
            self.model.load(capture, False)
            self.tree_view.expandToDepth(1)
            self.tree_view.resizeColumnToContents(0)
        else:
            logger.warning(f' {self.name} is NOT connected.')

    def on_expand_clicked(self):
        self.tree_view.expandAll()

    def on_collapse_clicked(self):
        self.tree_view.collapseAll()