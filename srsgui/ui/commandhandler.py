##! 
##! Copyright(c) 2022, 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

import time
import logging
from .qt.QtCore import QObject, QThread, Signal, Slot
from .qt.QtWidgets import QMessageBox

from srsgui.inst.instrument import Instrument

logger = logging.getLogger(__name__)


class CommandWorker(QObject):
    command_processed = Signal(str, str)
    inst_dict = {}
    figure_dict = {}

    def _check_connected(self, inst):
        if isinstance(inst, Instrument) and inst.is_connected():
            return True
        # raise ValueError('"{}" is NOT connected'.format(inst.get_name()))
        return False

    def handle_command(self, cmd, reply):
        try:
            reply = 'Not connected'
            keys = list(self.inst_dict.keys())

            inst_name = cmd.split('.', 1)[0]
            if inst_name in keys:
                inst = self.inst_dict[inst_name]
                if self._check_connected(inst):
                    reply = self.eval(cmd)
            elif inst_name in self.figure_dict:
                reply = self.eval(cmd)
            else:
                inst_name = cmd.split(':', 1)[0]
                if inst_name in keys:
                    inst = self.inst_dict[inst_name]
                    if self._check_connected(inst):
                        command = cmd.split(':', 1)[1]
                        reply = inst.handle_command(command)
                else:
                    if keys:
                        inst = self.inst_dict[keys[0]]
                        if self._check_connected(inst):
                            reply = inst.handle_command(cmd)
            self.command_processed.emit(cmd, reply)
        except Exception as e:
            logger.error('Error from CommandHandler: {}'.format(str(e)))

    def eval(self, cmd):
        if '=' in cmd:
            # TODO: check if assigned to a command
            exec(cmd, {}, self.inst_dict)
            return ''
        else:
            """
            # alternative eval function: does not work with IndexCommand yet
            try:
                tokens = cmd.split('.')
                if tokens[0] in self.inst_dict:
                    attr = self.inst_dict[tokens[0]]
                    for token in tokens[1:]:
                        attr = getattr(attr, token)
                    return str(attr)
                elif tokens[0] in self.figure_dict:
                    attr = self.figure_dict[tokens[0]]
                    for token in tokens[1:]:
                        attr = getattr(attr, token)
                    return str(attr)
                else:
                    KeyError('Unknown attribute: {}'.format(tokens[0]))
            except Exception as e:
                logger.error(e)
                return ''
            """
            reply = eval(cmd, self.figure_dict, self.inst_dict)
            if reply is not None:
                return str(reply)
            return ''


class CommandHandler(QObject):
    request_command = Signal(str, str)
    command_processed = Signal(str, str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.worker_thread = QThread()

        self.worker = CommandWorker()
        self.worker.moveToThread(self.worker_thread)
        self.request_command.connect(self.worker.handle_command)
        self.worker.command_processed.connect(self.command_processed)
        self.worker_thread.start()

    def process_command(self, cmd, reply):
        self.worker.inst_dict = self.parent.inst_dict
        self.worker.figure_dict = self.parent.dock_handler.get_figure_dict()
        self.request_command.emit(cmd, reply)

    def process_command_without_figure_dict(self, cmd, reply):
        """
        Handles a command from a parent without dock_handler
        """
        self.worker.inst_dict = self.parent.inst_dict
        self.worker.figure_dict = {}
        self.request_command.emit(cmd, reply)

    def stop(self):
        self.worker_thread.quit()
        self.worker_thread.wait()

