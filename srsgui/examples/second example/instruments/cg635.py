
from srsgui import Instrument, SerialInterface, FindListInput
from srsgui.inst import FloatCommand
from srsinst.sr860 import VisaInterface

class CG635(Instrument):
    _IdString = 'CG635'

    available_interfaces = [
        [   SerialInterface,
            {
                'COM port': FindListInput(),
                'baud rate': 9600
            }
        ],    
        [   VisaInterface,
            {
                'resource': FindListInput(),
            }
        ],        
    ]

    frequency = FloatCommand('FREQ')

    def set_frequency(self, f):
        self.send(f'FREQ {f}')
        
    def get_frequency(self):
        return self.query_float('FREQ?')
