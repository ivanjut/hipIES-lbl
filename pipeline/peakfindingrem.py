# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/peakfindingrem.py
# Compiled at: 2015-07-17 13:23:47
__author__ = 'remi'
import sys
from numpy import NaN, Inf, arange, isscalar, asarray, array
import pyqtgraph as pg

def peakdet(x, v, delta):
    maxtab = []
    mintab = []
    if x is None:
        x = arange(len(v))
    v = asarray(v)
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    lookformax = True
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        if lookformax:
            if this < mx - delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        elif this > mn + delta:
            mintab.append((mnpos, mn))
            mx = this
            mxpos = x[i]
            lookformax = True

    return (array(maxtab), array(mintab))


class peaktooltip:

    def __init__(self, x, y, widget):
        self.q, self.I, self.width, self.index = peakdet(x, y, 10)
        self.scatterPoints = pg.ScatterPlotItem(self.q, self.I, size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        self.display_text = pg.TextItem(text='', color=(176, 23, 31), anchor=(0, 1))
        self.display_text.hide()
        widget.addItem(self.scatterPoints)
        widget.addItem(self.display_text)
        self.scatterPoints.scene().sigMouseMoved.connect(self.onMove)
        return

    def onMove(self, pos):
        act_pos = self.scatterPoints.mapFromScene(pos)
        p1 = self.scatterPoints.pointsAt(act_pos)
        if len(p1) != 0:
            self.display_text.setText('q=%f\nI=%f' % (p1[0].pos().x(), p1[0].pos().y()))
            self.display_text.setPos(p1[0].pos())
            self.display_text.show()
        else:
            self.display_text.hide()
# okay decompiling peakfindingrem.pyc
