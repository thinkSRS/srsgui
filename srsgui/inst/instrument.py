
import time
from .communications import Interface, SerialInterface, TcpipInterface
from .component import Component
from .exceptions import InstIdError

from srsgui.task.inputs import ComPortListInput, IntegerListInput, BoolInput, \
                               Ip4Input, IntegerInput


class Instrument(Component):
    """ Base class for derived instrument classes.
    """

    # String should be in in the ID string of the instrument
    _IdString = "Not Available"

    available_interfaces = [
        [
            SerialInterface,
            {
                'port': ComPortListInput(),
                'baud_rate': IntegerListInput([9600, 115200]),
                'hardware_flow_control': BoolInput(['Off', 'On'])
            }
        ],
        [
            TcpipInterface,
            {
                'ip_address': Ip4Input('192.168.1.10'),
                'port': IntegerInput(23)
            }
        ]
    ]
    """
    Dictionary Specifies the communication interface available with an instrument.
    As default, SerialInterface and TcpipInterface is provided with the base class.
    VXI11 interface is available in srsinst.sr860 package.  
    """
    def __init__(self, interface_type=None, *args):
        """
        Initialize an instance of Instrument class

        When called with no argument, an instance is created without
        actual connection to a communication insterface.

        If you want to connect while initializing an instance,
        put the same arguments you use for open method.
        """
        super().__init__(None)
        self.comm = SerialInterface()
        self._id_string = None
        self._model_name = None
        self._serial_number = None
        self._firmware_version = None
        self.interface_dict = self.get_available_interfaces()
        Instrument.connect(self, interface_type, *args)  # make sure not to run a subclass method

    def connect(self, interface_type, *args):
        """
        Connect to an instrument over the specified communication interface

        If interface_type is 'serial',

        Parameters
        -----------
            interface_type: str
                Use **'serial'** for serial communication
            port : string
                serial port,  such as 'COM3' or '/dev/ttyUSB0'
            baud_rate : int, optional
                baud rate of the serial port, default is 114200, and SRS RGA uses 28800.
            hardware_flow_control: bool, optional
                RTS/CTS setting. The default is False, SRS RGA requires **True**.

        If interface_type is 'tcpip' without login,

        Parameters
        -----------
            interface_type: str
                Use  **'tcpip'**  for Ethernet communication
            ip_address : str
                IP address of a instrument, such as '192.168.1.100'
            port: int, optional
                TCP port number, default is 23 which is the TELNET port.

        If interface_type is 'tcpip' and login is required,

        Parameters
        -----------
            interface_type: str
                Use **'tcpip'** for Ethernet communication
            ip_address: str
                IP address of a instrument
            user_id: str
                user name for login.
            password : str
                password for login.
            port : int, optional
                TCP port number. The default is 818, which SRS RGA uses
        """
        term_char = self.get_term_char()  # To retain the term char when reopening
        if self.comm.is_connected():
            self.comm.disconnect()
            time.sleep(0.1)
        if not interface_type:
            return
        for interface, _ in self.available_interfaces:
            if interface_type == interface.NAME:
                self.comm = interface()
                self.comm.connect(*args)
                self.set_term_char(term_char)
                self.update_components()
                break

    def disconnect(self):
        """
        Disconnect from the instrument
        """
        if self.comm.is_connected():
            self.comm.disconnect()
        self._id_string = None
        self._model_name = None
        self._serial_number = None
        self._firmware_version = None

    def is_connected(self):
        """
        Check if the communication interface is connected.

        :rtype: bool
        """
        return self.comm.is_connected()

    def set_term_char(self, ch):
        """
        Set the termination character for the communication interface

        :param bytes ch: termination character
        """

        self.comm.set_term_char(ch)

    def get_term_char(self):
        """
        Get the current termination character

        :return: termination character for the communication interface
        :rtype: bytes
        """
        return self.comm.get_term_char()

    def send(self, cmd):
        """
        Send a remote command without a reply

        :param str cmd: remote command
        """
        self.comm.send(cmd)

    def query_text(self, cmd):
        """
        Send a remote command with a string reply, and return the reply as a string.

        :param str cmd: remote command
        :return: reply of the remote command
        :rtype: str
        """
        return self.comm.query_text(cmd)

    def query_int(self, cmd):
        """
        Send a remote command with a integer reply, and return the reply as a integer.

        :param str cmd: remote command
        :return: reply of the remote command
        :rtype: int
        """
        return self.comm.query_int(cmd)

    def query_float(self, cmd):
        """
        Send a remote command with a float reply, and return the reply as a float.

        :param str cmd: remote command
        :return: reply of the remote command
        :rtype: float
        """
        return self.comm.query_float(cmd)

    def check_id(self):
        """
        Check if the ID string of the instrument contains _IdString of the Insteument class
        A derived instrument class should make sure that check_id method is properly implemented.

        :return: tuple of (model name, serial number, firmware version)
        """

        if not self.is_connected():
            return None, None, None

        reply = self.query_text('*IDN?').strip()
        strings = reply.split(',')

        if len(strings) != 4:
            return None, None, None

        model_name = strings[1].strip()
        serial_number = strings[2].strip()
        firmware_version = strings[3].strip()

        if self._IdString not in reply:
            raise InstIdError("Invalid instrument: {} not in {}"
                              .format(self._IdString, reply))
        self._id_string = reply
        self._model_name = model_name
        self._serial_number = serial_number
        self._firmware_version = firmware_version
        return self._model_name, self._serial_number, self._firmware_version

    def get_available_interfaces(self):
        """
        Get available communication interfaces for the instrument

        :rtype: dict
        """
        d = {}
        for interface in self.available_interfaces:
            d[interface[0].NAME] = interface
        return d

    def get_info(self):
        """
        Get the instrument information

        default return value is a dictionalry containing model name, serial number,
        firmware version. A subclass can add more informaton into the dictionary
        as needed.

        :rtype: dict
        """
        d = self.comm.get_info()
        if type(d) is dict:
            d['model_name'] = self._model_name
            d['serial_number'] = self._serial_number
            d['firmware_version'] = self._firmware_version
        return d

    def get_status(self):
        """
        Get instrument status

        Returns a string with stauts and error infomation.
        This method will be called by the owner of the instrument
        to display status info to its output interface.

        :rtype: str
        """
        return 'Not implemented: Override it to returns a status string'

    def handle_command(self, cmd):
        """
        It sends a remote command and returns the reply, if the remote command returns a reply.
        if the remote command has no replay, it return a empty string.
        A terminal program will always get a reply for any remote command,
        unless unexpected timeout error  occurs

        :param str cmd: remote command
        """

        reply = ''
        if '?' in cmd:
            reply = self.query_text(cmd).strip()
        else:
            self.send(cmd)
        return reply

    def reset(self):
        """
        Reset the instrument.
        """
        raise NotImplementedError()

    def connect_with_parameter_string(self, parameter_string):
        """
        Connect the instrument using colon-separated parameter string from a config file
        """

        params = parameter_string.split(':', 1)
        if len(params) < 2:
            raise ValueError('Not enough parameters in "{}"'.format(parameter_string))
        interface_type = params[0].strip().lower()
        if interface_type in self.interface_dict:
            parameters = self.interface_dict[interface_type].parse_parameter_string(parameter_string)

            self.connect(*parameters)
        else:
            raise KeyError('Interface type {} not available for {}'
                           .format(interface_type, self.get_name()))
        return True

