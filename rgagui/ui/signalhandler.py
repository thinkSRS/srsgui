
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
from matplotlib.figure import Figure

from rgagui.task.callbacks import Callbacks


class SignalHandler(QObject, Callbacks):

    # Signal when task started
    sig_started = Signal()

    # Signal when task finished
    sig_finished = Signal()

    # signal for text output to UI
    sig_text_available = Signal(str)

    # emit to change UI input panel values for new parameters
    sig_parameter_changed = Signal()

    # Update a specific figure when multiple figures are used in a task
    sig_figure_update_requested = Signal(Figure)

    # emit when you need UI update for newly available data
    sig_data_available = Signal(dict)

    # signal used to get an answer for a question from UI
    sig_new_question = Signal(str, object)

    signals = [
        sig_started,
        sig_finished,
        sig_text_available,
        sig_parameter_changed,
        sig_figure_update_requested,
        sig_data_available,
        sig_new_question,
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

    def started(self):
        self.sig_started.emit()

    def finished(self):
        self.sig_finished.emit()

    def text_available(self, text: str):
        self.sig_text_available.emit(text)

    def parameter_changed(self):
        self.sig_parameter_changed.emit()

    def figure_update_requested(self, fig: Figure):
        self.sig_figure_update_requested.emit(fig)

    def data_available(self, data: dict):
        self.sig_data_available.emit(data)

    def new_question(self, question: str, return_type: object):
        self.sig_new_question.emit(question, return_type)

    def disconnect_all(self):
        for sig in self.signals:
            try:
                sig.disconnect()
            except Exception as e:
                print('{}'.format(e))
                pass
