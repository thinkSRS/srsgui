
import time
import threading

import serial
import socket
import select

from .exceptions import InstCommunicationError, InstLoginFailureError


EMPTY_BYTES = b''   # When socekt.recv() returns b'', the socket is closed.
TERM_CHAR = b'\r'   # Termination character for RGA


class Interface(object):
    """
    Base class for communication interfaces to be used in Instrument class.
    A subclass should implement all the methods in the class
    """

    # Currently available interface with sub classes
    SERIAL = 'serial'
    """serial interface type constant"""

    TCPIP = 'tcpip'
    """TCPIP interface type constant"""

    def __init__(self):
        self.type = None
        self._term_char = TERM_CHAR
        self._timeout = 10  # in second
        self._is_connected = False
        self._cmd_in_waiting = None  # query command waiting for reply
        self._endian = 'little'
        self._lock = threading.Lock()  # Any comm activity should acquire and release this lock to be thread-safe
        self.set_callbacks()

    def set_callbacks(self, queried=None, sent=None, recvd=None, connected=None, disconnected=None):
        """
        Set callback functions for query_text, send, recv, connect, disconnect operation of the interface.

        ``print`` and ``logging.debug`` is simple callback functions to use.

        :param function(msg:str) queried: function called after query_text()
        :param function(msg:str) sent: function called after send()
        :param function(msg:str) recvd: function called after recv()
        :param function(msg:str) connected: function called after connect()
        :param function(msg(str) disconnected: function called after disconnect()
        """
        if callable(queried):
            self._query_callback = queried
        else:
            self._query_callback = None

        if callable(sent):
            self._send_callback = sent
        else:
            self._send_callback = None

        if callable(recvd):
            self._recv_callback = recvd
        else:
            self._recv_callback = None

        if callable(connected):
            self._connect_callback = connected
        else:
            self._connect_callback = None

        if callable(disconnected):
            self._disconnect_callback = disconnected
        else:
            self._disconnect_callback = None

    def get_lock(self):
        """
        Get the lock to secure exclusive access to the communication interface
        """
        return self._lock

    def connect(self, *args, **kwargs):
        """
        connect to the communication interface

        Subclass will have its own connect arguments
        """
        raise NotImplementedError

    def disconnect(self):
        """
        Disconnect from the communication interface
        """
        raise NotImplementedError

    def reconnect(self):
        """
        Disconnect and connect again when communication interface is not responding
        """
        raise NotImplementedError

    def is_connected(self):
        """
        check if the communication interface is connected

        :rtype: bool
        """
        return self._is_connected

    def set_term_char(self, ch):
        """
        Set termination character for text-based communication

        Some instruments use the line-feed character, b'\\ n'
        as termination character for the remote commands and the replies,
        or others use the carriage return character, b'\\ r'.

        :param bytes ch: termination character
        """

        if type(ch) is not bytes and type(ch) is not bytearray:
            raise TypeError('term_char is not bytes')
        self._term_char = ch

    def get_term_char(self):
        """
        Get termination character for text-based communication

        :rtype: bytes
        """
        return self._term_char

    def _send(self, cmd):
        """
        Send a command over an interface without the lock.
        It should be implemented in subclasses.
        This is a protected method that a user should not call directly, because it is not thread-safe.
        Use send instead.

        :param cmd: a string of command that will be internally converted to bytes
        :return: None
        """
        raise NotImplementedError

    def _recv(self):
        """
        Receive a reply up to the termination character over an interface without the lock.
        It should be implemented in subclasses.
        This is a protected method that a user should not call directly,
        because it is not thread-safe.  Use recv instead.

        :return: bytes. It should be converted to string explicitly
        """
        raise NotImplementedError

    def _read_binary(self, length=4):
        """
        read data available now up to max_length bytes, regardless of termination character
        """
        raise NotImplementedError

    def _read_long(self):
        """
        Read 4 bytes from the communication interface and convert it to signed long

        :rtype: signed long
        """
        data = self._read_binary(4)
        value = int.from_bytes(data, self._endian, signed=True)
        return value

    def send(self, cmd):
        """
        Send a remote command to the instrument

        If the cmd does not have the termination character,
        it will attach one at the end of the cmd string,
        and convert the string to a byte array before sending

        :param str cmd: remote command to send
        """
        with self._lock:
            self._send(cmd)
            if self._send_callback:
                self._send_callback('Sent cmd: {}'.format(cmd))

    def recv(self):
        """
        Receive a byte array until a termination character and convert to a string

        :return: reply string converted from a byte array
        :rtype: str
        """

        with self._lock:
            reply = self._recv()
            if self._recv_callback:
                self._recv_callback('Received reply: {}'.format(reply))
            return reply

    def query_text(self, cmd):
        """
        Send a remote command and receive a reply with the lock acquired

        :param str cmd: remote command
        :rtype: str
        """
        raise NotImplementedError

    def query_int(self, cmd):
        """
        Query for an integer-returning remote command

        :param str cmd: remote command
        :rtype: int
        """
        return int(self.query_text(cmd))

    def query_float(self, cmd):
        """
        Query for a float-returning remote command

        :param str cmd: remote command
        :rtype: float
        """

        return float(self.query_text(cmd))

    def set_timeout(self, seconds):
        """
        Set timeout for send and recv operation of the communication interface

        :param float seconds: timeout value
        """
        raise NotImplementedError

    def get_timeout(self):
        """
        Get timeout value for send and recv operation of the communication interface

        :rtype: float
        """
        raise NotImplementedError

    def query_text_with_long_timeout(self, cmd, timeout=30.0):
        """
        Query a command returning a delayed reply

        Parameters
        -----------
            cmd: str
                remote command, such as CL, DG
            timeout: int
                timeout value to use for the remote command
        Returns
        ---------
            int
                Error status byte
        """
        old_timeout = self.get_timeout()
        self.set_timeout(timeout)
        reply = self.query_text(cmd)
        self.set_timeout(old_timeout)
        return reply

    def get_info(self) -> dict:
        """
        Return the interface information in a dict
        """
        return {'type': self.type}


