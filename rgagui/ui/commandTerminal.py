

from PyQt5.QtWidgets import QFrame, QMessageBox

from rga.base import Instrument

from .ui_commandTerminal import Ui_CommandTerminal


class CommandTerminal(QFrame, Ui_CommandTerminal):
    """
    Terminal to control instruments defined in the .taskconfig file
           Type a command in one of the following ways

    inst_name:remote_command

           'inst_name' is the first item after the prefix  "inst:" in a line in
           the .taskconfig file. 'Remote_command' after the colon is a raw remote
           command of the instrument. Terminals send the 'remote_command' directly
           to the instrument 'inst_name', and display a reply if the instrument
           sends one back.

           dut:*idn?
           dut:mi10  - This is a RGA100 command to set scan intial mass to 10

    inst_name.instrument_command

           When you use .before a command, the command is interpreted as a Python
           instrument command or a method defined in the Instrument subclass,
           which is the third item in the line starting with 'inst:' used
           in .taskconfig file.

           inst_name.(components.)dir  - it shows all available components, commands,
                   and methods in the instrument or its component as a Python dictionary.

                        rga.dir
                        rga.status.dir

           rga.status.id_string  - this returns the id string. It is a Python instrument
                   command defined in the rga.status component.
           rga.scan.initial_mass = 10  - this changes the scan initial mass to 10.
           rga.scan.get_analog_scan()  - this is a method defined in the rga.scan component.

           With the prefix of 'inst_name:' or 'inst_name.', you can specify which
           instrument receive the following command, as either a raw remote command or
           a instrument command defined in a Instrument subclass.

    command

           if you type a command without 'inst_name.' or 'inst_name:', the command goes
           to the first instrument in the .taskconfig file. A command with dot(s) is
           interpreted as a Python instrument command or a method. A command without
           any dot will be sent directly to the first instrument in the .taskconfig file
           as a raw remote command.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.parent = parent
        if not hasattr(parent, 'inst_dict'):
            raise AttributeError('Parent has no inst_dict')
        self.pbClear.clicked.connect(self.on_clear)
        self.pbSend.clicked.connect(self.on_send)
        self.leCommand.returnPressed.connect(self.on_send)
        self.leCommand.setText("Type  'help'  for more info")
        self.leCommand.selectAll()

    def on_clear(self):
        self.tbCommand.clear()

    def _check_connected(self, inst):
        if not (isinstance(inst, Instrument) and inst.is_connected()):
            msg_box = QMessageBox()
            msg_box.setText('"{}" is NOT connected'.format(inst.get_name()))
            msg_box.exec()
            return False
        return True

    def on_send(self):
        try:
            cmd = self.leCommand.text().strip()
            reply = ''
            self.tbCommand.append(cmd)
            self.leCommand.clear()
            cmd_lower = cmd.lower()
            if cmd_lower == 'cls':
                self.tbCommand.clear()
                return

            if cmd_lower == 'help':
                self.tbCommand.append(self.__doc__)
                return

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

            if reply != '':
                self.tbCommand.append(reply)

        except Exception as e:
            self.tbCommand.append('Error: {}'.format(str(e)))

    def eval(self, cmd):
        if '=' in cmd:
            exec(cmd, {}, self.parent.inst_dict)
            return ''
        else:
            reply = eval(cmd, self.parent.figure_dict, self.parent.inst_dict)
            if reply is not None:
                return str(reply)
            return ''
