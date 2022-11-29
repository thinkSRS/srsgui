import time
import logging
from matplotlib.axes import Axes
from rgagui.basetask import Task
from rga.rga100.scans import Scans

from .basescanplot import BaseScanPlot

logger = logging.getLogger(__name__)


class AnalogScanPlot(BaseScanPlot):
    def __init__(self, parent: Task, ax: Axes, scan: Scans, plot_name='', save_to_file=True):
        if not issubclass(type(parent), Task):
            raise TypeError('Invalid parent {} is not a Task subclass'.format(type(parent)))
        if not hasattr(ax, 'figure'):
            raise TypeError('ax has no figure attribute. type: "{}"'.format(type(ax)))

        super().__init__(ax, plot_name, save_to_file, parent)

        self.conversion_factor = 0.1
        self.unit = 'fA'

        self.scan = scan
        self.data = {'x': [], 'y': [], 'prev_x': [], 'prev_y': []}

        self.ax.set_xlabel("Mass (AMU)")
        self.ax.set_ylabel('Intensity ({})'.format(self.unit))
        self.prev_line, = self.ax.plot(self.data['x'], self.data['y'], label='Previous')
        self.line, = self.ax.plot(self.data['x'], self.data['y'], label='Current')
        self.ax.set_ylim(1, 100000)

        self.reset()

    def reset(self):
        self.initial_mass = self.scan.initial_mass
        self.final_mass = self.scan.final_mass
        self.resolution = self.scan.resolution
        self.set_x_axis(self.scan.get_mass_axis(True))

        self.ax.set_xlim(self.initial_mass, self.final_mass, auto=False)
        self.scan.set_callbacks(self.scan_data_available_callback,
                                None,
                                self.scan_finished_callback)

    def scan_data_available_callback(self, index):
        self.data['x'] = self.x_axis[:index]
        self.data['y'] = self.scan.spectrum[:index] * self.conversion_factor
        self.line.set_xdata(self.data['x'])
        self.line.set_ydata(self.data['y'])

        # Tell GUI to redraw the plot
        self.parent.request_figure_update(self.ax.figure)

    def scan_finished_callback(self):
        self.data['x'] = self.x_axis
        self.data['y'] = self.scan.spectrum * self.conversion_factor
        self.data['prev_x'] = self.data['x']
        self.data['prev_y'] = self.data['y']
        self.line.set_xdata(self.data['x'])
        self.line.set_ydata(self.data['y'])
        self.prev_line.set_xdata(self.data['prev_x'])
        self.prev_line.set_ydata(self.data['prev_y'])

        # Tell GUI to redraw the plot
        self.parent.request_figure_update(self.ax.figure)
        self.save_scan_data(self.scan.spectrum)

    def cleanup(self):
        """
        callback functions should be disconnected when task is finished
        """
        self.scan.set_callbacks(None, None, None)
