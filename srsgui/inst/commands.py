
"""
Module to wrap remote commands used in communication with an instrument
in `Python descriptors <https://docs.python.org/3/howto/descriptor.html>`_.

If an instrument has a remote command 'FREQ' for  setting and querying a value,
you will use the command from a terminal,

.. code-block::

    > FREQ?
    1000.0
    ? FREQ 500
    > FREQ?
    500.0

The instrument is defined as an instance of an Instrument subclass, fg,
you can use it from a Python interpreter prompt.

    >>> fg.query_float('FREQ?')
    1000.0
    >>> fg.send('FREQ 500')
    >>> fg.query_float('FREQ?')
    500.0

You can define a FloatCommand for the remote command in an Instrument subclass.

    frequency = FloatCommand('FREQ')

Now, you can use the command like an class attribute as following:

    >>> fg.frequency
    1000.0
    >>> fg.frequency = 500
    >>> fg.frequency
    500.0


Using Command class simplifies tedious usage of a many set and query remote commands

"""

from .exceptions import InstCommunicationError, InstSetError, InstQueryError


class Command(object):
    """
    Descriptor for a remote command to
    **set** and **query** a **string** value
    """
    _get_command_format = '{}?'
    _set_command_format = '{} {}'

    _set_enable = True
    _get_enable = True

    def __init__(self, remote_command_name, default_value=None):
        """
        Initialize a command with a remote command name

        :param str remote_command_name:
        """
        self.remote_command = remote_command_name
        self._get_convert_function = None
        self._set_convert_function = None

        self._value = ''
        self.default_value = default_value
        if default_value:
            self._value = default_value
        self.fmt = '{}'  # format for string conversion

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
    _set_enable = False

    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class SetCommand(Command):
    """
    Descriptor for  a remote command only to **set** a **string** value.
    To **query** a value is not allowed.
    """
    _get_enable = False

    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))


class BoolCommand(Command):
    """
    Descriptor for a remote command to
    **set** and **query** a **bool** value
    """

    def __init__(self, remote_command_name, default_value=None):
        super().__init__(remote_command_name, default_value)
        self._get_convert_function = lambda a: int(a) != 0
        self._set_convert_function = lambda a: '1' if a else '0'


class BoolGetCommand(BoolCommand):
    """
    Descriptor for  a remote command only to **query** a **bool** value.
    To **set** a value is not allowed.
    """
    _set_enable = False

    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class BoolSetCommand(BoolCommand):
    """
    Descriptor for  a remote command only to **set** a **bool** value.
    To **query** a value is not allowed.
    """
    _get_enable = False

    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))


class IntCommand(Command):
    """
    Descriptor for a remote command to
    **set** and **query** an **integer** value
    """

    def __init__(self, remote_command_name, unit='', min=0, max=65535, step=1, default_value=None):
        super().__init__(remote_command_name, default_value)
        self._get_convert_function = int

        self.unit = unit
        self.maximum = max
        self.minimum = min
        self.step = step


class IntGetCommand(IntCommand):
    """
    Descriptor for  a remote command only to **query** an **integer** value.
    To **set** a value is not allowed.
    """
    _set_enable = False

    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class IntSetCommand(IntCommand):
    """
    Descriptor for  a remote command only to **set** an **integer** value.
    To **query** a value is not allowed.
    """
    _get_enable = False

    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))


class FloatCommand(Command):
    """
    Descriptor for a remote command to
    **set** and **query** a **float** value
    """

    def __init__(self, remote_command_name, unit='', min=-1000.0, max=1000.0, step=1.0, fmt='{}', default_value=None):
        super().__init__(remote_command_name, default_value)
        self._get_convert_function = float

        self.unit = unit
        self.maximum = max
        self.minimum = min
        self.step = step
        self.fmt = fmt
        self.default_value = default_value


class FloatGetCommand(FloatCommand):
    """
    Descriptor for  a remote command only to **query** a **float** value.
    To **set** a value is not allowed.
    """
    _set_enable = False

    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))


class FloatSetCommand(FloatCommand):
    """
    Descriptor for  a remote command only to **set** a **float** value.
    To **query** a value is not allowed.
    """
    _get_enable = False

    def __get__(self, instance, instance_type):
        raise AttributeError('No query command for {}'
                             .format(self.remote_command))


class DictCommand(Command):
    """
    Descriptor for a remote command to
    **set** and **query** using a conversion dictionary
    """

    def __init__(self, remote_command_name, set_dict, get_dict=None, unit='', fmt='{}', default_value=None):
        super().__init__(remote_command_name, default_value)
        self.set_dict = set_dict
        if get_dict is None:
            self.get_dict = set_dict
        else:
            self.get_dict = get_dict
        self.key_type = type(list(set_dict.keys())[0])
        self.value_type = type(list(set_dict.values())[0])

        self._set_convert_function = self.key_to_value
        self._get_convert_function = self.value_to_key

        self.unit = unit
        self.fmt = fmt

    def key_to_value(self, key):
        if self.key_type(key) in self.set_dict:
            return self.set_dict[self.key_type(key)]
        else:
            raise KeyError('{} not in {} for {}'
                           .format(key, self.set_dict.keys(), self.remote_command))

    def value_to_key(self, value):
        index = list(self.get_dict.values()).index(self.value_type(value))
        key = list(self.get_dict.keys())[index]
        return key


class DictGetCommand(DictCommand):
    """
    Descriptor for  a remote command only to **query** a **dict** value.
    To **set** a value is not allowed.
    """
    _set_enable = False
    def __set__(self, instance, value):
        raise AttributeError('No set command for {}'
                             .format(self.remote_command))
