import time
import math
import logging
import numpy as np

from srsgui import Task
from srsgui import IntegerInput


class FourthTask(Task):
    """
    This is the second task using srsgui 
    """
    
    # Interactive input parameters to set before running 
    Count = 'number of updates'
    input_parameters = {
        Count: IntegerInput(100) 
    }
    FFTPlot = 'FFT plot'
    additional_figure_names = [FFTPlot]
    
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.logger = self.get_logger(__file__)
        
        self.osc = self.get_instrument('osc') # use the inst name in taskconfig file
        
        # Once you get the figure, the following are about Matplotlib things to plot
        self.figure = self.get_figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-1e-6, 1e-6)
        self.ax.set_ylim(-1, 1)
        self.ax.set_title('Clock waveform')
        self.x_data = [0]
        self.y_data = [0]
        self.line, = self.ax.plot(self.x_data,self.y_data)
        
        # Get the second figure for FFT plot.
        self.fft_fig = self.get_figure(self.FFTPlot)
        self.fft_ax = self.fft_fig.add_subplot(111)
        self.fft_ax.set_xlim(0, 2e8)
        self.fft_ax.set_ylim(1e-1, 1e9)
        self.fft_ax.set_title('FFT spectum')
        self.fft_x_data = [0]
        self.fft_y_data = [1]
        self.fft_ax.set_yscale('log')        
        self.fft_line, = self.fft_ax.plot(self.fft_x_data,self.fft_y_data)        
        
    def test(self):
        prev_time = time.time()
        for i in range(self.repeat_count):
            if not self.is_running(): # if the Stop button is pressed
                break
            
            # Add data to the Matplotlib line and update the figure
            t, v = self.osc.get_waveform('c1') # Get Ch. 1 waveform
            self.line.set_data(t, v)
            self.request_figure_update()

            for k in range(20):
                size = 2 ** k
                if size > len(v):
                    break
            size = size // 2
            
            x = np.linspace(0, 5e8, size//2 + 1)
            # x = np.arange(size/2 + 1)
            y = np.fft.rfft(v[:size])
            self.fft_line.set_data(x, y * np.conjugate(y) )
            self.request_figure_update(self.fft_fig) 
            
            current_time = time.time()
            diff = current_time - prev_time
            self.logger.info(f'Capture No. {i}, time: {diff:.3f} s')
            prev_time = current_time
            
    def cleanup(self):
        pass
        
        