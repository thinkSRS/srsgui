##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

import time

from srsgui.inst.exceptions import InstCommunicationError
from .interface import Interface
from .serial_ports import serial_ports

try:
    import serial
except (ImportError, ModuleNotFoundError):
    msg = "\n\nPython module 'serial' not found." \
          "\nInstall 'pyserial' using" \
          "\n\npip install pyserial" \
          "\n"
    raise ModuleNotFoundError(msg)


class SerialInterface(Interface):
    """Interface to use RS232 serial communication"""

    NAME = 'serial'

    def __init__(self):
        super(SerialInterface, self).__init__()
        self.type = SerialInterface.NAME
        self._serial = None
        self._port = None
        self._baud_rate = None
        self._hw_flow_control = False
        self._is_connected = False
        self._timeout = 3.0

        if hasattr(serial, 'PortNotOpenError'):
            self.port_not_open_error = serial.PortNotOpenError
        elif hasattr(serial, 'portNotOpenError'):
            self.port_not_open_error = serial.portNotOpenError
        else:
            self.port_not_open_error = InstCommunicationError

    def connect(self, port, baud_rate=115200, hardware_flow_control=False):
        """
        Connect to an instrument using the serial interface

        Parameters
        -----------
            port : str
                serial port to use for serial communication,
                e.g., 'COM3 for Windows, '/dev/ttyUSB0' for Linux

            baud_rate: integer, optional
                the default is 115200, You have to use the same baud rate
                with the connecting instrument.

            hardware_flow_control: bool, optional
                the default is False, some instruments require
                RTS/CTS hardware flow control to work properly

        """
        if port is None:
            self._port = None
            self._is_connected = False
            return
        try:
            self._serial = serial.Serial(port, baud_rate, timeout=self._timeout, rtscts=hardware_flow_control)
            self.clear_buffer()
        except serial.SerialException:
            self._is_connected = False
            raise InstCommunicationError('Failed to connect the serial port: ' + port)
        else:
            self._port = port
            self._baud_rate = baud_rate
            self._hw_flow_control = hardware_flow_control
            self._is_connected = True

            if self._connect_callback:
                self._connect_callback('Connected serial port: {} Baud rate: {}'
                                       .format(self._port, self._baud_rate))

    def disconnect(self):
        if self._is_connected:
            self._is_connected = False
            self._serial.close()
            if self._disconnect_callback:
                self._disconnect_callback('Disconnected serial port: {}'.format(self._port))

    @staticmethod
    def parse_parameter_string(param_string):
        connect_parameters = []
        params = param_string.split(':')
        num = len(params)
        interface_type = params[0].strip().lower()
        if interface_type != SerialInterface.NAME:
            return None
        if num > 4:
            raise ValueError('Too many parameters in "{}"'.format(param_string))
        if num > 1:
            connect_parameters.append(interface_type)  # 'serial'
            connect_parameters.append(params[1])  # port name
        if num > 2:
            connect_parameters.append(int(params[2]))  # baud rate
        if num > 3:
            connect_parameters.append(params[3].upper == 'TRUE')  # hardware flow control
        return connect_parameters

    def send_break(self, duration=0.1):
        """
        Send break signal over serial interface
        Parameters
        -----------
            duration: float, optioanl
                to set how long the break signal will be
        """
        self._serial.send_break(duration)

    def set_timeout(self, seconds):
        self._timeout = seconds
        if self._serial:
            self._serial.timeout = seconds

    def get_timeout(self):
        return self._timeout

    def _send(self, cmd):
        """
        Send a command over serial interface without the lock.
        This is a protected method that a user should not call directly, because it is not thread-safe.
        Use send instead.

        :param cmd: a string of command that will be internally converted to bytes
        :return: None
        """

        bytecmd = bytes(cmd, 'utf-8')
        if self._term_char not in bytecmd:
            bytecmd += self._term_char
        try:
            self._serial.write(bytecmd)
        except (self.port_not_open_error, AttributeError):
            raise InstCommunicationError('Port not open to write')
        except serial.SerialException:
            raise InstCommunicationError("Sending cmd '{}' to port '{}' failed".format(cmd, self._port))

    def _write_bibary(self, binary_array):
        if type(binary_array) not in (bytes, bytearray):
            raise TypeError('_write_binary requires bytes or bytearray')
        try:
            self._serial.write(binary_array)
        except (self.port_not_open_error, AttributeError):
            raise InstCommunicationError('Port not open to write')
        except serial.SerialException:
            raise InstCommunicationError("writing binary '{}' to port '{}' failed".format(
                (*map(hex, binary_array),), self._port))

    def _recv(self):
        """
        Receive a reply over serial interface without the lock.
        This is a protected method that a user should not call directly,
        because it is not thread-safe. Use recv instead.

        :return: bytes. It should be converted to string explicitly
        """

        try:
            reply = b''
            while True:
                out = self._serial.read(1)
                reply += out
                if out == self._term_char or out == b'':
                    break
            return reply
        except (self.port_not_open_error, AttributeError):
            raise InstCommunicationError('Port not open to read')
        except serial.SerialException:
            raise InstCommunicationError('Receive failed with cmd {} on port {}'
                                         .format(self._cmd_in_waiting, self._port))

    def _read_binary(self, length=4):

        try:
            data = self._serial.read(length)
            rem = length - len(data)
            if rem > 0:
                data += self._serial.read(rem)
            return data
        except (self.port_not_open_error, AttributeError):
            raise InstCommunicationError('Port not open to read')
        except serial.SerialException:
            raise InstCommunicationError('Receive failed with cmd {} on port {}'
                                         .format(self._cmd_in_waiting, self._port))

    def query_text(self, cmd):
        with self.get_lock():
            self._cmd_in_waiting = cmd
            self._send(cmd)
            reply = self._recv()
            if reply == b'':
                raise InstCommunicationError("Cmd '{}' on port '{}' timeout".format(cmd, self._port))
            if self._term_char not in reply:
                time.sleep(0.5)
                reply += self._recv()
            self._cmd_in_waiting = None
            decoded_reply = reply.decode(encoding='utf-8').strip()  # returns a string not bytes
            if self._query_callback:
                self._query_callback('Queried Cmd: {} Reply: {}'.format(cmd, decoded_reply))
            return decoded_reply

    def clear_buffer(self):
        """
        Read out any characters left in the communication buffer.
        """
        old_timeout = self._timeout
        self.set_timeout(0.1)
        while True:
            try:
                self.query_text('')
            except InstCommunicationError:
                break
        self.set_timeout(old_timeout)

    def get_info(self):
        """
        Get information on the communcation interface.
        """
        return {'type': self.type,
                'port': self._port,
                'baud_rate': self._baud_rate,
                'hardware_flow_control': self._hw_flow_control}

    @classmethod
    def find(cls):
        """
        Find available serial ports and return a list of the ports.
        """
        return serial_ports()
