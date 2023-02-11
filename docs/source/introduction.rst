
.. _top-of-creating-project:

Creating a project
===================

Here is how to create a ``srsgui`` project as shown in the example
directory.

    - Create file structure for a project.
    - Make a list of instrument classes and Python scripts to use in a .taskconfig file.
    - Define instrument drivers based on the Instrument class
    - Write Python scripts based on the Task class.
    - Open the configuration file in the SRSGUI application
    - Connect instruments from the Instruments menu, if connections not defined
      in the configuration file.
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
modules in two special subdirectory: instruments, tasks.
Whenever open a .taskconfig file from the SRSGUI application,
Python modules in those directories are forced to reload.

Typically, a Python interpreter loads a module when it is imported for the first time,
and never check again if the module is modified. When you make changes to a module,
and import the module again with a Python interpreter, it ignores it
because it is already imported before. The Python interpreter needs to restart
to take an effect of the changed modules.

When you open a .taskconfig file again from the ``srsgui`` application menu,
it reloads all the Python modules in the 2 subdirectories.
It helps when you modify and debug a module in the subdirectories.
Instead of restart the application every time a module is changed,
you can reopen the .taskconfig file to see the changes from modified modules.
If you modify a Python module other than the ones in the 2 directories
with respect to the current .taskconfig file, you have to restart the ``srsgui`` application
to use the modified module.

Python does not allow to use spaces in its package and module names.
Use underscore if you need spaces between words.


Populating the .taskconfig file
-----------------------------------

Each ``srsgui`` project has a \.taskconfig file. The configuration file
contains:

    - name of the project,
    - a list of instruments to use
    - a list tasks to run


The following is the configuration file in the example directory
of ``srsgui`` package without comment lines.

.. code-block::

    name: srsgui example project using an oscilloscope and a clock generator

    inst: cg,  instruments.cg635,   CG635
    inst: osc, instruments.sds1202, SDS1202
    
    task: \*IDN test,    tasks.first,  FirstTask
    task: Plot example, tasks.second, SecondTask
    ...


