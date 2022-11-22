

from rgagui.base.task import Task, round_float
from rgagui.base.inputs import ListInput, IntegerInput, StringInput, InstrumentInput
from rgagui.plots.timeplot import TimePlot

from instruments.get_instruments import get_rga

class DerivedPvsTScanTask(Task):

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

        self.rga.scan.speed = self.params[self.ScanSpeed]
        self.rga.scan.resolution = 10

        emission_current = self.rga.ionizer.emission_current
        cem_voltage = self.rga.cem.voltage
        self.logger.info('Emission current: {:.2f} mA CEM HV: {} V'.format(emission_current, cem_voltage))

        if self.params[self.IntensityUnit] == 0:
            self.conversion_factor = 0.1
            self.plot.set_conversion_factor(self.conversion_factor, 'fA')
        else:
            self.conversion_factor = self.rga.pressure.get_partial_pressure_sensitivity_in_torr()
            self.plot.set_conversion_factor(self.conversion_factor, 'Torr')

        # Set up an derived P vs T plot
        self.ax_pvst = self.get_figure(self.DerivedPvsTPlot).add_subplot(111)
        key_list = list(map(str, self.mass_list))
        self.pvst_plot = TimePlot(self, self.ax, 'P vs T Scan', key_list)
        self.pvst_plot.ax.set_yscale('log')

        # Set up an analog scan plot
        self.ax_analog = self.get_figure().add_subplot(111) # use the default figure


        # Set up a log plot for the last full analog scan
        self.ax_log = self.get_figure(self.LogPlot).add_subplot(111)


    def test(self):
        pass

    def cleanup(self):
        pass
