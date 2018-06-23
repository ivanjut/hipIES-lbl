# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/remesh.py
# Compiled at: 2015-08-05 14:50:27
import loader, numpy as np
from pyFAI import geometry
import sys, os
print os.getcwd()
try:
    from cWarpImage import warp_image
except ImportError:
    import sys
    print sys.path
    print 'Remeshing C extension is NOT LOADED!'

def calc_q_range(lims, geometry, alphai, cen):
    nanometer = 1000000000.0
    sdd = geometry.get_dist() * nanometer
    wavelen = geometry.get_wavelength() * nanometer
    pixel1 = geometry.get_pixel1() * nanometer
    pixel2 = geometry.get_pixel2() * nanometer
    y = np.array([0, lims[1] - 1], dtype=np.float) * pixel1
    z = np.array([0, lims[0] - 1], dtype=np.float) * pixel2
    y, z = np.meshgrid(y, z)
    y -= cen[0]
    z -= cen[1]
    tmp = np.sqrt(y ** 2 + sdd ** 2)
    cos2theta = sdd / tmp
    sin2theta = y / tmp
    tmp = np.sqrt(z ** 2 + sdd ** 2)
    cosalpha = sdd / tmp
    sinalpha = z / tmp
    k0 = 2.0 * np.pi / wavelen
    qx = k0 * (cosalpha * cos2theta - np.cos(alphai))
    qy = k0 * cosalpha * sin2theta
    qz = k0 * (sinalpha + np.sin(alphai))
    qp = np.sign(qy) * np.sqrt(qx ** 2 + qy ** 2)
    q_range = [qp.min(), qp.max(), qz.min(), qz.max()]
    return (
     q_range, k0)


def remesh(image, filename, geometry):
    shape = image.shape
    center = np.zeros(2, dtype=np.float)
    pixel = np.zeros(2, dtype=np.float)
    nanometer = 1000000000.0
    sdd = geometry.get_dist() * nanometer
    pixel[0] = geometry.get_pixel1() * nanometer
    pixel[1] = geometry.get_pixel2() * nanometer
    center[0] = geometry.get_poni2() * nanometer
    center[1] = shape[0] * pixel[0] - geometry.get_poni1() * nanometer
    print center
    paras = loader.loadparas(filename)
    if paras is None:
        print 'Failed to read incident angle'
        return (
         np.rot90(image, 3), None, None)
    if 'Sample Alpha Stage' in paras:
        alphai = np.deg2rad(float(paras['Sample Alpha Stage']))
    else:
        if 'Alpha' in paras:
            alphai = np.deg2rad(float(paras['Alpha']))
        else:
            return (
             np.rot90(image, 3), None, None)
    qrange, k0 = calc_q_range(image.shape, geometry, alphai, center)
    nqz = image.shape[0]
    dqz = (qrange[3] - qrange[2]) / (nqz - 1)
    nqp = np.int((qrange[1] - qrange[0]) / dqz)
    qvrt = np.linspace(qrange[2], qrange[3], nqz)
    qpar = qrange[0] + np.arange(nqp) * dqz
    qpar, qvrt = np.meshgrid(qpar, qvrt)
    try:
        center /= pixel
        qimg = warp_image(image, qpar, qvrt, pixel, center, alphai, k0, sdd, 0)
        return (
         np.rot90(qimg, 3), qpar, qvrt)
    except:
        cosi = np.cos(alphai)
        sini = np.sin(alphai)
        sina = qvrt / k0 - sini
        cosa2 = 1 - sina ** 2
        cosa = np.sqrt(cosa2)
        tana = sina / cosa
        t1 = cosa2 + cosi ** 2 - (qpar / k0) ** 2
        t2 = 2.0 * cosa * cosi
        cost = t1 / t2
        cost[t1 > t2] = 0
        with np.errstate(divide='ignore'):
            tant = np.sign(qpar) * np.sqrt(1.0 - cost ** 2) / cost
            tant[cost == 0] = 0
        map_x = (tant * sdd + center[0]) / pixel[0]
        map_y = (tana * sdd + center[1]) / pixel[1]
        m1 = t1 > t2
        m2 = np.logical_or(map_x < 0, map_x > 1474)
        mask = np.logical_or(m1, m2)
        map_x[mask] = -1
        qsize = map_x.size
        qshape = map_x.shape
        qimg = np.fromiter((image[(i, j)] for i, j in np.nditer([map_y.astype(int),
         map_x.astype(int)])), dtype=np.float, count=qsize).reshape(qshape)
        qimg[mask] = 0.0
        return (
         np.rot90(qimg, 3), qpar, qvrt)

    return


if __name__ == '__main__':
    import fabio, pylab as plt, time
    filename = 'Burst/calibration/AGB_5S_USE_2_2m.edf'
    image = fabio.open(filename).data
    sdd = 0.283351
    cen_y = 0.005363
    cen_x = 0.040123
    pixel = 0.000172
    geo = geometry.Geometry(sdd, cen_y, cen_x, 0, 0, 0)
    geo.set_wavelength(1.23984e-10)
    geo.set_pixel1(0.000172)
    geo.set_pixel2(0.000172)
    t0 = time.clock()
    qimg = remesh(image, filename, geo)
    t1 = time.clock() - t0
    print 'remesh clock time = %f' % t1
    plt.imshow(np.log(qimg + 5))
    plt.show()
# okay decompiling remesh.pyc
