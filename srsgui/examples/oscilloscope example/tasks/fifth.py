import time
import math
import logging
import numpy as np

from srsgui import Task
from srsgui import IntegerInput

from tasks.fourth import FourthTask


class FifthTask(FourthTask):
    """
It subclasses FourthTask (Display FFT waveform) to use simulated \
waveforms instead of ones from a real oscilloscope. \
By isolating and overriding hardware related codes in separate methods, \
An existing task can be reused.

Note that simple calculation of waveform adds side bands in FFT spectrum \
caused by time qunatization error.

No hardware connection is required to use simulated waveforms. \
    """  
 
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.set_freq = self.get_input_parameter(self.Frequency)
        
        self.logger = self.get_logger(__file__)      
        self.init_plots()

    def get_waveform(self, mode='square'):
        self.set_freq = self.get_input_parameter(self.Frequency)
        
        amplitude = 1.0 # Volt
        noise = 0.01     # Volt
        sara = 1e9  # Sampling rate : 1 GSa/s
        no_of_points = 2 ** 16

        # Calculate time vector
        t = np.linspace(-no_of_points / 2 / sara, no_of_points / 2 / sara, no_of_points)
        
        if mode == 'sine':
            d = amplitude * np.sin(2.0 * np.pi * t * self.set_freq) + noise * np.random.rand(no_of_points)
        else:
            a = t * self.set_freq
            b = a - np.int_(a)
            c = np.where(b <= 0.0, b + 1, b)
            if mode == 'sawtooth':
                d = 2.0 * c - 1.0
            else:  # default is square wave 
                d = np.where(c > 0.5, 1.0, -1.0)
        
        #Add random noise        
        v = amplitude * d + noise * np.random.rand(no_of_points)

        #Take time as if it is a real data acquisition 
        time.sleep(0.1)
        
        return t, v, sara
        
    def set_frequency(self, f):
        pass
