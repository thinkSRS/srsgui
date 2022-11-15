import time
from matplotlib.axes import Axes
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot

from rga.rga100.scans import Scans


class TimePlot(QObject):
    data_available = Signal()

    def __init__(self, ax: Axes, plot_name='', data_names=('Y',)):
        super().__init__()
        self.ax = ax
        self.data_keys = data_names

        self.data_available.connect(self.update)
        self.init_time = time.time()
        
        self.time = []
        self.data = {}
        self.lines = {}
        for key in self.data_keys:
            self.data[key] = []
            self.lines[key], = self.ax.plot(self.time, self.data[key], label=key.split()[0])
        self.ax.set_title(plot_name)
        self.ax.set_xlabel('Time (s)')
        self.ax.set_xlim(0, 300)

    def add_data(self, data_list=(0,), update_display=False):
        self.time.append(time.time() - self.init_time)
        
        for key, point in zip(self.data_keys, data_list):
            self.data[key].append(point)
        
        for key in self.data_keys:
            self.lines[key].set_xdata(self.time)
            self.lines[key].set_ydata(self.data[key])
            
        if update_display:
            self.data_available.emit()
            
        if len(self.time) == 1:
            min_value = min(data_list)
            max_value = max(data_list)
            self.ax.set_ylim(min_value - abs(min_value)/2, max_value + abs(max_value)/2)

    @Slot()
    def update(self):
        self.ax.figure.canvas.draw_idle()


class AnalogScanPlot(QObject):
    data_available = Signal()

    def __init__(self, ax: Axes, scan: Scans, plot_name=''):
        super().__init__()
        self.ax = ax
        self.scan = scan

        self.data_available.connect(self.update)
        self.data = {'x': [], 'y': []}

        self.ax.set_title(plot_name)
        self.ax.set_xlabel("Mass (AMU)")
        self.ax.set_ylabel('Ion Current(0.1fA)')
        self.line, = self.ax.plot(self.data['x'], self.data['y'])

        self.conversion_factor = 0.1
        self.reset()

    def reset(self):
        self.initial_mass = self.scan.initial_mass
        self.final_mass = self.scan.final_mass
        self.resolution = self.scan.resolution
        self.mass_axis = self.scan.get_mass_axis()
        self.ax.set_xlim(self.initial_mass, self.final_mass, auto=False)
        self.scan.set_callbacks(self.update_callback, None, self.update_on_scan_finished)

    def update_callback(self, index):
        self.data['x'] = self.mass_axis[:index]
        self.data['y'] = self.scan.spectrum[:index] * self.conversion_factor
        self.line.set_xdata(self.data['x'])
        self.line.set_ydata(self.data['y'])

        # Tell GUI to redraw the plot
        self.data_available.emit()

    def update_on_scan_finished(self):
        self.data['x'] = self.mass_axis
        self.data['y'] = self.scan.spectrum * self.conversion_factor
        self.line.set_xdata(self.data['x'])
        self.line.set_ydata(self.data['y'])

        # Tell GUI to redraw the plot
        self.data_available.emit()

    def update(self):
        self.ax.figure.canvas.draw_idle()

    def cleanup(self):
        """
        callback functions should be disconnected when task is finished
        """
        self.scan.set_callbacks(None, None, None)
