from logging import getLogger, Handler

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal

logger = getLogger(__name__)


class QtLogHandler(Handler):
    class SignalObject(QObject):
        new_message = Signal(str)

    def __init__(self, text_browser):
        super().__init__()
        self.sig = QtLogHandler.SignalObject()
        if not hasattr(text_browser, 'append'):
            logger.error("QtHandler needs a handler with a method append.")
            raise AttributeError

        self.text_browser = text_browser
        self.sig.new_message.connect(self.append)
        # self.sb = self.text_browser.verticalScrollBar()

    def emit(self, record):
        message = self.format(record)
        # print(type(message), 'Format:::: {}'.format(message))
        if message:
            self.sig.new_message.emit(message)
            # self.append(message)

    def append(self, message):
        self.text_browser.append(message)
        sb = self.text_browser.verticalScrollBar()
        sb.setValue(sb.maximum())

