
"""
Interface for input variables between Task and InputPanel in GUI

"""


class BaseInput:
    def __init__(self, default_value):
        self.default_value = default_value
        self.value = default_value

    def get_value(self):
        return self.value


class StringInput(BaseInput):
    pass


class PasswordInput(BaseInput):
    pass


class IntegerInput(BaseInput):
    def __init__(self, default_value, suffix='', minimum=0, maximum=65535, single_step=1):
        super().__init__(default_value)
        self.minimum = minimum
        self.maximum = maximum
        self.single_step = single_step
        self.suffix = suffix


class FloatInput(BaseInput):
    def __init__(self, default_value, suffix='', minimum=0.0, maximum=100.0, single_step=1):
        super().__init__(default_value)
        self.minimum = minimum
        self.maximum = maximum
        self.single_step = single_step
        self.suffix = suffix


class ListInput(BaseInput):
    def __init__(self, item_list, default_index=0):
        super().__init__(default_index)
        self.item_list = item_list
        self.text = ''

    def get_value(self):
        return self.text

    def get_index(self):
        return self.value


class BoolInput(ListInput):
    def __init__(self, item_list=('False', 'True'), default_index=0):
        super().__init__(item_list, default_index)

    def get_value(self):
        return 0 if self.value == 0 else 1


class IntegerListInput(ListInput):
    def __init__(self, item_list, default_index=0):
        super().__init__(item_list, default_index)
        li = []
        for item in self.item_list:
            if type(item) != int:
                raise TypeError('Item "{}" in IntListInput is not an integer'.format(item))
            li.append(str(item))
        if not len(li):
            raise ValueError('No item in the item_list')

        self.item_list = li
        self.text = self.item_list[self.value]

    def get_value(self):
        return int(self.text)


class FloatListInput(IntegerListInput):
    def get_value(self):
        return float(self.text)


class InstrumentInput(ListInput):
    """
    InputPanel will setup a QComboBox widget with inst_dict
    """

    def __init__(self, default_index=0):
        super().__init__([], default_index)


class FindListInput(ListInput):
    """
    Hold a list of available resources from a communication
    interface find() method
    """
    def __init__(self, default_index=0):
        super().__init__([], default_index)


class Ip4Input(BaseInput):
    def get_value(self):
        octets = self.value.split('.')
        if len(octets) != 4:
            raise ValueError('Invalid IP4 format: {}'.format(self.value))
        li = []
        msg = 'Invalid octet {} in "{}"'
        for octet in octets:
            try:
                num = int(octet)
                if 0 > num or num > 255:
                    raise ValueError(msg.format(octet, self.value))
                li.append(str(num))
            except:
                raise ValueError(msg.format(octet, self.value))
        return '.'.join(li)
