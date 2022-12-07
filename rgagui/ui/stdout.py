
import sys

from .qt.QtCore import QObject
from .qt.QtCore import Signal


# redirect STDOUT and STDERR to a function
class StdOut(QObject):
    textWritten = Signal(str)

    def __init__(self, output_function, parent=None):
        super().__init__(parent)
        self.textWritten.connect(output_function)
        sys.stdout = self
        sys.stderr = self

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass

    def __del__(self):
        try:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        except:
            # With PySide2, sys becomes None
            pass
