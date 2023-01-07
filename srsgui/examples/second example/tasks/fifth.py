import time
import math
import logging
import numpy as np

from srsgui import Task
from srsgui import IntegerInput, FloatInput


class FifthTask(Task):
    """
    This is the second task using srsgui 
    """
    
    # Interactive input parameters to set before running 
    Count = 'number of updates'
    Start = 'start freq.'
    Stop = 'stop freq.'
    Factor = 'Change factor'
    input_parameters = {
        Start: FloatInput(1000000, ' Hz', 1000, 100000000),
        Stop: FloatInput(10000000, ' Hz', 1000, 100000000),
        Factor: FloatInput(1.01, '', 0.01, 100, 0.001),
        Count: IntegerInput(1000) 
    }
    
    FFTPlot = 'FFT plot'
    FrequencyPlot = 'Frequency plot'
    additional_figure_names = [FFTPlot, FrequencyPlot]
    
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.start_frequency = self.get_input_parameter(self.Start)
        self.stop_frequency = self.get_input_parameter(self.Stop)
        self.change_factor = self.get_input_parameter(self.Factor)
        self.logger.info('{} {} {}'.format(
            self.start_frequency, self.stop_frequency,self.change_factor))
            
        self.logger = self.get_logger(__file__)
        
        self.cg = self.get_instrument('cg') # use the inst name in taskconfig file
        self.osc = self.get_instrument('osc') 
        
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

        # Get the third plot for frequency difference
        self.freq_fig = self.get_figure(self.FrequencyPlot)
        self.freq_ax = self.freq_fig.add_subplot(111)
        self.freq_ax.set_xlim(1e3, 1e8)
        self.freq_ax.set_ylim(-1e3, 1e3)
        self.freq_ax.set_title('Set Freq. - FFT peak freq.')
        self.freq_x_data = [self.start_frequency]
        self.freq_y_data = [0]
        #self.fft_ax.set_xscale('log')        
        self.freq_line, = self.freq_ax.plot(self.freq_x_data,self.freq_y_data)
        
    def test(self):
        prev_time = time.time()
        self.cg.frequency = self.start_frequency
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
            
            print(f'\n {len(v)} {np.argmax(y)}')
            
            self.freq_x_data.append(self.cg.frequency)
            self.freq_y_data.append(self.cg.frequency - x[np.argmax(y)//2 +1])
            self.freq_line.set_data(self.freq_x_data, self.freq_y_data)
            self.request_figure_update(self.freq_fig) 
            # self.cg.set_frequency(self.cg.frequency * self.change_factor)
            self.cg.frequency = self.cg.frequency * self.change_factor
            print(self.cg.frequency)
            if self.cg.frequency > self.stop_frequency:
                break
                
            current_time = time.time()
            diff = current_time - prev_time
            self.logger.info(f'Capture No. {i}, time: {diff:.3f} s')
            prev_time = current_time
            # time.sleep(0.01)
            
            
    def cleanup(self):
        pass
        
        