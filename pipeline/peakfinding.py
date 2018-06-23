# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/peakfinding.py
# Compiled at: 2015-07-21 18:12:19
from pylab import *
from scipy import signal
from scipy.ndimage import filters
from hipies import debug
import pyqtgraph as pg
from PySide import QtCore
import inspect
maxfiltercoef = 5
cwtrange = np.arange(1, 100)
maxfiltercoef = 5
cwtrange = np.arange(3, 100)
gaussiancentersigma = 2
gaussianwidthsigma = 5

@debug.timeit
def findpeaks(x, y):
    cwtdata = filters.gaussian_filter1d(filters.gaussian_filter1d(signal.cwt(y, signal.ricker, cwtrange), gaussiancentersigma, axis=1), gaussianwidthsigma, axis=0)
    maxima = cwtdata == filters.maximum_filter(cwtdata, 5)
    maximaloc = np.where(maxima == 1)
    x = np.array(x)
    y = np.array(y)
    return list(np.array(np.vstack([x[maximaloc[1]], y[maximaloc[1]], maximaloc])))


class peaktooltip:

    def __init__(self, x, y, widget):
        self.q, self.I, self.width, self.index = findpeaks(x, y)
        self.scatterPoints = pg.PlotDataItem(self.q, self.I, size=10, pen=pg.mkPen(None), symbolPen=None, symbolBrush=pg.mkBrush(255, 255, 255, 120), symbol='o')
        self.display_text = pg.TextItem(text='', color=(176, 23, 31), anchor=(0, 1))
        self.display_text.hide()
        widget.addItem(self.scatterPoints)
        widget.addItem(self.display_text)
        self.scatterPoints.scene().sigMouseMoved.connect(self.onMove)
        return

    def onMove(self, pixelpos):
        itempos = self.scatterPoints.mapFromScene(pixelpos)
        itemx = itempos.x()
        itemy = itempos.y()
        pixeldelta = 7
        delta = self.scatterPoints.mapFromScene(QtCore.QPointF(pixeldelta + pixelpos.x(), pixeldelta + pixelpos.y()))
        deltax = delta.x() - itemx
        deltay = -(delta.y() - itemy)
        p1 = [ point for point in zip(self.q, self.I) if itemx - deltax < point[0] and point[0] < itemx + deltax and itemy - deltay < point[1] and point[1] < itemy + deltay
             ]
        if len(p1) != 0:
            self.display_text.setText('q=%f\nI=%f' % (p1[0][0], p1[0][1]))
            self.display_text.setPos(*p1[0])
            self.display_text.show()
        else:
            self.display_text.hide()
# okay decompiling peakfinding.pyc
