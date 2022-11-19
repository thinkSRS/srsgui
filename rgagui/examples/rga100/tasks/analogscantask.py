
from datetime import datetime

from rgagui.base.task import Task, round_float
from rgagui.base.inputs import ListInput, IntegerInput, InstrumentInput
from rgagui.plots.analogscanplot import AnalogScanPlot

from instruments.get_instruments import get_rga


class AnalogScanTask(Task):
    """Task to run analog scans.
    """
    InstrumentName = 'instrument to control'
    StartMass = 'start mass'
    StopMass = 'stop mass'
    ScanSpeed = 'scan speed'
    StepSize = 'step per AMU'
    IntensityUnit = 'intensity unit'
    Reps = 'Repetition'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        InstrumentName: InstrumentInput(),
        StartMass: IntegerInput(1, " AMU", 0, 319, 1),
        StopMass: IntegerInput(50, " AMU", 1, 320, 1),
        ScanSpeed: IntegerInput(3, " ", 0, 9, 1),
        StepSize: IntegerInput(20, " steps per AMU", 10, 80, 1),
        IntensityUnit: ListInput(['Ion current (fA)', 'Partial Pressure (Torr)']),
        Reps: IntegerInput(100, " scans", 1, 1000000, 1),
    }

    def setup(self):
        # if True, detailed traceback info, when an exception happens
        self._log_error_detail = False

        # Get values to use for task  from input_parameters in GUI
        self.params = self.get_all_input_parameters()

        # Get logger to use
        self.logger = self.get_logger(__name__)
        self.logger.info('Start: {} Stop: {} Speed: {} Step: {}'.format(
            self.params[self.StartMass], self.params[self.StopMass],
            self.params[self.ScanSpeed], self.params[self.StepSize]))

        self.init_scan()

        # Set up an analog scan plot for the test
        self.ax = self.get_figure().add_subplot(111)
        self.plot = AnalogScanPlot(self, self.ax, self.rga.scan, 'Analog Scan')

        if self.params[self.IntensityUnit] == 0:
            self.conversion_factor = 0.1
            self.plot.set_conversion_factor(self.conversion_factor, 'fA')
        else:
            self.conversion_factor = self.rga.pressure.get_partial_pressure_sensitivity_in_torr()
            self.plot.set_conversion_factor(self.conversion_factor, 'Torr')

    def init_scan(self):
        # Get the instrument to use
        self.rga = get_rga(self, self.params[self.InstrumentName])
        self.id_string = self.rga.status.id_string
        emission_current = self.rga.ionizer.emission_current
        cem_voltage = self.rga.cem.voltage

        self.logger.info('Emission current: {:.2f} mA CEM HV: {} V'.format(emission_current, cem_voltage))
        self.rga.scan.set_parameters(self.params[self.StartMass],
                                     self.params[self.StopMass],
                                     self.params[self.ScanSpeed],
                                     self.params[self.StepSize])

    def test(self):
        self.set_task_passed(True)

        number_of_iteration = self.params[self.Reps]
        self.add_details('{}'.format(self.id_string), key='ID')

        self.mass_axis = self.rga.scan.get_mass_axis()

        for i in range(number_of_iteration):
            if not self.is_running():
                break
            try:
                self.rga.scan.get_analog_scan()
                self.logger.debug('scan {} finished'.format(i))

            except Exception as e:
                self.set_task_passed(False)
                self.logger.error(e)

    def cleanup(self):
        self.logger.info('Task finished')
        self.plot.cleanup() # Detach callback functions


if __name__ == '__main__':
    import logging
    from rga import RGA120 as Rga
    import matplotlib.pyplot as plt

    logging.basicConfig(level=logging.INFO)

    task = AnalogScanTask()

    rga = Rga('serial', 'COM3', 115200, True)
    rga.comm.set_callbacks(logging.info, logging.info)
    task.inst_dict = {'dut': rga}

    task.figure = plt.figure()
    task.figure_dict = {'plot': task.figure}

    task.set_input_parameter(task.Reps, 1)
    task.set_input_parameter(task.InstrumentName, 'dut')

    task.start()
    task.wait()
    plt.show()

