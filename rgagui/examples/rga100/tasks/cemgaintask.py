import sys
import math
import time
import math
import numpy as np

from rgagui.base.task import Task
from rgagui.base.inputs import FloatInput, IntegerInput, StringInput
from . import get_rga


class CEMGainTask(Task):
    """<b>Test to measure CEM gain at different CEM HV<br> \

    """
    GainToSet = 'gain to set'
    MassToMeasure = 'mass to measure'
    StartVoltage = 'start cem voltage'
    StopVoltage = 'stop cem voltage'
    StepVoltage = 'step size'
    ScanSpeed = 'scan speed'

    WaitTime = 'wait time'
    Notes = 'notes'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        GainToSet: IntegerInput(1000, " ", 100, 1000000, 100),
        MassToMeasure: IntegerInput(28, " AMU", 1, 320, 1),
        ScanSpeed: IntegerInput(3, " ", 0, 7, 1),
        WaitTime: IntegerInput(2, " s", 1, 100, 1),
    }

    def setup(self):
        self.logger = self.get_logger(__name__)

        self.data_dict['x'] = []
        self.data_dict['y'] = []

        self.data_dict['t'] = []  # time
        self.data_dict['i'] = []  # intensity

        # Get value to use for test from input_parameters
        self.gain_to_set_value = self.get_input_parameter(self.GainToSet)
        self.mass_to_measure_value = self.get_input_parameter(self.MassToMeasure)
        self.start_voltage_value = 800
        self.stop_voltage_value = 2000
        self.step_voltage_value = 160
        self.speed_value = self.get_input_parameter(self.ScanSpeed)
        self.wait_time_value = self.get_input_parameter(self.WaitTime)

        # initialize Plot
        self.ax1 = self.figure.add_subplot(121)
        self.ax1.set_title(self.__class__.__name__)
        self.ax1.set_xlabel("CEM HV (V)")
        self.ax1.set_ylabel('Gain')

        self.line1, = self.ax1.plot(self.data_dict['x'], self.data_dict['y'])
        self.ax1.set_xlim(self.start_voltage_value, self.stop_voltage_value, auto=False)
        self.ax1.set_ylim(1, 100000, auto=False)
        self.ax1.set_yscale('log')

        self.ax2 = self.figure.add_subplot(122)
        self.ax2.set_title('Ion current measurement')
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel('Intensity (0.1fA)')
        self.line2, = self.ax2.plot(self.data_dict['t'], self.data_dict['i'])
        self.ax2.set_xlim(0, 5)
        self.ax2.set_ylim(10, 1e9)
        self.ax2.set_yscale('log')

        # Initialize RGA
        self.rga = get_rga(self)
        print(self.rga.status.id_string)
        self.id_string = self.rga.status.id_string
        self.old_speed = self.rga.scan.speed
        self.old_hv = self.rga.cem.voltage


    def test(self):
        self.rga.scan.speed = self.speed_value
        self.rga.cem.voltage = 0

        rep = 4
        minimum_intensity = 200.0  # fA
        total = self.measure_intensity()
        saved_wait_time = self.wait_time_value
        self.wait_time_value = 0.0

        for i in range(rep):
            total += self.measure_intensity()
        fc_intensity = total / (rep + 1)

        if fc_intensity < minimum_intensity:  # if smaller than minimum_intensity 
            raise ValueError('FC reading {:.2f} is smaller than {} fA. Need more intensity to calibrate'.format(
                fc_intensity, minimum_intensity))

        self.logger.info('FC reading is {} fA at {} AMU and NF= {}'.format(
            fc_intensity, self.mass_to_measure_value, self.speed_value
        ))
        self.wait_time_value = saved_wait_time

        current_voltage = self.start_voltage_value
        gain = 0

        table_name = 'Gain vs. HV'
        self.create_table(table_name, 'CEM HV (V)', 'Gain')
        while (current_voltage <= self.stop_voltage_value) and \
              (gain < self.gain_to_set_value):
            if not self.is_running():
                break
            start_time = time.time()
            elapsed_time = 0
            self.data_dict['t'] = []
            self.data_dict['i'] = []
            self.notify_data_available(self.data_dict)

            self.rga.cem.voltage = current_voltage

            while elapsed_time <= self.wait_time_value:
                elapsed_time = time.time() - start_time
                intensity = self.rga.scan.get_single_mass_scan(self.mass_to_measure_value) / 10.0
                self.data_dict['t'].append(elapsed_time)
                self.data_dict['i'].append(intensity)
                self.notify_data_available(self.data_dict)

            gain = self.data_dict['i'][-1] / fc_intensity
            self.data_dict['x'].append(current_voltage)
            self.data_dict['y'].append(gain)

            self.notify_data_available(self.data_dict)

            gain_ratio = self.gain_to_set_value / gain

            if gain_ratio > 20 or gain < 0:
                voltage_ratio = 1.16
            elif gain_ratio > 5:
                voltage_ratio = 1.08
            elif gain_ratio > 2.5:
                voltage_ratio = 1.04
            else:
                voltage_ratio = 1.02

            self.add_data_to_table(table_name, round(current_voltage, 0), round(gain, 1))
            self.logger.info(f'CEM voltage: {current_voltage} Gain: {gain:.1f} Gain ratio: {gain_ratio:.1f}')
            current_voltage = int(current_voltage * voltage_ratio)

        log_gain = math.log10(self.gain_to_set_value)
        self.data_dict['log_y'] = [math.log10(a) if a > 0 else 0.001 for a in self.data_dict['y']]
        hv_to_set = int(np.interp(log_gain, self.data_dict['log_y'], self.data_dict['x']))
        self.logger.info(f'HV for gain {self.gain_to_set_value} : {hv_to_set:.0f}')

        measured_gain = self.measure_gain_at_voltage(hv_to_set)
        self.logger.info(f'Measured gain at HV {hv_to_set:.0f} V : {measured_gain:.0f}')

        error = abs(measured_gain - self.gain_to_set_value) / self.gain_to_set_value
        if error <= 0.10:
            self.rga.cem.voltage = hv_to_set
            self.rga.cem.stored_gain = round(measured_gain, 1)
            self.set_task_passed(True)
            self.add_details(f'Gain at {hv_to_set:.0f} V : {measured_gain:.0f}')
        else:
            self.set_task_passed(False)

    def update(self, data_dict):
        try:
            if data_dict['t'] == []:
                self.line2, = self.ax2.plot([], [])
            else:
                self.line1.set_xdata(data_dict['x'])
                self.line1.set_ydata(data_dict['y'])

                self.line2.set_xdata(data_dict['t'])
                self.line2.set_ydata(data_dict['i'])
            self.figure.canvas.draw_idle()

        except Exception as e:
            self.logger.error('update error: {}'.format(e))

    def cleanup(self):
        self.rga.scan.speed = self.old_speed
        self.rga.cem.voltage = self.old_hv
        self.rga.query_int('HV0')
        self.logger.info('Cleaned up')

    def measure_gain_at_voltage(self, voltage):
        self.rga.cem.voltage = 0
        time.sleep(2.0)
        fc_intensity = self.measure_intensity()
        self.rga.cem.voltage = voltage
        time.sleep(2.0)
        cem_intensity = self.measure_intensity()
        return cem_intensity / fc_intensity

    def measure_intensity(self):
        start_time = time.time()
        elapsed_time = 0
        while elapsed_time <= self.wait_time_value:
            elapsed_time = time.time() - start_time
            intensity = self.rga.scan.get_single_mass_scan(self.mass_to_measure_value) / 10.0
        return intensity


if __name__ == '__main__':
    import logging
    from rga import RGA120 as Rga
    import matplotlib.pyplot as plt

    logging.basicConfig(level=logging.DEBUG)
    
    test = CEMGainTask()
    test.figure = plt.figure()
    test.inst_dict = {'dut': Rga('tcpip', '172.25.70.181', 'admin', 'admin')}
    test.set_input_parameter(test.GainToSet, 500)
    
    test.start()
    test.wait()
    test.update(test.data_dict)
    plt.show()

