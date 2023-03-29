
import logging
from .jsonmodel import JsonModel

from .qt.QtCore import Qt
from .qt.QtWidgets import QWidget
from .ui_deviceinfowidget import Ui_DeviceInfoWidget

logger = logging.getLogger(__name__)


class DeviceInfoWidget(QWidget, Ui_DeviceInfoWidget):
    def __init__(self, parent=None):
        super(DeviceInfoWidget, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.inst = None
        self.name = None
        self.query_included = False

        self.model = JsonModel()
        self.model._headers = ["   Command  ", "   Value  "]
        self.tree_view.setModel(self.model)

        self.include_checkbox.stateChanged.connect(self.on_include_changed)
        self.update_button.clicked.connect(self.on_update_clicked)
        self.capture_button.clicked.connect(self.on_capture_clicked)

    def set_inst(self, name, inst):
        self.inst = inst
        self.name = name

    def on_include_changed(self, state):
        self.query_included = state

    def on_update_clicked(self):
        inst = self.inst
        browser = self.text_browser

        if inst.is_connected():
            msg = ''  # Name: {} \n S/N: {} \n F/W version: {} \n\n'.format(*inst.check_id())
            msg += '  * Info *\n {} \n\n'.format(inst.get_info())
            msg += '  * Status *\n {} \n'.format(inst.get_status())
        else:
            msg = "Disconnected"

        browser.clear()
        browser.append(msg)
        logger.debug('{}: {}'.format(self.name, msg.replace('\n', '')))

    def on_capture_clicked(self):
        if self.inst is not None and self.inst.is_connected():
            capture = self.inst.capture_commands(self.query_included)
            self.model.load(capture, False)
