import logging
from rga import UGA100, RGA100

UgaName = 'uga'
RgaName = 'rga'
"""
This is a name used in .taskConfig file for an instrument definition
"""

logger = logging.getLogger(__name__)


def get_ugs(task) -> UGA100:
    """
    Instead of using task.get_instrument() directly in a Task subclass,
    Defining a wrapper function with a instrument return type will help
    a context-sensitive editors display  attributes available
    for the instrument class.
    """

    return task.get_instrument(UgaName)
    
    
def get_rga(task) -> RGA100:
    """
    Get the RGA in a UGA, to run tasks in RGA example tasks
    """
    
    uga = task.get_instrument(UgaName)
    if uga.status.StateDict[uga.rga.state] != 'On':
        logger.warning('Rga is OFF')
    return uga.rga
