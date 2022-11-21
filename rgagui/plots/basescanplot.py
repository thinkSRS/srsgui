
import time
import logging
from matplotlib.axes import Axes
from rgagui.base import Task, round_float
from rga.rga100.scans import Scans

logger = logging.getLogger(__name__)


class BaseScanPlot:
    def __init__(self, ax: Axes, plot_name='', save_to_file=False, parent=None):
        self.type = self.__class__.__name__
        self.parent = parent
        self.ax = ax
        self.name = plot_name

        self.conversion_factor = 0.1
        self.unit = 'fA'
        self.save_to_file = False

        if save_to_file and hasattr(self.parent, 'session_handler') and self.parent.session_handler:
            self.save_to_file = True
        else:
            logger.error('parent has no session_handler')

        self.mass_axis = []
        self.data = {}

        self.header_saved = False
        self.initial_time = time.time()

        self.ax.set_title(self.name)

    def set_conversion_factor(self, factor=0.1, unit='fA'):
        old_factor = self.conversion_factor
        self.conversion_factor = factor
        self.unit = unit
        if self.parent:
            self.parent.add_details(' {:.4e} '.format(self.conversion_factor), 'Conversion factor')
            self.parent.add_details(' {} '.format(self.unit), 'Converted unit')

        factor_ratio = self.conversion_factor / old_factor
        bottom, top = self.ax.get_ylim()
        self.ax.set_ylim(bottom * factor_ratio, top * factor_ratio)
        self.ax.set_ylabel('Intensity ({})'.format(self.unit))

    def save_scan_data(self):
        if not self.save_to_file:
            return
        if not self.header_saved:
            self.parent.session_handler.add_dict_to_file(self.name, self.get_plot_info())
            self.parent.create_table_in_file(self.name, 'Elapsed time', *map(round_float, self.mass_axis))
            self.header_saved = True

        # write the spectrum in to the data file
        elapsed_time = round_float(time.time() - self.initial_time)
        # timestamp = datetime.now().strftime('%H:%M:%S')
        self.parent.add_to_table_in_file(self.name, elapsed_time, *self.scan.spectrum)

    def get_plot_info(self):
        return {
            'type': self.type,
            'xunit': 's',
            'yunit': self.unit,
            'axes_title': self.ax.get_title(),
            'axes_xlabel': self.ax.get_xlabel(),
            'axes_ylabel': self.ax.get_ylabel(),
            'axes_xlim': self.ax.get_xlim(),
            'axes_ylim': self.ax.get_ylim(),
            'axes_xsclae': self.ax.get_xscale(),
            'axes_yscale': self.ax.get_yscale(),
        }

    def cleanup(self):
        raise NotImplementedError()
