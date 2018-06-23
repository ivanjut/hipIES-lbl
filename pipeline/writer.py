# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/writer.py
# Compiled at: 2015-07-21 18:12:19
import nexpy.api.nexus as nx, numpy as np, scipy.ndimage
from PySide import QtCore
from hipies import debug
import multiprocessing, time, os

class nexusmerger(QtCore.QThread):

    def __init__(self, *args, **kwargs):
        super(nexusmerger, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        p = multiprocessing.Process(target=mergenexus, kwargs=self.kwargs)
        self.job = p
        p.start()


def mergenexus(**kwargs):
    path = kwargs['path']
    newfile = not os.path.isfile(path)
    if newfile:
        nxroot = nx.NXroot(nx.NXdata(kwargs['img']))
    else:
        nxroot = nx.load(path, mode='rw')
    if not hasattr(nxroot.data, 'rawfile'):
        nxroot.data.rawfile = kwargs['rawpath']
    if not hasattr(nxroot.data, 'thumb'):
        nxroot.data.thumbnail = kwargs['thumb']
    if not hasattr(nxroot.data, 'variation'):
        nxroot.data.variation = kwargs['variation'].items()
    if newfile:
        writenexus(nxroot, kwargs['path'])


def writenexus(nexroot, path):
    try:
        nexroot.save(path)
    except IOError:
        print 'IOError: Check that you have write permissions.'


def thumbnail(img, size=160.0):
    """
    Generate a thumbnail from an image
    """
    size = float(size)
    desiredsize = np.array([size, size])
    zoomfactor = np.max(desiredsize / np.array(img.shape))
    zoomfactor = 0.1
    img = resample(img)
    return img


avg = np.vectorize(np.average)

def resample(img, factor=10):
    return avg(blockshaped(img, factor))


def blockshaped(arr, factor):
    firstslice = np.array_split(arr, arr.shape[0] // factor)
    secondslice = map(lambda x: np.array_split(x, arr.shape[1] // factor, axis=1), firstslice)
    return np.array(secondslice)
# okay decompiling writer.pyc
