import logging
from srsgui import Task


class FirstTask(Task):
    """
    This is the first task using SRSGUI 
    
    Query *IDN? to 'cg' and 'osc' instuments 
    defined in the configuration file'
    """
    
    
    # No interactive input parameters to set before running 
    input_parameters = {}
    
    def setup(self):
        self.logger = self.get_logger(__file__)  #use Python logging 
        
        self.cg = self.get_instrument('cg')  # use the inst name in taskconfig file
        self.osc = self.get_instrument('osc')

    def test(self):
        print("\n\nLet's query instruments!!\n\n")
        
        cg_id_string = self.cg.query_text('*idn?')
        osc_id_string = self.osc.query_text('*idn?')
        
        self.logger.info(f"CG *IDN : {cg_id_string}")
        self.logger.info(f"OSC *IDN : {osc_id_string}")

    def cleanup(self):
        pass
        
        