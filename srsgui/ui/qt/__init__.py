"""
``srsgui.ui.qt`` subpackage enables SRSGUI to use either PyQt5 or Pyside2 as Qt binder for Python.
It checks if PyQt5 is installed first. If not found, it checks for PySide2 installation.
If you use PyQt5, the whole SRSGUI package is subjected to be used under the GPL3 license, which PyQt5 requires.
When you use PySide2, , which is provided under the LGPL license, you can use SRSGUI under its intended MIT license.
"""

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
