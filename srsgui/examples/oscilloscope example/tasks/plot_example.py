##! 
##! Copyright(c) 2022, 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

import time
import math

from srsgui import Task
from srsgui import IntegerInput


class PlotExample(Task):
    """
Example to demonstrate the use of matplotlib plot in a task.
No hardware connection is required.
Generates a plot of y = sin(x) vs. x, \
for x in the range [initial angle, final angle]. 
    """
    
    # Interactive input parameters to set before running 
    theta_init = 'initial angle'
    theta_final = 'final angle'
    input_parameters = {
        theta_init: IntegerInput(0,' deg'),
        theta_final: IntegerInput(360,' deg')
    }
    """
    Use input_parameters to get parameters used in the task 
    """

    def setup(self):

        # Get a value from input_parameters
        self.theta_i = self.get_input_parameter(self.theta_init)
        self.theta_f = self.get_input_parameter(self.theta_final)

        # Get the Python logging handler
        self.logger = self.get_logger(__file__)

        # Get the default Matplotlib figure
        self.figure = self.get_figure()

        # Once you get the figure, the followings are typical Matplotlib things to plot.
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(self.theta_i, self.theta_f)
        self.ax.set_ylim(-1.1, 1.1)
        x_txt = self.theta_i + 0.25*(self.theta_f - self.theta_i)
        y_txt = 0.5
        self.ax.text(x_txt, y_txt, 'Drawing sine curve...')
        self.line, = self.ax.plot([0], [0])
        
    def test(self):
        print("\n\nLet's plot!\n\n")
        
        x = []
        y = []
        rad = 180 / math.pi

        
        for i in range(self.theta_i, self.theta_f+1, 1):
            if not self.is_running():  # if the stop button is pressed, stop the task
                break
       
            self.logger.info(f'Adding point {i}')

            # Display in the result panel
            self.display_result(f'\n\nPlotting {i} degree...\n\n', clear=True)

            # Add data to the Matplotlib line and update the plot
            x.append(i)
            y.append(math.sin(i / rad))
            self.line.set_data(x, y)

            # Figure update should be done in the main thread, not locally.
            self.request_figure_update(self.figure)
            
            # Delay a bit as if a sine function computation takes time.
            time.sleep(0.01)

    def cleanup(self):
        self.display_result('Done!')
