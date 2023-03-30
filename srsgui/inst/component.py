from .communications import Interface
from .commands import Command, GetCommand, BoolCommand, IntCommand, \
                      FloatCommand, DictCommand
from .indexcommands import IndexCommand, BoolIndexCommand, IntIndexCommand, \
                           FloatIndexCommand, DictIndexCommand


class Component(object):
    """
    Class is used to build hierarchical structure in an instrument.
    An instrument can have multiple components and each component
    can also have multiple subcomponents. All the components
    inside an instrument shares the communication interface
    of the instrument.

    When the communication interface of an
    instrument changed, the instrument should call
    ``update_components()`` to update all its components.

    Component has a convenience attribute, ``dir`` that returns available subcomponents,
    commands and methods available from the component. ``dir`` combines the return values from
    ``get_component_dict()``, ``get_command_dict()`` and ``get_method_list()``.

    Component has a convenience method, ``get_component_dict()`` to get child
    components of an instance. This method helps a user to navigate through
    the component tree.

    Component contains Command and its subclasses along with
    IndexCommand and its subclasses as class attributes.
    A convenience method, ``get_command_dict()`` will show what commands are
    available from the component instance. each command is listed with:
    the name of the Command instance; the raw remote command associated with
    the command; the conversion_dict if it is a DictCommand instance;
    the index_dict for IndexCommand instance, if used.

    ``get_method_list()`` shows methods a component has, including ones
    inherited from the superclasses.

    The information available from the convenience methods are
    available interactively from context-sensitive editors, such as IDLE, Pycharm, VSCode.
    When the information from the editors are not complete, consulting with
    those convenience methods provides complete lists you can use.

    """

    class DirCommand(GetCommand):
        """
        Descriptor to run get_lists() with 'dir' command
        """
        def __get__(self, instance, instance_type):
            if hasattr(instance, 'get_lists'):
                return instance.get_lists()

    dir = DirCommand('dir')
    """ class instance of DirCommand"""

    exclude_capture = []
    """exclude commands from query in capture_commands"""

    def __init__(self, parent, name='unnamed'):
        self._name = name
        self._children = []
        if parent is None:
            self._parent = None
            self.comm = None
            return

        if not hasattr(parent, '_children') or not hasattr(parent, 'comm'):
            raise AttributeError('Error: parent is NOT a subclass of Component')

        if not isinstance(parent.comm, Interface):
            raise TypeError('Invalid Interface instance')

        self._parent = parent
        self._parent._children.append(self)
        self.comm = parent.comm
        self._add_parent_to_index_commands()

    def is_connected(self):
        """
        check if the current communication interface is open
        """
        return self.comm.is_connected()

    def set_name(self, name):
        """
        Set the name of the component
        """
        self._name = name

    def get_name(self):
        """
        Get the name of the component
        """

        return self._name

    def update_components(self):
        """
        Update the communication interface of child components with the parent's
        """
        self._add_parent_to_index_commands()
        for child in self._children:
            child.comm = self.comm
            child.update_components()
            child._add_parent_to_index_commands()

    def get_lists(self, include_superclass=True):
        """
        Get the directory containing a list of subcomponents in this component,
        a list of commands available in the component,
        a list of  method available in the component and its superclass
        """
        return {
            'components': self.get_component_dict(),
            'commands': self.get_command_dict(include_superclass),
            'methods': self.get_method_list(include_superclass),
        }

    def _add_parent_to_index_commands(self):
        # Add parent to ListCommands
        commands = self.get_command_dict()
        for cmd in commands:
            instance = self.__class__.__dict__[cmd]
            if hasattr(instance, "_add_parent"):
                instance._add_parent(self)

    def get_component_dict(self):
        """
        Get a dict of the child component of the component

        Returns
        --------
            list(str)
                list contain name of child compoents and its class name
        """
        component_list = {}
        for k in self.__dict__:
            if k =='_parent':
                continue
            instance = self.__dict__[k]
            if issubclass(instance.__class__,  Component):
                component_list[k] = ('instance of {}'.format(instance.__class__.__name__))
        return component_list

    def get_command_dict(self, include_superclass=False):
        """
        Get a dict of commands available from the component.

        list contains strings on command name, command type,  remote command it uses

        Returns
        --------
            list(str)
                list of commands
        """
        command_list = {}
        current_attributes = []
        end = -1 if include_superclass else 1
        for c in self.__class__.__mro__[:end]:  # loop through the classes including super classes
            if not issubclass(c, Component):  # it should be subclass of Component
                break
            if c == Component:  # But it should not be Component
                break
            for key in c.__dict__:
                if key.startswith('_'):
                    continue
                if key in current_attributes:
                    continue
                current_attributes.append(key)

                instance = c.__dict__[key]
                if issubclass(instance.__class__, Command) or \
                   issubclass(instance.__class__, IndexCommand):
                    command_list[key] = (instance.__class__.__name__, instance.remote_command)
        return command_list

    def get_method_list(self, include_superclass=False):
        """
        get a list of names of methods available from the component
        including methods inherited from the superclasses

        returns
        --------
            list(str)
                list of string of method names
        """
        method_list = []
        current_attributes = []
        end = -1 if include_superclass else 1
        for c in self.__class__.__mro__[:end]:  # loop through the classes including super classes
            if not issubclass(c, Component):  # it should be subclass of Component
                break
            if c == Component:  # But it should not be Component
                break

            for key in c.__dict__:
                if key == '_parent':
                    continue
                if key.startswith('__'):
                    continue

                child = c.__dict__[key]
                if key in current_attributes:
                    continue
                current_attributes.append(key)
                if callable(child):
                    method_list.append('{}'.format(key))
        return method_list

    def get_command_info(self, command_name):
        if not hasattr(self.__class__, command_name):
            raise AttributeError("No command named '{}' in {}".format(command_name, self.__class__.__name__))
        cmd = self.__class__.__dict__[command_name]
        if issubclass(cmd.__class__, DictCommand):
            info = (cmd.__class__.__name__, cmd.remote_command,
                    cmd.set_dict, cmd.get_dict, None)
        elif issubclass(cmd.__class__, DictIndexCommand):
            info = (cmd.__class__.__name__, cmd.remote_command,
                    cmd.set_dict, cmd.get_dict, cmd.index_dict)
        elif issubclass(cmd.__class__, IndexCommand):
            info = (cmd.__class__.__name__, cmd.remote_command,
                    None, None, cmd.index_dict)
        elif issubclass(cmd.__class__, Command):
            info = (cmd.__class__.__name__, cmd.remote_command,
                    None, None, None)
        else:
            raise AttributeError("'{}' is not a command in {}".format(command_name, self.__class__.__name__))
        return {'command class': info[0],
                'raw remote command': info[1],
                'set_dict': info[2],
                'get_dict': info[3],
                'index_dict': info[4]
                }

    def assert_command_key(self, command, key):
        """
        It asserts if the component has the command as a DictCommand and DictIndexCommand, and
        the command has the key in its set_dict.
        """

        if not hasattr(self.__class__, command):
            raise AttributeError("No command named '{}' in {}".format(command, self.__class__.__name__))

        cmd = self.__class__.__dict__[command]
        if not issubclass(cmd.__class__, DictCommand) and not issubclass(cmd.__class__, DictIndexCommand):
            raise TypeError("'{}' is not a DictCommand or DictIndexCommand in {}"
                            .format(command, self.__class__.__name__))
        if key not in cmd.set_dict:
            raise KeyError(f" '{key}' is in {cmd.set_dict} of command '{command}'.")

    def capture_commands(self, include_query_only=False, include_set_only=False,
                         include_excluded=False, include_methods=False, show_raw_cmds=False):
        """
        Query all command with both set and get methods in the component
        and its subcomponents
        """
        commands = {}

        # Recursive calls to capture commands from subcomponents
        for j in self.__dict__:
            if j =='_parent':
                continue

            instance = self.__dict__[j]
            if issubclass(instance.__class__,  Component):
                commands[j] = instance.capture_commands(include_query_only, include_set_only,
                                    include_excluded, include_methods, show_raw_cmds)

        # Capture commands from the current component
        current_attributes = []
        for c in self.__class__.__mro__:  # loop through the classes including super classes
            if not issubclass(c, Component):  # it should be subclass of Component
                break
            if c == Component:  # But it should not be Component
                break

            for key in c.__dict__:
                cmd_instance = c.__dict__[key]
                if key in current_attributes:
                    continue
                current_attributes.append(key)

                if show_raw_cmds and \
                    (issubclass(cmd_instance.__class__, Command) or \
                     issubclass(cmd_instance.__class__, IndexCommand)):
                    k = key + f' <{cmd_instance.remote_command}>'
                else:
                    k = key

                allowed = False
                if callable(cmd_instance):
                    if include_methods and not k.startswith('_'):
                        commands[k + '() [M]'] = ''
                    continue

                if cmd_instance in self.exclude_capture:
                    if include_excluded:
                        commands[k + ' [X]'] = ''
                    continue

                if issubclass(cmd_instance.__class__, Command):
                    if include_set_only:
                        if cmd_instance._set_enable and not cmd_instance._get_enable:
                            commands[k + ' [SO]'] = ''
                            continue

                    if include_query_only:
                        allowed = cmd_instance._get_enable
                    else:
                        allowed = cmd_instance._set_enable and cmd_instance._get_enable
                    if not allowed:
                        continue

                    if not cmd_instance._set_enable:
                        name = k + ' [QO]'
                    else:
                        name = k
                    commands[name] = cmd_instance.__get__(self, self.__class__)

                elif issubclass(cmd_instance.__class__, IndexCommand):
                    if include_query_only:
                        allowed = cmd_instance._get_enable
                    else:
                        allowed = cmd_instance._set_enable and cmd_instance._get_enable
                    if not allowed:
                        continue

                    if not cmd_instance._set_enable:
                        name = k + ' [QO]'
                    else:
                        name = k

                    commands[name] = {}
                    index = cmd_instance.index_min
                    while index <= cmd_instance.index_max:
                        try:
                            if cmd_instance.index_dict is None:
                                commands[name][index] = cmd_instance.__getitem__(index)
                            else:
                                for key, value in cmd_instance.index_dict.items():
                                    if value == index:
                                        commands[name][key] = cmd_instance.__getitem__(index)
                                        break
                            index += 1
                        except Exception as e:
                            print(f'  {type(e)} {e} command:{k} index: {index}')
                            break
        return commands

