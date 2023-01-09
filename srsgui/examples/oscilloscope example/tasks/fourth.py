import time
import math
import logging
import numpy as np

from srsgui import Task
from srsgui import IntegerInput


class FourthTask(Task):
    """
Set the frequency of clock generator output.
Get waveformss from the oscilloscope.
Calculate FFT of the waveform.
Plot the waveforms and repeat.  
    """
    
    # Interactive input parameters to set before running 
    Frequency = 'Frequency to set'
    Count = 'number of updates'
    input_parameters = {
        Frequency: IntegerInput(10000000, ' Hz', 100000, 100000000, 1000),
        Count: IntegerInput(10000)
    }
    
    # Add another figure for more plots
    FFTPlot = 'FFT plot'
    additional_figure_names = [FFTPlot]
    
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        
        self.logger = self.get_logger(__file__)
        
        self.osc = self.get_instrument('osc') # use the inst name in taskconfig file
        
        self.cg = self.get_instrument('cg')
        self.freq = self.cg.frequency  # Query frequency from cg
        
        self.init_plots()
        
    def test(self):
        prev_time = time.time()
        for i in range(self.repeat_count):
            if not self.is_running(): # if the Stop button is pressed
                break
                
            # Check if the user changed the set_frequency 
            set_freq = self.input_parameters[self.Frequency]
            if set_freq != self.freq:
                self.set_frequency(set_freq)
                self. freq = set_freq
                self.logger.info(f'Frequency changed to {self.freq}')
                time.sleep(0.01)
                
            # Add data to the Matplotlib line and update the figure
            t, v, sara = self.get_waveform()
            
            self.line.set_data(t, v)
            self.request_figure_update()

            # Calculate FFT with the waveform
            size = 2 ** int(np.log2(len(v)))  # largest power of 2 <= waveform length
            y = np.fft.rfft(v, size)
            x = np.linspace(0, sara /2, len(y))            
            self.fft_line.set_data(x, abs(y) / len(y))
            self.request_figure_update(self.fft_fig) 
            
            # Calculate time for each capture
            current_time = time.time()
            diff = current_time - prev_time
            self.logger.info(f'Time taken for waveform No. {i}: {diff:.3f} s')
            prev_time = current_time
            
    def cleanup(self):
        pass
        
    def init_plots(self):
        # Once you get the figure, the following are about Matplotlib things to plot
        self.figure = self.get_figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-1e-6, 1e-6)
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.set_title('Clock waveform')
        self.ax.set_xlabel('time (s)')
        self.ax.set_ylabel('Voltage (V)')
        self.x_data = [0]
        self.y_data = [0]
        self.line, = self.ax.plot(self.x_data,self.y_data)
        
        # Get the second figure for FFT plot.
        self.fft_fig = self.get_figure(self.FFTPlot)
        
        self.fft_ax = self.fft_fig.add_subplot(111)
        self.fft_ax.set_xlim(0, 2e8)
        self.fft_ax.set_ylim(1e-1, 1e9)
        self.fft_ax.set_title('FFT spectum')
        self.fft_ax.set_xlabel('time (s)')
        self.fft_ax.set_ylabel('Voltage (V)')        
        self.fft_x_data = [0]
        self.fft_y_data = [1]     
        self.fft_line, = self.fft_ax.semilogy(self.fft_x_data,self.fft_y_data)        
    
    def get_waveform(self):
        t, v = self.osc.get_waveform('c1') # Get Ch. 1 waveform
        sara = self.osc.get_sampling_rate()
        return t, v, sara
        
    def set_frequency(self, f):
        self.cg.frequency = f
