import logging
from rgagui.base.task import Task
from rga import UGA100, RGA100

UgaName = 'uga'
RgaName = 'rga'
"""
This is a name used in .taskConfig file for an instrument definition
"""

logger = logging.getLogger(__name__)


def get_rga(task: Task, name=None) -> RGA100:
    """
    Instead of using task.get_instrument() directly in a Task subclass,
    Defining a wrapper function that returns a specific instrument
    return type will help a context-sensitive editors to display
    attributes available for the instrument class.
    If name is None, the first instrument in the .taskconfig file is assumed.
    """
    if name is None:
        inst = list(task.inst_dict.values())[0]
    else:
        inst = task.get_instrument(name)

    if issubclass(type(inst), RGA100):
        return inst
    elif issubclass(type(inst), UGA100):
        return inst.rga
    else:
        raise TypeError('{} is not a RGA100 instance'.format(name))


def get_uga(task: Task, name=None) -> UGA100:
    inst = task.get_instrument(name)

    if not issubclass(type(inst), UGA100):
        raise TypeError('{} is not a UGa100 instance'.format(name))
    return inst
