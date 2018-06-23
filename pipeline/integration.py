# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/integration.py
# Compiled at: 2015-07-21 18:12:19
import numpy as np

def radialintegrate(dimg, cut=None):
    centerx = dimg.experiment.getvalue('Center X')
    centery = dimg.experiment.getvalue('Center Y')
    mask = dimg.experiment.mask
    if mask is None:
        print 'No mask defined, creating temporary empty mask.'
        mask = np.zeros_like(dimg.data)
    else:
        if not mask.shape == dimg.data.shape:
            print 'Mask dimensions do not match image dimensions. Mask will be ignored until this is corrected.'
            mask = np.zeros_like(dimg.data)
    invmask = 1 - mask
    data = dimg.data * invmask
    if cut is not None:
        invmask *= cut
        data *= cut
    x, y = np.indices(data.shape)
    r = np.sqrt((x - centerx) ** 2 + (y - centery) ** 2)
    r = r.astype(np.int)
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel(), invmask.ravel())
    with np.errstate(divide='ignore', invalid='ignore'):
        radialprofile = tbin / nr
    q = np.arange(radialprofile.shape[0])
    if dimg.experiment.iscalibrated:
        x = np.arange(radialprofile.shape[0])
        theta = np.arctan2(x * dimg.experiment.getvalue('Pixel Size X'), dimg.experiment.getvalue('Detector Distance'))
        wavelength = dimg.experiment.getvalue('Wavelength')
        q = 4 * np.pi / wavelength * np.sin(theta / 2) * 1e-10
        radialprofile = radialprofile * (radialprofile > 0) + 0.0001 * (radialprofile <= 0)
    return (
     q, radialprofile)


def pixel_2Dintegrate(dimg, mask=None):
    centerx = dimg.experiment.getvalue('Center X')
    centery = dimg.experiment.getvalue('Center Y')
    if mask is None:
        print 'No mask defined, creating temporary empty mask.'
        mask = np.zeros_like(dimg.data)
    data = dimg.data * (1 - mask)
    x, y = np.indices(data.shape)
    r = np.sqrt((x - centerx) ** 2 + (y - centery) ** 2)
    r = r.astype(np.int)
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel(), (1 - mask).ravel())
    radialprofile = tbin / nr
    return radialprofile


def chi_2Dintegrate(imgdata, cen, mu, mask=None, chires=30):
    """
    Integration over r for a chi range. Output is 30*
    """
    if mask is None:
        print 'No mask defined, creating temporary empty mask..'
        mask = np.zeros_like(imgdata)
    data = imgdata * (1 - mask)
    x, y = np.indices(data.shape).astype(np.float)
    r = np.sqrt((x - cen[0]) ** 2 + (y - cen[1]) ** 2)
    r = r.astype(np.int)
    delta = 3
    rinf = mu - delta / 2.0
    rsup = mu + delta / 2.0
    rmask = ((rinf < r) & (r < rsup) & (x < cen[0])).astype(np.int)
    data *= rmask
    chi = chires * np.arctan((y - cen[1]) / (x - cen[0]))
    chi += chires * np.pi / 2.0
    chi = np.round(chi).astype(np.int)
    chi *= chi > 0
    tbin = np.bincount(chi.ravel(), data.ravel())
    nr = np.bincount(chi.ravel(), rmask.ravel())
    angleprofile = tbin / nr
    return angleprofile


def radialintegratepyFAI(imgdata, experiment, mask=None, cut=None):
    data = imgdata.copy()
    AI = experiment.getAI()
    if mask is None:
        print 'No mask defined, creating temporary empty mask.'
        mask = np.zeros_like(data)
    if cut is not None:
        mask *= cut
        data *= cut
    xres = 10000
    q, radialprofile = AI.integrate1d(data, xres, mask=mask, method='full_csr')
    q = q[:-3] / 10.0
    radialprofile = radialprofile[:-3]
    return (
     q, radialprofile)


def cake(imgdata, experiment, mask=None, xres=1000, yres=1000):
    AI = experiment.getAI()
    return AI.integrate2d(imgdata.T, xres, yres, mask=mask)


def GetArc(Imagedata, center, radius1, radius2, angle1, angle2):
    mask = np.zeros_like(Imagedata)
    centerx = center[0]
    centery = center[1]
    y, x = np.indices(Imagedata.shape)
    r = np.sqrt((x - centerx) ** 2 + (y - centery) ** 2)
    mask = (r > radius1) & (r < radius2)
    theta = np.arctan2(y - centery, x - centerx) / 2 / np.pi * 360
    mask &= (theta > angle1) & (theta < angle2)
    mask = np.flipud(mask)
    return mask * Imagedata
# okay decompiling integration.pyc
