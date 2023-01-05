
from srsgui.inst.exceptions import InstCommunicationError
from .interface import Interface

try:
    import pyvisa
    VISA_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    VISA_AVAILABLE = False


class VisaInterface(Interface):
    """Interface to use VISA"""

    NAME = 'visa'

    if VISA_AVAILABLE:
        rm = pyvisa.ResourceManager()
    else:
        rm = None

    def __init__(self):
        super(VisaInterface, self).__init__()
        self.type = VisaInterface.NAME
        self._visa = None
        self._resource_name = None
        self._is_connected = False

        if not VISA_AVAILABLE:
            raise ImportError("PyVisa is not installed. Install PyVisa to use VISA interface")

    def connect(self, resource):
        try:
            self._visa = self.rm.open_resource(resource)
            self._resource_name = resource
        except Exception as e:
            raise InstCommunicationError('Failed to connect {}'.format(resource))
        else:
            self._is_connected = True

            if self._connect_callback:
                self._connect_callback('Connected serial port: {} Baud rate: {}'
                                       .format(self._port, self._baud_rate))

    def disconnect(self):
        self._visa.close()
        self._is_connected = False
        self._resource_name = None
        if self._disconnect_callback:
            self._disconnect_callback('Disconnected serial port: {}'.format(self._port))

    @staticmethod
    def parse_parameter_string(param_string):
        connect_parameters = []
        params = param_string.split(':', 1)
        interface_type = params[0].strip().lower()
        if interface_type != VisaInterface.NAME:
            return None
        if len(params) <= 1:
            raise ValueError('Not enough parameters in "{}"'.format(param_string))
        else:
            connect_parameters.append(interface_type)  # 'visa'
            connect_parameters.append(params[1])  # resource string
        return connect_parameters

    def _send(self, cmd):
        self._visa.write(cmd)

    def _recv(self):
        self._visa.read()

    def _read_binary(self, length=-1):
        self._visa.read_bytes(length)

    def query_text(self, cmd):
        reply = self._visa.query(cmd)
        return reply

    def clear_buffer(self):
        self._visa.clear()

    def get_info(self):
        return {'type': self.type,
                'resource_name': self._resource_name,
                }

    @classmethod
    def find(cls):
        if not cls.rm:
            return []

        raw_items = cls.rm.list_resources()
        items = []
        for item in raw_items:
            if not item.startswith('ASRL'):
                items.append(item)
        return items


