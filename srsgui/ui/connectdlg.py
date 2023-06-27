##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

import logging
from .qt.QtCore import Qt, QSettings
from .qt.QtWidgets import QDialog, QDialogButtonBox, \
                          QVBoxLayout, QGridLayout,\
                          QSpacerItem, QSizePolicy, \
                          QTabWidget, QWidget, QLabel, \
                          QLineEdit, QSpinBox, QComboBox, \
                          QMessageBox

from srsgui.inst.instrument import Instrument
from srsgui.task.inputs import BaseInput, IntegerInput, IntegerListInput, \
                               Ip4Input, BoolInput, StringInput, \
                               FindListInput, PasswordInput

logger = logging.getLogger(__name__)


class ConnectDlg(QDialog):
    """
    * To build the connection dialog box based on *available_interface* of subclasses of
      :class:`srsgui.inst.instrument.Instrument` class listed in the current .taskconfig file.

    * To connect to the selected interface of the instrument.
    """

    def __init__(self, inst, parent=None):
        super().__init__(parent)

        self.inst = inst
        self.parent = parent
        self.tabs = []
        self.settings = QSettings()

        self.resize(350, 100)
        self.setWindowTitle('Connect to "{}"'.format(self.inst.get_name()))
        self.verticalLayout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        if not issubclass(type(self.inst), Instrument):
            raise TypeError('Invalid instance of Instrument subclass: {}'.format(self.inst))
        if not hasattr(self.inst, 'available_interfaces'):
            raise AttributeError('No available_interfaces')

        for interface, args in self.inst.available_interfaces:
            if hasattr(interface, 'find'):
                self.find_items = interface.find()
            else:
                self.find_items = []
            tab = self.create_tab(args)
            self.tabWidget.addTab(tab, interface.NAME.upper())
            self.tabs.append(tab)
        self.load_setting()
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.verticalLayout.addWidget(self.tabWidget)
        self.verticalLayout.addWidget(self.buttonBox)

    def create_tab(self, parameters):
        tab = QWidget()
        tab.widget_dict = {}
        grid = QGridLayout(tab)
        for row, key in enumerate(parameters):
            label = QLabel(key.capitalize().replace('_', ' '))
            if issubclass(type(parameters[key]), BaseInput):
                widget = self.create_input_widget(parameters[key])
            else:
                widget = QLabel(str(parameters[key]))

            grid.addWidget(label, row, 0, 1, 1)
            grid.addWidget(widget, row, 1, 1, 1)
            tab.widget_dict[key] = widget
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        grid.addItem(spacer, row + 1, 1, 1, 1)
        return tab

    def create_input_widget(self, input_item):
        p = input_item
        if type(input_item) == StringInput:
            widget = QLineEdit()
            widget.setText(input_item.value)
            return widget

        elif type(input_item) == IntegerInput:
            widget = QSpinBox()
            if p.value < p.minimum or p.value > p.maximum:
                widget.setMinimum(p.value)
                widget.setMaximum(p.value)
                widget.setEnabled(False)
            else:
                widget.setMinimum(p.minimum)
                widget.setMaximum(p.maximum)
                widget.setEnabled(True)
            widget.setSingleStep(p.single_step)
            widget.setSuffix(p.suffix)
            widget.setValue(p.value)
            return widget

        elif type(input_item) == BoolInput:
            widget = QComboBox()
            widget.addItems(p.item_list)
            widget.setCurrentIndex(p.value)
            p.text = widget.currentText()
            return widget

        elif type(input_item) == IntegerListInput:
            widget = QComboBox()
            widget.addItems(p.item_list)
            widget.setCurrentIndex(p.value)
            p.text = widget.currentText()
            return widget

        elif type(input_item) == FindListInput:
            widget = QComboBox()
            widget.addItems(self.find_items)
            widget.setCurrentIndex(p.value)
            p.text = widget.currentText()
            return widget

        elif type(input_item) == Ip4Input:
            widget = QLineEdit()
            widget.setInputMask('000.000.000.000;_')
            widget.setText(input_item.value)
            widget.selectAll()
            return widget

        elif type(input_item) == PasswordInput:
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.Password)
            widget.setText(input_item.value)
            return widget

        else:
            return QLabel('Unknown input type: {}'.format(input_item.__class__.__name__))

    def accept(self):
        try:
            if self.inst.is_connected():
                self.inst.comm.disconnect()

            index = self.tabWidget.currentIndex()
            widgets = self.tabs[index].widget_dict
            interface, params = self.inst.available_interfaces[index]
            for key, widget in widgets.items():
                if type(widget) == QLineEdit:
                    params[key].value = widget.text()
                elif type(widget) == QComboBox:
                    params[key].value = widget.currentIndex()
                    params[key].text = widget.currentText()
                elif type(widget) != QLabel:
                    params[key].value = widget.value()
            args = []
            for v in params.values():
                if issubclass(type(v), BaseInput):
                    args.append(v.get_value())
                else:
                    args.append(v)
            # print('args: {}'.format(args))
            self.inst.connect(interface.NAME, *args)
        except Exception as e:
            msg = '{}: {}'.format(e.__class__.__name__, e)
            logger.error(msg)
            QMessageBox.warning(self, 'Error', msg)

        else:
            logger.info('Connected to {} interface'.format(interface.NAME))

        if self.inst.is_connected():
            try:
                self.inst.check_id()  # clear the comm buffer
                if self.inst.check_id()[0] is None:  # make sure it is a correct DUT
                    self.inst.disconnect()
                    err_string = 'Disconnected from an Invalid instrument'
                    logger.error(err_string)
                    QMessageBox.warning(self, 'Error', err_string)

            except Exception as e:
                err_string = 'Disconnected with error during ID checking: {}'.format(e)
                logger.error(err_string)
                QMessageBox.warning(self, 'Error', err_string)
                try:
                    self.inst.disconnect()
                except:
                    pass
            else:
                self.save_settings()

        QDialog.accept(self)  # This closes the dialog box.

    def save_settings(self):
        if not self.inst.is_connected():
            return
        try:
            base = 'ConnectDlg/{}/{}'.format(self.inst.get_name(), self.inst.comm.NAME)
            for interface, params in self.inst.available_interfaces:
                if interface.NAME == self.inst.comm.NAME:
                    for k, v in params.items():
                        if issubclass(type(v), BaseInput):
                            key = '{}/{}'.format(base, k)
                            self.settings.setValue(key, v.get_value())
                    break
        except Exception as e:
            logger.error('Error during save_settings: {}'.format(e))

    def load_setting(self):
        try:
            for index, (interface, params) in enumerate(self.inst.available_interfaces):
                tab = self.tabs[index]
                base = 'ConnectDlg/{}/{}'.format(self.inst.get_name(), interface.NAME)
                for k, v in params.items():
                    if issubclass(type(v), BaseInput):
                        key = '{}/{}'.format(base, k)
                        if k not in tab.widget_dict:
                            logger.error('{} not in {}'.format(key, tab.widget_dict))
                        widget = tab.widget_dict[k]
                        if type(widget) == QLineEdit:
                            val = self.settings.value(key, "")
                            if val:
                                widget.setText(val)
                        elif type(widget) == QSpinBox:
                            val = self.settings.value(key, -9999)
                            if val != -9999:
                                widget.setValue(val)
                        elif type(widget) == QComboBox:
                            val = self.settings.value(key, "")
                            if val:
                                index = widget.findText(str(val))
                                widget.setCurrentIndex(index)
        except Exception as e:
            logger.error('Error during load_settings: {}: {}'.format(e.__class__.__name__, e))
