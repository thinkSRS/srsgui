Troubleshooting
=================

General
--------
'PySide6.QtGui.QAction' object has no attribute 'menu'.
`````````````````````````````````````````````````````````

    It happens with PySide6 V.6.2.4. or earlier.
    It is fixed with V.6.5.1 or possibly before.
    If 'pip' does not allow to upgrade to a newer version, upgrade 'pip' first.

.. code-block::

    # Upgrade pip, if necessary.
    python -m pip install pip --upgrade

    # Upgrade PySide6 to the latest
    python -m pip install pyside6 --upgrade


TaskMain.__init__() takes 1 positional argument but 2 were given.
```````````````````````````````````````````````````````````````````

    It is a bug with PySide6 V.6.5.0. It is supposed to be fixed with the next Pyside6 release.
    Meanwhile, you have to downgrade PySide6 to V.6.4.3.

    It is fixed with PySide6 V.6.5.1.

.. code-block::

    # To downgrade to V. 6.4.3
    python -m pip uninstall pyside6
    python -m pip install pyside6==6.4.3

    # To upgrade to the latest version
    python -m pip install pyside6 --upgrade


    