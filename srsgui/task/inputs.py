
"""
Interface for input variables between Task and InputPanel in GUI

"""


class IntegerInput:
    def __init__(self, default_value, suffix='', minimum=0.0, maximum=0.0, single_step=1):
        self.minimum = minimum
        self.maximum = maximum
        self.single_step = single_step
        self.suffix = suffix
        self.default_value = default_value
        self.value = default_value


class FloatInput:
    def __init__(self, default_value, suffix='', minimum=0.0, maximum=0.0, single_step=1):
        self.minimum = minimum
        self.maximum = maximum
        self.single_step = single_step
        self.suffix = suffix
        self.default_value = default_value
        self.value = default_value


class StringInput:
    def __init__(self, default_value):
        self.default_value = default_value
        self.value = default_value


class ListInput:
    def __init__(self, item_list, default_index=0):
        self.item_list = item_list
        self.default_value = default_index
        self.value = default_index
        self.text = ''


class InstrumentInput:
    """
    InputPanel will set a QComboBox widget with inst_dict
    """

    def __init__(self, default_index=0):
        self.default_value = default_index
        self.value = default_index
        self.text = ''
