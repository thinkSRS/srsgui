
from rgagui.base.task import Task
from rgagui.base.inputs import FloatInput, IntegerInput, StringInput, ListInput
from instruments.get_instruments import get_rga


class CEMControlTask(Task):
    """
    Task to set CEM high voltage
    """

    CEMState = 'cem high voltage'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        CEMState: ListInput(['Off', 'On']),
    }

    def setup(self):

        self.logger = self.get_logger(__name__)

        self.cem_state_value = self.get_input_parameter(self.CEMState)

        self.rga = get_rga(self)

    def test(self):
        self.set_task_passed(True)
        try:
            self.logger.info('Saved CEM voltage: {:.0f}'.format(self.rga.cem.stored_voltage))
            self.logger.info('Saved CEM gain: {:.0f}'.format(self.rga.cem.stored_gain))
            self.logger.info('Current CEM voltage: {} V'.format(self.rga.cem.voltage))

            if self.cem_state_value:
                set_voltage = self.rga.cem.stored_voltage
                set_gain = self.rga.cem.stored_gain
                if set_voltage > 2500:
                    raise ValueError('MV {} value too big'.format(set_voltage))
            else:
                set_voltage = 0
                set_gain = 0
            self.logger.info('Setting CEM voltage to {} V'.format(set_voltage))
            self.add_details('{} V for gain {:.0f}'.format(set_voltage, set_gain))

            status_byte = None
            try:
                print('Previous errors: {}'.format(self.rga.status.get_error_text()))
                self.rga.cem.voltage = set_voltage
                status_byte = self.rga.cem.last_set_status
                self.logger.info('Errors after setting CEM voltage to {} V:  {}'
                                 .format(set_voltage,  self.rga.status.get_error_text(status_byte)))
            except Exception as e:
                self.logger.error('Error while setting CEM voltage to {} V: {}'.format(set_voltage, e))

            if status_byte:
                self.set_task_passed(False)

        except Exception as e:
            self.logger.error(e)
            self.set_task_passed(False)

    def cleanup(self):
        self.logger.info('Task finished')
