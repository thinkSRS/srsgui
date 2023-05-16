##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

import time
from srsgui import Task
from srsgui import IntegerInput


class ThirdTask(Task):
    """
It captures waveforms from an oscilloscope, \
and plot the waveforms real time.
    """
    
    # Use input_parameters to set parameters before running 
    Count = 'number of captures'
    input_parameters = {
        Count: IntegerInput(100) 
    }
    
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.logger = self.get_logger(__file__)        

        self.osc = self.get_instrument('osc') # use the inst name in taskconfig file
        
        # Get the Matplotlib figure to plot in
        self.figure = self.get_figure()

        # Once you get the figure, the following are about Matplotlib things to plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-1e-5, 1e-5)
        self.ax.set_ylim(-1.5, 1.5)
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
            t, v = self.osc.get_waveform('C1')  # Get a waveform of the Channel 1 from the oscilloscope
            self.line.set_data(t, v)
            self.request_figure_update()
            
            # Calculate the time for each capture
            current_time = time.time()
            diff = current_time - prev_time
            self.logger.info(f'Capture time for {len(v)} points of waveform {i}: {diff:.3f} s')
            prev_time = current_time
            
    def cleanup(self):
        pass
