
import time
import json
import sys
from typing import Any, Iterable, List, Dict, Union

from srsgui.ui.qt.QtWidgets import QTreeView, QApplication, QHeaderView
from srsgui.ui.qt.QtGui import QBrush, QColor
from srsgui.ui.qt.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, QFileInfo

from srsgui import Component

from .commanditem import CommandItem, Index
from .commanddelegate import CommandDelegate


class CommandModel(QAbstractItemModel):
    """ An editable model of Command and Component """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.show_methods = True
        self.show_excluded = True
        self.show_set_only = True
        self.show_query_only = True
        self.show_raw_remote_command = True

        self._rootItem = CommandItem()
        self._headers = ("  command  ", "  value  ")

    def clear(self):
        """ Clear data from the model """
        self.load(Component())

    def load(self, document: Component, sort=False):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(
            document, Component
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()

        self._rootItem = CommandItem.load(document, sort=sort)
        self._rootItem.value_type = type(document)

        self.endResetModel()

        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Override from QAbstractItemModel

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
                if self.show_methods:
                    name += ' [M]' if item.is_method else ''
                if self.show_excluded:
                    name += ' [EX]' if item.excluded else ''
                if self.show_set_only:
                    name += ' [SO]' if item.set_enable and not item.get_enable else ''
                if self.show_query_only:
                    name += ' [QO]' if item.get_enable and not item.set_enable else ''
                return name

            if index.column() == 1:
                item = index.internalPointer()
                v = item.value
                if v is None:
                    return
                unit = item.get_unit()
                fmt = item.get_format()
                try:
                    if unit:
                        val = f'{v:{fmt}}  {item.get_unit()}'
                    else:
                        val = f'{v:{fmt}}'
                except ValueError:
                    print(f'ValueError: {item.raw_remote_command} {v} {fmt} {unit}')
                    val = f'{v}'
                return val

        elif role == Qt.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                val = item.value
                # print('data', item.name, item.comp, val)
                return val

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
                item.set_value(value)
                self.dataChanged.emit(index, index, [Qt.EditRole])
                return True
            return False
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: Qt.ItemDataRole    ):
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
        """Return True if item is editable, False otherwise"""
        item = index.internalPointer()
        if type(item) == CommandItem:
            return item.is_editable()
        else:
            return False


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

    # inst = RGA100('tcpip','172.25.70.12','admin','admin')
    # inst = RGA120('tcpip','172.25.70.12','admin','admin')    
    
    # inst.comm.set_callbacks(print, print)
    # print(inst.check_id())

    model.load(inst)

    view.show()
    view.header().setSectionResizeMode(0, QHeaderView.Stretch)
    # view.setAlternatingRowColors(True)
    view.resize(500, 300)
    app.exec_()