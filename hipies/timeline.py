# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/timeline.py
# Compiled at: 2015-07-28 18:39:00
import pyqtgraph as pg
from PySide import QtGui, QtCore
import viewer, numpy as np, pipeline, os

class timelinetabtracker(QtGui.QWidget):
    """
    A light-weight version of the timeline tab that is retained when the full tab is disposed. Used to generate tab.
    """

    def __init__(self, paths, experiment, parent):
        super(timelinetabtracker, self).__init__()
        self.paths = paths
        self.experiment = experiment
        self.parent = parent
        self.tab = None
        parent.listmodel.widgetchanged()
        self.isloaded = False
        return

    def load(self):
        if not self.isloaded:
            self.layout = QtGui.QHBoxLayout(self)
            simg = pipeline.loader.imageseries(self.paths, self.experiment)
            self.tab = timelinetab(simg, self.parent)
            self.layout.addWidget(self.tab)
            self.isloaded = True

    def unload(self):
        if self.isloaded:
            self.layout.parent = None
            self.layout.deleteLater()
            print 'Successful unload!'
            self.isloaded = False
        return


class timelinetab(viewer.imageTab):

    def __init__(self, simg, parentwindow):
        self.variation = dict()
        self.simg = simg
        dimg = simg.first()
        super(timelinetab, self).__init__(dimg, parentwindow)
        self.parentwindow = parentwindow
        self.setvariationmode(0)
        self.gotomax()
        self.istimeline = True

    def reduce(self):
        pass

    def appendimage(self, d, paths):
        paths = [ os.path.join(d, path) for path in paths ]
        self.simg.appendimages(paths)
        self.plotvariation()

    def rescan(self):
        self.simg.scan(self.operationindex)
        self.plotvariation()

    def setvariationmode(self, index):
        self.operationindex = index
        self.rescan()

    def plotvariation(self):
        if len(self.simg.variation) == 0:
            return
        variation = np.array(self.simg.variation.items())
        variation = variation[variation[:, 0].argsort()]
        self.parentwindow.timeline.clear()
        self.parentwindow.timeline.enableAutoScale()
        self.timeruler = TimeRuler(pen=pg.mkPen('#FFA500', width=3), movable=True)
        self.parentwindow.timeline.addItem(self.timeruler)
        self.timeruler.setBounds([1, max(variation[:, 0])])
        self.timeruler.sigRedrawFrame.connect(self.redrawframe)
        self.parentwindow.timeline.plot(variation[:, 0], variation[:, 1])
        return

    def timerulermoved(self):
        pos = int(round(self.parentwindow.timeruler.value()))
        self.parentwindow.timeruler.blockSignals(True)
        self.parentwindow.timeruler.setValue(pos)
        self.parentwindow.timeruler.blockSignals(False)
        if pos != self.previousPos:
            self.redrawframe()
        self.previousPos = pos

    def timerulermouserelease(self, event):
        if event.button == QtCore.Qt.LeftButton:
            self.redrawimageFULL()

    def redrawframe(self, forcelow=False):
        key = self.timeruler.value() + 1
        self.dimg = self.simg.getDiffImage(key)
        self.redrawimage(forcelow=forcelow)

    def gotomax(self):
        pass

    def roi(self):
        if self.activeaction is None:
            self.activeaction = 'roi'
            left = self.dimg.experiment.getvalue('Center X') - 100
            right = self.dimg.experiment.getvalue('Center X') + 100
            up = self.dimg.experiment.getvalue('Center Y') - 100
            down = self.dimg.experiment.getvalue('Center Y') + 100
            self.ROI = pg.PolyLineROI([[left, up], [left, down], [right, down], [right, up]], pen=(6,
                                                                                                   9), closed=True)
            self.viewbox.addItem(self.ROI)

            def checkPointMove(handle, pos, modifiers):
                p = self.viewbox.mapToView(pos)
                if 0 < p.y() < self.dimg.data.shape[0] and 0 < p.x() < self.dimg.data.shape[1]:
                    return True
                return False

            self.ROI.checkPointMove = checkPointMove
        else:
            if self.activeaction == 'roi':
                self.activeaction = None
                roiarea = self.ROI.getArrayRegion(np.ones_like(self.dimg.data.T), self.imageitem, returnMappedCoords=True)
                boundrect = self.viewbox.itemBoundingRect(self.ROI)
                leftpad = boundrect.x()
                toppad = boundrect.y()
                roiarea = np.pad(roiarea, ((int(leftpad), 0), (int(toppad), 0)), mode='constant')
                roiarea = np.pad(roiarea, (
                 (
                  0, self.dimg.data.shape[0] - roiarea.shape[0]), (0, self.dimg.data.shape[1] - roiarea.shape[1])), mode='constant')
                self.simg.roi = roiarea
                self.viewbox.removeItem(self.ROI)
                self.rescan()
        return


class TimeRuler(pg.InfiniteLine):
    sigRedrawFrame = QtCore.Signal(bool)

    def __init__(self, pen, movable=True):
        self.previousPos = None
        super(TimeRuler, self).__init__(pen=pen, movable=movable)
        self.previousPos = int(round(self.value()))
        self.sigPositionChangeFinished.connect(self.endDrag)
        return

    def setPos(self, pos):
        if type(pos) is pg.Point:
            pos = pos.x()
        pos = int(round(pos))
        if pos != self.previousPos:
            self.blockSignals(True)
            super(TimeRuler, self).setPos(pos)
            self.blockSignals(False)
            self.sigRedrawFrame.emit(True)
            self.previousPos = pos

    def endDrag(self):
        self.sigRedrawFrame.emit(False)
# okay decompiling timeline.pyc
