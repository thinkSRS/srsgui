##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

import math
from .qt.QtCore import Qt
from .qt.QtWidgets import QWidget, QDoubleSpinBox, QSpinBox, QComboBox, \
                          QLineEdit, QLabel, QGridLayout, QPushButton, QScrollArea

from srsgui.inst.commands import Command, IntCommand, FloatCommand, DictCommand
from srsgui.inst.indexcommands import IntIndexCommand, FloatIndexCommand, DictIndexCommand

from srsgui.task.task import Task
from srsgui.task.inputs import IntegerInput, FloatInput, StringInput, \
                               ListInput, InstrumentInput, CommandInput

import logging
logger = logging.getLogger(__name__)


class InputPanel(QScrollArea):
    """
    To build the input panel in an instance of :class:`srsgui.ui.taskmain.TaskMain` class
    based on input_parameters of a subclass of :class:`srsgui.task.task.Task` class
    """
    FirstColumn = 0
    SecondColumn = 1

    def __init__(self, task_class: Task, parent):
        try:
            if not issubclass(task_class, Task):
                raise TypeError(" not a subclass of Task")
            super().__init__()

            self.parent = parent
            self.task_class = task_class

            self.inst_name = None
            self.inst_dict = self.parent.inst_dict
            self.command_handler = self.parent.command_handler
            self.command_dict = {}
            self.command_handler.command_processed.connect(self.handle_reply)

            params = self.task_class.input_parameters

            layout = QGridLayout()
            row = 0
            for name in params.keys():
                p = params[name]
                param_type = type(p)
                if param_type == StringInput:
                    widget = QLineEdit()
                    widget.setText(p.value)
                    setattr(self, name, widget)
                    label = QLabel(name)
                    layout.addWidget(label, row, self.FirstColumn)
                    layout.addWidget(widget, row, self.SecondColumn)
                    row += 1
                    continue
                elif param_type == InstrumentInput:
                    if not (self.parent and hasattr(self.parent, 'inst_dict')):
                        logger.error('No inst_dict available for InstrumentInput')
                        continue
                    widget = QComboBox()
                    widget.addItems(self.parent.inst_dict.keys())
                    widget.setCurrentIndex(p.value)
                    p.text = widget.currentText()
                    self.inst_name = p.text

                    setattr(self, name, widget)
                    label = QLabel(name)
                    layout.addWidget(label, row, self.FirstColumn)
                    layout.addWidget(widget, row, self.SecondColumn)
                    row += 1
                    continue
                elif issubclass(param_type, ListInput):
                    widget = QComboBox()
                    widget.addItems(p.item_list)
                    widget.setCurrentIndex(p.value)
                    p.text = widget.currentText()

                    setattr(self, name, widget)
                    label = QLabel(name)
                    layout.addWidget(label, row, self.FirstColumn)
                    layout.addWidget(widget, row, self.SecondColumn)
                    row += 1
                    continue

                elif param_type == CommandInput:
                    if not self.inst_name:
                        raise ValueError('CommandInput defined "{}" before any instrumentInput'
                                         .format(p.cmd_name))

                    if not self.inst_dict[self.inst_name].is_connected:
                        raise ValueError('{} is not connected'.format(self.inst_name))

                    p.set_inst_name(self.inst_name)
                    if issubclass(p.cmd_instance.__class__, IntCommand) or \
                       issubclass(p.cmd_instance.__class__, IntIndexCommand):
                        widget = QSpinBox()
                        widget.setSuffix(' ' + p.cmd_instance.unit)
                        widget.setMaximum(p.cmd_instance.maximum)
                        widget.setMinimum(p.cmd_instance.minimum)
                        widget.setSingleStep(p.cmd_instance.step)
                        widget.setAlignment(Qt.AlignRight)

                    elif issubclass(p.cmd_instance.__class__, FloatCommand) or \
                         issubclass(p.cmd_instance.__class__, FloatIndexCommand):
                        widget = QDoubleSpinBox()
                        widget.setSuffix(' ' + p.cmd_instance.unit)
                        widget.setMaximum(p.cmd_instance.maximum)
                        widget.setMinimum(p.cmd_instance.minimum)
                        widget.setSingleStep(p.cmd_instance.step)
                        widget.setDecimals(math.ceil(math.log10(1.0 / p.cmd_instance.step)))
                        widget.setAlignment(Qt.AlignRight)

                    elif issubclass(p.cmd_instance.__class__, DictCommand) or \
                         issubclass(p.cmd_instance.__class__, DictIndexCommand):
                        widget = QComboBox()
                        item_list = map(str, p.cmd_instance.set_dict.keys())
                        widget.addItems(item_list)
                        if p.value is None:
                            p.value = 0
                        widget.setCurrentIndex(p.value)
                        p.text = widget.currentText()

                    else:
                        widget = QLineEdit()

                    self.command_dict[p.cmd] = widget
                    self.command_handler.process_command(p.cmd, '')

                    setattr(self, name, widget)

                    label = QLabel(name)
                    layout.addWidget(label, row, self.FirstColumn)
                    layout.addWidget(widget, row, self.SecondColumn)
                    row += 1
                    continue

                elif param_type == FloatInput:
                    widget = QDoubleSpinBox()
                    setattr(self, name, widget)
                    widget.setDecimals(4)
                    widget.setAlignment(Qt.AlignRight)
                elif param_type == IntegerInput:
                    widget = QSpinBox()
                    setattr(self, name, widget)
                    widget.setAlignment(Qt.AlignRight)
                else:
                    raise TypeError('Unknown input type: {}'.format(param_type))

                if p.value < p.minimum or p.value > p.maximum:
                    widget.setMinimum(p.value)
                    widget.setMaximum(p.value)
                    widget.setEnabled(False)
                else:
                    widget.setMinimum(p.minimum)
                    widget.setMaximum(p.maximum)
                    widget.setEnabled(True)
                widget.setSingleStep(p.single_step)
                widget.setSuffix(' ' + p.suffix)
                widget.setValue(p.value)

                label = QLabel(name.capitalize())
                layout.addWidget(label, row, self.FirstColumn)
                layout.addWidget(widget, row, self.SecondColumn)
                row += 1

            if row > 0:
                self.pb_default = QPushButton("Default")
                layout.addWidget(self.pb_default, row, 0)
                self.pb_apply = QPushButton("Apply")
                layout.addWidget(self.pb_apply, row, 1)
                self.pb_default.clicked.connect(self.on_default)
                self.pb_apply.clicked.connect(self.on_apply)

            wid = QWidget()
            wid.setLayout(layout)
            self.setWidget(wid)
            self.setWidgetResizable(True)

        except Exception as e:
            logger.error(e)
        logger.debug("{} init done".format(self.__class__.__name__))

    def update(self):
        try:
            params = self.task_class.input_parameters
            for i in params.keys():
                widget = getattr(self, i, None)
                if type(widget) == QLineEdit:
                    widget.setText(params[i].value)
                elif type(widget) == QComboBox:
                    widget.setCurrentIndex(params[i].value)
                else:
                    widget.setValue(params[i].value)
            logger.debug("{} updated".format(self.__class__.__name__))
        except Exception as e:
            logger.error(e)

    def on_default(self):
        try:
            params = self.task_class.input_parameters
            for name in params.keys():
                if params[name].default_value is None:
                    continue
                widget = getattr(self, name, None)
                cmd = None
                if type(widget) == QLineEdit and type(params[name].default_value) == str:
                    params[name].value = params[name].default_value
                    widget.setText(params[name].default_value)
                    if type(params[name]) == CommandInput:
                        cmd = '{} = "{}"'.format(params[name].cmd, params[name].default_value)
                elif type(widget) == QComboBox and type(params[name].default_value) == int:
                    params[name].value = params[name].default_value
                    widget.setCurrentIndex(params[name].default_value)
                    params[name].text = widget.currentText()
                    if type(params[name]) == CommandInput:
                        if hasattr(params[name].cmd_instance, 'key_type') and \
                           getattr(params[name].cmd_instance, 'key_type') == 'int':
                            cmd = '{} = {}'.format(params[name].cmd, params[name].default_value)
                        else:
                            cmd = '{} = "{}"'.format(params[name].cmd, params[name].text)
                elif type(widget) == QSpinBox and type(params[name].default_value) == int:
                    params[name].value = params[name].default_value
                    widget.setValue(params[name].default_value)
                    if type(params[name]) == CommandInput:
                        cmd = '{} = {}'.format(params[name].cmd, params[name].default_value)
                elif type(widget) == QDoubleSpinBox and type(params[name].default_value) == float:
                    params[name].value = params[name].default_value
                    widget.setValue(params[name].default_value)
                    if type(params[name]) == CommandInput:
                        cmd = '{} = {}'.format(params[name].cmd, params[name].default_value)
                else:
                    logger.error('error to reset "{}" to default, {}'.
                                 format(name, params[name].default_value))
                if cmd:
                    self.command_handler.process_command(cmd, '')
            logger.debug("{} reset to default".format(self.__class__.__name__))
        except Exception as e:
            logger.error(e)

    def on_apply(self):
        try:
            params = self.task_class.input_parameters
            for name in params.keys():
                widget = getattr(self, name, None)
                cmd = None
                if type(widget) == QLineEdit:
                    params[name].value = widget.text()
                    if type(params[name]) == CommandInput:
                        cmd = '{} = "{}"'.format(params[name].cmd, widget.text())

                elif type(widget) == QComboBox:
                    params[name].value = widget.currentIndex()
                    params[name].text = widget.currentText()
                    if type(params[name]) == CommandInput:
                        if hasattr(params[name].cmd_instance, 'key_type') and \
                           getattr(params[name].cmd_instance, 'key_type') is str:
                            fmt = '{} = "{}"'
                        else:
                            fmt = '{} = {}'
                        cmd = fmt.format(params[name].cmd, widget.currentText())

                elif type(widget) in (QSpinBox, QDoubleSpinBox):
                    params[name].value = widget.value()
                    if type(params[name]) == CommandInput:
                        cmd = '{} = {}'.format(params[name].cmd, widget.value())

                if cmd:
                    self.command_handler.process_command(cmd, '')

            logger.debug("{} apply parameters from panel".format(self.__class__.__name__))
        except Exception as e:
            logger.error(e)

    def handle_reply(self, cmd, reply):
        try:
            if cmd in self.command_dict:
                if type(self.command_dict[cmd]) == QSpinBox:
                    self.command_dict[cmd].setValue(int(reply))

                elif type(self.command_dict[cmd]) == QDoubleSpinBox:
                    self.command_dict[cmd].setValue(float(reply))

                elif type(self.command_dict[cmd]) == QComboBox:
                    index = self.command_dict[cmd].findText(reply)
                    self.command_dict[cmd].setCurrentIndex(index)

                elif type(self.command_dict[cmd]) == QLineEdit:
                    self.command_dict[cmd].setText(reply)

                else:
                    logger.error('Unhandled Command: {}'.format(cmd))

        except Exception as e:
            logger.error(e)
