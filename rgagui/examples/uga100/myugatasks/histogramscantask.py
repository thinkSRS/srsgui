
import numpy
from datetime import datetime

from rgagui.basetask.task import Task, round_float
from rgagui.basetask.inputs import ListInput, IntegerInput
from . import get_rga

class HistogramScanTask(Task):
    """Task ro run histogram scans.
    """

    StartMass = 'start mass'
    StopMass = 'stop mass'
    ScanSpeed = 'scan speed'
    IntensityUnit = 'intensity unit'
    Reps = 'Repetition'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        StartMass: IntegerInput(1, " AMU", 0, 319, 1),
        StopMass: IntegerInput(50, " AMU", 1, 320, 1),
        ScanSpeed: IntegerInput(3, " ", 0, 9, 1),
        IntensityUnit: ListInput(['Ion current (fA)', 'Partial Pressure (Torr)']),
        Reps: IntegerInput(100, " scans", 1, 1000000, 1),
    }

    def setup(self):
        self._log_error_detail = False

        # Get values to use for task  from input_parameters in GUI
        self.start_value = self.get_input_parameter(self.StartMass)
        self.stop_value  = self.get_input_parameter(self.StopMass)
        self.speed_value = self.get_input_parameter(self.ScanSpeed)
        self.unit_value  = self.get_input_parameter(self.IntensityUnit)
        self.reps_value  = self.get_input_parameter(self.Reps)

        # Get logger to use
        self.logger = self.get_logger(__name__)
        self.logger.info('Start: {} Stop: {} Speed: {}'.format(
            self.start_value, self.stop_value, self.speed_value))

        self.init_scan()

        self.data_dict['x'] = self.mass_axis
        self.data_dict['y'] = numpy.zeros_like(self.mass_axis)
        self.init_plot()

    def init_scan(self):
        # Get the instrument to use
        self.rga = get_rga(self)
        print(self.rga.status.id_string)

        if self.unit_value == 0:
            self.conversion_factor = 0.1
        else:
            self.conversion_factor = self.rga.pressure.get_partial_pressure_sensitivity_in_torr()

        self.logger.debug('Conversion factor: {:.3e}'.format(self.conversion_factor))
        self.logger.info('Emission current: {:.2f} mA CEM HV: {} V'
                         .format(self.rga.ionizer.emission_current, self.rga.cem.voltage))

        self.rga.scan.set_callbacks(self.update_callback, self.scan_started_callback, None)

        self.rga.scan.set_parameters(self.start_value,
                                     self.stop_value,
                                     self.speed_value)
        self.mass_axis = self.rga.scan.get_mass_axis(False)  # Get the mass axis for histogram scan

    def scan_started_callback(self):
        self.last_index = 0

        # Initialize the rectangles in the bar plot when a scan started
        for rect in self.rects:
            rect.set_height(0)

        # Tell GUI to redraw the plot
        self.notify_data_available()

    # The scan calls this callback when data is available
    def update_callback(self, index):
        i = self.last_index
        while i <= index:
            # Update rectangles for new data
            self.rects[i].set_height(self.rga.scan.spectrum[i] * self.conversion_factor)
            i += 1

        self.last_index = index
        self.notify_data_available()

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

        self.rects = self.ax.bar(self.data_dict['x'], self.data_dict['y'])
        self.ax.set_xlim(self.start_value, self.stop_value, auto=False)

    def test(self):
        self.set_task_passed(True)

        number_of_iteration = self.reps_value
        self.add_details('{}'.format(self.rga.status.id_string), key='ID')

        # Create a table in the data file
        self.create_table_in_file('Mass spectra', 'time', *map(round_float, self.mass_axis))

        for i in range(number_of_iteration):
            if not self.is_running():
                break
            try:
                self.rga.scan.get_histogram_scan()
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

    test = HistogramScanTask()
    test.figure = plt.figure()
    rga = Rga('serial', 'COM3', 115200, True)
    rga.comm.set_callbacks(logging.info, logging.info)
    test.inst_dict = {'dut': rga}

    test.set_input_parameter(test.Reps, 1)
    
    test.start()
    test.wait()
    test.update_on_scan_finished()
    plt.show()

