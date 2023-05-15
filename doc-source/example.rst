
.. _top-of-example-project:

Example project
=================

When you run the ``srsgui`` application, it shows in the console window
where the Python is running from, and where ``srsgui`` is located.
If you go into the directory where ``srsgui`` resides, you can find
the 'examples' directory. When you find a  .taskconfig file in "oscilloscope example"
directory, Open the file from the menu */File/Open Config* of ``srsgui`` application.
If you plan to modify files in the project, you better copy the whole example directory
to where you usually keep your documents for programing. And open the .taskconfig file
form the copied directory, then no worries about losing the original files.

As an example project of ``srsgui``, I wanted to use ubiquitous measurement
instruments with remote communication available. I happened to have an
oscilloscope and a function generator (more specifically, a clock generator)
on my desk:

    - Siglent SDS1202XE_ digital oscilloscope (1 GSa/s, 200 MHz bandwidth),
      I bought it because of its affordable price and it works nicely!

    - Stanford Research Systems CG635_, 2 GHz Clock Generator
      (Disclaimer: I work for the company).

I built a project that controls both instruments and
capture output waveform from the clock generator with the oscilloscope,
run FFT and display the waveforms in ``srsgui`` application.

Any oscilloscope and function generator will work for this example.
If you got interested in ``srsgui``, I bet you can find an oscilloscope
and a function generator somewhere in your building.

If you could not, don't worry. Even without an any instruments, we can generate
simulated waveform to demonstrate the usability of ``srsgui`` as an organizer for
Python scripts and GUI environment for convenient data acquisition and data visualization.


Directory structure
---------------------

Let's look at the directory structure of the project.

.. code-block::

    /Oscilloscope example project directory
        /instruments
            cg635.py
            sds1202.py
        /tasks
            first.py
            second.py
            ...

        oscilloscope example project.taskconfig

This file structure follows the guideline described in
:ref:`Creating file structure for a project`.
We have two instrument driver scripts for SDS1202XE_ and CG635_
in the subdirectory called **instruments**, five task scripts
in the subdirectory called **tasks** along with a configuration file
in the project root directory.

Project configuration file
-----------------------------

The structure of a .taskconfig file is simple and
explained in :ref:`Populating the .taskconfig file`

.. code-block::
    :linenos:

    name: Srsgui example project using an oscilloscope and a clock generator

    inst: cg,  instruments.cg635,   CG635
    inst: osc, instruments.sds1202, SDS1202

    task: *IDN test,                 tasks.first,  FirstTask
    task: Plot example,              tasks.second, SecondTask
    ...

Instrument drivers
--------------------

CG635
-------

Let's take a look into the instrument/cg635.py module. Even though it seems long,
it has only 5 line if the comment lines removed. If you have a CG635,
congratulations! You can use the file as is. If you have any function
generator that can change the output frequency, you can use it instead of CG635
in the example. You change the class name and _IdString to match the instrument name,
along with _term_char, and find out the command to change frequency, referring to the manual.
And save it to a different name. Change the inst: line for 'cg'
in the .taskconfig file to match the module path and the class name.

.. code-block::
    :linenos:

    from srsgui import Instrument
    from srsgui.inst import FloatCommand

    class CG635(Instrument):
        _IdString = 'CG635'
        frequency = FloatCommand('FREQ')

Without redefining **availab_interfaces** class attribute, you can use the serial
communication only. If you want to use GPIB communication, you have to uncomment the
**available_interfaces** in CG635 class.

.. code-block::

    from srsgui import SerialInterface, FindListInput
    from srsinst.sr860 import VisaInterface

    available_interfaces = [
        [   SerialInterface,
            {
                'COM port': FindListInput(),
                'baud rate': 9600
            }
        ],
        [   VisaInterface,
            {
                'resource': FindListInput(),
            }
        ],
    ]

you have to install `srsinst.sr860`_ for VisaInterface class, and PyVISA_ and
its backend library, following PyVisa installation instruction.

Once CG635 is connected, you will see the connection information in the instrument info panel,
and you can use it in the terminal, as shown below.

.. figure:: ./_static/cg-terminal-screen-capture.png
    :align: center
    :figclass: align-center

|

To fix the 'Not implemented' warning,
:meth:`Instrument.get_status() <srsgui.inst.instrument.Instrument.get_status>`
need to be redefined. To feel better, we can override it  as a CG635 method as following:

.. code-block::

    def get_status(self):
        return 'Status: OK'

