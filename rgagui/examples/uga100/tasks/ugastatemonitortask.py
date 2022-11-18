import time
import numpy as np
from rgagui.base.task import Task
from rgagui.base.inputs import InstrumentInput, IntegerInput
from rgagui.plots.timeplot import TimePlot

from instruments.get_instruments import get_uga

            
class UGAStateMonitorTask(Task):
    """
    update
    """
    InstrumentName = 'uga to monitor'
    UpdatePeriod = 'update period'
    input_parameters = {
        InstrumentName: InstrumentInput(),
        UpdatePeriod: IntegerInput(2, ' s', 1, 60, 1)
    }

    def setup(self):
        self.logger = self.get_logger(__name__)
        self.params = self.get_all_input_parameters()
        self.uga = get_uga(self, self.params[self.InstrumentName])
        self.ax = self.figure.subplots(nrows=1, ncols=2, sharex=True)
        
        self.pressure_plot = TimePlot(self, self.ax[0], 'Pressure', 
            ['IG pressure', 'PG pressure', 'CM pressure'])
        self.pressure_plot.ax.set_yscale('log')
        
        self.temperature_plot = TimePlot(self, self.ax[1], 'Temperature', 
            ['Chamber Temperature', 'Elbow Temperature', 'Sample Inlet Temperature',
             'Capillary Temperature', 'Turbo Pump Temperature'])
   
    def test(self):
        while True:
            if not self.is_running():
                break
                
            self.display_device_info(device_name=self.params[self.InstrumentName], update=True)
            
            self.pressure_plot.add_data([self.uga.ig.get_pressure(), self.uga.rp.get_pressure(),
                         self.uga.bp.get_pressure()])
                         
            self.temperature_plot.add_data([self.uga.temperature.chamber, self.uga.temperature.elbow,
                         self.uga.temperature.sample_inlet, self.uga.temperature.capillary,
                         self.uga.temperature.turbo_pump], True)
                         
            time.sleep(self.params[self.UpdatePeriod])
            
    def cleanup(self):
        pass
