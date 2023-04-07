
import sys
import math
from srsgui.ui.qt.QtWidgets import QApplication, QWidget, QSpinBox, QDoubleSpinBox, QLabel, QFormLayout
from srsgui.ui.qt.QtCore import Qt


class IntegerSpinBox(QSpinBox):
    """
    Adjust step size depending on the cursor postion
    """
    
    def stepBy(self, steps):        
        prefix_len = len(self.prefix())
        min_pos = prefix_len + 1 if self.value() < 0 else prefix_len

        text = self.lineEdit().text()
        cur_pos = self.lineEdit().cursorPosition()
        sep_pos = len(text)

        if cur_pos < min_pos:
            return
        
        exponent = sep_pos - cur_pos
            
        single_step = 10 ** exponent        
        self.setSingleStep(single_step)
        
        super().stepBy(steps)

        self.lineEdit().deselect()
        
        min_pos = prefix_len + 1 if self.value() < 0 else prefix_len
        
        text = self.lineEdit().text()
        new_sep_pos = len(text)
        
        new_cur_pos = cur_pos + new_sep_pos - sep_pos        
        if new_cur_pos < min_pos:
            new_cur_pos = min_pos
        self.lineEdit().setCursorPosition(new_cur_pos)


class FloatSpinBox(QDoubleSpinBox):
    """
    Adjust step size depending on the cursor postion
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minimum_step = 0.1
        self.significant_figures = 4

    def set_minimum_step(self, value):
        self.minimum_step = value
        step = self.minimum_step if self.minimum_step > 1e-12 else 1e-12
        self.decimals = math.ceil(math.log10(1.0 / step))

    def set_significant_figures(self, value):
        self.significant_figures = value

    def valueFromText(self, text):
        try:
            if self.suffix():
                unit_len = len(self.suffix())
                value = float(text[:-unit_len])
            else:
                value = float(text)
            if value < self.minimum():
                value = self.minimum()
            elif value > self.maximum():
                value = self.maximum()
        except ValueError:
            print('valueFromText ValueError', text, self.suffix())
            value = self.minimum()
        return value

    def textFromValue(self, value):
        try:
            if value == 0:
                return '0.0'

            digits = math.ceil(math.log10(abs(value)))
            digits = 0 if digits < 0 else digits

            if digits == self.significant_figures:
                step = 1
            else:
                step = 10 ** (digits - self.significant_figures)
            value = round(value / step) * step
            prec = self.significant_figures - digits
        except Exception as e:
            print(e)

        format_string = '{:.' + str(prec) + 'f}'
        text = format_string.format(value)
        return text
    
    def stepBy(self, steps):        
        prefix_len = len(self.prefix())
        min_pos = prefix_len + 1 if self.value() < 0 else prefix_len

        text = self.lineEdit().text()
        cur_pos = self.lineEdit().cursorPosition()
        sep_pos = text.find('.')
        if sep_pos < 0:
            sep_pos = len(text)
            
        if cur_pos < min_pos:
            return
        
        exponent = sep_pos - cur_pos
        if exponent == -1:
            cur_pos += 1
            
        if exponent < -1:
            exponent += 1
            
        single_step = 10 ** exponent        
        self.setSingleStep(single_step)
        
        super().stepBy(steps)

        self.lineEdit().deselect()
        
        min_pos = prefix_len + 1 if self.value() < 0 else prefix_len
        
        text = self.lineEdit().text()
        new_sep_pos = text.find('.')
        if new_sep_pos < 0:
            new_sep_pos = len(text)
        
        new_cur_pos = cur_pos + new_sep_pos - sep_pos        
        if new_cur_pos < min_pos:
            new_cur_pos = min_pos
        self.lineEdit().setCursorPosition(new_cur_pos)


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyQt QSpinBox')
        self.setMinimumWidth(300)

        # create a grid layout
        layout = QFormLayout()
        self.setLayout(layout)

        amount = FloatSpinBox(minimum=-100, maximum=1000, value=20, prefix='$')

        amount.valueChanged.connect(self.update)

        self.result_label = QLabel('', self)

        layout.addRow('Amount:', amount)
        layout.addRow(self.result_label)

        # show the window
        self.show()

    def update(self, value):
        self.result_label.setText(f'Current Value: {value:.3f}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