class SerialInterface(Interface):
    """Interface to use RS232 serial communication"""

    def __init__(self):
        super(SerialInterface, self).__init__()
        self.type = Interface.SERIAL
        self._serial = None
        self._port = None
        self._baud = None
        self._hw_flow_control = False
        self._is_connected = False
        self._timeout = 3.0

        if hasattr(serial, 'PortNotOpenError'):
            self.port_not_open_error = serial.PortNotOpenError
        elif hasattr(serial, 'portNotOpenError'):
            self.port_not_open_error = serial.portNotOpenError
        else:
            self.port_not_open_error = InstCommunicationError

    def connect(self, port, baud=115200, hardware_flow_control=False):
        """
        Connect to an instrument using the serial interface

        Parameters
        -----------
            port : str
                serial port to use for serial communication,
                e.g., 'COM3 for Windows, '/dev/ttyUSB0' for Linux
            baud: integer, optional
                the default is 115200, You have to use the same baud rate
                with the connecting instrument.

            hardware_flow_control: bool, optional
                the default is False, some instrument requires
                hardware flow control to work properly

        """
        if port is None:
            self._port = None
            self._is_connected = False
            return
        try:
            self._serial = serial.Serial(port, baud, timeout=self._timeout, rtscts=hardware_flow_control)
            self.clear_buffer()
        except serial.SerialException:
            self._is_connected = False
            raise InstCommunicationError('Failed to connect the serial port: ' + port)
        else:
            self._port = port
            self._baud = baud
            self._hw_flow_control = hardware_flow_control
            self._is_connected = True

            if self._connect_callback:
                self._connect_callback('Connected serial port: {} Baud rate: {}'
                                       .format(self._port, self._baud))

    def disconnect(self):
        if self._is_connected:
            self._is_connected = False
            self._serial.close()
            if self._disconnect_callback:
                self._disconnect_callback('Disconnected serial port: {}'.format(self._port))

    def reconnect(self):
        self.disconnect()
        self.connect(self._port, self._baud)

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
        with self._lock:
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
                'baud': self._baud,
                'hardware_flow_control': self._hw_flow_control}


