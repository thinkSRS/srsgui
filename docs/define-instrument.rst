
Defining an instrument class
------------------------------

An instrument class is a subclass derived from the
:class:`Instrument<srsgui.inst.instrument.Instrument>` class.
The **_IdString** must be defined. 
(This is used to check if a connected
instrument is of the proper type to be used with the subclass).

.. code-block::

    from srsgui import Instrument
    class CG635(Instrument):
        _IdString = 'CG635'
        _term_char = b'\r'  # Add this line if the carriage return is the termination character
                            # of the instrument, instead of the line feed (ASCII: 0x10, b'\n').


If the instrument has:
    1. the **\*IDN?** remote command, and
    2. either RS232 serial communication or Ethernet TCPIP communication port available,

the instrument can be connected and used in task scripts and in the terminal,
with 4 lines of definition, as shown above. If it does not have a \*IDN? remote command,
the :meth:`check_id()<srsgui.inst.instrument.Instrument.check_id>` method in :class:`Instrument<srsgui.inst.instrument.Instrument>`
class needs to be reimplemented.

Available_interfaces
^^^^^^^^^^^^^^^^^^^^^

`available_interfaces` defines what communication interfaces are available for the instrument.
The base :class:`Instrument<srsgui.inst.instrument.Instrument>` class has the following
definition for serial and TCP/IP communication interfaces:

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

If your instrument needs interfaces other than serial and TCP/IP, 
``srsgui`` allows additional communication classes derived from the
:class:`Interface <srsgui.inst.communication.interface.Interface>` class.
Currently there are two external communication interfaces available from the
`srsinst.sr860`_ package: ``Vxi11Interface`` and ``VisaInterface``,
which covers for VXI11_, GPIB_ and USB-TMC_. You can import the interface modules
from `srsinst.sr860`_ .

`available_interfaces` in the SR860 class is defined as following:

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

Defining `available_interfaces` is all you need to do to get a customized
dialog box opened for the instrument in ``srsgui`` application.

.. figure:: ./_static/connect-dialog-box-capture.png
    :align: center
    :figclass: align-center

For ``VisaInterface``, you have to get PyVISA_ working before running ``srsgui`` application.
This involves installation of the PyVISA package and its backend library.
Refer to PyVISA_ documentation for installation details.

Interacting with an instrument
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once an ``Instrument`` class is defined, you can connect to and communicate with the instrument 
via keyboard by launching a Python interpreter from your command prompt:

.. code-block::

    C:\srsgui>python
    Python 3.8.3 (tags/v3.8.3:6f8c832, May 13 2020, 22:37:02) [MSC v.1924 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    >>> from srsinst.sr860 import SR860
    >>> from srsgui import SerialInterface
    >>> SerialInterface.find()
    ['COM3', 'COM4', 'COM256']
    >>> lia = SR860('serial','COM4',115200, False)
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

Furthermore, by adding the instrument to a .taskconfig file 
and opening the .taskconfig file in the ``srsgui`` application, 
you can use the built-in terminal to interact with multiple instruments at once, 
and use high level ``Instrument`` class attributes and methods.

Below is an image of the ``srsgui`` application captured with the example project opened.
As you can see, you can interact with the clock generator and oscilloscope in many ways.
You can see two examples of  commands sent to the oscilloscope ``osc``: 
``\*idn?``, and ``sara?``
as well as two commands sent to the the clock generator ``cg``
``\*idn?``, and ``freq(?)``.

.. figure:: ./_static/terminal-with-example.png
    :align: center
    :figclass: align-center

|


Component, Commands, and IndexCommands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`Instrument <srsgui.inst.instrument.Instrument>` class uses
:class:`Component <srsgui.inst.component.Component>` class,
:mod:`Command <srsgui.inst.commands>` classes and
:mod:`IndexCommand <srsgui.inst.indexcommands>` classes
to organize the functionality of an instrument.

If you have to deal with hundreds of remote commands to use an instrument remotely,
organizing them in a manageable way is crucial. `Srsinst.sr860`_ package shows how these
convenience classes are used to organize a large set of remote commands.


.. _PyVisa: https://pyvisa.readthedocs.io/en/latest/
.. _srsinst.sr860: https://pypi.org/project/srsinst.sr860/
.. _VXI11: https://www.lxistandard.org/About/VXI-11-and-LXI.aspx
.. _GPIB: https://en.wikipedia.org/wiki/IEEE-488
.. _USB-TMC: https://www.testandmeasurementtips.com/remote-communication-with-usbtmc-faq/
.. _thread: https://realpython.com/intro-to-python-threading/
.. _QThread: https://doc.qt.io/qt-6/qthread.html
