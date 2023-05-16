##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

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

The instrument is defined as an instance of an Instrument subclass, ``fg``,
you can use it from a Python interpreter prompt.

    >>> fg.query_float('PARAM? 1')
    1000.0
    >>> fg.send('PARAM 1, 500')
    >>> fg.query_float('PARAM? 1')
    500.0

You can define a FloatIndexCommand for the remote command in an Instrument subclass.

    >>> fit_parameter = FloatIndexCommand('PARAM', index_max=3)

Now, you can use the command like an class attribute as following:

    >>> fg.fit_parameter[1]
    1000.0
    >>> fg.fit_parameter[1] = 500
    >>> fg.fit_parameter[1]
    500.0

Sometimes, it is hard to remember whtat a n index means for the command.
You can assign  an index_dict to use the dictionary keys instead of the numberic index.

    >>> IndexDict = {'front': 0, 'back': 1, 'left':2, 'right':3}
    >>> fit_parameter = FloatIndexCommand('PARAM', index_max=3, index_min=0, index_dict=IndexDict)
    >>> fg.fit_parameter['back']
    500.0
    >>> fg.fit_parameter['back'] = 1000
    >>> fg.fit_parameter['back']
    1000.0

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
    _get_enable = True
    _set_enable = True

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
            index_min: int, optional
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
        reply = None
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
            if reply:
                raise InstQueryError('Error during conversion CMD: {} Reply: {}, Hex:{}'
                                     .format(query_string, reply, (*map(hex, reply.encode('ascii')),)))
            else:
                raise InstQueryError('CMD: {} returned "{}"'.format(query_string, reply))
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
                raise InstIndexError("Key '{}' not in index_dict of {}"
                                     .format(index, self.remote_command))
        else:
            raise InstIndexError('Index {} should be an integer or key in index_dict of {}'
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
    _set_enable = False
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
    _set_enable = False
    def __setitem__(self, instance, value):
        raise InstIndexError('No set allowed for index command {}'
                             .format(self.remote_command))


class IntIndexCommand(IndexCommand):
    """
    Command class for a remote command with index
    using **set** and **query** returning an **integer**
    """

    def __init__(self, remote_command_name, index_max, index_min=0, index_dict=None,
                 unit='', value_min=0, value_nax=65535, step=1):
        super().__init__(remote_command_name, index_max, index_min, index_dict)
        self._get_convert_function = int

        self.unit = unit
        self.maximum = value_nax
        self.minimum = value_min
        self.step = step


class IntIndexGetCommand(IntIndexCommand):
    """
    Command class for a remote command with index
    using only **query** returning an **integer**, without **set**.
    """
    _set_enable = False

    def __setitem__(self, instance, value):
        raise InstIndexError('No set allowed for index command {}'
                             .format(self.remote_command))


class FloatIndexCommand(IndexCommand):
    """
    Command class for a remote command with index
    using **set** and **query** returning an **float**
    """

    def __init__(self, remote_command_name, index_max, index_min=0, index_dict=None,
                 unit='', value_min=-1e6, value_max=1e6, step=1e-9, significant_figures=4, default_valaue=0.0 ):
        super().__init__(remote_command_name, index_max, index_min, index_dict)
        self._get_convert_function = float

        self.unit = unit
        self.maximum = value_max
        self.minimum = value_min
        self.step = step
        self.significant_figures = significant_figures
        self.default_valaue = default_valaue


class FloatIndexGetCommand(FloatIndexCommand):
    """
    Command class for a remote command with index
    using only **query** returning an **float**, without **set**.
    """
    _set_enable = False
    def __setitem__(self, instance, value):
        raise InstIndexError('No set allowed for index command {}'
                             .format(self.remote_command))


class DictIndexCommand(IndexCommand):
    """
    Descriptor for a remote command to
    **set** and **query** using a conversion dictionary
    """

    def __init__(self, remote_command_name, set_dict, index_max, index_min=0,
                 index_dict=None, get_dict=None, unit=''):
        super().__init__(remote_command_name, index_max, index_min, index_dict)
        self.set_dict = set_dict
        if get_dict is None:
            self.get_dict = self.set_dict
        self.key_type = type(list(set_dict.keys())[0])
        self.value_type = type(list(set_dict.values())[0])

        self._set_convert_function = self.key_to_value
        self._get_convert_function = self.value_to_key

        self.unit = unit

    def key_to_value(self, key):
        if self.key_type(key) in self.set_dict:
            return self.set_dict[self.key_type(key)]
        else:
            raise KeyError('{} not exists in {}'
                           .format(key, self.set_dict.keys()))

    def value_to_key(self, value):
        index = list(self.get_dict.values()).index(self.value_type(value))
        key = list(self.get_dict.keys())[index]
        return key
