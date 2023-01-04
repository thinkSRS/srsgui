
import logging
from matplotlib.figure import Figure

logger = logging.getLogger(__file__)


class Callbacks:

    def started(self):
        logger.info('Task started')

    def finished(self):
        logger.info('Task finished')

    def text_available(self, text: str):
        print(text)

    def parameter_changed(self):
        logger.info('Task.InputParameters changed')

    def figure_update_requested(self, fig: Figure):
        fig.canvas.draw_idle()

    def data_available(self, data: dict):
        logger.info('data available')

    def new_question(self, question: str, return_type: object):
        logger.info('Question: {}'.format(question))
