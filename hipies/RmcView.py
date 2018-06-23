# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/RmcView.py
# Compiled at: 2015-07-28 18:39:00
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg, glob
from PIL import Image
import os, re

def calcscale(imv):
    """
    
    """
    image = imv.getProcessedImage()
    scale = imv.scalemax / float(image[imv.currentIndex].shape[1])
    return scale


class imagetimeline(list):

    @property
    def shape(self):
        return (
         len(self), self[-1].shape[0], self[-1].shape[0])

    def __getitem__(self, item):
        return list.__getitem__(self, item)

    @property
    def ndim(self):
        return 3

    @property
    def size(self):
        return sum(map(np.size, self))

    @property
    def max(self):
        return max(map(np.max, self))

    @property
    def min(self):
        return min(map(np.min, self))

    @property
    def dtype(self):
        return type(self[0][(0, 0)])


class TimelineView(pg.ImageView):

    def __init__(self, scalemax, *args, **kwargs):
        super(TimelineView, self).__init__(*args, **kwargs)
        self.scalemax = scalemax

    def quickMinMax(self, data):
        return (
         min(map(np.min, data)), max(map(np.max, data)))

    def updateImage(self, autoHistogramRange=True):
        if self.image is None:
            return
        scale = calcscale(self)
        image = self.getProcessedImage()
        if autoHistogramRange:
            self.ui.histogram.setHistogramRange(self.levelMin, self.levelMax)
        if self.axes['t'] is None:
            self.imageItem.updateImage(image)
        else:
            self.ui.roiPlot.show()
            self.imageItem.updateImage(image[self.currentIndex])
        self.imageItem.resetTransform()
        self.imageItem.scale(scale, scale)
        print 'Image shape' + str(image.shape)
        print 'Scale set to: ' + str(scale)
        return


class rmcView(QtGui.QTabWidget):

    def __init__(self, root, loadingfactors=None):
        super(rmcView, self).__init__()
        paths = glob.glob(os.path.join(root, '[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]_model.tif'))
        indices = dict(zip(paths, [ re.findall('\\d{4}', os.path.basename(path)) for path in paths ]))
        tiles = dict()
        for path, ind in indices.iteritems():
            if int(ind[1]) in tiles:
                tiles[int(ind[1])].append(path)
            else:
                tiles[int(ind[1])] = [
                 path]

        for tile, loadingfactor in zip(tiles, loadingfactors):
            images = []
            paths = sorted(tiles[tile])
            for path in paths:
                img = Image.open(path).convert('L')
                img = np.array(img)
                print path
                print img.shape
                images.append(img)

            data = imagetimeline(images)
            sizemax = max(map(np.shape, data))[0]
            view = TimelineView(sizemax)
            view.setImage(data)
            scale = calcscale(view)
            view.imageItem.resetTransform()
            view.imageItem.scale(scale, scale)
            view.autoRange()
            view.getHistogramWidget().setHidden(True)
            view.ui.roiBtn.setHidden(True)
            view.ui.menuBtn.setHidden(True)
            if loadingfactors is None:
                self.addTab(view, u'Tile ' + str(tile + 1))
            else:
                self.addTab(view, str(loadingfactor))

        return


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
    root = '/Users/austinblair/Downloads/test_20150714_144045/'
    root = '/home/ablair/test_20150714_144045/'
    win = QtGui.QMainWindow()
    win.resize(800, 800)
    win.setWindowTitle('pyqtgraph example: Hiprmc ')
    win.setCentralWidget(rmcView(root))
    win.show()
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
# okay decompiling RmcView.pyc
