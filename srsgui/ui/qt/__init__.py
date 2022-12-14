
PYQT5 = 'PyQt5'
PYSIDE2 = 'PySide2'
QT_BINDER = PYQT5

try:
    from PyQt5 import QtCore
except (ImportError, ModuleNotFoundError):
    QT_BINDER = PYSIDE2

if QT_BINDER == PYSIDE2:
    try:
        from PySide2 import QtCore
    except (ImportError, ModuleNotFoundError):
        QT_BINDER = None

if not QT_BINDER:
    msg = "\n\nPython package 'PySide2' is required to run in Graphic User Interface." \
          "\nTry again after installing 'PySide2' with" \
          "\n\npip install pyside2" \
          "\n\nOr your system may have a different way to install it."
    raise ModuleNotFoundError(msg)
