Troubleshooting
=================

General
--------

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


    