##! 
##! Copyright(c) 2022, 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

import logging

from srsgui.ui.qt.QtCore import Qt
from srsgui.ui.qt.QtWidgets import QStyledItemDelegate, QComboBox

from srsgui.inst import DictCommand, FloatCommand, IntCommand, \
                        FloatIndexCommand, IntIndexCommand, DictIndexCommand

from .commandspinbox import FloatSpinBox, IntegerSpinBox
from .commanditem import Index

logger = logging.getLogger(__file__)


class CommandDelegate(QStyledItemDelegate):
    """ A custom delegate for editing CommandItem """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        if item.comp_type == Index:
            comp = item.parent().comp
            comp_type = item.parent().comp_type
        else:
            comp = item.comp
            comp_type = item.comp_type

        if issubclass(comp_type, FloatCommand) or issubclass(comp_type, FloatIndexCommand):
            editor = FloatSpinBox(parent)
            editor.setDecimals(10)
            editor.setSingleStep(0.1)
            editor.setMinimum(comp.minimum)
            editor.setMaximum(comp.maximum)
            editor.setSuffix(' ' + comp.unit)
            editor.set_significant_figures(comp.significant_figures)
            editor.set_minimum_step(comp.step)
            return editor

        elif issubclass(comp_type, IntCommand) or issubclass(comp_type, IntIndexCommand):
            editor = IntegerSpinBox(parent)
            editor.setMinimum(comp.minimum)
            editor.setMaximum(comp.maximum)
            editor.setSuffix(' ' + comp.unit)
            return editor

        elif comp_type in (DictCommand, DictIndexCommand):
            editor = QComboBox(parent)
            for key in comp.set_dict.keys():
                editor.addItem(str(key))
            return editor

        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):

        if type(editor) in (FloatSpinBox, IntegerSpinBox):
            item = index.internalPointer()
            val = index.model().data(index, Qt.EditRole)
            editor.setValue(val)

        elif type(editor) == QComboBox:
            item = index.internalPointer()
            val = index.model().data(index, Qt.EditRole)
            editor.setCurrentText(str(val))
        return super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):

        try:
            item = index.internalPointer()
            if item.comp_type == Index:
                comp = item.parent().comp
                comp_type = item.parent().comp_type
            else:
                comp = item.comp
                comp_type = item.comp_type

            if issubclass(comp_type, FloatCommand) or issubclass(comp_type, FloatIndexCommand):
                value = editor.value()
                model.setData(index, value, Qt.EditRole)
                item.precision = editor.precision
            elif issubclass(comp_type, IntCommand) or issubclass(comp_type, IntIndexCommand):
                pass

                value = editor.value()
                model.setData(index, value, Qt.EditRole)
            elif comp_type in (DictCommand, DictIndexCommand):
                val = editor.currentText()
                convert = type(list(comp.get_dict.keys())[0])
                value = convert(val)
                model.setData(index, value, Qt.EditRole)
            else:
                return super().setModelData(editor, model, index)
        except Exception as e:
            logger.error(e)

    def updateEditorGeometry(self, editor, option, index):
        return super().updateEditorGeometry(editor, option, index)

