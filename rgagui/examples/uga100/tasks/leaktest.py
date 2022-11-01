import sys
import os
import time
import math
import numpy as np

from rgagui.base.task import Task, round_float
from rgagui.base.inputs import FloatInput, IntegerInput, StringInput
import logging

from instruments.inst_http import InstHttpMixin
from instruments.igc100    import Igc100

# define matplotlib level before importing to supress debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt

from srs_insts.rga import Rga


class IgcMixin(InstHttpMixin, Igc100):
    pass


class LeakTest(Task):
    """<b>Test to measure CEM gain at different CEM HV<br> \

    """
    Mass = 'mass'
    ScanSpeed = 'scan speed'
    RunTime = 'stop after'

    Notes = 'notes'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        Mass: IntegerInput(28, 'AMU', 1, 320, 1),
        ScanSpeed: IntegerInput(5, '', 1, 10, 1),
        RunTime: IntegerInput(600, " s", 1, 86400, 10),
        Notes: StringInput('')
    }

    def setup(self):
        self.logger = self.get_logger(__name__)

        self.data_dict['t'] = []
        self.data_dict['ig'] = []
        self.data_dict['pg'] = []
        self.data_dict['fp'] = []
        
        # Get value to use for test from input_parameters
        self.mass = self.input_parameters[self.Mass].value
        self.scan_speed = self.input_parameters[self.ScanSpeed].value
        self.run_time_value = self.input_parameters[self.RunTime].value
        self.notes_value = self.input_parameters[self.Notes].value

        self.logger.info("Notes: {} ".format(self.notes_value))

        self.ax1 = self.figure.add_subplot(111)
        self.ax1.set_title('IG pressure')
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel('IG pressure (Torr)')

        self.line1, = self.ax1.plot(self.data_dict['t'], self.data_dict['ig'])
        self.line2, = self.ax1.plot(self.data_dict['t'], self.data_dict['fp'])
        self.line3, = self.ax1.plot(self.data_dict['t'], self.data_dict['pg'])        
        
        self.ax1.set_xlim(0, 100, auto=False)
        self.ax1.set_ylim(1e-9, 1e-5, auto=False)
        self.ax1.set_yscale('log')

        self.rga = self.get_rga()

        # self.igc = self.get_instrument('igc')
        self.igc = IgcMixin()
        self.igc.set_url(os.environ.get("IGCURL"), 'igc')
        self.igc.set_auth(os.environ.get("IGCUSER"), os.environ.get("IGCPASS"))

        #self.logger.info(self.igc.query_text('*IDN?'))

    def get_mass_intensity(self, mass):
        return self.rga.scan.get_single_mass_scan(mass)        
        
    def test(self):
        table_name = 'Pressure vs. time'
        first_column_name = 'Time (s)'
        second_column_name = 'IG (Torr)'
        third_column_name = 'FP (Torr)'
        forth_column_name = 'PG (Torr)'
        
        self.create_table(table_name, first_column_name, second_column_name, third_column_name, forth_column_name)

        start_time = time.time()
        elapsed_time = 0
        self.set_task_passed(True)
        sp = self.rga.query_float('sp?')
        tp = self.rga.query_float('st?')
        while elapsed_time < self.run_time_value:
            try:
                if not self.is_running():
                    break

                elapsed_time = time.time() - start_time
                ig_pressure = self.igc.get_ig_pressure()
                total_pressure = self.rga.query_float('elec:pressure:reading?')  # in 0.1fA *
                tp = self.rga.query_float('PRESSURE:SENS:TOTAL?')
                sp = self.rga.query_float('PRESSURE:SENS:PARTIAL?')
                total_pressure *= 1e-13 / tp  # in Torr (default:1e-16A / 1e-3A/Torr)
                partial_pressure = self.get_mass_intensity(self.mass) * 1e-13 / sp

                self.add_data_to_table(
                    table_name, round(elapsed_time, 1),
                    round_float(ig_pressure), round_float(total_pressure), round_float(partial_pressure))

                self.data_dict['t'].append(elapsed_time)
                self.data_dict['ig'].append(ig_pressure)
                self.data_dict['fp'].append(total_pressure)
                self.data_dict['pg'].append(partial_pressure)
                self.notify_data_available(self.data_dict)
            except Exception as e:
                self.logger.error(e)
                self.set_task_passed(False)
                break

        self.add_details('IG: {:.3e} Torr'.format(ig_pressure))

    def update(self, data_dict):
        try:
            if data_dict['t'] == []:
                self.line1, = self.ax1.plot([], [])
                self.line3, = self.ax1.plot([], [])
            else:
                self.line1.set_xdata(data_dict['t'])
                self.line1.set_ydata(data_dict['ig'])

                self.line2.set_xdata(data_dict['t'])
                self.line2.set_ydata(data_dict['fp'])

                self.line3.set_xdata(data_dict['t'])
                self.line3.set_ydata(data_dict['pg'])
                
            self.figure.canvas.draw_idle()

        except Exception as e:
            self.logger.error('update error: {}'.format(e))

    def cleanup(self):
        self.logger.info('Test cleaned up')


if __name__ == '__main__':
    from srs_insts.rga import Rga

    class Parent:
        def __init__(self):
            self.inst_dict = {'dut': Rga('tcpip', '172.25.128.14', 'srsuga', 'srsuga')}
            self.figure = plt.figure()

    logging.basicConfig()
    parent = Parent()
    test = IgcPressureMonitorTest(parent)
    test.start()
    test.wait()
    test.update(test.data_dict)
    plt.show()

