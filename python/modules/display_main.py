import json
import os

from . import QtCore, QtGui, QtWidgets
from . import icetray, dataio, dataclasses, simclasses, santa
from . import expanduser, geometry_filename, km3net_seatray, icecube_icetray, nan
from . import pulseType, particleType, selectedPulses, selectedParticles


from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from .display_classes import ComboTextBox, CheckboxScroll
from .display_canvas import SantaCanvas
from .function_wrapper import dom_z


if km3net_seatray:
    from . import antares_common

def GeometrySearch(infile):
    geometry = None
    detector_depth = None
    frame = infile.pop_frame()
    while frame.Stop != icetray.I3Frame.DAQ and frame.Stop != icetray.I3Frame.Physics:
        if frame.Has('I3Geometry'):
            geometry = frame['I3Geometry']
            break    
        frame = infile.pop_frame()

    if geometry:
        allOMs = geometry.omgeo.keys()
        ##detector_depth =[ dom_z(geometry, max(allOMs)) - 30., dom_z(geometry, min(allOMs)) + 50.]
        detector_depth =[ -510, 510] # Hardcoded for now
    return geometry, detector_depth


class SantaDisplay(QtWidgets.QMainWindow):
    def __init__(self):
        self.infile = None
        self.frame  = None
        self.pulseSeriesList  = None
        self.recoList = None
        self.selected_pulses = []
        self.selected_pulse_main = None
        self.selected_recos = []
        self.profile_path = os.path.expanduser('~/.santa_event_display_profile.json')
        #self.strings   = array([86])

        QtWidgets.QMainWindow.__init__(self)

        self.setGeometry(50, 50, 1100, 700)
        self.setWindowTitle('SANTA event display')
        self.setWindowIcon(QtGui.QIcon('../resources/display-icon.png'))
        
        # Main container
        self.mainFrame = QtWidgets.QFrame(self)
        self.canvas = SantaCanvas(self.mainFrame, width=11, height=11, dpi=100)
        self.load_profile()
        self.toolbar = NavigationToolbar(self.canvas, self.mainFrame)
        self.setControlCenter()

        mainBox = QtWidgets.QHBoxLayout(self.mainFrame)
        mainBox.setContentsMargins(0, 0, 0, 0)
        mainBox.setSpacing(4)
        mainBox.addWidget(self.canvas, 4)
        mainBox.addWidget(self.controlCenter, 1)
        self.mainFrame.setLayout(mainBox)

        self.setCentralWidget(self.mainFrame)

        self.menubar = self.santaMenu()
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready!')

        # Ipython interactive console / push frame into it
        try:
            from modules.ipython_console import IpythonConsole
            self.console = IpythonConsole()
            self.console.show()
        except:
            self.console = None
            print('SANTA-display: interactive console could not be loaded. The viewer will still work, but you will not be able to access the frame objects from a terminal')

    # Control bar to the right side
    def setControlCenter(self):
        self.controlCenter = QtWidgets.QWidget()
        self.controlCenter.setMinimumWidth(280)
        self.controlLayout = QtWidgets.QVBoxLayout()
        self.controlLayout.setSpacing(8)
        self.controlLayout.setContentsMargins(6, 6, 6, 6)

        self.openFileButton = QtWidgets.QPushButton('Open file')
        self.openFileButton.clicked.connect(self.openI3File)
        self.firstFrameButton = QtWidgets.QPushButton('<<')
        self.firstFrameButton.clicked.connect(self.firstFrame)
        self.previousFrameButton = QtWidgets.QPushButton('<')
        self.previousFrameButton.clicked.connect(self.previousFrame)
        self.nextFrameButton = QtWidgets.QPushButton('>')
        self.nextFrameButton.clicked.connect(self.nextFrame)
        self.lastFrameButton = QtWidgets.QPushButton('>>')
        self.lastFrameButton.clicked.connect(self.lastFrame)
        self.refreshPlotsButton = QtWidgets.QPushButton('Refresh')
        self.refreshPlotsButton.clicked.connect(self.refreshPlots)
        self.imageParamsButton = QtWidgets.QPushButton('Image params')
        self.imageParamsButton.clicked.connect(self.openImageParameters)

        navigationBox = QtWidgets.QGridLayout()
        navigationBox.addWidget(self.openFileButton, 0, 0, 1, 4)
        navigationBox.addWidget(self.firstFrameButton, 1, 0)
        navigationBox.addWidget(self.previousFrameButton, 1, 1)
        navigationBox.addWidget(self.nextFrameButton, 1, 2)
        navigationBox.addWidget(self.lastFrameButton, 1, 3)
        navigationBox.addWidget(self.refreshPlotsButton, 2, 0, 1, 4)
        navigationBox.addWidget(self.imageParamsButton, 3, 0, 1, 4)
        navigationBox.setColumnStretch(0, 1)
        navigationBox.setColumnStretch(1, 1)
        navigationBox.setColumnStretch(2, 1)
        navigationBox.setColumnStretch(3, 1)

        self.frameLabel = QtWidgets.QLabel('Frame: 0 / 0', self.controlCenter)
        self.frameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.frameSpin = QtWidgets.QSpinBox(self.controlCenter)
        self.frameSpin.setMinimum(1)
        self.frameSpin.setMaximum(1)
        self.frameSpin.setEnabled(False)
        self.frameSpin.setKeyboardTracking(False)
        self.frameSpin.valueChanged.connect(self.gotoFrame)

        self.fileLabel = QtWidgets.QLabel('File: None', self.controlCenter)
        self.fileLabel.setWordWrap(True)
        self.fileLabel.setMinimumHeight(40)

        self.strSelectorBox = ComboTextBox(self.controlCenter)
        self.simplify = QtWidgets.QCheckBox('Selected info only', self.controlCenter)
        self.simplify.setChecked(True)
        self.simplify.stateChanged.connect(self.refreshLists)

        self.logQ     = QtWidgets.QCheckBox('Plot log(Q)', self.controlCenter)
        self.integrate= QtWidgets.QCheckBox('Integrate Q / show first only', self.controlCenter)

        self.seriesScroll = CheckboxScroll(self.controlCenter)
        self.recoScroll   = CheckboxScroll(self.controlCenter)

        self.seriesGroup = QtWidgets.QGroupBox('Pulse series', self.controlCenter)
        self.recoGroup = QtWidgets.QGroupBox('Reco objects', self.controlCenter)
        seriesLayout = QtWidgets.QVBoxLayout()
        seriesLayout.setContentsMargins(4, 4, 4, 4)
        seriesLayout.addWidget(self.seriesScroll)
        self.seriesGroup.setLayout(seriesLayout)
        recoLayout = QtWidgets.QVBoxLayout()
        recoLayout.setContentsMargins(4, 4, 4, 4)
        recoLayout.addWidget(self.recoScroll)
        self.recoGroup.setLayout(recoLayout)

        self.controlLayout.addLayout(navigationBox)
        self.controlLayout.addWidget(self.frameLabel)
        self.controlLayout.addWidget(self.frameSpin)
        self.controlLayout.addWidget(self.fileLabel)
        self.controlLayout.addWidget(self.strSelectorBox)
        self.controlLayout.addWidget(self.toolbar)
        self.controlLayout.addWidget(self.simplify)
        self.controlLayout.addWidget(self.logQ)
        self.controlLayout.addWidget(self.integrate)
        self.controlLayout.addWidget(self.seriesGroup)
        self.controlLayout.addWidget(self.recoGroup)
        self.controlLayout.addStretch(1)
        self.controlCenter.setLayout(self.controlLayout)
     

    def santaMenu(self):
        # Actions
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)

        openFile = QtWidgets.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.openI3File)

        # Menu buttons
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(exitAction)

        return menubar

    def openI3File(self):
        self.canvas.detectorGeometry = None
        if self.infile is not None:
            self.infile.close()

        self.infile_name, _filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', expanduser('~'))
        if not self.infile_name:
            return

        self.infile = dataio.I3File(self.infile_name, 'r')
        self.fileLabel.setText('File: %s' % self.infile_name)
        self.statusbar.showMessage('Opening file and searching for geometry...')

        self.canvas.detectorGeometry, self.canvas.detectorDepth = GeometrySearch(self.infile)

        if self.canvas.detectorGeometry is None:
            self.statusbar.showMessage('No geometry in input file, loading default geometry...')
            try:
                ginfile = dataio.I3File(geometry_filename)
                self.canvas.detectorGeometry, self.canvas.detectorDepth = GeometrySearch(ginfile)
                ginfile.close()
            except:
                QtWidgets.QMessageBox.warning(self, 'Geometry load failed',
                    'Could not load default geometry from usr_cfg. Check the configuration file.')
                return
        else:
            self.statusbar.showMessage('Geometry definition found in input file')

        self.apply_profile_detector_depth()

        self.total_frames = 1
        self.current_frame = 0

        for _ in self.infile:
            self.total_frames += 1

        self.infile.close()
        self.infile = dataio.I3File(self.infile_name, 'r')
        self.frameSpin.setMaximum(max(self.total_frames, 1))
        self.frameSpin.setEnabled(True)
        self.frameLabel.setText('Frame: 0 / %i' % self.total_frames)
        self.statusbar.showMessage('Physics frames in file: %i' % self.total_frames)
        self.nextFrame()

    def apply_profile_detector_depth(self):
        if hasattr(self.canvas, 'detectorDepth') and isinstance(self.canvas.detectorDepth, (list, tuple)):
            try:
                manual_depth = [float(self.canvas.detectorDepth[0]), float(self.canvas.detectorDepth[1])]
                self.canvas.detectorDepth = manual_depth
            except Exception:
                pass

    def load_profile(self):
        if not os.path.isfile(self.profile_path):
            return
        try:
            with open(self.profile_path, 'r') as profile_file:
                data = json.load(profile_file)
            if 'font_scale' in data:
                self.canvas.font_scale = float(data['font_scale'])
                self.canvas.fontP.set_size(self.canvas.get_font_size())
            if 'xsize' in data:
                self.canvas.xsize = float(data['xsize'])
            if 'detector_depth' in data and isinstance(data['detector_depth'], list) and len(data['detector_depth']) == 2:
                self.canvas.detectorDepth = [float(data['detector_depth'][0]), float(data['detector_depth'][1])]
        except Exception:
            pass

    def save_profile(self):
        try:
            profile_data = {
                'font_scale': self.canvas.font_scale,
                'xsize': self.canvas.xsize,
                'detector_depth': [self.canvas.detectorDepth[0], self.canvas.detectorDepth[1]]
            }
            with open(self.profile_path, 'w') as profile_file:
                json.dump(profile_data, profile_file, indent=2)
        except Exception:
            pass

    def nextFrame(self):
        if self.infile is None:
            self.statusbar.showMessage('Open a file first.')
            return
        if not self.infile.more():
            self.statusbar.showMessage('No more frames in file.')
            return

        self.frame = self.infile.pop_physics()
        self.current_frame += 1

        if self.console is not None:
            self.console.updateFrame(self.frame)

        self.updateFrameStatus()
        self.statusbar.showMessage('Physics frame %i / %i' % (self.current_frame, self.total_frames))
        self.refreshLists()
        self.refreshPlots()

    def previousFrame(self):
        if self.infile is None:
            self.statusbar.showMessage('Open a file first.')
            return
        if self.current_frame <= 1:
            self.statusbar.showMessage('Already at the first frame.')
            return
        self.gotoFrameIndex(self.current_frame - 1)

    def firstFrame(self):
        if self.infile is None:
            return
        self.gotoFrameIndex(1)

    def lastFrame(self):
        if self.infile is None:
            return
        self.gotoFrameIndex(self.total_frames)

    def gotoFrame(self):
        if self.infile is None:
            return
        target = self.frameSpin.value()
        if target == self.current_frame:
            return
        self.gotoFrameIndex(target)

    def gotoFrameIndex(self, target):
        if self.infile is None or target < 1 or target > self.total_frames:
            return
        self.infile.close()
        self.infile = dataio.I3File(self.infile_name, 'r')
        for _ in range(target - 1):
            self.infile.pop_physics()
        self.current_frame = target - 1
        self.nextFrame()

    def updateFrameStatus(self):
        self.frameLabel.setText('Frame: %i / %i' % (self.current_frame, self.total_frames))
        self.frameSpin.blockSignals(True)
        self.frameSpin.setValue(self.current_frame)
        self.frameSpin.blockSignals(False)
        self.previousFrameButton.setEnabled(self.current_frame > 1)
        self.firstFrameButton.setEnabled(self.current_frame > 1)
        self.nextFrameButton.setEnabled(self.current_frame < self.total_frames)
        self.lastFrameButton.setEnabled(self.current_frame < self.total_frames)


    def refreshPlots(self):
        if self.infile == None:
            self.openI3File()
        series_name_list = self.seriesScroll.checkAllItems(self.pulseSeriesList)
        recos_name_list = self.recoScroll.checkAllItems(self.recoList)
        main_series = self.seriesScroll.getMainSeries(self.pulseSeriesList)
        print(main_series)
        self.canvas.update_figure(self.frame, series_name_list, recos_name_list, 
                                  main_series, self.strSelectorBox.selectedItem(), 
                                  self.logQ.isChecked(), self.integrate.isChecked())
        
    def openImageParameters(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Image parameters')
        layout = QtWidgets.QVBoxLayout(dialog)

        label = QtWidgets.QLabel('Scale plot labels and legend')
        layout.addWidget(label)

        slider_layout = QtWidgets.QHBoxLayout()
        self.imageScaleSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal, dialog)
        self.imageScaleSlider.setMinimum(50)
        self.imageScaleSlider.setMaximum(200)
        self.imageScaleSlider.setTickInterval(10)
        self.imageScaleSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.imageScaleSlider.setValue(int(self.canvas.font_scale * 100))

        value_label = QtWidgets.QLabel('%d%%' % self.imageScaleSlider.value(), dialog)
        self.imageScaleSlider.valueChanged.connect(lambda value: value_label.setText('%d%%' % value))

        slider_layout.addWidget(self.imageScaleSlider)
        slider_layout.addWidget(value_label)
        layout.addLayout(slider_layout)

        zoom_label = QtWidgets.QLabel('X-axis zoom', dialog)
        layout.addWidget(zoom_label)
        self.imageZoomSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal, dialog)
        self.imageZoomSlider.setMinimum(10)
        self.imageZoomSlider.setMaximum(4000)
        self.imageZoomSlider.setTickInterval(100)
        self.imageZoomSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.imageZoomSlider.setValue(int(self.canvas.xsize))

        zoom_value_label = QtWidgets.QLabel('%d' % self.imageZoomSlider.value(), dialog)
        self.imageZoomSlider.valueChanged.connect(lambda value: zoom_value_label.setText('%d' % value))
        zoom_layout = QtWidgets.QHBoxLayout()
        zoom_layout.addWidget(self.imageZoomSlider)
        zoom_layout.addWidget(zoom_value_label)
        layout.addLayout(zoom_layout)

        depth_label = QtWidgets.QLabel('Detector depth range (min, max)', dialog)
        layout.addWidget(depth_label)
        depth_layout = QtWidgets.QHBoxLayout()
        minDepthEdit = QtWidgets.QLineEdit(str(self.canvas.detectorDepth[0]), dialog)
        maxDepthEdit = QtWidgets.QLineEdit(str(self.canvas.detectorDepth[1]), dialog)
        validator = QtGui.QDoubleValidator(dialog)
        minDepthEdit.setValidator(validator)
        maxDepthEdit.setValidator(validator)
        depth_layout.addWidget(minDepthEdit)
        depth_layout.addWidget(maxDepthEdit)
        layout.addLayout(depth_layout)
        slider_layout.addWidget(self.imageScaleSlider)
        slider_layout.addWidget(value_label)
        layout.addLayout(slider_layout)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, dialog)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        def accept_params():
            try:
                new_xsize = float(self.imageZoomSlider.value())
                new_min_depth = float(minDepthEdit.text())
                new_max_depth = float(maxDepthEdit.text())
            except ValueError:
                QtWidgets.QMessageBox.warning(dialog, 'Invalid input', 'Detector depths and zoom must be numeric values.')
                return
            if new_min_depth >= new_max_depth:
                QtWidgets.QMessageBox.warning(dialog, 'Invalid depth range', 'Minimum depth must be less than maximum depth.')
                return
            self.canvas.set_font_scale(self.imageScaleSlider.value() / 100.0)
            self.canvas.xsize = new_xsize
            self.canvas.detectorDepth = [new_min_depth, new_max_depth]
            self.save_profile()
            self.refreshPlots()
            dialog.accept()

        button_box.accepted.disconnect()
        button_box.accepted.connect(accept_params)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            pass
    def refreshLists(self):
        if self.simplify.isChecked():
            self.readFramePulses(True)
            self.readFrameRecos(True)
        else:
            self.readFramePulses(False)
            self.readFrameRecos(False)


    def readFramePulses(self, selected):
        if self.pulseSeriesList is not None:
            previousList = self.pulseSeriesList
            self.selected_pulses = self.seriesScroll.checkAllItems(self.pulseSeriesList)
            self.selected_pulse_main = self.seriesScroll.getMainSeries(self.pulseSeriesList)
        else:
            previousList = []
        self.pulseSeriesList = []
        for one_key in self.frame.keys():
            try:
                type(self.frame[one_key])
            except:
                continue
            if type(self.frame[one_key]) in pulseType:
                if selected:
                    for oneSelected in selectedPulses:
                        if oneSelected in one_key:
                            self.pulseSeriesList.append(one_key)
                            break
                else:
                    self.pulseSeriesList.append(one_key)
        self.pulseSeriesList.sort()

        mainItem = None
        if self.selected_pulse_main in self.pulseSeriesList:
            mainItem = self.selected_pulse_main
        else:
            for selected in self.selected_pulses:
                if selected in self.pulseSeriesList:
                    mainItem = selected
                    break

        self.seriesScroll.updateItems(self.pulseSeriesList, previousList,
                                      selectedItems=self.selected_pulses,
                                      mainItem=mainItem)


    def readFrameRecos(self, selected):
        if self.recoList is not None:
            previousList = self.recoList
            self.selected_recos = self.recoScroll.checkAllItems(self.recoList)
        else:
            previousList = []
        self.recoList = []

        # Find the MC information, put it as separate particles
        # This function had to change because of deprecation of mctree methods
        # Selecting the most energetic track and cascade
        #if (not self.frame.Has('MCMostEtrack')) and (not self.frame.Has('MCMostEcascade')):
        trackE = 0.
        cascadeE = 0.
        for one_key in self.frame.keys():
            if 'MCTree' in one_key and type(self.frame[one_key]) == dataclasses.I3MCTree:
                print(self.frame[one_key])

                # Loop over all particles
                for p in self.frame[one_key]:
                    if p.type == p.ParticleType.Hadrons:
                        if p.energy > cascadeE:
                            cascadeE = p.energy
                            self.frame['MCMostEcascade'] = p
                    elif abs(p.pdg_encoding) == 13:
                        if p.energy > trackE:
                            trackE = p.energy
                            self.frame['MCMostEtrack'] = p
                    
        for one_key in self.frame.keys():
            try:
                type(self.frame[one_key])
            except:
                continue
            if type(self.frame[one_key]) in particleType:
                if selected:
                    for oneSelected in selectedParticles:
                        if oneSelected in one_key:
                            self.recoList.append(one_key)
                            break
                else:
                    self.recoList.append(one_key)
        self.recoList.sort()

        self.recoScroll.updateItems(self.recoList, previousList,
                                    selectedItems=self.selected_recos) 

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtWidgets.QMessageBox.Yes | 
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            if self.console:
                self.console.close()
            event.accept()
        else:
            event.ignore()
