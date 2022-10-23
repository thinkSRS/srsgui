#!/usr/bin/env python3

import sys

from PyQt5.QtWidgets import QApplication
from .ui.calmain import CalMain


def main():
    app = QApplication(sys.argv)
    main_window = CalMain()
    main_window.show()
    app.exec()


if __name__ == '__main':
    main()


