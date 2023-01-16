import time
import math
import logging
import numpy as np
from srsgui import Task
from srsgui import IntegerInput


class FourthTask(Task):
    """
Change the frequency of the clock generator output interactively, \
capture waveforms from the oscilloscope, \
calculate FFT of the waveforms, \
plot the waveforms and repeat until the stop button pressed.  
    """

    # Interactive input parameters to set before running 
    Frequency = 'Frequency to set'
    Count = 'number of runs'
    input_parameters = {
        Frequency: IntegerInput(10000000, ' Hz', 100000, 200000000, 1000),
        Count: IntegerInput(10000)
    }

    # Add another figure for more plots
    FFTPlot = 'FFT plot'
    additional_figure_names = [FFTPlot]

    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.set_freq = self.input_parameters[self.Frequency]

        self.logger = self.get_logger(__file__)
        
        self.osc = self.get_instrument('osc') # use the inst name in taskconfig file
        
        self.cg = self.get_instrument('cg')
        self.cg.frequency = self.set_freq  # Set cg frequency
        
        self.init_plots()
        
    def test(self):
        prev_time = time.time()
        for i in range(self.repeat_count):
            if not self.is_running(): # if the Stop button is pressed
                break
                
            # Check if the user changed the set_frequency 
            freq = self.get_input_parameter(self.Frequency)
            if self.set_freq != freq:
                self.set_frequency(freq)
                self.logger.info(f'Frequency changed to {freq} Hz')
                self.set_freq = freq
                
            # Get a waveform from the oscillscope and update the plot 
            t, v, sara = self.get_waveform()
            self.line.set_data(t, v)
            self.request_figure_update()

            # Calculate FFT with the waveform and update the plot
            size = 2 ** int(np.log2(len(v)))  # largest power of 2 <= waveform length

            window = np.hanning(size)  # get a FFT window
            y = np.fft.rfft(v[:size] * window)
            x = np.linspace(0, sara /2, len(y))
            self.fft_line.set_data(x, abs(y) / len(y))

            self.request_figure_update(self.fft_fig) 

            # Calculate time for each capture
            current_time = time.time()
            diff = current_time - prev_time
            print(f'Waveform no. {i}, {len(v)} points, time taken: {diff:.3f} s')
            prev_time = current_time
            
    def cleanup(self):
        pass
        
    def init_plots(self):
        # Once you get the figure, the following are about Matplotlib things to plot
        self.figure = self.get_figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-1e-6, 1e-6)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_title('Clock waveform')
        self.ax.set_xlabel('time (s)')
        self.ax.set_ylabel('Amplitude (V)')
        self.x_data = [0]
        self.y_data = [0]
        self.line, = self.ax.plot(self.x_data,self.y_data)

        # Get the second figure for FFT plot.
        self.fft_fig = self.get_figure(self.FFTPlot)

        self.fft_ax = self.fft_fig.add_subplot(111)
        self.fft_ax.set_xlim(0, 1e8)
        self.fft_ax.set_ylim(1e-5, 1e1)
        self.fft_ax.set_title('FFT spectum')
        self.fft_ax.set_xlabel('Frequency (Hz)')
        self.fft_ax.set_ylabel('Magnitude (V)')
        self.fft_x_data = [0]
        self.fft_y_data = [1]     
        self.fft_line, = self.fft_ax.semilogy(self.fft_x_data,self.fft_y_data)        

    def get_waveform(self):
        t, v = self.osc.get_waveform('c1') # Get Ch. 1 waveform
        sara = self.osc.get_sampling_rate()
        return t, v, sara
        
    def set_frequency(self, f):
        self.cg.frequency = f
