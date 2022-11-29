
from rgagui.basetask.task import Task
from rgagui.basetask.inputs import ListInput, IntegerInput, StringInput, InstrumentInput
from rgagui.plots.timeplot import TimePlot
from rgagui.plots.analogscanplot import AnalogScanPlot

from instruments.get_instruments import get_rga


class DerivedPvsTScanTask(Task):
    """Task to run analog scans wide enough to cover all the specified masses
and extract ion intensity for the masses from the analog scans.
    """
    InstrumentName = 'instrument to control'
    MassesToMeasure = 'masses to measure'
    ScanSpeed = 'scan speed'
    IntensityUnit = 'intensity unit'

    LogPlot = 'log_scan_plot'
    DerivedPvsTPlot = 'derived_pvst'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        InstrumentName: InstrumentInput(),
        MassesToMeasure: StringInput("2, 18, 28, 44"),
        ScanSpeed: IntegerInput(3, " ", 0, 9, 1),
        IntensityUnit: ListInput(['Ion current (fA)', 'Partial Pressure (Torr)']),
    }
    additional_figure_names = [LogPlot, DerivedPvsTPlot]

    def setup(self):
        # Get values to use for task  from input_parameters in GUI
        self.params = self.get_all_input_parameters()

        # Get logger to use
        self.logger = self.get_logger(__name__)

        self.mass_list = list(map(int, self.params[self.MassesToMeasure].split(',')))

        self.rga = get_rga(self, self.params[self.InstrumentName])
        self.id_string = self.rga.status.id_string

        margin = 5
        init_mass = min(self.mass_list) - 5 if min(self.mass_list) > margin else 1
        fin_mass = max(self.mass_list) + 5 if max(self.mass_list) < self.rga.scan.get_max_mass() \
            else self.rga.scan.get_max_mass
        self.rga.scan.speed = self.params[self.ScanSpeed]
        self.rga.scan.resolution = 10
        self.rga.scan.set_parameters(init_mass, fin_mass, self.params[self.ScanSpeed], self.rga.scan.resolution)
        self.logger.info('Scan initial mass: {}, final mass: {}, scan speed: {}, steps per AMU: {}'
                         .format(init_mass, fin_mass, self.params[self.ScanSpeed], self.rga.scan.resolution))

        emission_current = self.rga.ionizer.emission_current
        cem_voltage = self.rga.cem.voltage
        self.logger.info('Emission current: {:.2f} mA CEM HV: {} V'.format(emission_current, cem_voltage))

        # Set up an derived P vs T plot
        self.ax_pvst = self.get_figure(self.DerivedPvsTPlot).add_subplot(111)
        key_list = list(map(str, self.mass_list))
        self.pvst_plot = TimePlot(self, self.ax_pvst, 'Derived P vs T', key_list)
        self.pvst_plot.ax.set_yscale('log')

        # Set up a log plot for the last full analog scan
        self.ax_log = self.get_figure(self.LogPlot).add_subplot(111)
        self.plot_log = AnalogScanPlot(self, self.ax_log, self.rga.scan, 'Analog Scan In Log')
        self.rga.scan.set_callbacks(None, None, None)  # use no callbacks for self.plot_log
        self.ax_log.set_yscale('log')

        # Set up an analog scan plot
        self.ax_analog = self.get_figure().add_subplot(111) # use the default figure
        self.plot_analog = AnalogScanPlot(self, self.ax_analog, self.rga.scan, 'Analog Scan')

        if self.params[self.IntensityUnit] == 0:
            self.conversion_factor = 0.1
            self.plot_analog.set_conversion_factor(self.conversion_factor, 'fA')
            self.plot_log.set_conversion_factor(self.conversion_factor, 'fA')
            self.pvst_plot.set_conversion_factor(self.conversion_factor, 'fA')
        else:
            self.conversion_factor = self.rga.pressure.get_partial_pressure_sensitivity_in_torr()
            self.plot_analog.set_conversion_factor(self.conversion_factor, 'Torr')
            self.plot_log.set_conversion_factor(self.conversion_factor, 'Torr')
            self.pvst_plot.set_conversion_factor(self.conversion_factor, 'Torr')

    def test(self):
        self.set_task_passed(True)
        while True:
            if not self.is_running():
                break

            try:
                self.rga.scan.get_analog_scan()

                self.plot_log.line.set_xdata(self.plot_log.x_axis)
                self.plot_log.line.set_ydata(self.plot_log.scan.spectrum)
                self.request_figure_update(self.plot_log.ax.figure)

                intensity = []
                for m in self.mass_list:
                    intensity.append(self.rga.scan.get_peak_intensity_from_analog_scan_spectrum(m, True))

                self.pvst_plot.add_data(intensity, True)

            except Exception as e:
                self.set_task_passed(False)
                self.logger.error('{}: {}'.format(e.__class__.__name__, e))
                if not self.rga.is_connected():
                    self.logger.error('"{}" is disconnected'.format(self.params[self.InstrumentName]))
                    break

    def cleanup(self):
        pass
