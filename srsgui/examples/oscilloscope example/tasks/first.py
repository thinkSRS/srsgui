
from srsgui import Task


class FirstTask(Task):
    """
Query *IDN? to instruments, 'cg' and 'osc' \
defined in the configuration file.
    """
    
    # No interactive input parameters to set before running 
    input_parameters = {}
    
    def setup(self):
        self.logger = self.get_logger(__file__)  # To use Python logging
        
        self.cg = self.get_instrument('cg')  # To use the instrument defined in taskconfig file
        self.osc = self.get_instrument('osc')

    def test(self):
        print("\n\nLet's query IDs of instruments!!\n\n")
        
        cg_id_string = self.cg.query_text('*idn?')
        osc_id_string = self.osc.query_text('*idn?')
        
        self.logger.info(f"CG *IDN : {cg_id_string}")
        self.logger.info(f"OSC *IDN : {osc_id_string}")

        # Set clock frequency tp 10 MHz
        self.cg.frequency = 10000000

        # If frequency is not defined, use send()
        # self.cg.send('FREQ 10000000')

    def cleanup(self):
        pass
