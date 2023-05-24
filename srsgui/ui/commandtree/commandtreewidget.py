##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

import logging
import time

from srsgui.ui.qt.QtCore import Qt, QModelIndex
from srsgui.ui.qt.QtWidgets import QWidget

from .ui_commandtreewidget import Ui_CommandTreeWidget
from .commandmodel import CommandModel
from .commanddelegate import CommandDelegate

logger = logging.getLogger(__name__)


class CommandTreeWidget(QWidget, Ui_CommandTreeWidget):
    """
    CommandTreeWidget is used to display an Instrument class in a tree view
    based on Qt Model/View architecture.
    """

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

        self.capture_time = 0.0  # time of the last capture
        self.capture_time_limit = 5.0  # seconds before a new capture

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
        self.tree_view.query_only_included = state
        self.tree_view.update_item_display()

    def on_set_only_changed(self, state):
        self.tree_view.set_only_included = state
        self.tree_view.update_item_display()

    def on_excluded_changed(self, state):
        self.tree_view.excluded_included = state
        self.tree_view.update_item_display()

    def on_method_changed(self, state):
        self.tree_view.method_included = state
        self.tree_view.update_item_display()

    def on_raw_command_changed(self, state):
        self.tree_view.show_raw_command = state
        self.model.show_raw_remote_command = self.tree_view.show_raw_command
        self.model.dataChanged.emit(QModelIndex(), QModelIndex())

    def on_capture_clicked(self):
        # Limit the frequency of new capture
        if self.parent and hasattr(self.parent, 'is_task_running'):
            if self.parent.is_task_running():
                logger.warning('No capture allowed during a task running')
                return

        current_time = time.time()
        if current_time - self.capture_time < self.capture_time_limit:
            return
        else:
            self.capture_time = current_time

        if self.inst is not None and self.inst.is_connected():
            try:
                self.model.show_raw_remote_command = self.show_raw_command
                self.model.load(self.inst)
                self.tree_view.expandToDepth(1)
                self.tree_view.resizeColumnToContents(0)
                # self.tree_view.collapseAll()
                self.tree_view.update_item_display()
                self.tree_view.connect_methods_to_buttons()

            except Exception as e:
                logger.error(f'Failed to load command tree from {self.name}: {e}')
        else:
            logger.warning(f' {self.name} is NOT connected.')

    def on_expand_clicked(self):
        self.tree_view.expandAll()

    def on_collapse_clicked(self):
        self.tree_view.collapseAll()

    def closeEvent(self, event) -> None:
        self.model.command_handler.stop()


if __name__ == '__main__':
    import sys
    from srsgui.ui.qt.QtWidgets import QApplication, QHeaderView
    from srsinst.sr860 import SR860

    app = QApplication(sys.argv)

    widget = CommandTreeWidget()

    inst = SR860('tcpip', '172.25.70.129')
    inst.query_text(' ')

    widget.set_inst('lockin', inst)

    # print(inst.check_id())
    # inst.comm.set_callbacks(print, print)

    # widget.model.load(inst)

    widget.show()

    widget.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
    widget.resize(600, 400)

    app.exec_()
