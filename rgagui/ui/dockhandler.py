
import logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QMenu, QAction, QWidget, \
                            QVBoxLayout, QTextBrowser

from matplotlib.figure import Figure
import matplotlib.image as mpimg

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .commandTerminal import CommandTerminal

logger = logging.getLogger(__name__)


class DockHandler(object):
    DefaultConsoleName = 'Console'
    DefaultTerminalName = 'Terminal'
    DefaultFigureName = 'Plot'
    MenuName = 'menu_View'

    def __init__(self, parent):
        if not (hasattr(parent, self.MenuName) and
                type(parent.menu_View) == QMenu
                ):
            raise AttributeError('Parent does not have all Attributes required')
        self.parent = parent
        self.dock_dict = {}
        self.named_figure_docks = []
        self.fig_dock_area = Qt.RightDockWidgetArea
        try:
            parent.menu_View.triggered.disconnect()
        except:
            pass
        actions = parent.menu_View.actions()
        for action in actions:
            parent.menu_View.removeAction(action)

        self.dock_dict = {}

        self.init_figure_dock(self.DefaultFigureName)
        self.init_terminal()
        self.init_console()
        fig = self.dock_dict.pop(self.DefaultFigureName)
        self.dock_dict[self.DefaultFigureName] = fig

        parent.tabifyDockWidget(self.get_dock(self.DefaultTerminalName),
                                self.get_dock(self.DefaultConsoleName))
        self.default_dock = self.dock_dict[self.DefaultFigureName]
        self.default_figure = self.dock_dict[self.DefaultFigureName].figure

        parent.menu_View.triggered.connect(self.onDockMenuSelected)
        for key in self.dock_dict:
            action_dock = QAction(parent)
            action_dock.setText(key)
            action_dock.setCheckable(True)
            parent.menu_View.addAction(action_dock)

    def init_console(self):
        try:
            name = self.DefaultConsoleName
            console_dock = QDockWidget(self.parent)
            console_dock.setObjectName(name)
            console_dock.setFloating(False)
            console_dock.setWindowTitle(name)

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

            self.terminal_widget = CommandTerminal(self.parent)
            terminal_dock.setWidget(self.terminal_widget)
            self.parent.addDockWidget(Qt.RightDockWidgetArea, terminal_dock)
            self.dock_dict[name] = terminal_dock
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
            self.setup_figure_canvas(figure_dock)
            figure_dock.toolbar.hide()

            self.parent.addDockWidget(self.fig_dock_area, figure_dock)
            self.dock_dict[name] = figure_dock
            if len(self.dock_dict) > 3:
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
            ax.imshow(img)
            ax.axis('off')
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

    def get_dock(self, name=None) -> QDockWidget:
        if name is None:
            return self.default_dock

        if name not in self.dock_dict:
            raise KeyError('No dock widget named {}'.format(name))
        return self.dock_dict[name]

    def onDockMenuSelected(self, action):
        try:
            name = action.text()
            widget = self.dock_dict[name]
            if not widget.isVisible():
                widget.setVisible(True)
                action.setChecked(True)
            else:
                widget.setVisible(False)
                action.setChecked(False)

        except Exception as e:
            logger.error(e)

    def update_figures(self, name_list):
        try:
            while len(self.dock_dict) > 3:
                name, fig = self.dock_dict.popitem()
                self.parent.removeDockWidget(fig)
                self.named_figure_docks.append(fig)
                # logger.deubg('removed {} {}'.format(name, fig))

            for name in name_list:
                if self.named_figure_docks:
                    dock = self.named_figure_docks.pop()
                    dock.setWindowTitle(name)
                    dock.setObjectName(name)
                    self.dock_dict[name] = dock
                    self.parent.addDockWidget(self.fig_dock_area, dock)
                    dock.setVisible(True)
                    self.parent.tabifyDockWidget(self.default_dock, dock)
                    # logger.debug('add {} {}'.format(name, dock))
                else:
                    self.init_figure_dock(name)
                    # logger.debug('init {}'.format(name))
            self.update_menu()
        except Exception as e:
            logger.error(e)

    def update_menu(self):
        if not hasattr(self.parent, self.MenuName):
            return
        actions = self.parent.menu_View.actions()
        for action in actions:
            self.parent.menu_View.removeAction(action)
        for key in self.dock_dict:
            action_dock = QAction(self.parent)
            action_dock.setText(key)
            action_dock.setCheckable(True)
            self.parent.menu_View.addAction(action_dock)

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

    def show_toolbar(self):
        for dock in self.dock_dict.values():
            if hasattr(dock, 'toolbar'):
                dock.toolbar.show()
