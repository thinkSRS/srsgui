from srsgui import Instrument, TcpipInterface, Ip4Input, FindListInput, StringInput

# Uncomment the follwoing import to use VisaInterface and Vxi11Interface
# from srsinst.sr860 import VisaInterface, Vxi11Interface

class SDS1202(Instrument):
    _IdString = 'SDS1202'

    # Uncomment the following dictionary to use a cusomized 
    # Communication interface definition.
    # Vxi11Interface and ViaInterface are availabe from 
    # srsinst.sr860 package using pip.
    #
    #    pip install srsinst.sr860
    #
    # VisaInterface requires PyVisa package to be installed manually.
    # Note that PyVisa requires a separate backend driver installation, too.
    """
    available_interfaces = [
        [   Vxi11Interface,
            {
                'ip_address': Ip4Input('192.168.1.10'),
            }
        ],
        
        [   VisaInterface,
            {
                'resource': FindListInput(),
            }
        ],
        
        [   TcpipInterface,
            {
                'ip_address': Ip4Input('192.168.1.10'),
                'port': 5025
            }
        ],
    ]
    """

    def get_waveform(self, channel):
        """
        Get a waveform from a channel of the oscilloscope
        
        The code is from the page 267 of Siglent digital oscilloscope
        programming guide, PG01-E02D
        """
        
        CODE_DIV = 25
        HOR_GRID = 14
    
        self.send('chdr off')
        vdiv = self.query_float(f'{channel}:vdiv?')
        offset = self.query_float(f'{channel}:ofst?')
        tdiv = self.query_float('tdiv?')
        sara - self.get_sampling_rate()
        
        with self.comm.get_lock(): # Use the lock to be thread-safe during query
            self.comm._send(f'{channel}:wf? dat2')
            
            recv = self.comm._read_binary(16) 
            # With VXI11, it returns whole data, not just 16 bytes.
            
            header = recv[:16].split(b'#', 1)
            length = header[1][1:].decode(encoding='utf-8')
            num = int(length)
            num_to_read = num + 2 - (len(recv) - 16)
            if num_to_read > 0:
                recv += self.comm._read_binary(num_to_read)
                
        ending = recv[-2:]
        if ending != b'\n\n':
            print('Invalid ending detected: {}'.format(ending))
            return [], []
            
        volt_values = []
        time_values = []
        for index, point in enumerate(recv[16:-2]):
            if point > 127:
                point -= 256
            v = point / CODE_DIV * vdiv - offset
            t = -tdiv * HOR_GRID / 2 + index / sara
            volt_values.append(v)
            time_values.append(t)
        return time_values, volt_values
            
    def get_sampling_rate(self):
        sara = self.query_text('sara?')
        sara_units = {'G':1e9, 'M': 1e6, 'k': 1e3}
        for unit in sara_units:
            if sara.find(unit) >= 0:
                sara = sara.split(unit)
                sara = float(sara[0]) * sara_units(unit)
                break
        return float(sara)
 
        
        
