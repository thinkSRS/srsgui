import sys
import inspect
import logging

from srsgui.ui.qt.QtCore import Qt, QModelIndex
from srsgui.ui.qt.QtWidgets import QTreeView, QApplication, QHeaderView

from .commandmodel import CommandModel
from .commanddelegate import CommandDelegate
from .commandspinbox import RunButton


class CommandTreeView(QTreeView):
    def __init__(self, parent=None):
        super(CommandTreeView, self).__init__(parent)
        
        self.query_only_included = False
        self.set_only_included = False
        self.excluded_included = False
        self.method_included = False
        self.show_raw_command = False

    def update_item_display(self, parent=QModelIndex()):
        for i in range(self.model().rowCount(parent)):
            index = self.model().index(i, 0, parent)
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
            self.setRowHidden(i, parent, state)

    def connect_methods_to_buttons(self, parent=QModelIndex()):
        for i in range(self.model().rowCount(parent)):
            index = self.model().index(i, 0, parent)
            self.connect_methods_to_buttons(index)
            try:
                item = index.internalPointer()
                if item.is_method:
                    widget_index = self.model().index(i, 1, parent)
                    spec = inspect.getfullargspec(item.comp)
                    if spec.defaults is None:
                        flag = len(spec.args) == 1
                    else:
                        flag = len(spec.args) - len(spec.defaults) == 1
                    if flag:
                        parent_comp = item.parent().comp
                        meth = getattr(parent_comp, item.name)
                        if meth and meth.__func__ in parent_comp.allow_run_button:
                            button = RunButton()
                            button.pressed.connect(meth)
                            self.setIndexWidget(widget_index, button)
            except Exception as e:
                logging.error(e)


if __name__ == "__main__":
    from srsinst.sr860 import SR860

    app = QApplication(sys.argv)
    view = CommandTreeView()
    delegate = CommandDelegate()
    model = CommandModel()

    view.setModel(model)
    view.setItemDelegate(delegate)

    inst = SR860('tcpip', '172.25.70.129')
    inst.query_text(' ')

    # print(inst.check_id())
    # inst.comm.set_callbacks(print, print)

    model.load(inst)

    view.show()
    view.header().setSectionResizeMode(0, QHeaderView.Stretch)
    view.resize(500, 300)
    app.exec_()
