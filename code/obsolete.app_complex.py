#!/Users/ssg/.pyenv/shims/python
# -*- coding: utf-8 -*-
import sys
import threading
from os import listdir
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QLabel, QSlider, QComboBox
from parameterSetup import ParameterSetup
import importlib
from dummyReadDaqServer import DummyReadDAQServer
from classifierClient import ClassifierClient
from connectionCheckClient import ConnectionCheckClient
from drawGraph import DynamicGraphCanvas, DynamicGraphCanvas4KS, DynamicGraphCanvas4KSHist
from predictionResultLabel import PredictionResultLabel
from fileManagement import filterByPrefix, getAllEEGFiles, getFileIDFromEEGFile

class RemApplication(QMainWindow):
    """
    GUI application, uses two classes
    - ClassifierClient (in classifierClient.py)
    - ReadDAQServer (in readDaqServer.py)
    """

    def __init__(self, host, port, args):

        # set parameters
        self.params = ParameterSetup()
        self.label_recordWaves = 'Record original wave'
        self.label_notRecordWaves = 'No wave recording'
        self.recordWaves = self.params.writeWholeWaves
        self.channelNum = 2 if self.params.showCh2 else 1
        # self.str_method_deep = "Deep Learning"
        # self.str_method_rf = "Random Forest"
        # self.str_method_classical = "Classical"
        # self.methodName = self.str_method_deep
        # self.setClassifierType(self.params)
        self.classifierType = "deep"
        self.extractorType = self.params.extractorType
        self.ch2_mode_str_video = "Video"
        self.ch2_mode_str_emg = "EMG"
        self.ch2_mode_str_none = "None"
        self.channelNumAlreadySelected = 0
        self.graphNum = 4
        self.port2 = port + 1
        self.defaultSleepTime = 1
        # self.channelNumForPrediction = 0

        super(RemApplication, self).__init__()
        self.initUI()
        # self.graph = tf.get_default_graph()
        ### moved below on 2020.2.24
        '''
        self.t = threading.Thread(target=self.start_reader, daemon=True)
        self.t.start()
        '''

    def start_reader(self):
        def to_f(inpt):
            try:
                return float(inpt)
            except Exception:
                return None

        statusbar = self.statusBar()
        try:
            '''
            if len(args) > 1:
                inputFileID = args[1]
                if inputFileID == 'm':
                    print('@ self.client = ClassifierClient(...) for len(args) > 1 and inputFileID == m')
                    self.client = ClassifierClient(channelOpt, self.recordWaves, self.extractorType, self.classifierType)
                else:
                    print('@ self.client = ClassifierClient(...) for len(args) > 1 and inputFileID != m')
                    self.client = ClassifierClient(channelOpt, self.recordWaves, self.extractorType, self.classifierType, inputFileID=inputFileID)
            else:
                print('@ self.client = ClassifierClient(...) for len(args) <= 1')
                self.client = ClassifierClient(channelOpt, self.recordWaves, self.extractorType, self.classifierType)
            self.client.hasGUI = True
            # print('classifierClient started by ' + str(channelOpt) + ' channel.')
            '''
            # below added on 2020.2.24
            self.client.predictionStateOn()

        except Exception as e:
            print('Exception in self.client = ...')
            statusbar.showMessage(str(e))
            raise e

        self.client.setGraph(self.listOfGraphs)
        self.client.setPredictionResult(self.listOfPredictionResults)
        self.client.setchi2ResLabel(self.chi2ResLabel)
        self.client.setdResLabel(self.dResLabel)
        self.client.setdGraph(self.dGraph)
        self.client.setdHist(self.dHist)

        try:
            if self.readFromDaq:
                module = importlib.import_module('readDaqServer')
                ReadDAQServer = getattr(module, 'ReadDAQServer')
                self.server = ReadDAQServer(self.client, self.recordWaves)
            else:
                self.server = DummyReadDAQServer(self.client, self.inputFileID, self.recordWaves, self.channelNum, self.offsetWindowID, self.sleepTime)

        except Exception as e:
            print(str(e))
            statusbar.showMessage(str(e))
            raise e

        self.server.serve()
        # self.t.start()
        ### if len(args) > 1:
        ###    self.server.setTrueLabels(self.listOfTrueLabels)
        message = 'successfully started!'
        statusbar.showMessage(message)

    # def stop_reader(self):
        # self.t.terminate()
        # self.t.join()

    # def run(self):
        ### with self.graph.as_default():
            # self.server.serve()

    ### below commented out on 2020.2.24
    '''
    def predictionStateOnEEGonly(self):
        if self.channelNumAlreadySelected == 0:
            self.client.params.useCh2ForReplace = False
            self.client.predictionStateOn()
            self.clientButton1chan.setChecked(True)
            self.channelNumAlreadySelected = 1
        else:
            if self.client.params.useCh2ForReplace == False:
                self.clientButton1chan.setChecked(True)
            else:
                self.clientButton1chan.setChecked(False)
        '''

    def predictionStateOnEEGandCh2(self):
        ### below added on 2020.2.24
        self.t = threading.Thread(target=self.start_reader, daemon=True)
        self.t.start()
        if self.channelNumAlreadySelected == 0:
            ### below commented out on 2020.2.24
            # self.client.params.useCh2ForReplace = True
            # self.client.predictionStateOn()
            self.clientButton2chan.setChecked(True)
            self.channelNumAlreadySelected = 1
        else:
            if self.client.params.useCh2ForReplace == True:
                self.clientButton2chan.setChecked(True)
            else:
                self.clientButton2chan.setChecked(False)

    def check_connection(self):
        statusbar = self.statusBar()
        try:
            self.check_client = ConnectionCheckClient()
            print('ConnectionCheckClient started.')
        except Exception as e:
            statusbar.showMessage(str(e))
            raise e

    def toggleWaveRecord(self):
        self.recordWaves = True
        self.waveRecordButton.setChecked(True)
        self.waveNotRecordButton.setChecked(False)

    def toggleWaveNotRecord(self):
        self.recordWaves = False
        self.waveRecordButton.setChecked(False)
        self.waveNotRecordButton.setChecked(True)

    '''
    def method_choice(self, text):
        self.methodName = text
        self.setClassifierType(self.params)
    '''

    '''
    def setClassifierType(self, params):
        if self.methodName == self.str_method_deep:
            self.classifierType = 'deep'
            self.extractorType = params.extractorType
        if self.methodName == self.str_method_rf:
            self.extractorType = 'freqHistoWithTime'
            self.classifierType = 'rf'
        if self.methodName == self.str_method_classical:
            self.extractorType = 'classical'
            self.classifierType = 'static'
    '''

    def ch2_thresh_change(self):
        ch2_thresh_slider_value = self.ch2_thresh_slider.value()
        self.client.ch2_thresh_value = ch2_thresh_slider_value / 4
        self.ch2_thresh.setText(str(self.client.ch2_thresh_value))

    def ch2_mode_choice(self, text):
        self.ch2_mode = text
        self.client.ch2_mode = self.ch2_mode
        if self.ch2_mode == self.ch2_mode_str_emg:
            self.client.ch2_standardize = 1
        else:
            self.client.ch2_standardize = 0

    def initUI(self):
        ### below commented out on 2020.2.24
        '''
        self.clientButton1chan = QtWidgets.QPushButton('Predict (EEG only)', self)
        self.clientButton1chan.setCheckable(True)
        # self.channelNumForPrediction = 1
        self.clientButton1chan.clicked.connect(self.predictionStateOnEEGonly)
        self.clientButton1chan.resize(self.clientButton1chan.sizeHint())
        self.clientButton1chan.move(5, 10)
        '''

        self.clientButton2chan = QtWidgets.QPushButton('Predict (EEG + Ch.2)', self)
        self.clientButton2chan.setCheckable(True)
        # self.channelNumForPrediction = 2
        self.clientButton2chan.clicked.connect(self.predictionStateOnEEGandCh2)
        self.clientButton2chan.resize(self.clientButton2chan.sizeHint())
        ### self.clientButton2chan.move(145, 10)
        self.clientButton2chan.move(5, 10)

        '''
        self.methodName = self.str_method_deep
        method_combobox = QtWidgets.QComboBox(self)
        method_combobox.addItem(self.str_method_deep)
        method_combobox.addItem(self.str_method_classical)
        method_combobox.addItem(self.str_method_rf)
        method_combobox.move(335, 10)
        method_combobox.activated[str].connect(self.method_choice)
        '''

        checkConnectionButton = QtWidgets.QPushButton('Check connection', self)
        checkConnectionButton.clicked.connect(self.check_connection)
        checkConnectionButton.resize(checkConnectionButton.sizeHint())
        checkConnectionButton.move(440, 10)

        '''
        self.nameLabel_eeg = QLabel(self)
        self.nameLabel_eeg.setText('EEG std:')
        self.nameLabel_eeg.move(10, 35)
        self.eeg_std = QLineEdit(self)
        self.eeg_std.move(65, 40)
        self.eeg_std.resize(30, 20)

        self.nameLabel_ch2 = QLabel(self)
        self.nameLabel_ch2.setText('Ch.2 std:')
        self.nameLabel_ch2.move(105, 35)
        self.ch2_std = QLineEdit(self)
        self.ch2_std.move(160, 40)
        self.ch2_std.resize(30, 20)
        '''

        self.nameLabel_ch2_mode_label = QLabel(self)
        self.nameLabel_ch2_mode_label.setText('Mode:')
        self.nameLabel_ch2_mode_label.move(10, 35)

        if self.params.useCh2ForReplace:
            self.ch2_mode = self.ch2_mode_str_video
        else:
            self.ch2_mode = self.ch2_mode_str_none
        self.ch2_mode_combobox = QtWidgets.QComboBox(self)
        self.ch2_mode_combobox.addItem(self.ch2_mode_str_video)
        self.ch2_mode_combobox.addItem(self.ch2_mode_str_emg)
        self.ch2_mode_combobox.addItem(self.ch2_mode_str_none)
        self.ch2_mode_combobox.move(50, 38)
        self.ch2_mode_combobox.activated[str].connect(self.ch2_mode_choice)

        self.nameLabel_ch2_thresh = QLabel(self)
        self.nameLabel_ch2_thresh.setText('Thresh for R->W:')
        self.nameLabel_ch2_thresh.move(160, 35)
        self.nameLabel_ch2_thresh.resize(125, 20)
        self.ch2_thresh = QLineEdit(self)
        self.ch2_thresh.setText(str(self.params.ch2_thresh_default))
        self.ch2_thresh.move(270, 40)
        self.ch2_thresh.resize(30, 20)

        self.ch2_thresh_slider = QSlider(Qt.Horizontal, self)
        self.ch2_thresh_slider.move(310, 35)
        self.ch2_thresh_slider.resize(220, 20)
        self.ch2_thresh_slider.setMinimum(-8)
        self.ch2_thresh_slider.setMaximum(16)
        self.ch2_thresh_slider.setValue(4)
        self.ch2_thresh_slider.setTickPosition(QSlider.TicksBelow)
        self.ch2_thresh_slider.setTickInterval(1)
        self.ch2_thresh_slider.valueChanged.connect(self.ch2_thresh_change)

        self.font = QtGui.QFont()
        self.font.setPointSize(18)
        self.font.setBold(True)
        self.font.setWeight(75)

        self.nameLabel_chi2 = QLabel(self)
        self.nameLabel_chi2.setText('KS chi2:')
        self.nameLabel_chi2.move(540, 35)
        self.nameLabel_chi2.setFont(self.font)
        self.chi2ResLabel = QLabel(self)
        self.chi2ResLabel.move(620, 35)
        self.chi2ResLabel.resize(70, 30)
        self.chi2ResLabel.setFont(self.font)

        self.dHist = DynamicGraphCanvas4KSHist(self, width=1.5, height=0.8, dpi=100)
        self.dHist.move(690, 5)

        self.dGraph = DynamicGraphCanvas4KS(self, width=4.5, height=0.8, dpi=100)
        self.dGraph.move(830, 5)

        self.nameLabel_d = QLabel(self)
        self.nameLabel_d.setText('d:')
        self.nameLabel_d.move(520, 60)
        self.nameLabel_d.setFont(self.font)
        self.dResLabel = QLabel(self)
        self.dResLabel.move(580, 60)
        self.dResLabel.resize(90, 30)
        self.dResLabel.setFont(self.font)

        self.waveRecordButton = QtWidgets.QPushButton(self.label_recordWaves, self)
        self.waveRecordButton.clicked.connect(self.toggleWaveRecord)
        self.waveRecordButton.resize(self.waveRecordButton.sizeHint())
        self.waveRecordButton.update()
        self.waveRecordButton.move(10, 60)
        self.waveRecordButton.setCheckable(True)

        self.waveNotRecordButton = QtWidgets.QPushButton(self.label_notRecordWaves, self)
        self.waveNotRecordButton.clicked.connect(self.toggleWaveNotRecord)
        self.waveNotRecordButton.resize(self.waveNotRecordButton.sizeHint())
        self.waveNotRecordButton.update()
        self.waveNotRecordButton.move(180, 60)
        self.waveNotRecordButton.setCheckable(True)
        if self.recordWaves:
            self.toggleWaveRecord()
        else:
            self.toggleWaveNotRecord()

        quitButton = QtWidgets.QPushButton('Quit Application', self)
        ### commented out on 2020.2.24
        ### quitButton.clicked.connect(self.stop_reader)
        quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        quitButton.resize(quitButton.sizeHint())
        quitButton.move(350, 60)

        self.listOfPredictionResults = []
        self.listOfGraphs = []
        self.listOfGraphs.append([])
        self.listOfGraphs.append([])

        for graphID in range(self.graphNum):

            self.listOfPredictionResults.append(PredictionResultLabel(self))
            predXLoc = (graphID * 300) + 110
            predYLoc = 100
            self.listOfPredictionResults[graphID].move(predXLoc, predYLoc)

            xLoc = (graphID * 300) + 10
            for chanID in range(2):
                yLoc = (chanID * 200) + 140
                self.listOfGraphs[chanID].append(DynamicGraphCanvas(self, width=3, height=2, dpi=100))
                self.listOfGraphs[chanID][graphID].move(xLoc, yLoc)

        self.setWindowTitle('Sleep Staging')
        xSize = self.graphNum * 310
        self.resize(xSize, 600)
        self.show()
        self.activateWindow()
        statusbar = self.statusBar()
        self.readFromDaq = False
        try:
            if len(args) > 5:
                print('Too many arquments for running app.py.')
                quit()
            self.sleepTime = float(args[4]) if len(args) > 4 else self.defaultSleepTime
            self.offsetWindowID = int(args[3]) if len(args) > 3 else 0
            self.inputFileID = args[2] if len(args) > 2 else self.randomlySelectInputFileID()
            if len(args) > 1:
                classifierID = args[1]
                if classifierID == 'm':
                    classifierID = self.randomlySelectClassifierID()
                self.client = ClassifierClient(self.recordWaves, self.extractorType, self.classifierType, classifierID, self.inputFileID, self.offsetWindowID)
            else:   # Neither classifierID nor inputFileID are specified.
                self.readFromDaq = True
                classifierID = self.randomlySelectClassifierID()
                print('Data is read from DAQ. classifier ID is randomly selected.')
                self.client = ClassifierClient(self.recordWaves, self.extractorType, self.classifierType, classifierID)
            self.client.hasGUI = True
        except Exception as e:
            print('Exception in self.client = ...')
            statusbar.showMessage(str(e))
            raise e

    # def NoEEGFileException(Exception):
    #    pass

    def randomlySelectInputFileID(self):
        eegFiles = getAllEEGFiles(self.params)
        return getFileIDFromEEGFile(eegFiles[np.random.randint(len(eegFiles))])

    def randomlySelectClassifierID(self):
        all_files = listdir(self.params.finalClassifierDir)
        prefix = 'params.'
        paramFiles = filterByPrefix(all_files, prefix)
        paramFile = paramFiles[np.random.randint(len(paramFiles))]
        return paramFile.split('.')[1]

if __name__ == '__main__':
    args = sys.argv
    app = QtWidgets.QApplication(args)
    host, port = '127.0.0.1', 50007
    mainapp = RemApplication(host, port, args)
    mainapp.activateWindow()
    sys.exit(app.exec_())
