
from datetime import datetime

from rgagui.base.task import Task, round_float
from rgagui.base.inputs import ListInput, IntegerInput
from . import get_rga


class AnalogScanTask(Task):
    """Task ro run analog scans.
    """

    StartMass = 'start mass'
    StopMass = 'stop mass'
    ScanSpeed = 'scan speed'
    StepSize = 'step per AMU'
    IntensityUnit = 'intensity unit'
    Reps = 'Repetition'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        StartMass: IntegerInput(1, " AMU", 0, 319, 1),
        StopMass: IntegerInput(50, " AMU", 1, 320, 1),
        ScanSpeed: IntegerInput(3, " ", 0, 9, 1),
        StepSize: IntegerInput(20, " steps per AMU", 10, 80, 1),
        IntensityUnit: ListInput(['Ion current (fA)', 'Partial Pressure (Torr)']),
        Reps: IntegerInput(100, " scans", 1, 1000000, 1),
    }

    def setup(self):
        self._log_error_detail = False

        # Get values to use for task  from input_parameters in GUI
        self.start_value = self.get_input_parameter(self.StartMass)
        self.stop_value  = self.get_input_parameter(self.StopMass)
        self.speed_value = self.get_input_parameter(self.ScanSpeed)
        self.step_value  = self.get_input_parameter(self.StepSize)
        self.unit_value  = self.get_input_parameter(self.IntensityUnit)
        self.reps_value  = self.get_input_parameter(self.Reps)

        # Get logger to use
        self.logger = self.get_logger(__name__)
        self.logger.info('Start: {} Stop: {} Speed: {} Step: {}'.format(
            self.start_value, self.stop_value, self.speed_value, self.step_value))

        self.data_dict['x'] = []
        self.data_dict['y'] = []

        self.init_plot()
        self.init_scan()

    def init_plot(self):
        # Set up a plot using matplotlib axes
        # self.figure is used to draw on the GUI window.
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.__class__.__name__)
        self.ax.set_xlabel("Mass (AMU)")
        self.ax.set_ylabel('Ion Current(0.1fA)')

        if self.unit_value == 0:
            self.ax.set_ylabel('Ion Current (fA)')
            self.ax.set_ylim(-1000, 100000, auto=False)
        else:
            self.ax.set_ylabel('Partial pressure (Torr)')
            self.ax.set_ylim(-1e-10, 1e-9, auto=False)

        self.line, = self.ax.plot(self.data_dict['x'], self.data_dict['y'])
        self.ax.set_xlim(self.start_value, self.stop_value, auto=False)

    def init_scan(self):
        # Get the instrument to use
        self.rga = get_rga(self)

        self.id_string = self.rga.status.id_string
        emission_current = self.rga.ionizer.emission_current
        cem_voltage = self.rga.cem.voltage

        if self.unit_value == 0:
            self.conversion_factor = 0.1
        else:
            self.conversion_factor = self.rga.pressure.get_partial_pressure_sensitivity_in_torr()

        self.logger.info('Emission current: {:.2f} mA CEM HV: {} V'.format(emission_current, cem_voltage))

        self.rga.scan.set_callbacks(self.update_callback, None, self.update_on_scan_finished)

        self.rga.scan.set_parameters(self.start_value,
                                     self.stop_value,
                                     self.speed_value,
                                     self.step_value)

    # The scan calls this callback whne data is available
    def update_callback(self, index):
        self.data_dict['x'] = self.mass_axis[:index]
        self.data_dict['y'] = self.rga.scan.spectrum[:index] * self.conversion_factor
        self.line.set_xdata(self.data_dict['x'])
        self.line.set_ydata(self.data_dict['y'])

        # Tell GUI to redraw the plot
        self.notify_data_available()

    def update_on_scan_finished(self):
        self.data_dict['x'] = self.mass_axis
        self.data_dict['y'] = self.rga.scan.spectrum * self.conversion_factor
        self.line.set_xdata(self.data_dict['x'])
        self.line.set_ydata(self.data_dict['y'])

        # Tell GUI to redraw the plot
        self.notify_data_available()

    def test(self):
        self.set_task_passed(True)

        number_of_iteration = self.reps_value
        self.add_details('{}'.format(self.id_string), key='ID')

        self.mass_axis = self.rga.scan.get_mass_axis()

        # Create a table in the data file
        self.create_table_in_file('Mass spectra', 'time', *map(round_float, self.mass_axis))

        for i in range(number_of_iteration):
            if not self.is_running():
                break
            try:
                self.rga.scan.get_analog_scan()
                self.logger.debug('scan {} finished'.format(i))

                # write the spectrum in to the data file
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.add_to_table_in_file(timestamp, *self.rga.scan.spectrum)

            except Exception as e:
                self.set_task_passed(False)
                self.logger.error(e)

    def cleanup(self):
        self.logger.info('Task finished')


if __name__ == '__main__':
    import logging
    from rga import RGA120 as Rga
    import matplotlib.pyplot as plt

    logging.basicConfig(level=logging.INFO)

    test = AnalogScanTask()
    test.figure = plt.figure()
    rga = Rga('serial', 'COM3', 115200, True)
    rga.comm.set_callbacks(logging.info, logging.info)
    test.inst_dict = {'dut': rga}

    test.set_input_parameter(test.Reps, 1)
    
    test.start()
    test.wait()
    test.update_on_scan_finished()
    plt.show()

