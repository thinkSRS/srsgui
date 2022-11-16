

import time
import numpy
from matplotlib.axes import Axes
from rgagui.base import Task
from rga.rga100.scans import Scans


class HistogramScanPlot:
    def __init__(self, parent: Task, ax: Axes, scan: Scans, plot_name=''):
        if not issubclass(type(parent), Task):
            raise TypeError('Invalid parent {} is not a Task subclass'.format(type(parent)))
        if not hasattr(ax, 'figure'):
            raise TypeError('ax has no figure attribute. type: "{}"'.format(type(ax)))

        self.parent = parent
        self.ax = ax
        self.scan = scan

        self.data = {'x': [], 'y': []}

        self.conversion_factor = 0.1
        self.unit = 'fA'

        self.ax.set_title(plot_name)
        self.ax.set_xlabel("Mass (AMU)")
        self.ax.set_ylabel('Ion Current ({})'.format(self.unit))
        self.reset()

    def reset(self):
        self.initial_mass = self.scan.initial_mass
        self.final_mass = self.scan.final_mass
        self.mass_axis = self.scan.get_mass_axis(False)

        self.data['x'] = self.mass_axis
        self.data['y'] = numpy.zeros_like(self.mass_axis)
        self.rects = self.ax.bar(self.data['x'], self.data['y'])

        self.ax.set_xlim(self.initial_mass, self.final_mass, auto=False)
        self.scan.set_callbacks(self.update_callback,
                                self.scan_started_callback,
                                None)

    def set_conversion_factor(self, factor=0.1, unit='fA'):
        self.conversion_factor = factor
        self.unit = unit
        self.ax.set_ylabel('Ion Current ({})'.format(self.unit))

    # The scan calls this callback when data is available
    def update_callback(self, index):
        i = self.last_index
        while i <= index:
            # Update rectangles for new data
            self.rects[i].set_height(self.scan.spectrum[i] * self.conversion_factor)
            i += 1

        self.last_index = index
        self.parent.request_figure_update(self.ax.figure)

    def scan_started_callback(self):
        self.last_index = 0

        # Initialize the rectangles in the bar plot when a scan started
        for rect in self.rects:
            rect.set_height(0)

        # Tell GUI to redraw the plot
        self.parent.request_figure_update(self.ax.figure)

    def cleanup(self):
        """
        callback functions should be disconnected when task is finished
        """
        self.scan.set_callbacks(None, None, None)
