# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/variation.py
# Compiled at: 2015-07-28 18:39:00
import numpy as np, loader, scipy.ndimage, warnings

def chisquared(p, c, n, r):
    return np.sum(r * np.square(c.astype(float) - p))


def absdiff(p, c, n, r):
    return np.sum(r * np.abs(c - p))


def normabsdiff(p, c, n, r):
    return np.sum(r * np.abs(c - p) / p)


def sumintensity(p, c, n, r):
    return np.sum(r * c)


def normabsdiffderiv(p, c, n, r):
    return -np.sum(r * (np.abs(n - c) / c) + np.sum(np.abs(c - p) / c))


operations = [
 chisquared, absdiff, normabsdiff, sumintensity, normabsdiffderiv]

def filevariation(operationindex, filea, c, filec, roi=None):
    p = loader.loadimage(filea)
    n = loader.loadimage(filec)
    print 'previous frame:' + filea
    return variation(operationindex, p, c, n, roi)


def variation(operationindex, imga, imgb=None, imgc=None, roi=None):
    if imga is not None and imgb is not None and imgc is not None:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                p = scipy.ndimage.zoom(imga, 0.1, order=1)
                c = scipy.ndimage.zoom(imgb, 0.1, order=1)
                n = scipy.ndimage.zoom(imgc, 0.1, order=1)
                p = scipy.ndimage.gaussian_filter(p, 3)
                c = scipy.ndimage.gaussian_filter(c, 3)
                n = scipy.ndimage.gaussian_filter(n, 3)
                if roi is not None:
                    r = scipy.ndimage.zoom(roi, 0.1, order=1)
                    r = np.rot90(scipy.ndimage.gaussian_filter(r, 3), 1)
                else:
                    r = 1
            with np.errstate(divide='ignore'):
                return operations[operationindex](p, c, n, r)
        except TypeError:
            print 'Variation could not be determined for a frame.'

    else:
        print 'Variation could not be determined for a frame.'
    return 0
# okay decompiling variation.pyc
