
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

    def __init__(self, parent):
        if not (hasattr(parent, 'loggingDockWidget') and
                hasattr(parent, 'dock_dict') and
                hasattr(parent, 'menu_View') and
                type(parent.loggingDockWidget) == QDockWidget and
                type(parent.dock_dict) == dict and
                type(parent.menu_View) == QMenu
                ):
            raise AttributeError('Parent does not have all Attributes required')
        self.parent = parent
        self.unused_figure_docks = []

        try:
            parent.menu_View.triggered.disconnect()
        except:
            pass
        actions = parent.menu_View.actions()
        for action in actions:
            parent.menu_View.removeAction(action)

        parent.dock_dict = {self.DefaultConsoleName: parent.loggingDockWidget}

        parent.removeDockWidget(parent.loggingDockWidget)

        self.init_figure_dock(self.DefaultFigureName)
        self.init_terminal()

        parent.addDockWidget(Qt.RightDockWidgetArea, parent.loggingDockWidget)
        parent.loggingDockWidget.setVisible(True)
        parent.tabifyDockWidget(self.get_dock(self.DefaultTerminalName),
                                parent.loggingDockWidget)
        self.default_dock = parent.dock_dict[self.DefaultFigureName]
        self.default_figure = parent.dock_dict[self.DefaultFigureName].figure

        parent.menu_View.triggered.connect(self.onDockMenuSelected)
        for key in parent.dock_dict:
            action_dock = QAction(parent)
            action_dock.setText(key)
            action_dock.setCheckable(True)
            parent.menu_View.addAction(action_dock)

    def init_terminal(self):
        try:
            name = self.DefaultTerminalName
            terminal_dock = QDockWidget(self.parent)
            terminal_dock.setObjectName(name)
            terminal_dock.setFloating(False)
            terminal_dock.setWindowTitle(name)

            terminal_widget = CommandTerminal(self.parent)
            terminal_dock.setWidget(terminal_widget)
            self.parent.addDockWidget(Qt.RightDockWidgetArea, terminal_dock)
            self.parent.dock_dict[name] = terminal_dock
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

    def init_figure_dock(self, name):
        try:
            figure_dock = QDockWidget(self.parent)
            figure_dock.setObjectName(name)
            figure_dock.setFloating(False)
            figure_dock.setWindowTitle(name)
            self.setup_figure_canvas(figure_dock)
            figure_dock.toolbar.hide()

            self.parent.addDockWidget(Qt.RightDockWidgetArea, figure_dock)
            self.parent.dock_dict[name] = figure_dock
            if len(self.parent.dock_dict) > 3:
                self.parent.tabifyDockWidget(self.get_dock(), figure_dock)
        except Exception as e:
            logger.error(e)

    def get_terminal(self):
        return self.parent.dock_dict[self.DefaultTerminalName].widget()

    def get_figure(self, name=None) -> Figure:
        if name is None:
            return self.default_figure

        if name not in self.parent.dock_dict:
            raise KeyError('No figure named {}'.format(name))
        return self.parent.dock_dict[name].figure

    def get_dock(self, name=None) -> QDockWidget:
        if name is None:
            return self.default_dock

        if name not in self.parent.dock_dict:
            raise KeyError('No dock widget named {}'.format(name))
        return self.parent.dock_dict[name]

    def onDockMenuSelected(self, action):
        try:
            name = action.text()
            widget = self.parent.dock_dict[name]
            if not widget.isVisible():
                widget.setVisible(True)
                action.setChecked(True)
            else:
                widget.setVisible(False)
                action.setChecked(False)

        except Exception as e:
            print(e)

    def clear(self):
        pass

