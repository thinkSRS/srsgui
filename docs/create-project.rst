
.. _top-of-creating-project:

Creating a project
===================

Here is how to create an ``srsgui`` project as shown in the examples
directory.

    - Create file structure for a project.
    - Make a list of instrument classes and Python scripts in a .taskconfig file.
    - Define instrument drivers based on the :class:`Instrument<srsgui.inst.instrument.Instrument>` class
    - Write Python scripts based on the :class:`Task<srsgui.task.task.Task>` class.
    - Open the configuration file in the ``srsgui`` application
    - Connect instruments from the Instruments menu (if connections are not defined
      in the .taskconfig file).
    - Select a task from the Task menu and run it.


Creating file structure for a project
------------------------------------------

Each ``srsgui`` project makes a use of the predefined directory structure.

.. code-block::

    /Project root directory
        /instruments
        /tasks
        project.taskconfig

A project directory has a .taskconfig configuration file and multiple Python
modules in two special subdirectories: ``instruments`` and ``tasks``.
Whenever .taskconfig file is loaded in the SRSGUI application,
Python modules in those directories will be forced to reload.

Typically, a Python interpreter loads a module when it is imported for the first time,
and does not check again if the module has been modified. When you make changes to a module, save it,
and run a script using it, you would not see the changes because the Python interpreter
would not use the modified module, as long as the previous copy of the module is in memory.
The Python interpreter needs to restart for the changed modules to take effect.

When you open (or re-open) a .taskconfig file from the ``srsgui`` application,
it reloads all the Python modules in the 2 subdirectories.
Instead of restarting the ``srsgui`` application every time a module is changed,
you can reopen the .taskconfig file to see the changes from modified modules.
If you modify a Python module other than those in the 2 directories
with respect to the current .taskconfig file, you have to restart the ``srsgui`` application
to use the modified module.

Python does not allow use of spaces in its package and module names.
Use underscores if you need spaces between words.


Populating the .taskconfig file
-----------------------------------

Each ``srsgui`` project has a \.taskconfig file. The configuration file
contains:

    - name of the project
    - a list of instruments to use
    - a list tasks to run


The following is the configuration file in the examples directory
of ``srsgui`` package (comment lines have been removed).

.. code-block::

    name: Srsgui Example - Oscilloscope and Clock Generator

    inst: cg,  instruments.cg635,   CG635
    inst: osc, instruments.sds1202, SDS1202

    task: *IDN test,    tasks.first,  FirstTask
    task: Plot example, tasks.second, SecondTask
    ...


The keyword `name:` is used as

    - The title of the SRSGUI application main window (see the top of
      this :ref:`screen capture <top-of-screen-capture-1>`).
    - The ddirectory name for the project data, which is saved under ~/home/task-results

You can specify a list of instrument classes to be included in the project using the `inst:` keyword.
The first column after the keyword is the name of the instrument used across the project:

    - Menu items under **Instruments** menu. Selecting an instrument from this menu is
      allows you to connect and disconnect the selected instrument.
    - Tab labels in the Instrument Info panel (in the top left corner under the red STOP button
      in this :ref:`screen capture <top-of-screen-capture-1>`).
    - Name used in the Terminal to specify an instrument (at the bottom right corner in this
      :ref:`screen capture <top-of-screen-capture-1>`). 
      Keep names short if you plan to interact with instruments frequently via the Terminal.
    - Argument in :meth:`get_instrument() <srsgui.task.task.Task.get_instrument>` method in
      :class:`Task<srsgui.task.task.Task>` class.

The second column is the path to the module that contains the instrument class.
The path can be relative to the .taskconfig file if it is a local module,

.. code-block::

    inst: cg,  instruments.cg635,   CG635

or a path from the Python site_package directory.

.. code-block::

    inst: lia, srsinst.sr860,  SR860

The third column is the name of the class defined in the module.

.. _fixed_connection_parameters:

You can add the optional fourth column if an instrument is used with a fixed connection parameters.
This automatically establishes the connection to the instrument when the .taskconfig is loaded.

.. code-block::

    inst: cg2,  instruments.cg635,   CG635,   serial:COM4:9600
    inst: osc2, instruments.sds1202, SDS1202, tcpip:192.168.1.100:5035




The first instrument that appears in the configuration file is the default instrument.
When a command is entered from the terminal of the srsgui application, without instrument prefix,
it will be sent to the default instrument.


The keyword 'task:' is used to specify a task class to be used in the configuration file.
The columns that follow the `task` keyword are (in order)

  1. The name of the task,
  2. The path to the module, the third one is 
  3. The name of the task class.

When you open a .taskconfig file, in ``srsgui`` application, the names of the tasks
appear as menu items under the Task menu, as shown at the top of
this :ref:`screen capture <top-of-screen-capture-1>`.

You can select one of the task items and run the task.


.. _PyVisa: https://pyvisa.readthedocs.io/en/latest/
.. _srsinst.sr860: https://pypi.org/project/srsinst.sr860/
.. _VXI11: https://www.lxistandard.org/About/VXI-11-and-LXI.aspx
.. _GPIB: https://en.wikipedia.org/wiki/IEEE-488
.. _USB-TMC: https://www.testandmeasurementtips.com/remote-communication-with-usbtmc-faq/
.. _thread: https://realpython.com/intro-to-python-threading/
.. _QThread: https://doc.qt.io/qt-6/qthread.html
