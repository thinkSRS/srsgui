Installation
==============

Preparation
------------

To install ``srsgui``,  make sure you have Python version 3.7 or later
is available from the command line. you can check your Python version
by running:

.. code-block::

    python --version

.. note::
    Commands running from the command prompt shown here are assumed using a Windows computer system.
    If you use other systems, commands may be different. Refer to
    `this page. <install-packages_>`_

If you have a Python older than the required version,
`install a newer Python. <install-python_>`_

Using `virtual environment <virtual-environment_>`_ avoids possible dependency conflict among Python packages.
If you want to use a virtual environment, create one with
your favorite virtual environment package. If you do not have a preference,
use Python default ``venv``.

.. code-block::

    python -m venv env
    .\env\Scripts\activate

.. note::
    Commands to use ``venv`` are different among computer systems. Other than Windows, refer to
    `this page <venv_>`_.

Srsgui installation
--------------------

To run ``srsgui`` as a GUI application, install it with [full] option using pip_:

.. code-block::

    python -m pip install srsgui[full]

It will install ``srsgui`` package along with
the 3 main packages (pyserial_, matplotlib_, pyside6_) and their dependencies.

If

    - you plan only to use the instrument driver part of ``srsgui`` package without GUI support,
    - your system install matplotlib_ or pyside6_ from sources other than pip
      (Some linux systems do so),
    - you want to use pyqt5_ or pyside2_ instead of pyside6_ as GUI backend,
    - you have trouble with full installation and you want to install dependency manually,

you can install without the extra [full] option:

.. code-block::

    python -m pip install srsgui

It will install ``srsgui`` with pyserial_ only.

.. note::
    ``srsgui`` runs with either pyside6_, pyside2_, or pyqt5_ installed as GUI backend.
    If your system already have pyside2_, pyqt5_ installed, you do not have to install pyside6_

        python -m pip show pyside2
        python -m pip show pyqt5

    will show if pyside2_, or pyqt5_ is installed.

Running srsgui application
----------------------------

After ``srsgui`` is installed, you can start ``srsgui`` application from the command line

.. code-block::

    srsgui

    or

    python -m srsgui

``srsgui`` installs a executable script named "srsgui" in Python/Scripts directory.
If the directory is included in PATH environment variable, **srsgui** command will work.
Otherwise, **python -m srsgui** will work regardless of PATH setting.

.. _top-of-initial-screen-capture:

.. figure:: ./_static/initial-screen-capture.png
    :align: center
    :figclass: align-center

If you see the application is open and running, the installation is successful!

.. note::
    Instead of seeing the application running, you may get errors, probably ImportError.
    Carefully look through the exception traceback to find out which package causes the error.
    When the latest python is installed, some packages may not install properly. If the problem
    is not from ``srsgui`` directly, web search of the problem usually finds a fix.


.. _install-packages: https://packaging.python.org/en/latest/tutorials/installing-packages/
.. _install-python: https://realpython.com/installing-python/
.. _virtual-environment: https://realpython.com/python-virtual-environments-a-primer/
.. _venv: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
.. _pip: https://realpython.com/what-is-pip/
.. _pyserial: https://pyserial.readthedocs.io/en/latest/pyserial.html
.. _matplotlib: https://matplotlib.org/stable/tutorials/introductory/quick_start.html
.. _pyside6: https://wiki.qt.io/Qt_for_Python
.. _pyside2: https://pypi.org/project/PySide2/
.. _pyqt5: https://pypi.org/project/PyQt5/
.. _numpy: https://numpy.org/install/