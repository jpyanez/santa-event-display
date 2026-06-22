from os import getpid
from . import QtGui, QtWidgets, icetray, dataclasses, simclasses, dataio
from PyQt5.QtWidgets import QMainWindow

import sys
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

class QIPythonWidget(RichJupyterWidget):
    """ Convenience class for a live IPython console widget. We can replace the standard banner using the customBanner argument"""
    def __init__(self,customBanner=None,*args,**kwargs):
        if customBanner!=None: self.banner=customBanner
        super(QIPythonWidget, self).__init__(*args,**kwargs)

        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt5'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            # app = QtWidgets.QApplication.instance()
            # if app is not None:
            #     app.quit()
        self.exit_requested.connect(stop)

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)
    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()    
    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)        
    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)


class IpythonConsole(QMainWindow):
    """ Main GUI Widget including a button and IPython Console widget inside vertical layout """
    def __init__(self, parent=None):
        super(IpythonConsole, self).__init__(parent)
        self.app = QtWidgets.QApplication(sys.argv)
        self.setWindowIcon(QtGui.QIcon('../resources/display-icon.png'))
        self.setWindowTitle('SANTA interactive console')
        print('Reached here')
        layout = QtGui.QVBoxLayout(self)
        self.ipyConsole = QIPythonWidget(customBanner="Ipython console for the SANTA viewer\n")

        layout.addWidget(self.ipyConsole)        
        self.ipyConsole.pushVariables({"dataclasses":dataclasses, "simclasses":simclasses,
                                       "icetray":icetray, "dataio":dataio,
                                       "frame":None})
        self.ipyConsole.printText("Use the 'whos' command for information.")              

    def updateFrame(self, frame):
        self.ipyConsole.pushVariables({"frame":frame})

