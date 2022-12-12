#!/usr/bin/env python3

import sys
from pathlib import Path
from srsgui.ui.qt.QtWidgets import QApplication
from .ui.taskmain import TaskMain


def main():
    app = QApplication(sys.argv)
    main_window = TaskMain()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
