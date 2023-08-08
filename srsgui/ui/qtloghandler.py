##! 
##! Copyright(c) 2022, 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

from logging import getLogger, Handler

from .qt.QtCore import QObject
from .qt.QtCore import Signal

RedError = '<font color="red"><b>-ERROR-</b></font>'
logger = getLogger(__name__)


class QtLogHandler(Handler):
    """
    Subclass logging.Handler to be used with QTextBrowser widget.
    """

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
        self.text_browser.append(message.replace('-ERROR-', RedError, 1))
        sb = self.text_browser.verticalScrollBar()
        sb.setValue(sb.maximum())

