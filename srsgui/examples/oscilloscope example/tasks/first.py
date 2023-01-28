
from srsgui import Task


class FirstTask(Task):
    """
Query *IDN? to instruments, 'cg' and 'osc' \
defined in the configuration file.
    """
    
    # No interactive input parameters to set before running 
    input_parameters = {}
    
    def setup(self):
        # To use Python logging
        self.logger = self.get_logger(__file__)

        # To use the instrument defined in .taskconfig file
        self.cg = self.get_instrument('cg')
        self.osc = self.get_instrument('osc')

        # Set clock frequency tp 10 MHz

        # frequency is define as FloatCommand in CG635 class
        self.cg.frequency = 10000000
        self.logger.info(f'Current frequency: {self.cg.frequency}')

        # You can do the same thing with FloatCommand defined.
        # You can use send() and query_float() with raw remote command
        # self.cg.send('FREQ 10000000')
        # self.current_frequency = self.cg.query_float('FREQ?')
        # self.logger.info(self.current_frequency)

    def test(self):
        # You can use print() only with one argument.
        print("\n\nLet's query IDs of instruments!!\n\n")

        # Use query_text for raw remote command query returning string
        cg_id_string = self.cg.query_text('*idn?')
        osc_id_string = self.osc.query_text('*idn?')
        
        self.logger.info(f"CG *IDN : {cg_id_string}")
        self.logger.info(f"OSC *IDN : {osc_id_string}")

    def cleanup(self):
        # We have nothing to clean up
        pass
