
import numpy
from datetime import datetime

from rgagui.base.task import Task, round_float
from rgagui.base.inputs import ListInput, IntegerInput, InstrumentInput
from rgagui.plots.histogramscanplot import HistogramScanPlot

from instruments.get_instruments import get_rga


class HistogramScanTask(Task):
    """Task ro run histogram scans.
    """

    InstrumentName = 'instrument to control'
    StartMass = 'start mass'
    StopMass = 'stop mass'
    ScanSpeed = 'scan speed'
    IntensityUnit = 'intensity unit'
    Reps = 'Repetition'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        InstrumentName: InstrumentInput(),
        StartMass: IntegerInput(1, " AMU", 0, 319, 1),
        StopMass: IntegerInput(50, " AMU", 1, 320, 1),
        ScanSpeed: IntegerInput(3, " ", 0, 9, 1),
        IntensityUnit: ListInput(['Ion current (fA)', 'Partial Pressure (Torr)']),
        Reps: IntegerInput(100, " scans", 1, 1000000, 1),
    }

    def setup(self):
        self._log_error_detail = False

        # Get values to use for task  from input_parameters in GUI
        self.params = self.get_all_input_parameters()
        # Get logger to use
        self.logger = self.get_logger(__name__)

        self.logger.info('Start: {} Stop: {} Speed: {} '.format(
            self.params[self.StartMass], self.params[self.StopMass],
            self.params[self.ScanSpeed]))

        self.init_scan()

        # Set up an analog scan plot for the test
        self.ax = self.get_figure().add_subplot(111)

        self.plot = HistogramScanPlot(self, self.ax, self.rga.scan, 'Histogram')

        if self.params[self.IntensityUnit] == 0:
            self.conversion_factor = 0.1
            self.plot.set_conversion_factor(self.conversion_factor, 'fA')
        else:
            self.conversion_factor = self.rga.pressure.get_partial_pressure_sensitivity_in_torr()
            self.plot.set_conversion_factor(self.conversion_factor, 'Torr')
        self.logger.debug('Conversion factor: {:.3e}'.format(self.conversion_factor))

    def init_scan(self):
        # Get the instrument to use
        self.rga = get_rga(self, self.params[self.InstrumentName])
        self.id_string = self.rga.status.id_string
        emission_current = self.rga.ionizer.emission_current
        cem_voltage = self.rga.cem.voltage

        self.logger.info('Emission current: {:.2f} mA CEM HV: {} V'.format(emission_current, cem_voltage))
        self.rga.scan.set_parameters(self.params[self.StartMass],
                                     self.params[self.StopMass],
                                     self.params[self.ScanSpeed])
        self.mass_axis = self.rga.scan.get_mass_axis(False)  # Get the mass axis for histogram scan

    def test(self):
        self.set_task_passed(True)

        number_of_iteration = self.params[self.Reps]
        self.add_details('{}'.format(self.rga.status.id_string), key='ID')

        for i in range(number_of_iteration):
            if not self.is_running():
                break
            try:
                self.rga.scan.get_histogram_scan()
                self.logger.debug('scan {} finished'.format(i))

            except Exception as e:
                self.set_task_passed(False)
                self.logger.error('{}: {}'.format(e.__class__.__name__, e))

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

