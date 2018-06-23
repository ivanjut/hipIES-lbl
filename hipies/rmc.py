# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/rmc.py
# Compiled at: 2015-08-07 12:42:25
import os, RmcView, time, subprocess
from PySide import QtGui, QtCore
from pipeline import hig, loader

class gui:

    def __init__(self, ui):
        self.ui = ui
        self.ui.rmcbutton.clicked.connect(self.showrmc)
        self.ui.rmcaddfiles.clicked.connect(self.addfiles)
        self.ui.rmcremovefiles.clicked.connect(self.removefiles)
        self.ui.rmcExecute.clicked.connect(self.execute)
        self.ui.rmcAddloadingfactor.clicked.connect(self.addloadingfactor)
        self.ui.rmcSubtractloadingfactor.clicked.connect(self.subtractloadingfactor)
        self.ui.rmcopen.clicked.connect(self.open)
        self.ui.rmcreset.clicked.connect(self.reset)
        self.ui.rmcreset_2.clicked.connect(self.reset2)

    def open(self):
        Outputdirectory = QtGui.QFileDialog.getExistingDirectory(self.ui, 'Select an Output directory')
        self.ui.rmcoutput.setText(Outputdirectory)

    def reset(self):
        self.ui.rmcoutput.setText('')

    def reset2(self):
        self.ui.rmcoutput.setText('')
        self.ui.rmcLoadingfactors.clear()
        self.ui.rmcSteps.setValue(99)
        self.ui.rmcScalefactor.setValue(1)
        self.ui.rmcModlestartsize.setValue(1)
        self.ui.rmcRunName.setText('')
        self.ui.rmcinputpaths.clear()

    def showrmc(self):
        """
        switch to timeline view
        """
        self.ui.viewmode.setCurrentIndex(3)
        self.ui.sidemode.setCurrentIndex(1)

    def addfiles(self):
        paths, ok = QtGui.QFileDialog.getOpenFileNames(self.ui, 'Add files to RMC', os.curdir, '*.tif *.edf *.fits *.tif')
        self.ui.rmcinputpaths.addItems(paths)

    def removefiles(self):
        for index in self.ui.rmcinputpaths.selectedIndexes():
            item = self.ui.rmcinputpaths.takeItem(index.row())
            item = None

        return

    def addloadingfactor(self):
        loadingfactor, _ = QtGui.QInputDialog.getDouble(self.ui, 'Loading Factor', 'Enter a loading factor:', value=0, minValue=0, maxValue=1000, decimals=3)
        newItem = QtGui.QListWidgetItem()
        newItem.setText(str(loadingfactor))
        self.ui.rmcLoadingfactors.addItem(newItem)

    def subtractloadingfactor(self):
        for index in self.ui.rmcLoadingfactors.selectedIndexes():
            item = self.ui.rmcLoadingfactors.takeItem(index.row())
            item = None

        return

    def runRemotely(self):
        [
         'scp test_input.hig ablair@parratt.lbl.gov:~/  ',
         'ssh -t ablair@parratt.lbl.gov   ']
        RemoteProcess = subprocess.Popen('scp test_input.hig ablair@parratt.lbl.gov:~/  ')

    executeNumber = 0

    def execute(self):
        steps = self.ui.rmcSteps.value()
        scalefactor = self.ui.rmcScalefactor.value()
        modlestartsize = self.ui.rmcModlestartsize.value()
        loadingfactors = []
        for item in iterAllItems(self.ui.rmcLoadingfactors):
            loadingfactors.append(item.text())

        rip = self.ui.rmcinputpaths
        inputpaths = [ rip.item(index).text() for index in xrange(rip.count()) ]
        tiles = len(loadingfactors)
        for path in inputpaths:
            d = {'hipRMCInput': {'instrumentation': {'inputimage': path, 'imagesize': loader.loadimage(path).shape[0:2], 
                                                   'numtiles': tiles, 
                                                   'loadingfactors': loadingfactors}, 
                               'computation': {'runname': os.path.join(self.ui.rmcoutput.text(), self.ui.rmcRunName.text()), 
                                               'modelstartsize': [
                                                                modlestartsize, modlestartsize], 
                                               'numstepsfactor': steps, 
                                               'scalefactor': scalefactor}}}
            h = hig.hig(**d)
            h.write('test_input.hig')
            self.rmcdaemon = RMCThread()
            self.rmcdaemon.sig_finished.connect(self.displayoutput)
            self.rmcdaemon.start()

    def displayoutput(self, exitcode):
        print 'Finished', exitcode
        path = os.path.join(self.ui.rmcoutput.text(), self.ui.rmcRunName.text())
        loadingfactors = []
        for item in iterAllItems(self.ui.rmcLoadingfactors):
            loadingfactors.append(item.text())

        layout = self.ui.rmclayout
        layout.addWidget(RmcView.rmcView(path, loadingfactors))


def iterAllItems(w):
    for i in range(w.count()):
        yield w.item(i)


class RMCThread(QtCore.QThread):
    sig_finished = QtCore.Signal(int)

    def run(self):
        process = subprocess.Popen(['./hiprmc', 'test_input.hig'])
        while process.poll() is None:
            time.sleep(0.5)

        self.sig_finished.emit(process.poll())
        return

    def stop(self):
        self.exiting = True
        print 'thread stop - %s' % self.exiting

    def __del__(self):
        self.exiting = True
        self.wait()
# okay decompiling rmc.pyc