The keyword 'name:' is use as

    - Title of the SRSGUI application main window (Look at the top of
      this :ref:`screen capture <top-of-screen-capture-1>`.
    - Directory name for the project data saving under ~/home/task-results

You can specify a list instrument classes to be included in the project using 'inst:' keyword.
The first column after the keyword is the name of the instrument used across the project:

    - Menu items under **Instruments** menu. It is used to connect and disconnect
      the selected instrument.
    - Tab labels in Instrument Info panel (int the top left corner under the red STOP button
      in this :ref:`screen capture <top-of-screen-capture-1>`.
    - Name used in terminal to specify a instrument. Make it short if you use a lot
      in the terminal at the bottom right corner in this
      :ref:`screen capture <top-of-screen-capture-1>`.

    - Argument in :meth:`get_instrument() <srsgui.task.task.Task.get_instrument>` method in
      :class:`Task<srsgui.task.task.Task>` class.

The second column is the path to the module that contains the instrument class.
The path can be relative to the .taskconfig file if it is a local module,

.. code-block::

    inst: cg,  instruments.cg635,   CG635

or absolute path from the Python site_pacakge directory.

.. code-block::

    inst: lia, srsinst.sr860.instruments.sr860,  SR860

The third column is the name of the class defined for a instrument in the module.


You can add the optional fourth column if an instrument used with a fixed connection parameters.

.. code-block::

    inst: cg2,  instruments.cg635,   CG635,   serial:COM4:9600
    inst: osc2, instruments.sds1202, SDS1202, tcpip:192.168.1.100:5035

It gets the instruments connected, while a configuration file is opening.


The first instrument that appears in the configuration file is the default instrument.
When a command is typed in without instrument prefix, it will be sent to the default instrument.


The keyword 'task:' is used to specify a task class to be used in the configuration file.
the first column after the 'task:' keyword is the name of the task,
the second is path to the module,
the third one is the name of the task class. It specifies a task class in the same way
with instrument classes.

When you open a .taskconfig file, in ``srsgui`` application, the names of the tasks
appear as menu items under the Task menu (at the top of
this :ref:`screen capture <top-of-screen-capture-1>`.

You can select one of the task items and run the task.


Defining instrument classes
------------------------------

an instrument class is a subclass derived from the
:class:`Instrument<srsgui.inst.instrument.Instrument>` class.
Minimum requirement is to have **_IdString** to check if a connected
instrument is a correct instrument  that can be used with the class.

.. code-block::

    from srsgui import Instrument
    class CG635(Instrument):
        _IdString = 'CG635'
        _term_char = b'\r'  # Add this line if the carriage return is the termination character.
                            # instead of the line feed (ASCII: 0x10, b'\n').

If the instrument has:
    1. the **\*IDN?** remote command
    2. either RS232 serial communication or Ethernet TCPIP communication port available,

the instrument can be connected and used in task scripts and in the terminal,
with 4 lines of definition like above. If it does not have the \*IDN? remote command,
:meth:`check_id()<srsgui.inst.instrument.Instrument.check_id>` method in Instrument
class needs to be reimplemented.

Available_interfaces
^^^^^^^^^^^^^^^^^^^^^

`Available_interface` defines what kind of communication is available for the instrument,
the base :class:`Instrument<srsgui.inst.instrument.Instrument>` class has the following
definition for serial and TCPIP communication interfaces:

.. code-block::

    available_interfaces = [
        [   SerialInterface,
            {
                'port': FindListInput(),
                'baud_rate': IntegerListInput([9600, 115200]),
                'hardware_flow_control': BoolInput(['Off', 'On'])
            }
        ],
        [   TcpipInterface,
            {
                'ip_address': Ip4Input('192.168.1.10'),
                'port': IntegerInput(23)
            }
        ]
    ]

If your instrument needs other than serial and TCPIP interfaces, ``srsgui`` allows to add
other communication classes derived from
:class:`Interface <srsgui.inst.communication.interface.Interface>` class.
Currently there are two external communication insterfaces are available from
`srsinst.sr860`_ package: ``Vxi11Interface`` and ``VisaInterface``,
which covers for VXI11_, GPIB_ and USB-TMC_. You can import the interface modules
from `srsinst.sr860`_ .

Available_interfaces in SSR865 class is define as following:

.. code-block::

    available_interfaces = [
        [   Vxi11Interface,
            {
                'ip_address': Ip4Input('192.168.1.10'),
            }
        ],
        [   VisaInterface,
            {
                'resource': FindListInput(),
            }
        ],
        [   TcpipInterface,
            {
                'ip_address': Ip4Input('192.168.1.10'),
                'port': 23
            }
        ],
        [   SerialInterface,
            {
                'port': FindListInput(),
                'baud_rate': IntegerListInput([9600, 19200, 38400, 115200,
                                               230400, 460800], 3)
            }
        ],
    ]

The definition of available_interfaces is all you need to do to get a customized
dialog box opened for the instrument in ``srsgui`` application.

.. figure:: ./_static/connect-dialog-box-capture.png
    :align: center
    :figclass: align-center

Of course, you have to make PyVisa_ working for ``VisaInterface``
before running ``srsgui`` application.

From Python interperter, you can connect to a instrument, and use it once it is defined.

.. code-block::

    C:\srsgui>python
    Python 3.8.3 (tags/v3.8.3:6f8c832, May 13 2020, 22:37:02) [MSC v.1924 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    >>> from srsinst.sr860 import SR865
    >>> from srsgui import SerialInte
    >>> SerialInterface.find()
    ['COM3', 'COM4', 'COM256']
    >>> lia = SR865('serial','COM4',115200, False)
    >>> lia.query_text('*idn?')
    'Stanford_Research_Systems,SR865A,002725,v1.34'
    >>> lia.disconnect()
    >>>
    >>> from srsinst.sr860 import VisaInterface
    >>> VisaInterface.find()
    ['USB0::0xB506::0x2000::002725::INSTR', 'GPIB0::4::INSTR']
    >>> lia.connect('visa', 'USB0::0xB506::0x2000::002725::INSTR')
    >>> lia.query_text('*idn?')
    'Stanford_Research_Systems,SR865A,002725,v1.34\n'
    >>>

Well, these operations are what you can do with PyVisa_ itself. Defining an instrument class,
adding it in a .taskconfig file, and opening it in ``srsgui`` application, let you
use the terminal to interact with multiple instrument at once.

Below is an image of terminal captured with the example project opened.
As you can see, you can interact with the clock generator and oscilloscope in many ways.
There are two commands for osc: \*idn?, sara? used, and two commands for cg:
\*idn?, freq(?) used in the terminal.

.. figure:: ./_static/terminal-with-example.png
    :align: center
    :figclass: align-center

|


Component, Commands and IndexCommands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`Instrument <srsgui.inst.instrument.Instrument>` class uses
:class:`Component <srsgui.inst.component.Component>` class,
:mod:`Command <srsgui.inst.commands>` classes and
:mod:`IndexCommand <srsgui.inst.indexcommands>` classes
to organize the functionality of the instrument.

If you have hundreds of remote commands to deal with an instrument,
organized them in a manageable way is crucial. Well, look into srsinst.sr860
documentation to see these convenience classes are used to organize a large set of
remote commands.


Writing a task script
-----------------------

When you write a Python script that runs with `'srsgui``, you make a subclass of
:class:`Task <srsgui.task.task.Task>` class, and implement
:meth:`setup<srsgui.task.task.Task.setup>`,
:meth:`setup<srsgui.task.task.Task.test>` and
:meth:`setup<srsgui.task.task.Task.cleanup>`.

Following is the simplest form of a task. Even though it does not do much,
``srsgui`` is happy to run the task, if it is included in a .taskconfig file.

.. _top-of-bare-bone-task:

.. code-block::

    from srsgui import Task

    class ZerothTask(Task):
        def setup(self):
            print('Setup done.')
           
        def test(self):
            print('Test finished.')
            
        def cleanup(self):
            print('Cleanup done.')

When a task runs, the setup() method runs first. if the setup finished with an exception,
the task is aborted without runing test() or cleanup(). If the setup() method completes
without exception, the test() method runs next. Regardless of exception happened while
the test() is finished, running the cleanup() method completes the task.

You write a task based on the template above any way you want, just use resources and APIs
provided in Task class for Graphic User Interface (GUI) input and output. As long as
you tasks do not misuse the limited GUI resources available from Task class,
your task will run along with ``srsgui`` application.

A task is a Python thread_ (if it is run by an application with Qt backend,
it will be QThread_.), running as concurrently with the main application.

The :class:`Task <srsgui.task.task.Task>` is designed with much consideration
on protection of the main application from crashing caused by unhandled Exception,
while a buggy task running. ``srsgui`` provides information as much as Python
interpreter does. After modifying a task, reopen the .taskconfig file will reload
the modified task before you run it again.


The main application is supposed to provide the resources a task needs,
and responds to the callbacks from the task.

    set_inst_dict,
    set_data_dict,
    set_figure_dict,
    set_session_handler,
    log handler,
    set_callback_handler.

The main application and
the running task are separate threads, and the main application responds only to
the callbacks from the task.

For text output
    callbacks.text_available
    display_device_info
    display_result
    update_datatus
    logger.info
    logger.error
    logger.warning
    print

input panel,
    callbacks.parameter_changed
    input_parameters

    get_input_parameters
    get_all_input_parameters


    set_inputparameters
    notify_parameter_changed

figure,
    callbacks.request_figure_update - draw
    callbacks.notify_data_available - update
    clear_figure
    get_figure

question,
    callbacks.new_question
    ask_question
    qustion_background_update

session_handler,
    add_details
    create_table
    add_data_to_table
    create_table_in_file
    add_to_table_in_file

inst_dict
    get_instrument


Part of your script does not interact with GUI, you can do that have done with
a typical scripts. You can reuqest http, send e-mails, make sounds,
run long computation.

Once you learn how to take advantage of the limited resources
that ``srsgui`` provides in your script you can run GUI happy scripts



.. _PyVisa: https://pyvisa.readthedocs.io/en/latest/
.. _srsinst.sr860: https://pypi.org/project/srsinst.sr860/
.. _VXI11: https://www.lxistandard.org/About/VXI-11-and-LXI.aspx
.. _GPIB: https://en.wikipedia.org/wiki/IEEE-488
.. _USB-TMC: https://www.testandmeasurementtips.com/remote-communication-with-usbtmc-faq/
.. _thread: https://realpython.com/intro-to-python-threading/
.. _QThread: https://doc.qt.io/qt-6/qthread.html
