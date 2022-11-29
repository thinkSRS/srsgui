from rgagui.basetask import Task
from rga import RGA100, UGA100


def get_rga(task:Task, name=None) -> RGA100:
    """
    Instead of using task.get_instrument() directly in a Task subclass,
    Defining a wrapper function with a instrument return type will help
    a context-sensitive editors display  attributes available
    for the instrument class.
    index is assumed from InstrumentInput .
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
        return None

