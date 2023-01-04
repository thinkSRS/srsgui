from .communications import Interface
from .commands import Command, GetCommand
from .indexcommands import IndexCommand


class Component(object):
    """
    Class is used to build hierarchical structure in an instrument.
    An instrument can have multiple components and a component
    can also have multiple subcomponents. All the components
    inside an instrument shares the communication interface
    of the instrument.

    When the communication interface of an
    instrument changed, the instrument should call
    ``update_components()`` to update all its components.

    Component contains Command and its subclasses along with
    StrIndexCommand and its subclasses as class attributes.
    A convenience method, ``get_command_list()`` will show what commands are available
    from the component instance

    Component has a convenience method, ``get_component_list()`` to get child
    components of an instance. This method helps a user to navigate through
    component tree, even without the documentation.

    ``get_method_list()`` shows methods a component has, including ones
    inherited from the superclasses.

    The information available from the convenience methods are
    available interactively from context-sensitive editors, such as IDLE, Pycharm, VSCode.
    When the information from the editors are not complete, consulting with those convenience methods
    provides complete lists you can use.

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

    def get_lists(self):
        """
        Get the directory containing a list of subcomponents in this component,
        a list of commands available in the component,
        a list of  method available in the component and its superclass
        """
        return {
            'components': self._get_component_list(),
            'commands': self._get_command_list(),
            'methods': self._get_method_list()
        }

    def _add_parent_to_index_commands(self):
        # Add parent to ListCommands
        commands = self._get_command_list()
        for cmd in commands:
            instance = self.__class__.__dict__[cmd[0]]
            if hasattr(instance, "_add_parent"):
                instance._add_parent(self)

    def _get_component_list(self):
        """
        Get a list of the child component of the component

        Returns
        --------
            list(str)
                list contain name of child compoents and its class name
        """
        component_list =[]
        for k in self.__dict__:
            if k =='_parent':
                continue
            instance = self.__dict__[k]
            if issubclass(instance.__class__,  Component):
                component_list.append((k, 'instance of {}'.format(instance.__class__.__name__)))
        return component_list

    def _get_command_list(self):
        """
        Get a list of commands available from the component.

        list contains strings on command name, command type,  remote command it uses

        Returns
        --------
            list(str)
                list of commands
        """
        command_list = []
        for k in self.__class__.__dict__:
            instance = self.__class__.__dict__[k]
            if issubclass(instance.__class__, Command) or \
               issubclass(instance.__class__, IndexCommand):
                command_list.append((k, instance.__class__.__name__, instance.remote_command))
        return command_list

    def _get_method_list(self):
        """
        get a list of names of methods available from the component
        including methods inherited from the superclasses

        returns
        --------
            list(str)
                list of string of method names
        """
        method_list = []
        current_attributes= []
        for c in self.__class__.__mro__:  # loop through the classes including super classes
            if not issubclass(c, Component):  # it should be subclass of Component
                continue
            if c == Component:  # But it should not be Component
                continue

            for key in c.__dict__:
                if key == '_parent':
                    continue
                if key.startswith('__'):
                    continue
                if key not in c.__dict__:
                    continue

                child = c.__dict__[key]
                if key in current_attributes:
                    continue
                current_attributes.append(key)
                if callable(child):
                    method_list.append('{}()'.format(key))
        return method_list
