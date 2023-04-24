
from srsgui.ui.qt.QtCore import QObject, QThread, QModelIndex, Signal
from .commanditem import Index


class CommandWorker(QObject):
    query_processed = Signal(tuple)
    set_processed = Signal(tuple)
    set_command_sent = Signal(str, str)
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
        item.set_value(v)
        sent_command = self.construct_set_command_string(item, v)
        self.set_command_sent.emit(sent_command, None)
        print(sent_command)
        
        new_value = item.query_value()
        changed = old_value != new_value
        self.set_processed.emit((index, new_value, changed))

    def construct_set_command_string(self, item, value):
        self.buffer = []
        self.get_item_name(item)
        self.buffer.reverse()
        if type(value) is str:
            s = '{} = "{}"'.format('.'.join(self.buffer), value)
        else:
            s = '{} = {}'.format('.'.join(self.buffer), value)

        s = s.replace('.[', '[')
        return s

    def get_item_name(self, item):
        if item is None:
            return None
        elif item.comp_type == Index:
            if type(item.comp) is str:
                self.buffer.append('["{}"]'.format(item.name))
                self.get_item_name(item.parent())
            else:
                self.buffer.append('[{}]'.format(item.name))
                self.get_item_name(item.parent())
        else:
            self.buffer.append(item.name)
            self.get_item_name(item.parent())


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

