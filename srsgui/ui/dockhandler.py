import time
import logging

from .qt.QtCore import Qt
from .qt.QtWidgets import QDockWidget, QMenu, QAction, QWidget, \
                          QVBoxLayout, QTextBrowser


from matplotlib.figure import Figure
import matplotlib.image as mpimg

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .commandterminal import CommandTerminal
from .capturecommandwidget import CaptureCommandWidget

logger = logging.getLogger(__name__)

# define matplotlib level before importing to suppress debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)


class DockHandler(object):
    """
    To handle all the QDockWidget instances used for the console, terminal, matplotlib figure windows,
    along with the Docks menu in the main application.
    """

    DefaultConsoleName = 'Console'
    DefaultTerminalName = 'Terminal'
    DefaultFigureName = 'plot'
    MenuDocksName = 'menu_Docks'
    MenuPlotName = 'menu_Plot'

    TitleFormat = '{} - Capture'

    def __init__(self, parent):
        if not (hasattr(parent, self.MenuDocksName) and
                type(parent.menu_Docks) == QMenu and
                hasattr(parent, self.MenuPlotName) and
                type(parent.menu_Plot) == QMenu
                ):
            raise AttributeError('Parent does not have all Attributes required')
        self.parent = parent
        self.dock_dict = {}

        self.active_inst_dock_names = []
        self.removed_inst_docks = []

        self.active_figure_dock_names = []
        self.removed_figure_docks = []
        self.fig_dock_area = Qt.RightDockWidgetArea
        try:
            parent.menu_Docks.triggered.disconnect()
        except:
            pass
        actions = parent.menu_Docks.actions()
        for action in actions:
            parent.menu_Docks.removeAction(action)

        self.init_figure_dock(self.DefaultFigureName)
        self.init_terminal()
        self.init_console()
        self.init_inst_dock('instrument info')
        list(self.dock_dict.values())[-1].hide()

        fig = self.dock_dict.pop(self.DefaultFigureName)
        self.dock_dict[self.DefaultFigureName] = fig

        parent.tabifyDockWidget(self.get_dock(self.DefaultTerminalName),
                                self.get_dock(self.DefaultConsoleName))
        self.default_dock = self.dock_dict[self.DefaultFigureName]
        self.default_figure = self.dock_dict[self.DefaultFigureName].figure

        parent.menu_Docks.triggered.connect(self.onMenuDocksSelected)
        for key in self.dock_dict:
            action_dock = QAction(parent)
            action_dock.setText(key)
            parent.menu_Docks.addAction(action_dock)
        self.init_plot_menu()

        self._figure_update_period = 0.1
        self.figure_update_time_dict = {}  # last update time of figures

    def init_plot_menu(self):
        try:
            self.parent.menu_Plot.triggered.disconnect()
        except:
            pass
        actions = self.parent.menu_Plot.actions()
        for action in actions:
            self.parent.menu_Plot.removeAction(action)

        # self.parent.menu_Plot.triggered.connect(self.onMenuPlotSelected)
        self.action_tight_layout = QAction(self.parent)
        self.action_tight_layout.setText('Adjust Layout')
        self.action_tight_layout.triggered.connect(self.onTightLayout)
        self.parent.menu_Plot.addAction(self.action_tight_layout)

        self.action_toolbar = QAction(self.parent)
        self.show_toolbar(False)
        self.action_toolbar.triggered.connect(self.onToolbar)
        self.parent.menu_Plot.addAction(self.action_toolbar)

    def onTightLayout(self):
        for fig in self.get_figure_dict().values():
            if len(fig.get_axes()) > 0:
                fig.tight_layout()

    def onToolbar(self):
        if self.toolbar_visible:
            self.show_toolbar(False)
        else:
            self.show_toolbar(True)

    def init_console(self):
        try:
            name = self.DefaultConsoleName
            console_dock = QDockWidget(self.parent)
            console_dock.setObjectName(name)
            console_dock.setFloating(False)
            console_dock.setWindowTitle(name)
            console_dock.setMinimumSize(250, 150)

            self.console = QTextBrowser(self.parent)
            console_dock.setWidget(self.console)
            self.parent.addDockWidget(Qt.RightDockWidgetArea, console_dock)
            self.dock_dict[name] = console_dock
        except Exception as e:
            logger.error(e)

    def init_terminal(self):
        try:
            name = self.DefaultTerminalName
            terminal_dock = QDockWidget(self.parent)
            terminal_dock.setObjectName(name)
            terminal_dock.setFloating(False)
            terminal_dock.setWindowTitle(name)
            terminal_dock.setMinimumSize(250, 150)

            self.terminal_widget = CommandTerminal(self.parent)
            terminal_dock.setWidget(self.terminal_widget)
            self.parent.addDockWidget(Qt.RightDockWidgetArea, terminal_dock)
            self.dock_dict[name] = terminal_dock
        except Exception as e:
            logger.error(e)

    def init_inst_dock(self, name):
        try:
            inst_dock = QDockWidget(self.parent)
            inst_dock.setObjectName(name)
            inst_dock.setFloating(False)

            title = self.TitleFormat.format(name)
            inst_dock.setWindowTitle(title)
            inst_dock.setMinimumSize(250, 150)

            inst_dock.command_capture_widget = CaptureCommandWidget(self.parent)
            inst_dock.setWidget(inst_dock.command_capture_widget)
            self.parent.addDockWidget(Qt.LeftDockWidgetArea, inst_dock)
            self.dock_dict[title] = inst_dock
            self.active_inst_dock_names.append(title)
            if len(self.active_inst_dock_names) > 1:
                self.parent.tabifyDockWidget(
                    self.dock_dict[self.active_inst_dock_names[0]], inst_dock)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def setup_figure_canvas(widget: QDockWidget):
        widget.figure = Figure()
        widget.canvas = FigureCanvas(widget.figure)
        widget.toolbar = NavigationToolbar(widget.canvas, widget)
        layout = QVBoxLayout()
        layout.addWidget(widget.canvas)
        layout.addWidget(widget.toolbar)

        # use setWidget to put inside DockWidget
        # setLayout works for putting into QFrame
        child = QWidget()
        child.setLayout(layout)
        widget.setWidget(child)

    def init_figure_dock(self, name):
        try:
            figure_dock = QDockWidget(self.parent)
            figure_dock.setObjectName(name)
            figure_dock.setFloating(False)
            figure_dock.setWindowTitle(name)
            figure_dock.setMinimumSize(300, 300)
            self.setup_figure_canvas(figure_dock)
            figure_dock.toolbar.hide()

            self.parent.addDockWidget(self.fig_dock_area, figure_dock)
            self.dock_dict[name] = figure_dock
            self.active_figure_dock_names.append(name)
            if len(self.active_figure_dock_names) > 1:
                self.parent.tabifyDockWidget(self.get_dock(), figure_dock)
        except Exception as e:
            logger.error(e)

    def display_image(self, image_file, figure=None):
        try:
            if figure is None:
                figure = self.default_figure
            figure.clear()
            img = mpimg.imread(image_file)
            ax = figure.subplots()
            ax.axis('off')
            ax.imshow(img)
            figure.canvas.draw_idle()
        except Exception as e:
            logger.error(f"Error in display_image: {e}")

    def get_terminal(self):
        return self.dock_dict[self.DefaultTerminalName].widget()

    def get_figure(self, name=None) -> Figure:
        if name is None:
            return self.default_figure

        if name not in self.dock_dict:
            raise KeyError('No figure named {}'.format(name))
        return self.dock_dict[name].figure

    def set_figure_update_period(self, period):
        self._figure_update_period = period

    def get_figure_update_period(self):
        return self._figure_update_period

    def update_figure(self, figure: Figure):
        if type(figure) is not Figure:
            raise TypeError('{} is not  a Figure'.format(type(figure)))

        current_time = time.time()
        if figure in self.figure_update_time_dict:
            if current_time - self.figure_update_time_dict[figure] < self._figure_update_period:
                return
        figure.canvas.draw_idle()
        self.figure_update_time_dict[figure] = current_time

    def get_dock(self, name=None) -> QDockWidget:
        if name is None:
            return self.default_dock

        if name not in self.dock_dict:
            raise KeyError('No dock widget named {}'.format(name))
        return self.dock_dict[name]

    def onMenuDocksSelected(self, action):
        try:
            name = action.text()
            widget = self.dock_dict[name]
            widget.setVisible(True)
            widget.raise_()
        except Exception as e:
            logger.error(e)

    def reset_inst_docks(self):
        try:
            while len(self.active_inst_dock_names):
                name = self.active_inst_dock_names.pop()
                if name in self.dock_dict:
                    dock = self.dock_dict.pop(name)
                    dock.setVisible(False)
                    self.parent.removeDockWidget(dock)
                    self.removed_inst_docks.append(dock)
                    # logger.debug('removed {} {}'.format(name, dock))
            for inst in self.parent.inst_dict:
                title = self.TitleFormat.format(inst)
                if self.removed_inst_docks:
                    dock = self.removed_inst_docks.pop()
                    dock.setWindowTitle(title)
                    dock.setObjectName(title)
                    self.dock_dict[title] = dock
                    self.active_inst_dock_names.append(title)
                    self.parent.addDockWidget(Qt.LeftDockWidgetArea, dock)
                    if len(self.active_inst_dock_names) > 1:
                        self.parent.tabifyDockWidget(
                            self.dock_dict[self.active_inst_dock_names[0]], dock)
                else:
                    self.init_inst_dock(inst)
                    dock = list(self.dock_dict.values())[-1]
                dock.setVisible(False)
                dock.command_capture_widget.set_inst(inst, self.parent.inst_dict[inst])
                self.update_menu()
        except Exception as e:
            logger.error(e)

    def reset_figures(self, name_list):
        try:
            self.figure_update_time_dict = {}

            while len(self.active_figure_dock_names) > 1:
                name = self.active_figure_dock_names.pop()
                if name in self.dock_dict:
                    fig = self.dock_dict.pop(name)
                    fig.setVisible(False)
                    self.parent.removeDockWidget(fig)
                    self.removed_figure_docks.append(fig)
                    # logger.debug('removed {} {}'.format(name, fig))

            for name in name_list:
                if self.removed_figure_docks:
                    dock = self.removed_figure_docks.pop()
                    dock.setWindowTitle(name)
                    dock.setObjectName(name)
                    self.dock_dict[name] = dock
                    self.active_figure_dock_names.append(name)
                    self.parent.addDockWidget(self.fig_dock_area, dock)
                    dock.setVisible(True)
                    if len(self.active_figure_dock_names) > 1:
                        self.parent.tabifyDockWidget(self.default_dock, dock)
                    # logger.debug('add {} {}'.format(name, dock))
                else:
                    self.init_figure_dock(name)
                    # logger.debug('init {}'.format(name))
            self.update_menu()
        except Exception as e:
            logger.error(e)

    def update_menu(self):
        if not hasattr(self.parent, self.MenuDocksName):
            return
        actions = self.parent.menu_Docks.actions()
        for action in actions:
            self.parent.menu_Docks.removeAction(action)
        for key in self.dock_dict:
            action_dock = QAction(self.parent)
            action_dock.setText(key)
            self.parent.menu_Docks.addAction(action_dock)

    def get_figure_dict(self):
        fig_dict = {}
        for name, dock in self.dock_dict.items():
            if hasattr(dock, 'figure'):
                fig_dict[name] = dock.figure
        return fig_dict

    def clear_figures(self, name=None):
        if name is None:
            for fig in self.get_figure_dict():
                self.get_figure(fig).clear()
        else:
            self.get_figure(name).clear()

    def show_toolbar(self, state=True):
        if state:
            self.action_toolbar.setText('Hide Toolbar')
            self.toolbar_visible = True
            for dock in self.dock_dict.values():
                if hasattr(dock, 'toolbar'):
                    dock.toolbar.show()
        else:
            self.action_toolbar.setText('Show Toolbar')
            self.toolbar_visible = False
            for dock in self.dock_dict.values():
                if hasattr(dock, 'toolbar'):
                    dock.toolbar.hide()