We will use only one command \.frequency, or its raw remote command, 'freq' in this example.
Because 'cg' is the default instrument, the first instrument mentioned in the .taskconfig file,
you can send any raw remote command without 'cg:' prefix if you want to.
Both '\*idn?' and 'cg:\*idn?' will return the correct reply.

We use the prefix 'cg:' for raw remote command and the prefix 'cg.' for Python commands.
In the terminal all attribute and method of CG835 calss can be used with prefix 'cg.'.
Because we defined frequency as a FloatCommand, we can use 'cg.frequency' property in the
terminal and any python scripts, once get_instrument('cg') in a task class.
Because qurey_float() is the float query command defined in the Instrument class,
you can use it in the terminal.

Actually you can use all the attribute and method defined in CG635 class and its super classes.
There is cg.dir() method defined in Component class. It shows all the available
components, commands, and method. It helps us to navigate through resources
available with the class.

.. figure:: ./_static/cg-dir-terminal-screen-capture.png
    :align: center
    :figclass: align-center

|

From the terminal, you can control all the instruments, as much as you can do with task scripts.
Defining many useful methods in an instrument class provides more controls from the terminal,
while you are tweaking to find optimal operation parameters of instruments.

SDS1202
--------

Even though you may not have an SDS1202 oscilloscope that I happened
to use for this example, I bet you can find an oscilloscope somewhere
in your building. When you get a hold of one, it may have a USB connector only,
like a lot of base model oscilloscopes do.
It means you have to use USB-TMC interface. In order to do that, you need to
install PyVISA amd make it work. You need to uncomment the available_interfaces of
SDS1202 class, modify it to fit the specification of your oscilloscope, along with
changing to the correct _IdString. And you have to get waveform download working.
If you are lucky, you can find a working Python snippet from judicious web search.
If not you have to decipher the programming manual of the oscilloscope to make the waveform
download working. It may take time, It will be very rewarding for your data acquisition
skill set improvement.

Other than the binary waveform download, Communication with an oscilloscope will work OK
using text based communication for most of remote commands.

With default available_interfaces of Instrument class, TcpipInterface should be used with port 5025.

The instrument driver for SDS1202 will work with 4 lines of code, just like CG635,
before adding the method to download waveforms from the oscilloscope. Add attributes and methods
incrementally as you need to use more functions of the instrument.

.. code-block::
    :linenos:

    import numpy as np
    from srsgui import Instrument

    class SDS1202(Instrument):
        _IdString = 'SDS1202'

        def get_waveform(self, channel):
            ...

        def get_sampling_rate(self):
            ...

Once the oscilloscope is connected to the application, you can use the terminal to explore the oscilloscope.

.. figure:: ./_static/osc-dir-terminal-screen-capture.png
    :align: center
    :figclass: align-center

|

Becasue 'osc' is not the default instrument, you have to use the prefix 'osc:' with all the
raw remote commands you send to the instrument. As shown with 'osc.dir', there are many methods
avaiable with 'osc.' Even osc.get_waveform() is available from the terminal. The terminal kindly
tells me that there is a missing argument in a function call, when you use a method incorrectly.
You can see osc.get_waveform(channel) method returns two numpy array, if you run it.
Since the terminal only allow to use attributes and methods of instruments defined in the
configuration file, if you have more useful methods defined for the instrument,
you can do more in the terminal. However, you are supposed to run more sophisticated data
handling in tasks not from the terminal.

Tasks
-------

How to run a task
^^^^^^^^^^^^^^^^^^^

Start ``srsgui`` application. You can see where the .config file is opened
from the console window (:ref:`here <top-of-initial-screen-capture>`).
If you made a copy of the original example from the ``srsgui``
package directory, open it again from the correct directory.

If there is no error message in the Console window, connect the function generator
and the oscilloscope from the Instruments menu, clicking the instrument name
that you want to connect.

Select the first task (\*IDN test) from the Tasks menu or otheres in the Tasks menu
and click the green arrow in the tool bar to run the task.


The overall structure of a task is described in :ref:`Writing a task script` section.
There are 5 tasks are included in the example project. They gradually adds more features
on the top of the previous tasks. Hopefully, they show most of Task class usage.


FirstTask
-----------

The first task shows:

    - How to use module-level logger for Python logging_ in a task
    - How to use instruments defined in the configuration file
    - How to use text output to the console window

