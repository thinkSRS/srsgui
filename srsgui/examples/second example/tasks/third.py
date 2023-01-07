import time
import math
import logging
from srsgui import Task
from srsgui import IntegerInput


class ThirdTask(Task):
    """
    This is the second task using srsgui 
    """
    
    # Interactive input parameters to set before running 
    Count = 'number of updates'
    input_parameters = {
        Count: IntegerInput(100) 
    }
    
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.logger = self.get_logger(__file__)
        

        self.osc = self.get_instrument('osc') # use the inst name in taskconfig file
        
        # Once you get the figure, the following are about Matplotlib things to plot
        self.figure = self.get_figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-1e-3, 1e-3)
        self.ax.set_ylim(-1, 1)
        self.ax.set_title('Scope waveform Capture')
        self.x_data = [0]
        self.y_data = [0]
        self.line, = self.ax.plot(self.x_data,self.y_data)
        
    def test(self):
        prev_time = time.time()
        for i in range(self.repeat_count):
            if not self.is_running(): # if the Stop button is pressed
                break
            
            # Add data to the Matplotlib line and update the figure
            t, v = self.osc.get_waveform('c1') # Get Ch. 1 waveform
            self.line.set_data(t, v)
            self.request_figure_update()
            
            current_time = time.time()
            diff = current_time - prev_time
            self.logger.info(f'No. {i}, capture time: {diff:.3f} s')
            prev_time = current_time
            
    def cleanup(self):
        pass
        
        