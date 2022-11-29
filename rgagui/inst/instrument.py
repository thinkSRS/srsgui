# Base instrument class module

import time
from .communications import Interface, SerialInterface, TcpipInterface
from .component import Component
from .exceptions import InstIdError


class Instrument(Component):
    """ This is base instrument class
    """
    SERIAL = Interface.SERIAL
    TCPIP = Interface.TCPIP

    # String should be in in the *idn string of the instrument
    _IdString = "Not Available"

    def __init__(self, interface_type=Interface.SERIAL, *args):
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

        num = len(args)
        if interface_type == Instrument.TCPIP:
            self.comm = TcpipInterface()

            if num == 4 or num == 3:
                self.comm.connect(*args)
            elif num == 2 or num == 1:
                self.comm.connect_without_login(*args)
            else:
                raise TypeError("Invalid Parameters for TcpipInterface")
        elif interface_type == Instrument.SERIAL:
            if not isinstance(self.comm, SerialInterface):
                self.comm = SerialInterface()
            if 0 < num < 4:
                self.comm.connect(*args)
        else:
            raise TypeError("Unknown Interface type: {}".format(interface_type))
        self.set_term_char(term_char)
        self.update_components()

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
        Send a remote command with a string reply, and receive the reply

        :param str cmd: remote command
        :return: reply of the remote command
        :rtype: str
        """
        return self.comm.query_text(cmd)

    def query_int(self, cmd):
        """
        Send a remote command with a integer reply, and receive the reply

        :param str cmd: remote command
        :return: reply of the remote command
        :rtype: int
        """
        return self.comm.query_int(cmd)

    def query_float(self, cmd):
        """
        Send a remote command with a float reply, and receive the reply

        :param str cmd: remote command
        :return: reply of the remote command
        :rtype: float
        """
        return self.comm.query_float(cmd)

    def check_id(self):
        """
        Check if the ID string of the instrument contains _IdString of the Insteument class

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
        return 'Not implemented: it should return a status string'

    def handle_command(self, cmd):
        """
        It send a remote command and returns the reply. if the remote command has no replay,
        it return a empty string. A termianl program will always get a reply for any remote command,
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
