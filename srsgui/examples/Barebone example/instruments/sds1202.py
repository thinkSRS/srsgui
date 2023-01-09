from srsgui import Instrument

class SDS1202(Instrument):
    _IdString = 'SDS1202'


    # If your instrument has carriage return as the termination character,
    # uncomment the __init__method to change the termination character 
    # from line feed to carriage return. 
    # With a wrong term char, communication may not work
    
    """
    def __init__(self, interface_type=None, *args):

        super().__init__(interface_type, *args)
        self.set_term_char(b'\r')
    """