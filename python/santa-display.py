#!/usr/bin/env python3

import os, sys
os.environ['QT_API'] = 'pyqt5'

from PyQt5 import QtCore, QtGui, QtWidgets


from modules.mpl_config import configureMatplotlib
from modules.display_main import SantaDisplay

def main():
    """ SANTA display main function """
    configureMatplotlib()
    app = QtWidgets.QApplication(sys.argv)
    display = SantaDisplay(sys.argv)
    display.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