class TcpipInterface(Interface):
    """Interface to use Ethernet TCP/IP communication"""

    RGA_PORT = 818
    TELNET_PORT = 23

    def __init__(self):
        super(TcpipInterface, self).__init__()
        self.type = Interface.TCPIP
        try:
            # Create an AF_INET, STREAM socket (TCPIP)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except OSError as msg:
            raise InstCommunicationError(
                'Failed to create socket. Error code: {0} , Error message : {1}'
                .format(msg.errno, msg.strerror))

        self._is_connected = False
        self._ip_address = ''
        self._userid = ''
        self._password = ''
        self._tcp_port = TcpipInterface.RGA_PORT
        self._timeout = 20

    def _send(self, cmd):
        """
        Send a command over TCP/IP without the lock.
        This is a protected method that a user should not call directly,
        because it is not thread-safe. Use send instead.

        :param cmd: a string of command that will be internally converted to bytes
        :return: None
        """

        byte_cmd = bytes(cmd, 'utf-8')
        if self._term_char not in byte_cmd:
            byte_cmd += self._term_char

        try:
            self.socket.sendall(byte_cmd)
        except OSError:
            raise InstCommunicationError("Sending cmd '{}' to IP address: '{}' failed"
                                         .format(cmd, self._ip_address))

    def _recv(self):
        """
        Receive a reply over TCP/IP without the lock.
        This is a protected method that a user should not call directly,
        because it is not thread-safe.  Use recv instead.

        :return: bytes. It should be converted to string explicitly
        """

        reply = None
        try:
            # Now receive data
            ready, _, _ = select.select([self.socket], [], [], self._timeout)
            if self.socket in ready:
                reply = self.socket.recv(1024)
                if reply == EMPTY_BYTES:
                    self.disconnect()
                    raise InstCommunicationError("Connection closed with cmd: '{}' on IP: '{}' "
                                                 .format(self._cmd_in_waiting, self._ip_address))
        except TimeoutError:
            raise InstCommunicationError("Socket timeout with cmd: '{}' on IP: '{}' "
                                         .format(self._cmd_in_waiting, self._ip_address))
        except ConnectionResetError:
            self.disconnect()
            raise InstCommunicationError("Connection Reset with cmd: '{}' on IP: '{}' "
                                         .format(self._cmd_in_waiting, self._ip_address))
        except OSError:
            self.disconnect()
            raise InstCommunicationError("Connection closed with socket error with cmd: '{}' on IP: '{}' "
                                         .format(self._cmd_in_waiting, self._ip_address))

        if reply is None:
            raise InstCommunicationError("Timeout with Cmd: '{}' on IP: '{}' "
                                         .format(self._cmd_in_waiting, self._ip_address))
        return reply

    def _read_binary(self, length=4):

        try:
            data_buffer = b''
            rem = length
            while rem > 0:
                ready, _, _ = select.select([self.socket], [], [], self._timeout)
                if ready:
                    data = self.socket.recv(rem)
                else:
                    raise InstCommunicationError("Timeout with _read_binary")
                if data == EMPTY_BYTES:
                    self.disconnect()
                    raise InstCommunicationError(" Connection closed with _read_binary ")
                data_buffer += data
                rem = length - len(data_buffer)
            return data_buffer
        except TimeoutError:
            raise InstCommunicationError("Socket timeout with _read_binary")
        except ConnectionResetError:
            self.disconnect()
            raise InstCommunicationError("Connection Reset with _read_binary")
        except OSError:
            self.disconnect()
            raise InstCommunicationError("Connection closed with OSError in _read_binary")

    def query_text(self, cmd):
        with self._lock:
            self._cmd_in_waiting = cmd
            self._send(cmd)
            reply = self._recv()
            if self._term_char not in reply:
                time.sleep(0.5)
                reply += self._recv()
            self._cmd_in_waiting = None
            decoded_reply = reply.decode(encoding='utf-8').strip()  # returns a string not bytes
            if self._query_callback:
                self._query_callback('Queried Cmd: {} Reply: {}'.format(cmd, decoded_reply))
            return decoded_reply

    def connect_without_login(self, ip_address, port=TELNET_PORT):
        """
        Connect to a instrument that does not require login
        """

        self.socket.settimeout(self._timeout)
        try:
            self.socket.settimeout(self._timeout)
            self.socket.connect((ip_address, port))
            self._is_connected = True
            self._ip_address = ip_address
            self._tcp_port = port
            if self._connect_callback:
                self._connect_callback('Connected TCPIP IP:{} port:()'
                                       .format(ip_address, port))

        except TimeoutError:
            raise InstCommunicationError('Timeout connecting to ' + str(ip_address))
        except OSError:
            raise InstCommunicationError('Failed connecting to ' + str(ip_address))

    def set_timeout(self, seconds):
        self._timeout = seconds
        self.socket.settimeout(seconds)

    def get_timeout(self):
        return self._timeout

    def connect(self, ip_address, userid, password, port=RGA_PORT):
        """
        Connect and login to an instrument

        Parameters
        -----------
            ip_address: str
                IP address of the instrument to connect, e.g., "192.168.1.100"
            userid: str
                User name to login
            password: str
                Password to login
            port: int, optional
                the default is 818, SRS RGA port.
        """

        self.socket.settimeout(self._timeout)
        try:
            self.socket.connect((ip_address, port))
            self._is_connected = True
        except TimeoutError:
            raise InstCommunicationError('Timeout connecting to ' + str(ip_address))
        except OSError:
            raise InstCommunicationError('Failed connecting to ' + str(ip_address))

        rep = 3
        i = 0
        with self._lock:
            for i in range(rep):
                self._send(' ')  # Send a blank command
                time.sleep(2.0)  # This delay is important to sync the log in prompts.
                                 # 1.0 s is not enough for VPN connection during backup.
                reply = self._recv()
                a = reply.split(b'\r')
                if reply is not None:
                    if b'Name:' in a[-1]:  # Is the last prompt 'Name:' ?
                        break
            if i == rep - 1:
                raise InstCommunicationError('No login prompt error')

            self._send(userid)
            time.sleep(0.5)
            self._recv()

            self._send(password)
            time.sleep(0.5)
            reply = self._recv()

            if b'Welcome' in reply:
                self._ip_address = ip_address
                self._tcp_port = port
                self._userid = userid
                self._password = password
                self.socket.setblocking(False)  # this is for using select instead of timeout setting
                if self._connect_callback:
                    self._connect_callback('Connected TCPIP IP: {} port: {}'
                                           .format(ip_address, port))

            else:
                self.disconnect()
                raise InstLoginFailureError('Check if user id and password are correct.')

    def disconnect(self):
        self._is_connected = False
        self.socket.close()
        if self._disconnect_callback:
            self._disconnect_callback('Disconnected TCPIP IP: {} port: {}'
                                      .format(self._ip_address, self._tcp_port))

    def reconnect(self):
        """ Close the existing socket and open a new one in case of the socket broken
        """

        self.disconnect()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(self._ip_address, self._userid, self._password)

    def clear_buffer(self):
        """
        It does not do anything for TCPIP interface
        """
        pass

    def get_info(self):
        return {'type': self.type,
                'ip_address': self._ip_address,
                'port': self._tcp_port}