It is not much different from the :ref:`bare bone structure <top-of-bare-bone-task>`
shown in the :ref:`Writing a task script` section.

.. literalinclude:: ../srsgui/examples/oscilloscope example/tasks/first.py
    :language: Python
    :linenos:

Using **self.logger** sends the logging output to the console window, the master logging file in
~/task-results directory/mainlog-xx.txt.x, and to the task result data file located in
~/task-results/project-name-in-config-file/RNxxx directory.

With :meth:`get_instrument <srsgui.task.task.Task.get_instrument>` you can get the instrument
defined in the configuration file in a task. **Do not disconnect the instrument in the task!**
Instrument Connectivity is managed in the application level.

It show how much it simplifies remote command set and query transactions by defining frequency
attribute using :mod:`srsgui.inst.commands` module.

SecondTask
-----------

The second task shows:

    - How to define :attr:`input_parameters <srsgui.task.task.Task.input_parameters>`
      for interactive user input from the application input panel
    - How to get matploglib figure and use it to plot
    - How to send text output to result window using
      :meth:`display_result() <srsgui.task.task.Task.display_result>`
    - How to stop the main loop by checking
      :meth:`is_running() <srsgui.task.task.Task.is_running>`.

.. literalinclude:: ../srsgui/examples/oscilloscope example/tasks/second.py
    :language: Python
    :linenos:

Using matplotlib_ is straightforward. No harder than standard plots using figures and axes.
Refer to matplotlib_ documentation on how to use it.

The important differences using matplotlib in ``srsgui`` are:
    - You have to get the figure using get_figure(), not creating one  on your own.
    - You create plots during setup(), because it is slow process. During test(),
      you just update data using set_data() or similiar methods for data update.
    - You have use request_figure_update() to redraw the plot, after set_data().
      The event loop handler in the main application will update the plot at its earliest
      convenience.


.. figure:: ./_static/second-task-screen-capture.png
    :align: center
    :figclass: align-center

|

ThirdTask
-----------

The third task uses the oscilloscope only. It gets the number of captures from user input,
repeat oscilloscope waveform capture and update the waveform plot. It stops after repeats
the number of times selected berfore run, or when the Stop button is pressued.
When it runs it captures and display a waveform with 700000 points every 0.2 second
over TCPIP communcation.


.. literalinclude:: ../srsgui/examples/oscilloscope example/tasks/third.py
    :language: Python
    :linenos:

FourthTask
-----------

The fourth example is the climax of the examples series. It uses input_parameters
to change output frequency of the clock generator interactively, captures waveforms
from the oscilloscope, run FFT of the waveforms with Numpy, and plot
using 2 matplotlib figures.

by adding the names of figures that you want to use in additional_figure_names,
``srsgui`` provides more figures to the task before it starts.

.. literalinclude:: ../srsgui/examples/oscilloscope example/tasks/fourth.py
    :language: Python
    :linenos:

FifthTask
----------

the fifth examples is to show how to subclass an existing task class to reuse.
the method get_waveform() in the fourth example is reimplemented to generate
simulated waveform that runs without any real oscilloscope.

Note that the square wave edge calculation is crude, and causing modulation in pulse width
that shows side bands in FFT spectrum, if the set frequency is not commensurated with
the sampling rate. To generate clean square wave, the rising and falling edges should
have at least two points to represent exact phase. Direct transition from low to high
without any intermediate points suffers from subtle modulation in time domain,
which manifests as side bands in FFT. This is a common problem in digital signal
processing. It is not a problem in the real world, because the signal is analog,
and the sampling rate is limited by the bandwidth of the signal.


.. literalinclude:: ../srsgui/examples/oscilloscope example/tasks/fourth.py
    :language: Python
    :linenos:



.. _PyVisa: https://pyvisa.readthedocs.io/en/latest/
.. _srsinst.sr860: https://pypi.org/project/srsinst.sr860/
.. _VXI11: https://www.lxistandard.org/About/VXI-11-and-LXI.aspx
.. _GPIB: https://en.wikipedia.org/wiki/IEEE-488
.. _USB-TMC: https://www.testandmeasurementtips.com/remote-communication-with-usbtmc-faq/
.. _SDS1202XE: https://siglentna.com/product/sds1202x-e/
.. _SRS: https://thinksrs.com/
.. _CG635: https://thinksrs.com/products/cg635.html
.. _logging: https://docs.python.org/3/howto/logging.html
.. _matplotlib: https://matplotlib.org/stable/index.html