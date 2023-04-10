
import logging

from srsgui.ui.qt.QtCore import Qt, QModelIndex
from srsgui.ui.qt.QtWidgets import QWidget

from .ui_commandcapturewidget import Ui_CommandCaptureWidget

from .commandmodel import CommandModel
from .commanddelegate import CommandDelegate

logger = logging.getLogger(__name__)


class CommandTreeWidget(QWidget, Ui_CommandCaptureWidget):
    def __init__(self, parent=None):
        super(CommandTreeWidget, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)

        self.inst = None
        self.name = None
        self.query_only_included = False
        self.set_only_included = False
        self.excluded_included = False
        self.method_included = False
        self.show_raw_command = False

        self.model = CommandModel()
        self.tree_view.setItemDelegate(CommandDelegate())
        self.tree_view.setModel(self.model)

        self.expand_button.hide()

        self.query_only_checkbox.stateChanged.connect(self.on_query_only_changed)
        self.set_only_checkbox.stateChanged.connect(self.on_set_only_changed)
        self.excluded_checkbox.stateChanged.connect(self.on_excluded_changed)
        self.method_checkbox.stateChanged.connect(self.on_method_changed)
        self.raw_command_checkbox.stateChanged.connect(self.on_raw_command_changed)

        self.capture_button.clicked.connect(self.on_capture_clicked)
        self.expand_button.clicked.connect(self.on_expand_clicked)
        self.collapse_button.clicked.connect(self.on_collapse_clicked)

    def set_inst(self, name, inst):
        self.inst = inst
        self.name = name

    def on_query_only_changed(self, state):
        self.query_only_included = state
        self.update_item_display()

    def update_item_display(self, parent=QModelIndex()):
        for i in range(self.model.rowCount(parent)):
            index = self.model.index(i, 0, parent)
            self.update_item_display(index)

            item = index.internalPointer()
            query_only = set_only = is_method = is_excluded = False
            if not self.query_only_included:
                if not item.set_enable and item.get_enable:
                    query_only = True
            if not self.set_only_included:
                if item.set_enable and not item.get_enable:
                    set_only = True
            if not self.method_included:
                if item.is_method:
                    is_method = True
            if not self.excluded_included:
                if item.excluded:
                    is_excluded = True
            state = query_only or set_only or is_method or is_excluded
            self.tree_view.setRowHidden(i, parent, state)

    def on_set_only_changed(self, state):
        self.set_only_included = state
        self.update_item_display()

    def on_excluded_changed(self, state):
        self.excluded_included = state
        self.update_item_display()

    def on_method_changed(self, state):
        self.method_included = state
        self.update_item_display()

    def on_raw_command_changed(self, state):
        self.show_raw_command = state
        self.model.show_raw_remote_command = self.show_raw_command

    def on_capture_clicked(self):
        if self.inst is not None and self.inst.is_connected():
            try:
                self.model.show_raw_remote_command = self.show_raw_command
                self.model.load(self.inst, False)
                self.tree_view.expandToDepth(1)
                self.tree_view.resizeColumnToContents(0)
                # self.tree_view.collapseAll()
                self.update_item_display()
            except Exception as e:
                logger.error(f'Failed to load command tree from {self.name}: {e}')
        else:
            logger.warning(f' {self.name} is NOT connected.')

    def on_expand_clicked(self):
        self.tree_view.expandAll()

    def on_collapse_clicked(self):
        self.tree_view.collapseAll()
