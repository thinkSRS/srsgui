
import time
import logging
from .qt.QtCore import QThread, Signal
from .qt.QtWidgets import QMessageBox

from srsgui.inst.instrument import Instrument

logger = logging.getLogger(__name__)


class CommandHandler(QThread):
    command_processed = Signal(str, str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.inst_dict = self.parent.inst_dict
        self.terminal = self.parent.terminal_widget
        self.keep_running = True
        self.cmd_queue = []

    def run(self):
        while self.keep_running:
            if self.cmd_queue:
                cmd = self.cmd_queue.pop()
                self.handle_command(cmd, '')
            else:
                self.msleep(10)

    def stop(self):
        self.keep_running = False

    def _check_connected(self, inst):
        if isinstance(inst, Instrument) and inst.is_connected():
            return True
        # raise ValueError('"{}" is NOT connected'.format(inst.get_name()))
        return False

    def process_command(self, cmd, reply):
        self.cmd_queue.append(cmd)

    def handle_command(self, cmd, reply):
        try:
            reply = 'Not connected'
            keys = list(self.parent.inst_dict.keys())
            inst_name = cmd.split('.', 1)[0]
            if inst_name in keys:
                inst = self.parent.get_inst(inst_name)
                if self._check_connected(inst):
                    reply = self.eval(cmd)
            elif inst_name in self.parent.figure_dict:
                reply = self.eval(cmd)
            else:
                inst_name = cmd.split(':', 1)[0]
                if inst_name in keys:
                    inst = self.parent.get_inst(inst_name)
                    if self._check_connected(inst):
                        command = cmd.split(':', 1)[1]
                        reply = inst.handle_command(command)
                else:
                    inst = self.parent.get_inst(keys[0])
                    if self._check_connected(inst):
                        reply = inst.handle_command(cmd)

            self.command_processed.emit(cmd, reply)
        except Exception as e:
            logger.error('Error from CommandHandler: {}'.format(str(e)))

    def eval(self, cmd):
        if '=' in cmd:
            # TODO: check if assigned to a command
            exec(cmd, {}, self.parent.inst_dict)
            return ''
        else:
            reply = eval(cmd, self.parent.figure_dict, self.parent.inst_dict)
            if reply is not None:
                return str(reply)
            return ''
