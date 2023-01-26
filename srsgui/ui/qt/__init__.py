"""
``srsgui.ui.qt`` subpackage enables SRSGUI to use either PySide6, Pyside2 or PyQt5 as Qt binder for Python.
It checks if either Qt binder is installed in the order listed above. If any found installed, it uses the one.
If you use PyQt6 or PyQt5, the whole SRSGUI package is subjected to be used under the GPL3 license, which PyQt requires.
When you use PySide6 or PySide2, , which is provided under the LGPL license, you can use SRSGUI under its intended MIT license.
"""

from importlib import import_module

PYSIDE6 = 'PySide6'
PYSIDE2 = 'PySide2'
PYQT6 = 'PyQt6'
PYQT5 = 'PyQt5'

BINDER_LIST = [PYSIDE6, PYSIDE2, PYQT5]
QT_BINDER = None
QT_BINDER_VERSION = None

for binder in BINDER_LIST:
    try:
        qt_lib = import_module(binder)
        core = import_module('.QtCore', binder)

        QT_BINDER = binder
        if binder in [PYSIDE6, PYSIDE2]:
            QT_BINDER_VERSION = getattr(qt_lib, '__version__')
        elif binder in [PYQT6, PYQT5]:
            QT_BINDER_VERSION = getattr(core, 'PYQT_VERSION_STR')
        break
    except (ImportError, ModuleNotFoundError):
        pass

if not QT_BINDER:
    msg = "\n\nPython package 'PySide2' is required to run in Graphic User Interface." \
          "\nTry again after installing 'PySide2' with" \
          "\n\npip install pyside2" \
          "\n\nOr your system may have a different way to install it."
    raise ModuleNotFoundError(msg)
