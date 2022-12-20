
import logging
from .qt.QtCore import Qt
from .qt.QtWidgets import QDialog, QDialogButtonBox, \
                          QVBoxLayout, QGridLayout,\
                          QSpacerItem, QSizePolicy, \
                          QTabWidget, QWidget, QLabel, \
                          QLineEdit, QSpinBox, QComboBox, \
                          QMessageBox

from srsgui.inst.communications import Interface, SerialInterface, TcpipInterface
from srsgui import Instrument
from srsgui.task.inputs import BaseInput, IntegerInput, IntegerListInput, \
                               Ip4Input, BoolInput, StringInput, \
                               ComPortListInput

logger = logging.getLogger(__name__)


class ConnectDlg(QDialog):
    def __init__(self, inst, parent=None):
        super().__init__(parent)

        self.inst = inst
        self.parent = parent
        self.tabs = []

        self.resize(350, 100)
        self.verticalLayout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        if not issubclass(type(self.inst), Instrument):
            raise TypeError('Invalid instance of Instrument subclass: {}'.format(self.inst))
        if not hasattr(self.inst, 'available_interfaces'):
            raise AttributeError('No available_interfaces')

        for interface, args in self.inst.available_interfaces:
            tab = self.create_tab(args)
            self.tabs.append(tab)
            self.tabWidget.addTab(tab, interface.NAME.upper())

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
            widget = self.create_input_widget(parameters[key])
            grid.addWidget(label, row, 0, 1, 1)
            grid.addWidget(widget, row, 1, 1, 1)
            tab.widget_dict[key] = widget
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        grid.addItem(spacer, row+1, 1, 1, 1)
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

        elif type(input_item) == ComPortListInput:
            widget = QComboBox()
            widget.addItems(SerialInterface.find())
            widget.setCurrentIndex(p.value)
            p.text = widget.currentText()
            return widget

        elif type(input_item) == Ip4Input:
            widget = QLineEdit()
            widget.setInputMask('000.000.000.000;_')
            widget.setText(input_item.value)
            widget.selectAll()
            return widget
        else:
            return QLabel('Unkwon input type: {}'.format(input_item.__class__.__name__))

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
                else:
                    params[key].value = widget.value()
            args = []
            for v in params.values():
                if issubclass(type(v), BaseInput):
                    args.append(v.get_value())
                else:
                    args.append(v)
            print('args: {}'.format(args))
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
                # self.save_settings()
                pass
        QDialog.accept(self)  # This ends the dialog box.


