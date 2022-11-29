
import time
from rga.uga100.components import Status
from rgagui.basetask.task import Task
from rgagui.basetask.inputs import InstrumentInput, ListInput, IntegerInput
from instruments.get_instruments import get_uga


class UGAModeControlTask(Task):
    """
    update
    """
    InstrumentName = 'uga to control'
    ModeIndex = 'mode control'
    UpdatePeriod = 'update period'
    LeakTestMass = 'mass for leak test'
    ModeList = ['Start', 'Stop', 'Sleep', 'Leak Test On', 'Leak Test Off', 'System Bake On', 'System Bake Off']

    input_parameters = {
        InstrumentName: InstrumentInput(),
        ModeIndex: ListInput(ModeList),
        LeakTestMass: IntegerInput(4, ' AMU', 1, 100),
        UpdatePeriod: IntegerInput(2, ' s', 1, 60, 1)
    }

    def setup(self):
        self.logger = self.get_logger(__name__)
        self.instrument_name_value = self.get_input_parameter(self.InstrumentName)
        self.mode_index_value = self.get_input_parameter(self.ModeIndex)
        self.leak_test_mass_value = self.get_input_parameter(self.LeakTestMass)
        self.update_period_value = self.get_input_parameter(self.UpdatePeriod)

        self.uga = get_uga(self, self.instrument_name_value)
        print(self.uga.status.id_string)
        while self.uga.status.error != 0:
            pass
        self.immediate_state = Status.ModeDict[self.uga.mode.state]
        self.final_state = self.immediate_state
        self.logger.info('Current mode before changing: {}'.format(self.immediate_state))

    def test(self):
        if self.mode_index_value == 0:
            self.uga.mode.start()
            self.immediate_state = 'START'
            self.final_state = 'READY'

        elif self.mode_index_value == 1:
            self.uga.mode.stop()
            self.immediate_state = 'STOP'
            self.final_state = 'OFF'

        elif self.mode_index_value == 2:
            self.uga.mode.sleep()
            self.immediate_state = 'SLEEP'
            self.final_state = 'IDLE'

        elif self.mode_index_value == 3:
            if Status.ModeDict[self.uga.mode.state] != 'READY':
                raise ValueError('Leak test mode is available only from READY state')
            self.uga.mode.leak_test_mass = self.leak_test_mass_value
            self.uga.mode.leak_test = True
            self.immediate_state = 'READY'
            self.final_state = 'LEAK TEST'

        elif self.mode_index_value == 4:
            if Status.ModeDict[self.uga.mode.state] != 'LEAK TEST':
                raise ValueError('Leak test mode is not on')

            self.uga.mode.leak_test = False
            self.immediate_state = 'LEAK TEST'
            self.final_state = 'READY'
        elif self.mode_index_value == 5:
            self.immediate_state = Status.ModeDict[self.uga.mode.state]
            self.uga.mode.bake = True
            self.final_state = 'SYSTEM BAKE'

        elif self.mode_index_value == 6:
            if Status.ModeDict[self.uga.mode.state] != 'SYSTEM BAKE':
                raise ValueError('SYSTEM BAKE is not on')
            self.uga.mode.bake = False
            self.immediate_state = 'START'
            self.final_state = 'READY'

        error_code = self.uga.status.error
        if error_code > 10:
            raise ValueError('Error "{}" when trying to change to  {}'
                             .format(self.uga.status.error_message[error_code], self.final_state))
        else:
            self.logger.info('UGA mode changing to {}'.format(self.final_state))

        self.display_device_info(device_name=self.instrument_name_value, update=True)

        time.sleep(self.update_period_value)
        current_state = Status.ModeDict[self.uga.mode.state]
        while current_state in [self.immediate_state, self.final_state]:
            if not self.is_running():
                break
            self.display_device_info(device_name=self.instrument_name_value, update=True)
            current_state = Status.ModeDict[self.uga.mode.state]
            if current_state == self.final_state:
                self.logger.info('Mode successfully changed to {}'.format(self.final_state))
                break
            time.sleep(self.update_period_value)

        self.display_device_info(device_name=self.instrument_name_value, update=True)
        self.set_task_passed(True)

    def cleanup(self):
        pass
