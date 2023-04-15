
from srsgui.ui.qt.QtCore import QObject, QThread, QModelIndex, Signal


class CommandWorker(QObject):
    query_processed = Signal(tuple)
    set_processed = Signal(tuple)

    def handle_query(self, index: QModelIndex):
        item = index.internalPointer()
        old_value = item.value
        new_value = item.query_value()
        changed = old_value != new_value
        # print('Query cmd: {}, Reply:{}'.format(item.name, new_value))
        self.query_processed.emit((index, new_value, changed))

    def handle_set(self, cmd_tuple):
        index = cmd_tuple[0]
        v = cmd_tuple[1]

        item = index.internalPointer()
        old_value = item.value
        print('Set starts')
        item.set_value(v)
        new_value = item.query_value()
        changed = old_value != new_value
        # print('Set cmd: {}, Parameter: {}'.format(item.name, new_value))
        self.set_processed.emit((index, new_value, changed))


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

