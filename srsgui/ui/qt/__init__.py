
PYQT5 = 'PyQt5'
PYSIDE2 = 'PySide2'

try:
    from PyQt5 import QtCore
    QT_BINDER = PYQT5
except (ImportError, ModuleNotFoundError):
    QT_BINDER = PYSIDE2
    from PySide2 import QtCore
