

import time
import numpy
from matplotlib.axes import Axes
from rgagui.base import Task, round_float
from rga.rga100.scans import Scans


class HistogramScanPlot:
    def __init__(self, parent: Task, ax: Axes, scan: Scans, plot_name='', save_data=True):
        if not issubclass(type(parent), Task):
            raise TypeError('Invalid parent {} is not a Task subclass'.format(type(parent)))
        if not hasattr(ax, 'figure'):
            raise TypeError('ax has no figure attribute. type: "{}"'.format(type(ax)))

        self.parent = parent
        self.ax = ax
        self.scan = scan
        self.name = plot_name
        self.save_data = save_data

        self.mass_axis = self.scan.get_mass_axis(False)
        x = self.mass_axis
        y = numpy.zeros_like(x)
        self.data = {'x': x, 'y': y, 'prev_x': x, 'prev_y': y}

        self.conversion_factor = 0.1
        self.unit = 'fA'

        self.ax.set_title(plot_name)
        self.ax.set_xlabel("Mass (AMU)")
        self.ax.set_ylim(1, 100000)
        self.ax.set_ylabel('Ion Current ({})'.format(self.unit))

        self.prev_rects = self.ax.bar(self.data['x'], self.data['y'])
        self.rects = self.ax.bar(self.data['x'], self.data['y'])

        self.reset()

        if self.save_data:
            self.parent.create_table_in_file(self.name, 'Elapsed time', *map(round_float, self.mass_axis))

        self.initial_time = time.time()

    def reset(self):
        self.initial_mass = self.scan.initial_mass
        self.final_mass = self.scan.final_mass
        self.mass_axis = self.scan.get_mass_axis(False)

        self.data['x'] = self.mass_axis
        self.data['y'] = numpy.zeros_like(self.mass_axis)

        self.ax.set_xlim(self.initial_mass, self.final_mass, auto=False)
        self.scan.set_callbacks(self.update_callback,
                                self.scan_started_callback,
                                self.scan_finished_callback)

    def set_conversion_factor(self, factor=0.1, unit='fA'):
        old_factor = self.conversion_factor
        self.conversion_factor = factor
        self.unit = unit
        self.parent.add_details(' {:.4e} '.format(self.conversion_factor), 'Conversion factor')
        self.parent.add_details(' {} '.format(self.unit), 'Converted unit')

        factor_ratio = self.conversion_factor / old_factor
        bottom, top = self.ax.get_ylim()
        self.ax.set_ylim(bottom * factor_ratio, top * factor_ratio)
        self.ax.set_ylabel('Ion Current ({})'.format(self.unit))

    # The scan calls this callback when data is available
    def update_callback(self, index):
        i = self.last_index
        while i <= index:
            # Update rectangles for new data
            inten = self.scan.spectrum[i] * self.conversion_factor
            self.rects[i].set_height(inten)
            self.data['y'].append(inten)
            i += 1

        self.last_index = index
        self.parent.request_figure_update(self.ax.figure)

    def scan_started_callback(self):
        self.last_index = 0

        # Initialize the rectangles in the bar plot when a scan started
        for rect1, rect2 in zip(self.prev_rects, self.rects):
            rect1.set_height(rect2.get_height())
        self.data['prev_y'] = self.scan.previous_spectrum * self.conversion_factor

        for rect in self.rects:
            rect.set_height(0)
            self.data['y'] = []

        # Tell GUI to redraw the plot
        self.parent.request_figure_update(self.ax.figure)

    def scan_finished_callback(self):
        if self.save_data:
            # write the spectrum in to the data file
            elapsed_time = round_float(time.time() - self.initial_time)
            # timestamp = datetime.now().strftime('%H:%M:%S')
            self.parent.add_to_table_in_file(self.name, elapsed_time, *self.scan.spectrum)

    def cleanup(self):
        """
        callback functions should be disconnected when task is finished
        """
        self.scan.set_callbacks(None, None, None)
