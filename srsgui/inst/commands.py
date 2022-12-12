
"""
Module to wrap remote command communication with an instrument in
`Python descriptors <https://docs.python.org/3/howto/descriptor.html>`_.
"""

from .exceptions import InstCommunicationError, InstSetError, InstQueryError


class Command(object):
    """
    Descriptor for a remote command to
    **set** and **query** a **string** value
    """
    _get_command_format = '{}?'
    _set_command_format = '{} {}'

    def __init__(self, remote_command_name):
        """
        Initialize a command with a remote command name

        :param str remote_command_name:
        """
        self.remote_command = remote_command_name
        self._get_convert_function = None
        self._set_convert_function = None
        self._value = ''

    def __get__(self, instance, instance_type):
        if instance is None:
            return self

        query_string = self._get_command_format.format(self.remote_command)
        reply = None
        try:
            reply = instance.comm.query_text(query_string)
            if callable(self._get_convert_function):
                self._value = self._get_convert_function(reply)

            else:
                self._value = reply
        except InstCommunicationError:
            raise InstQueryError('Error during querying: CMD: {}'.format(query_string))
        except ValueError:
            raise InstQueryError('Error during conversion CMD: {} Reply: {}'
                                 .format(query_string, reply))
        return self._value

    def __set__(self, instance, value):
        if instance is None:
            return

        try:
            set_string = self.remote_command
            if callable(self._set_convert_function):
                converted_value = self._set_convert_function(value)
            else:
                converted_value = value
            set_string = self._set_command_format.format(self.remote_command, converted_value)
            instance.comm.send(set_string)

        except InstCommunicationError:
            raise InstSetError('Error during setting: CMD:{} '.format(set_string))
        except ValueError:
            raise InstSetError('Error during conversion: CMD: {}'
                               .format(set_string))


class GetCommand(Command):
    """
    Descriptor for  a remote command only to **query** a **string** value.
    To **set** a value is not allowed.
    """
    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class SetCommand(Command):
    """
    Descriptor for  a remote command only to **set** a **string** value.
    To **query** a value is not allowed.
    """
    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))


class BoolCommand(Command):
    """
    Descriptor for a remote command to
    **set** and **query** a **bool** value
    """

    def __init__(self, remote_command_name):
        super().__init__(remote_command_name)
        self._get_convert_function = lambda a: int(a) != 0
        self._set_convert_function = lambda a: '1' if a else '0'


class BoolGetCommand(BoolCommand):
    """
    Descriptor for  a remote command only to **query** a **bool** value.
    To **set** a value is not allowed.
    """

    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class BoolSetCommand(BoolCommand):
    """
    Descriptor for  a remote command only to **set** a **bool** value.
    To **query** a value is not allowed.
    """

    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))


class IntCommand(Command):
    """
    Descriptor for a remote command to
    **set** and **query** an **integer** value
    """

    def __init__(self, remote_command_name):
        super().__init__(remote_command_name)
        self._get_convert_function = int


class IntGetCommand(IntCommand):
    """
    Descriptor for  a remote command only to **query** an **integer** value.
    To **set** a value is not allowed.
    """

    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class IntSetCommand(IntCommand):
    """
    Descriptor for  a remote command only to **set** an **integer** value.
    To **query** a value is not allowed.
    """

    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))


class FloatCommand(Command):
    """
    Descriptor for a remote command to
    **set** and **query** a **float** value
    """

    def __init__(self, remote_command_name):
        super().__init__(remote_command_name)
        self._get_convert_function = float


class FloatGetCommand(FloatCommand):
    """
    Descriptor for  a remote command only to **query** a **float** value.
    To **set** a value is not allowed.
    """

    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class FloatSetCommand(FloatCommand):
    """
    Descriptor for  a remote command only to **set** a **float** value.
    To **query** a value is not allowed.
    """

    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))

