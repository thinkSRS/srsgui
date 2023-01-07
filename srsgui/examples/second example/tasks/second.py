import time
import math
import logging
from srsgui import Task
from srsgui import IntegerInput


class SecondTask(Task):
    """
    This is the second task using srsgui.

    No instruments are required connected 
    to plot a sine curve.
    """
    
    # Interactive input parameters to set before running 
    Angle = 'angle to plot'
    input_parameters = {
        Angle: IntegerInput(360, ' degree') # How many degree do you want to plot
    }
    
    def setup(self):
    
        self.total_angle = self.get_input_parameter(self.Angle)
        
        self.logger = self.get_logger(__file__)
        
        # Once you get the figure, the followings are Matplotlib things to plot.
        self.figure = self.get_figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(0, self.total_angle)
        self.ax.set_ylim(-1, 1)
        self.ax.text(0.1 * self.total_angle, 0.5, 'Drawing sine curve...')
        self.x_data = [0]
        self.y_data = [0]
        self.line, = self.ax.plot(self.x_data,self.y_data)
        
    def test(self):
        print("\n\nLet's plot!\n\n")
        
        for i in range(self.total_angle):
            if not self.is_running(): # if the Stop button is pressed
                break
       
            self.logger.info(f'Adding point {i}')
            self.display_result(f'\n\nPlotting {i} degree...\n\n', clear=True)
            # Add data to the Matplotlib line and update the figure
            self.x_data.append(i)
            self.y_data.append(math.sin((i/180) * math.pi))
            self.line.set_data(self.x_data, self.y_data)
            self.request_figure_update()
            
            # Delay a bit as if data computation takes time.
            time.sleep(0.01)

    def cleanup(self):
        self.display_result('Done!')
        
        
        