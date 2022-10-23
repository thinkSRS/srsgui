
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QSpinBox, QComboBox, \
                            QLineEdit, QLabel, QGridLayout, QPushButton

from rgagui.basetest.basetest  import BaseTest
from rgagui.basetest.baseinput import IntegerInput, FloatInput, StringInput, ListInput

import logging
logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())


# build a input panels from input_parameters of BaseTest subclasses
class InputPanel(QWidget):
    FirstColumn = 0
    SecondColumn = 1

    def __init__(self, test: BaseTest, parent=None):
        try:
            if not isinstance(test, BaseTest) and not issubclass(test, BaseTest):
                raise TypeError(" not a subclass of BaseTest")
            super().__init__()
            layout = QGridLayout()
            self.test = test
            params = self.test.input_parameters

            row = 0
            for i in params.keys():
                p = params[i]
                if type(p) == StringInput:
                    widget = QLineEdit()
                    widget.setText(p.value)
                    setattr(self, i, widget)
                    label = QLabel(i.capitalize())
                    layout.addWidget(label, row, self.FirstColumn)
                    layout.addWidget(widget, row, self.SecondColumn)
                    row += 1
                    continue
                elif type(p) == ListInput:
                    widget = QComboBox()
                    widget.addItems(p.item_list)
                    widget.setCurrentIndex(p.value)

                    setattr(self, i, widget)
                    label = QLabel(i.capitalize())
                    layout.addWidget(label, row, self.FirstColumn)
                    layout.addWidget(widget, row, self.SecondColumn)
                    row += 1
                    continue

                elif type(p) == FloatInput:
                    widget = QDoubleSpinBox()
                    setattr(self, i, widget)
                    widget.setDecimals(4)
                    widget.setAlignment(Qt.AlignRight)
                elif type(p) == IntegerInput:
                    widget = QSpinBox()
                    setattr(self, i, widget)
                    widget.setAlignment(Qt.AlignRight)
                else:
                    raise TypeError('Unknown input type')

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

                label = QLabel(i.capitalize())
                layout.addWidget(label, row, self.FirstColumn)
                layout.addWidget(widget, row, self.SecondColumn)
                row += 1

            self.pb_default = QPushButton("Default")
            layout.addWidget(self.pb_default, row, 0)
            self.pb_apply = QPushButton("Apply")
            layout.addWidget(self.pb_apply, row, 1)
            self.setLayout(layout)

            self.pb_default.clicked.connect(self.on_default)
            self.pb_apply.clicked.connect(self.on_apply)
        except Exception as e:
            print(e)
        logger.debug("{} init done".format(self.__class__.__name__))

    def update(self):
        try:
            params = self.test.input_parameters
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
            params = self.test.input_parameters
            for i in params.keys():
                params[i].value = params[i].default_value
                widget = getattr(self, i, None)
                if type(widget) == QLineEdit:
                    widget.setText(params[i].default_value)
                elif type(widget) == QComboBox:
                    widget.setCurrentIndex(params[i].default_value)
                else:
                    widget.setValue(params[i].default_value)
            logger.debug("{} reset to default".format(self.__class__.__name__))
        except Exception as e:
            logger.error(e)

    def on_apply(self):
        params = self.test.input_parameters
        for i in params.keys():
            widget = getattr(self, i, None)
            if type(widget) == QLineEdit:
                params[i].value = widget.text()
            elif type(widget) == QComboBox:
                params[i].value = widget.currentIndex()
            else:
                params[i].value = widget.value()
        logger.debug("{} apply parameters from panel".format(self.__class__.__name__))
