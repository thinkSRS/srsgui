##! 
##! Copyright(c) 2022, 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

import logging

from srsgui.ui.qt.QtCore import QObject, QThread, QModelIndex, Signal
from .commanditem import Index

logger = logging.getLogger(__name__)


class CommandWorker(QObject):
    query_processed = Signal(tuple)
    set_processed = Signal(tuple)

    def handle_query(self, index: QModelIndex):
        try:
            item = index.internalPointer()
            old_value = item.value
            new_value = item.query_value()
            changed = old_value != new_value
            self.query_processed.emit((index, new_value, changed))
        except Exception as e:
            logger.error(e)

    def handle_set(self, cmd_tuple):
        try:
            index = cmd_tuple[0]
            v = cmd_tuple[1]

            item = index.internalPointer()
            old_value = item.value
            item.set_value(v)
            new_value = item.query_value()
            changed = old_value != new_value
            self.set_processed.emit((index, new_value, changed))
        except Exception as e:
            logger.error(e)


class CommandHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.worker_thread = QThread()

        self.worker = CommandWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

    def stop(self):
        self.worker_thread.quit()
        self.worker_thread.wait()
