import time
import numpy as np
from rgagui.base.task import Task
from rgagui.base.inputs import InstrumentInput, IntegerInput
from rgagui.plots.timeplot import TimePlot
from rgagui.plots.analogscanplot import AnalogScanPlot
from rgagui.plots.histogramscanplot import HistogramScanPlot

from instruments.get_instruments import get_uga, get_rga

            
class UGAMultiplotTask(Task):
    """
    Run multiple plots for UGA
    """
    InstrumentName = 'uga to monitor'
    input_parameters = {
        InstrumentName: InstrumentInput(),
    }

    figure_names = ['Analog Scan', 'Histogram Scan', 'RGA Analog Scan']

    def setup(self):
        self.logger = self.get_logger(__name__)
        
        self.instrument_name_value = self.get_input_parameter(self.InstrumentName)
        self.uga = get_uga(self, self.instrument_name_value)
        if self.uga.rga.state != 1:
            raise ValueError('UGA RGA is off')
        self.uga.rga.scan.set_parameters(1, 50, 5, 10)

        self.rga = get_rga(self, 'rga')

        self.ax = self.get_figure().subplots(nrows=1, ncols=2, sharex=True)
        self.ax_analog = self.get_figure('Analog Scan').add_subplot(111)
        self.ax_histogram = self.get_figure('Histogram Scan').add_subplot(111)
        self.ax_rga_analog = self.get_figure('RGA Analog Scan').add_subplot(111)

        self.pressure_plot = TimePlot(self, self.ax[0], 'Pressure', 
            ['IG pressure', 'PG pressure', 'CM pressure'])
        self.pressure_plot.ax.set_yscale('log')
        
        self.temperature_plot = TimePlot(self, self.ax[1], 'Temperature', 
            ['Chamber Temperature', 'Elbow Temperature', 'Sample Inlet Temperature',
             'Capillary Temperature', 'Turbo Pump Temperature'])

        self.analog_scan_plot = AnalogScanPlot(self, self.ax_analog, self.uga.rga.scan, 'Analog Scan')
        self.histogram_scan_plot = HistogramScanPlot(self, self.ax_histogram, self.uga.rga.scan, 'Histogram Scan')

        self.rga_analog_scan_plot = AnalogScanPlot(self, self.ax_rga_analog,
                                                   self.rga.scan, 'RGA analog')

    def test(self):
        while True:
            if not self.is_running():
                break
                
            self.display_device_info(device_name=self.instrument_name_value, update=True)
            
            self.pressure_plot.add_data([self.uga.ig.get_pressure(), self.uga.rp.get_pressure(),
                         self.uga.bp.get_pressure()])
                         
            self.temperature_plot.add_data([self.uga.temperature.chamber, self.uga.temperature.elbow,
                         self.uga.temperature.sample_inlet, self.uga.temperature.capillary,
                         self.uga.temperature.turbo_pump], True)

            self.uga.rga.scan.set_parameters(1, 50, 5, 10)
            self.analog_scan_plot.reset()
            self.uga.rga.scan.get_analog_scan()

            self.uga.rga.scan.set_parameters(10, 45, 3, 10)
            self.histogram_scan_plot.reset()
            self.uga.rga.scan.get_histogram_scan()

            self.rga.scan.set_parameters(1, 50, 3, 10)
            self.rga.scan.get_analog_scan()

    def cleanup(self):
        self.analog_scan_plot.cleanup()
        self.histogram_scan_plot.cleanup()
        self.rga_analog_scan_plot.cleanup()
        self.temperature_plot.cleanup()
        self.pressure_plot.cleanup()
