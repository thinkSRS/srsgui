
import time
import logging

from matplotlib.axes import Axes
from rgagui.base import Task, round_float

logger = logging.getLogger(__name__)


class TimePlot:
    def __init__(self, parent: Task, ax: Axes, plot_name='', data_names=('Y',), save_data=True):
        if not issubclass(type(parent), Task):
            raise TypeError('Invalid parent {} is not a Task subclass'.format(type(parent)))
        # if type(ax) is not Axes or AxesSubplot:
        #    raise TypeError('ax is not a Matplotlib Axes class, but "{}"'.format(type(ax)))

        self.type = 'time_plot'
        self.parent = parent                    
        self.ax = ax
        self.name = plot_name

        if hasattr(self.parent, 'session_handler') and self.parent.session_handler:
            self.save_data = save_data
        else:
            self.save_data = False
            logger.error('parent has no session_handler')

        self.unit = ''

        self.data_keys = data_names
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
        self.ax.legend()

        self.header_saved = False
        self.initial_time = time.time()

    def add_data(self, data_list=(0,), update_figure=False):
        self.time.append(time.time() - self.init_time)
        
        for key, point in zip(self.data_keys, data_list):
            self.data[key].append(point)
        
        for key in self.data_keys:
            self.lines[key].set_xdata(self.time)
            self.lines[key].set_ydata(self.data[key])
           
        if len(self.time) == 1:
            min_value = min(data_list)
            max_value = max(data_list)
            self.ax.set_ylim(min_value - abs(min_value)/2, max_value + abs(max_value)/2)
        if update_figure:
            self.parent.request_figure_update(self.ax.figure)

        if self.save_data:
            self.save_scan_data(data_list)

    def save_scan_data(self, data_list):
        if not self.header_saved:
            self.parent.session_handler.add_dict_to_file(self.name, self.get_plot_info())
            self.parent.create_table_in_file(self.name, 'Elapsed time', *self.data_keys)
            self.header_saved = True

        # write the spectrum in to the data file
        elapsed_time = round_float(time.time() - self.initial_time)
        # timestamp = datetime.now().strftime('%H:%M:%S')
        self.parent.add_to_table_in_file(self.name, elapsed_time, *map(round_float, data_list))

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
        pass
