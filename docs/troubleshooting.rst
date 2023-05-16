Troubleshooting
=================

General
--------

TaskMain.__init__() takes 1 positional argument but 2 were given.
```````````````````````````````````````````````````````````````````

    It is a bug with Pyside6 V6.5.0. It is supposed to be fixed with the next Pyside6 release.
    Meanwhile, you have to downgrade Pyside6 to V.6.4.3.
    
.. code-block::

    python -m pip uninstall pyside6
    python -m pip install pyside6==6.4.3
    
    