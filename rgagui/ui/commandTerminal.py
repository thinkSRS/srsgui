

from PyQt5.QtWidgets import QFrame, QMessageBox

from rga.base import Instrument

from .ui_commandTerminal import Ui_CommandTerminal


class CommandTerminal(QFrame, Ui_CommandTerminal):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.parent = parent
        if not hasattr(parent, 'inst_dict'):
            raise AttributeError('Parent has no inst_dict')

        self.pbClear.clicked.connect(self.on_clear)
        self.pbSend.clicked.connect(self.on_send)
        self.leCommand.returnPressed.connect(self.on_send)

    def on_clear(self):
        self.tbCommand.clear()

    def on_send(self):
        try:
            inst = self.parent.get_dut()
            if not (isinstance(inst, Instrument) and inst.is_connected()):
                msg_box = QMessageBox()
                msg_box.setText("No DUT connected")
                msg_box.exec()
                return

            cmd = self.leCommand.text().strip()
            self.tbCommand.append(cmd)
            self.leCommand.clear()

            if cmd.lower() == 'cls':
                self.tbCommand.clear()
                return

            keys = self.parent.inst_dict.keys()
            if cmd.split('.', 1)[0] in keys:
                reply = self.eval(cmd)
            else:
                inst_name = cmd.split(':', 1)[0]
                if inst_name in keys:
                    command = cmd.split(':', 1)[1]
                    reply = self.parent.inst_dict[inst_name].handle_command(command)
                else:
                    reply = inst.handle_command(cmd)

            if reply != '':
                self.tbCommand.append(reply)

        except Exception as e:
            self.tbCommand.append('Error: {}'.format(str(e)))

    def eval(self, cmd):
        if '=' in cmd:
            exec(cmd, {}, self.parent.inst_dict)
            return ''
        else:
            reply = eval(cmd, {}, self.parent.inst_dict)
            if reply is not None:
                return str(reply)
            return ''
