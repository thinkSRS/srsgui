
from rgagui.basetask.task import Task
from rgagui.basetask.inputs import FloatInput, InstrumentInput
from instruments.get_instruments import get_rga


class FilamentControlTask(Task):
    """
    Task to set filament emission current
    """
    # Input parameter name
    InstrumentName = 'instrument to control'
    EmissionCurrent = 'emission current'

    # input_parameters values are used to change interactively from GUI
    input_parameters = {
        InstrumentName: InstrumentInput(),
        EmissionCurrent: FloatInput(1.0, " mA", 0.0, 3.5, 0.02),
    }

    def setup(self):
        # Get the logger to use
        self.logger = self.get_logger(__name__)

        # Get the input parameters from GUI
        self.params = self.get_all_input_parameters()

        # Get rga from the instrument
        self.rga = get_rga(self, self.params[self.InstrumentName])

    def test(self):
        self.logger.info('Filament emission current before change: {} mA'.format(self.rga.ionizer.emission_current))
        self.logger.info('Setting emission current to {} mA'.format(self.params[self.EmissionCurrent]))

        error_bites = ''
        try:
            # Clear filament error before changing emission current
            print('Previous errors: {}'.format(self.rga.status.get_error_text()))

            self.rga.ionizer.emission_current = self.params[self.EmissionCurrent]
            error_bits = self.rga.status.get_errors()
            self.logger.info('Errors after setting emission current:  {}'
                             .format(self.rga.status.get_error_text(error_bits)))
            if 'FL' not in error_bits:
                self.set_task_passed(True)
        except Exception as e:
            self.logger.error(e)

    def cleanup(self):
        self.logger.info('Task finished')


if __name__ == '__main__':
    import logging
    from rga import RGA120 as Rga
    import matplotlib.pyplot as plt

    logging.basicConfig(level=logging.INFO)
    
    task = FilamentControlTask()

    rga = Rga('tcpip', '172.25.70.181', 'admin', 'admin')
    rga.comm.set_callbacks(logging.info, logging.info)
    task.inst_dict = {'dut': rga}

    task.figure = plt.figure()
    task.figure_dict = {'plot': task.figure}

    task.set_input_parameter(test.EmissionCurrent, 0.5)
    task.set_input_parameter(task.InstrumentName, 'dut')

    task.start()
    task.wait()

