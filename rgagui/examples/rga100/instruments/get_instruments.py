from rga import RGA100

RgaName = 'rga'
"""
This is a name used in .taskConfig file for an instrument definition
"""


def get_rga(task) -> RGA100:
    """
    Instead of using task.get_instrument() directly in a Task subclass,
    Defining a wrapper function with a instrument return type will help
    a context-sensitive editors display  attributes available
    for the instrument class.
    """
    return task.get_instrument(RgaName)
