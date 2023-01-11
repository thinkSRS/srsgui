import time
import math

from srsgui import Task
from srsgui import IntegerInput


class SecondTask(Task):
    """
It shows how to use a Matplotlib plot in a task. \
No hardware connection is required to plot a sine curve.
    """
    
    # Interactive input parameters to set before running 
    Angle = 'final angle to plot'
    input_parameters = {
        Angle: IntegerInput(360, ' degree')
    }
    """
    Use input_parameters to get parameters used in the task 
    """

    def setup(self):

        # Get a value from input_parameters
        self.total_angle = self.get_input_parameter(self.Angle)

        # Get the Python logging handler
        self.logger = self.get_logger(__file__)

        # Get the default Matplotlib figure
        self.figure = self.get_figure()

        # Once you get the figure, the followings are typical Matplotlib things to plot.
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(0, self.total_angle)
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.text(0.1 * self.total_angle, 0.5, 'Drawing sine curve...')
        self.line, = self.ax.plot([0], [0])
        
    def test(self):
        print("\n\nLet's plot!\n\n")
        
        x = []
        y = []
        rad = 180 / math.pi

        for i in range(self.total_angle):
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
