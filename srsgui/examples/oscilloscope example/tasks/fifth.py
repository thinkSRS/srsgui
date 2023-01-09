import time
import math
import logging
import numpy as np

from srsgui import Task
from srsgui import IntegerInput

from tasks.fourth import FourthTask

class FifthTask(FourthTask):
    """
No hardware required to use simulated waveforms.
It subclasses FourthTask (Display FFT waveform) to use simulated \
waveforms instead of ones from a real oscilloscope.
By isolating hardware related parts in separate methods, \
it is easy to reuse an existing task.    
    """  
 
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.freq = self.get_input_parameter(self.Frequency)
        
        self.logger = self.get_logger(__file__)      
        self.init_plots()
        
    def get_waveform(self, mode='square'):
        freq = self.get_input_parameter(self.Frequency)
        
        amplitude = 1.0 # Volt
        noise = 0.1     # Volt
        ma_points = 10  # points for moving average 
        sara = 1e9  # Sampling rate : 1 GHz
        no_of_points = 2 ** 15

        # Calculate time vector
        t = np.linspace(-no_of_points / 2 / sara, no_of_points / 2 / sara, no_of_points)
        
        if mode == 'sine':
            v = amplitude * np.sin(2.0 * np.pi * t * freq) + noise * np.random.rand(no_of_points)
        else:
            a = t * freq
            b = a - np.int_(a)
            c = np.where(b <= 0.0, b + 1, b)
            if mode == 'sawtooth':
                d = 2.0 * c - 1.0
            else:  # default is square wave 
                d = np.where(c > 0.5, 1.0, -1.0)
        
        #Add linear convolution and random noise
        e = np.convolve(d, np.ones(ma_points)/ ma_points, 'same')
        v = amplitude * e + noise * np.random.rand(no_of_points)

        #Take time as if it is a real data acquisition 
        time.sleep(0.1)
        
        return t, v, sara
        
    def set_frequency(self, f):
        pass
