import time
import math
import logging
import numpy as np

from srsgui import Task
from srsgui import IntegerInput

from tasks.fourth import FourthTask

try:
    #Use SciPy signal library if available
    from scipy import signal
except:
    SCIPY_IMPORTED = False
else:
    SCIPY_IMPORTED = True

class FifthTask(FourthTask):
    """
It subclasses FourthTask (Display FFT waveform) to use simulated \
waveforms instead of ones from a real oscilloscope. \
By isolating and overriding hardware related codes in separate methods, \
the existing task can be reused.

Note that simply calculated square waveform adds modulated side bands \
in FFT spectrum caused by time quantization error.

No hardware connection is required to use simulated waveforms. \
    """  
 
    def setup(self):
        self.repeat_count = self.get_input_parameter(self.Count)
        self.set_freq = self.get_input_parameter(self.Frequency)

        if SCIPY_IMPORTED:
            # Butterworth filter to simulate 200 MHz bandwith of the oscilloscope 
            self.sos = signal.butter(2, 2e8, 'low', fs = 1e9, output='sos')

        self.logger = self.get_logger(__file__)      
        self.init_plots()

    def get_waveform(self, mode='square'):
        self.set_freq = self.get_input_parameter(self.Frequency)
        
        amplitude = 1.0 # Volt
        noise = 0.02     # Volt
        sara = 1e9  # Sampling rate : 1 GSa/s
        no_of_points = 2 ** 16

        # Calculate time vector
        t = np.linspace(-no_of_points / 2 / sara, no_of_points / 2 / sara, no_of_points)

        if mode == 'sine':
            d = np.sin(2.0 * np.pi * self.set_freq * t)
        else:
            a = self.set_freq * t
            b = a - np.int_(a)
            c = np.where(b <= 0.0, b + 1, b)
            if mode == 'sawtooth':
                d = 2.0 * c - 1.0
            else:  # default is square wave 
                d = np.where(c > 0.5, 1.0, -1.0)

        if SCIPY_IMPORTED:
            # Apply 200 MHz low pass fiilter
            d = signal.sosfilt(self.sos, d)
        
        # Add random noise
        v = amplitude * d + noise * np.random.rand(no_of_points)

        # Take time as if it is a real data acquisition
        time.sleep(0.05)
        
        return t, v, sara
        
    def set_frequency(self, f):
        pass
