
import time
from matplotlib.axes import Axes
from rgagui.base import Task
from rga.rga100.scans import Scans


class AnalogScanPlot:
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
        self.line, = self.ax.plot(self.data['x'], self.data['y'])
        self.ax.set_ylim(1, 100000)
        self.reset()

    def reset(self):
        self.initial_mass = self.scan.initial_mass
        self.final_mass = self.scan.final_mass
        self.resolution = self.scan.resolution
        self.mass_axis = self.scan.get_mass_axis()
        self.ax.set_xlim(self.initial_mass, self.final_mass, auto=False)
        self.scan.set_callbacks(self.update_on_scan_data_available,
                                None,
                                self.update_on_scan_finished)

    def set_conversion_factor(self, factor=0.1, unit='fA'):
        old_factor = self.conversion_factor
        self.conversion_factor = factor
        self.unit = unit
        factor_ratio = self.conversion_factor / old_factor
        bottom, top = self.ax.get_ylim()
        self.ax.set_ylim(bottom * factor_ratio, top * factor_ratio)
        self.ax.set_ylabel('Ion Current ({})'.format(self.unit))

    def update_on_scan_data_available(self, index):
        self.data['x'] = self.mass_axis[:index]
        self.data['y'] = self.scan.spectrum[:index] * self.conversion_factor
        self.line.set_xdata(self.data['x'])
        self.line.set_ydata(self.data['y'])

        # Tell GUI to redraw the plot
        self.parent.request_figure_update(self.ax.figure)

    def update_on_scan_finished(self):
        self.data['x'] = self.mass_axis
        self.data['y'] = self.scan.spectrum * self.conversion_factor
        self.line.set_xdata(self.data['x'])
        self.line.set_ydata(self.data['y'])

        # Tell GUI to redraw the plot
        self.parent.request_figure_update(self.ax.figure)

    def cleanup(self):
        """
        callback functions should be disconnected when task is finished
        """
        self.scan.set_callbacks(None, None, None)
