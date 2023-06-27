##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

import logging
from matplotlib.figure import Figure

logger = logging.getLogger(__file__)


class Callbacks:
    """
    Base callbacks used by :class:`Task <srsgui.task.task.Task>` class.
    The parent of Task should subclass Callbacks class, override callback methods that it will use
    and call set_callback_handler() to make it available to the Task subclass.
    """
    def started(self):

        logger.info('Task started')

    def finished(self):
        logger.info('Task finished')

    def text_available(self, text: str):

        print(text)

    def parameter_changed(self):
        """
        Override to do something when a parameter in input_parameters is changed
        """
        logger.info('Task.InputParameters changed')

    def figure_update_requested(self, fig: Figure):
        fig.canvas.draw_idle()

    def data_available(self, data: dict):
        logger.info('data available')

    def new_question(self, question: str, return_type: object):
        logger.info('Question: {}'.format(question))
