
import threading

TERM_CHAR = b'\r'   # Termination character for RGA


class Interface(object):
    """
    Base class for communication interfaces to be used in Instrument class.
    A subclass should implement all the methods in the class
    """

    connection_parameters = {}
    """Define parameters to be used in GUI setting """

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

    @staticmethod
    def parse_parameter_string(param_string):
        """
        Parse a connection parameter string used in .taskconfig file
        """
        raise NotImplementedError

    def get_parameter_string_from_connection_parameters(self):
        """
        convert connection_parameter dictionary to parameter sting
        """
        raise NotImplementedError

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
        with self.get_lock():
            self._send(cmd)
            if self._send_callback:
                self._send_callback('Sent cmd: {}'.format(cmd))

    def recv(self):
        """
        Receive a byte array until a termination character and convert to a string

        :return: reply string converted from a byte array
        :rtype: str
        """

        with self.get_lock():
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
