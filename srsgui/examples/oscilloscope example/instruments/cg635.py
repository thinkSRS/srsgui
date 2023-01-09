
from srsgui import Instrument
from srsgui.inst import FloatCommand

# Uncomment the following import to use VisaInterface
# from srsgui import SerialInterface, FindListInput
# from srsinst.sr860 import VisaInterface


class CG635(Instrument):
    _IdString = 'CG635'

    # Uncomment the following dictionary to use a cusomized 
    # Communication interface definition.
    # ViaInterface is availabe from srsinst.sr860 package.
    # VisaInterface requires PyVisa package to be installed manually.
    # Note that PyVisa requires a separate backend driver installation, too.
    """
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
    """

    frequency = FloatCommand('FREQ')
    """
    FloatCommand is used to encapsulate a remote command to set and qurty a float value
    To set a value,
        cg.freqeuncy = 1e7
        
    to query a value
        f = cg.frequemcy
    """

    # To use promoted communication class methods to set and query a remote command for a float value,
    # uncomment the following methods.    
    """
    def set_frequency(self, f):
        self.send(f'FREQ {f}')
        
    def get_frequency(self):
        return self.query_float('FREQ?')
    """
