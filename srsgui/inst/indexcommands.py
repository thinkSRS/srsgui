"""
Module to wrap remote commands with an index argument in dunder methods, __setitem__ and __get_item__.

If an instrument has a remote command using an index, 'PARAM', for  setting and querying a value,
you will use the command from a terminal,

.. code-block::

    > PARAM? 1
    1000.0
    ? PARAM 1, 500
    > PARAM? 1
    500.0

The instrument is defined as an instance of an Instrument subclass, fg,
you can use it from a Python interpreter prompt.

    >>> fg.query_float('PARAM? 1')
    1000.0
    >>> fg.send('PARAM 1, 500')
    >>> fg.query_float('PARAM? 1')
    500.0

You can define a FloatIndexCommand for the remote command in an Instrument subclass.

    fit_parameter = FloatIndexCommand('PARAM', index_max=10)

Now, you can use the command like an class attribute as following:

    >>> fg.fit_parameter[1]
    1000.0
    >>> fg.fit_parameter[1] = 500
    >>> fg.fit_parameter[1]
    500.0

Using IndexCommand class simplifies tedious usage of a many set and query remote commands
with an index argument
"""

from .exceptions import InstCommunicationError, InstSetError, InstQueryError, InstIndexError
from .communications import Interface


class IndexCommand(object):
    """
    Command class for a remote command with index
    using **set** and **query** returning an **string**
    """

    def __init__(self, remote_command_name, index_max, index_min=0, index_dict=None):
        """
        Initialize IndexCommand with a remote command name, maximum index, minimum index,
        along with an optional index name dict

        Parameters
        -----------
            remote_command_name: str
                Remote command name it uses
            index_max: int
                the maximum index value allowed
            index_mina: int, optional
        :param str remote_command_name:
        """
        self.index_max = index_max
        self.index_min = index_min
        self.remote_command = remote_command_name
        self.index_dict = index_dict

        self._parent = None
        self._get_convert_function = None
        self._set_convert_function = None

    def __set__(self, instance, value):
        raise InstSetError('No set for IndexCommand for {}'
                             .format(self.remote_command))

    def __getitem__(self, index):
        converted_index = self._convert_index(index)
        query_string = '{}? {}'.format(self.remote_command, converted_index)
        value = None
        try:
            reply = self._parent.comm.query_text(query_string)
            if callable(self._get_convert_function):
                value = self._get_convert_function(reply)

            else:
                value = reply
        except InstCommunicationError:
            raise InstQueryError('Error during querying: CMD: {}'.format(query_string))
        except ValueError:
            raise InstQueryError('Error during conversion CMD: {} Reply: {}'
                                 .format(query_string, reply))
        return value

    def __setitem__(self, index, value):
        converted_index = self._convert_index(index)
        set_string = '{} {}, '.format(self.remote_command, converted_index)
        try:
            if callable(self._set_convert_function):
                converted_value = self._set_convert_function(value)
            else:
                converted_value = value
            set_string = '{} {}'.format(set_string, converted_value)
            self._parent.comm.send(set_string)

        except InstCommunicationError:
            raise InstSetError('Error during setting: CMD:{} ' + set_string)
        except ValueError:
            raise InstSetError('Error during conversion: CMD: {}'
                               .format(set_string))

    def _add_parent(self, parent):
        if not (hasattr(parent, 'comm') and issubclass(type(parent.comm), Interface)):
            raise InstCommunicationError('parent is not Interface class')
        self._parent = parent

    def _convert_index(self, index):
        if type(index) == int:
            converted_index = index
        elif type(index) == str and type(self.index_dict) == dict:
            if index in self.index_dict:
                converted_index = self.index_dict[index]
            else:
                raise InstIndexError('Key {} not in IndexDict for {}'
                                     .format(index, self.remote_command))
        else:
            raise InstIndexError('Index {} should be an integer or key in index_dict for {}'
                                 .format(index, self.remote_command))
        if self.index_min > converted_index or converted_index > self.index_max:
            raise InstIndexError('Index {} is out of range from {} to {} for {}'
                                 .format(converted_index, self.index_min,
                                         self.index_max, self.remote_command))
        return converted_index


class IndexGetCommand(IndexCommand):
    """
    Command class for a remote command with index
    using only **query** returning an **string**, without **set**.
    """

    def __setitem__(self, instance, value):
        raise InstIndexError('No set allowed for index command {}'
                             .format(self.remote_command))


class BoolIndexCommand(IndexCommand):
    """
    Command class for a remote command with index
    using **set** and **query** returning a **bool**
    """

    def __init__(self, remote_command_name, index_max, index_min=0, index_dict=None):
        super().__init__(remote_command_name, index_max, index_min, index_dict)
        self._get_convert_function = lambda a: int(a) != 0
        self._set_convert_function = lambda a: '1' if a else '0'


class BoolIndexGetCommand(BoolIndexCommand):
    """
    Command class for a remote command with index
    using only **query** returning a **bool**, without **set**.
    """

    def __setitem__(self, instance, value):
        raise InstIndexError('No set allowed for index command {}'
                             .format(self.remote_command))


class IntIndexCommand(IndexCommand):
    """
    Command class for a remote command with index
    using **set** and **query** returning an **integer**
    """

    def __init__(self, remote_command_name, index_max, index_min=0, index_dict=None):
        super().__init__(remote_command_name, index_max, index_min, index_dict)
        self._get_convert_function = int


class IntIndexGetCommand(IntIndexCommand):
    """
    Command class for a remote command with index
    using only **query** returning an **integer**, without **set**.
    """

    def __setitem__(self, instance, value):
        raise InstIndexError('No set allowed for index command {}'
                             .format(self.remote_command))


class FloatIndexCommand(IndexCommand):
    """
    Command class for a remote command with index
    using **set** and **query** returning an **float**
    """

    def __init__(self, remote_command_name, index_max, index_min=0, index_dict=None):
        super().__init__(remote_command_name, index_max, index_min, index_dict)
        self._get_convert_function = float


class FloatIndexGetCommand(FloatIndexCommand):
    """
    Command class for a remote command with index
    using only **query** returning an **float**, without **set**.
    """

    def __setitem__(self, instance, value):
        raise InstIndexError('No set allowed for index command {}'
                             .format(self.remote_command))
