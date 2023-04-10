
import time
from srsgui import Component
from srsgui.inst import Command, IndexCommand, \
                        FloatCommand, FloatIndexCommand


class Index:
    pass


class CommandItem:
    """A Command item corresponding to a line in QTreeView"""

    def __init__(self, parent: "CommandItem" = None):
        self._parent = parent
        self._children = []
        self._value = None
        
        self.name = ""
        self.value_type = None  # There are 3 types of values: str, int, and float
        self.precision = 4
        
        self.comp = None
        self.comp_type = None   # There are 5 types of components: Component, Commands, IndexCommands, method and Index
        self.set_enable = False
        self.get_enable = False
        self.is_method = False
        self.excluded = False
        self.raw_remote_command = ""
        self.timestamp = 0.0

    def appendChild(self, item: "CommandItem"):
        """Add item as a child"""
        self._children.append(item)

    def child(self, row: int) -> "CommandItem":
        """Return the child of the current item from the given row"""
        return self._children[row]

    def parent(self) -> "CommandItem":
        """Return the parent of the current item"""
        return self._parent

    def childCount(self) -> int:
        """Return the number of children of the current item"""
        return len(self._children)

    def row(self) -> int:
        """Return the row where the current item occupies in the parent"""
        return self._parent._children.index(self) if self._parent else 0

    @property
    def value(self):
        """Return the value of the current item"""
        try:
            ts = time.time()
            if ts - self.timestamp < 0.1: # Update value later than 0.1 s
                return self._value

            if self.comp_type == Index and self.get_enable and not self.excluded:
                self._value = self._parent.comp.__getitem__(self.comp)
                self._value_type = type(self._value)
                self.timestamp = ts
            elif issubclass(type(self.comp), Command) and self.get_enable and not self.excluded:
                self._value = self.comp.__get__(self._parent.comp, self._parent.comp.__class__)
                self._value_type = type(self._value)
                self.timestamp = ts
            else:
                self._value_type = type(self._value)

            # Round float to its precision
            if self.comp_type == FloatCommand:
                self._value = round(self._value, self.precision)
            elif self.comp_type == Index and self._parent.comp_type == FloatIndexCommand:
                self._value = round(self._value, self.precision)
        except Exception as e:
            print(e, self.name)
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def set_value(self, value):
        """Set value to the instrument and update the value of the item"""
        if self.comp_type == Index:
            self._parent.comp.__setitem__(self.comp, value)
            self._value = self._parent.comp.__getitem__(self.comp)
            self.timestamp = time.time()
        elif issubclass(type(self.comp), Command):
            self.comp.__set__(self._parent.comp, value)
            self._value = self.comp.__get__(self._parent.comp, self._parent.comp.__class__)
            self.timestamp = time.time()
        else:
            self._value = value

    def is_editable(self):
        """Return True if the item is editable"""
        if self.comp_type == Index and \
                self.set_enable and self.get_enable and not self.excluded:
            return True
        elif issubclass(type(self.comp), Command) and \
                self.set_enable and self.get_enable and not self.excluded:
            return True
        else:
            return False

    def get_unit(self):
        """Return the unit of the item"""
        comp = None
        if self.comp_type == Index:
            comp = self.parent().comp
        elif issubclass(type(self.comp), Command) or \
             issubclass(type(self.comp), IndexCommand):
            comp = self.comp

        if comp and hasattr(comp, 'unit'):
            return comp.unit
        else:
            return ""

    def get_format(self):
        """Return the format of the item"""
        comp = None
        if self.comp_type == Index:
            comp = self.parent().comp
        elif issubclass(type(self.comp), Command) or \
             issubclass(type(self.comp), IndexCommand):
            comp = self.comp

        if comp and hasattr(comp, 'fmt'):
            return comp.fmt
        else:
            return ''

    @classmethod
    def load(
        cls, comp, parent: "CommandItem" = None, sort=False
    ) -> "CommandItem":
        """Create a 'root' CommandItem from a Component and 
        populate its subcomponent and commands recursively.

        Returns:
            CommandItem: CommandItem
        """
        root_item = CommandItem(parent)
        root_item.name = "root"
        root_item.comp = comp

        if issubclass(comp.__class__, Component):
            for j in comp.__dict__:
                if j == '_parent':
                    continue
                instance = comp.__dict__[j]
                if issubclass(instance.__class__,  Component):                
                    child = cls.load(instance, root_item, sort)
                    child.name = j
                    child.comp = instance
                    if instance in comp.exclude_capture:
                        child.excluded = True
                    child.comp_type = type(instance)
                    root_item.appendChild(child)

            current_attributes = []
            for c in comp.__class__.__mro__:  # loop through the classes including super classes
                if not issubclass(c, Component):  # it should be a subclass of Component
                    break
                if c == Component:  # But it should not be Component
                    break

                for key in c.__dict__:
                    cmd_instance = c.__dict__[key]
                    if key in current_attributes:
                        continue
                    current_attributes.append(key)

                    if issubclass(cmd_instance.__class__, Command):
                        child = cls.load(cmd_instance, root_item, sort)
                        child.name = key
                        child.comp = cmd_instance
                        child.comp_type = type(cmd_instance)

                        root_item.appendChild(child)

                    elif issubclass(cmd_instance.__class__, IndexCommand):
                        child = cls.load(cmd_instance, root_item, sort)
                        child.name = key
                        child.comp = cmd_instance
                        child.comp_type = type(cmd_instance)
                        root_item.appendChild(child)

                    elif callable(cmd_instance):
                        if issubclass(cmd_instance.__class__, type):
                            continue
                        if key.startswith('_'):
                            continue
                        
                        child = cls.load(cmd_instance, root_item, sort)
                        child.name = key
                        child.comp = cmd_instance
                        child.comp_type = type(cmd_instance)
                        root_item.appendChild(child)
        else:
            if callable(comp):
                root_item.comp = comp
                root_item.comp_type = type(comp)
                root_item.is_method = True

            elif issubclass(type(comp), Command):
                root_item.comp = comp
                root_item.comp_type = type(comp)
                root_item.excluded = comp in root_item.parent().comp.exclude_capture
                root_item.raw_remote_command = comp.remote_command
                root_item.set_enable = comp._set_enable
                root_item.get_enable = comp._get_enable

            elif issubclass(type(comp), IndexCommand):
                root_item.comp = comp
                root_item.comp_type = type(comp)
                root_item.excluded = comp in root_item.parent().comp.exclude_capture
                root_item.raw_remote_command = comp.remote_command
                root_item.set_enable = comp._set_enable
                root_item.get_enable = comp._get_enable

                try:
                    if comp.index_dict is None:
                        index = comp.index_min
                        while index <= comp.index_max:
                            child = cls.load(index, root_item, sort)
                            child.name = f'{index}'
                            child.comp = index
                            child.comp_type = Index
                            child.excluded = root_item.excluded
                            child.set_enable = root_item.set_enable
                            child.get_enable = root_item.get_enable
                            root_item.appendChild(child)
                            index += 1
                    else:
                        for key in comp.index_dict:
                            child = cls.load(key, root_item, sort)
                            child.name = f'{key}'
                            child.comp = key
                            child.comp_type = Index
                            child.exluded = root_item.excluded
                            child.set_enable = comp._set_enable
                            child.get_enable = comp._get_enable
                            root_item.appendChild(child)
                except Exception as e:
                    print(f'  {type(e)} {e} command:{comp.remote_command} index: {index}')
        return root_item
