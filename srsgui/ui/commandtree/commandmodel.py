##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

import sys

from typing import Any, Iterable, List, Dict, Union

from srsgui.ui.qt.QtWidgets import QTreeView, QApplication, QHeaderView
from srsgui.ui.qt.QtGui import QBrush, QColor
from srsgui.ui.qt.QtCore import QAbstractItemModel, QModelIndex, \
                                QObject, Qt, Signal

from srsgui import Component

from .commanditem import CommandItem, Index
from .commanddelegate import CommandDelegate
from .commandhandler import CommandHandler


class CommandModel(QAbstractItemModel):
    """ An editable model of Command and Component """

    # Signal to request to process a query to an outside command processor
    query_requested = Signal(QModelIndex)

    # Signal to request to process a set to an outside command processor
    set_requested = Signal(tuple)

    # Signal to display full Python command to CommandTerminal
    set_command_sent = Signal(str, str)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.show_raw_remote_command = True

        self._rootItem = CommandItem()
        self._headers = ("  Command  ", "  Value  ")

    def clear(self):
        """ Clear data from the model """
        self.load(Component())

    def load(self, document: Component):
        """Load model from a ComponentItem instance returned by CommandItem.loads()

        Arguments:
            document: Component instance
        """

        assert isinstance(
            document, Component
        ), "`document` must be a Component, " f"not {type(document)}"

        self.beginResetModel()

        self._rootItem = CommandItem.load(document)
        self._rootItem.value_type = type(document)

        self.endResetModel()
        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """
        Override from QAbstractItemModel

        Return data from an item according index and role
        """

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if index.column() == 0:
                item = index.internalPointer()
                name = item.name

                if self.show_raw_remote_command:
                    name += f' <{item.raw_remote_command}>' if item.raw_remote_command else ''

                name += ' [M]' if item.is_method else ''
                name += ' [EX]' if item.excluded else ''
                name += ' [SO]' if item.set_enable and not item.get_enable else ''
                name += ' [QO]' if item.get_enable and not item.set_enable else ''
                return name

            if index.column() == 1:
                item = index.internalPointer()
                self.query_requested.emit(index)
                return item.get_formatted_value()

        elif role == Qt.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                self.query_requested.emit(index)
                return item.value

        elif role == Qt.BackgroundRole:
            item = index.internalPointer()
            if item.comp_type != Index and issubclass(item.comp_type, Component):
                return QBrush(QColor(243, 230, 225))
            if item.row() % 2 == 0:
                return QBrush(QColor(240, 240, 253))

        elif role == Qt.ToolTipRole:
            item = index.internalPointer()
            if item.is_method or issubclass(item.comp_type, Component):
                if hasattr(item.comp, '__doc__') and index.column() == 0:
                    return item.comp.__doc__

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Set CommandItem according to index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)
        """

        if role == Qt.EditRole:

            if index.column() == 1:
                item = index.internalPointer()
                self.set_requested.emit((index, value))
                sent_command = item.construct_set_command_string(value)
                self.set_command_sent.emit(sent_command, None)

                # item.set_value(value)
                # self.dataChanged.emit(index, index, [Qt.EditRole])
                return True

            return False
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        it returns only data for columns (orientation = Horizontal)
        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index
        """

        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(CommandModel, self).flags(index)

        if index.column() == 1 and self.is_item_editable(index):
            return Qt.ItemIsEditable | flags
        else:
            return flags

    def is_item_editable(self, index: QModelIndex) -> bool:
        """
        Return True if item is editable, False otherwise
        """
        item = index.internalPointer()
        if type(item) == CommandItem:
            return item.is_editable()
        else:
            return False

    def handle_command(self, cmd_tuple):
        """
        External command processor calls this slot once a command is processed
        """
        index = cmd_tuple[0]
        value = cmd_tuple[1]
        changed = cmd_tuple[2]
        if changed:
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])


if __name__ == "__main__":
    from srsinst.sr860 import SR860

    app = QApplication(sys.argv)
    view = QTreeView()
    delegate = CommandDelegate()
    model = CommandModel()

    view.setModel(model)
    view.setItemDelegate(delegate)

    inst = SR860('tcpip', '172.25.70.129')
    inst.query_text(' ')

    model.load(inst)

    view.show()
    view.header().setSectionResizeMode(0, QHeaderView.Stretch)
    view.resize(500, 300)
    app.exec_()
