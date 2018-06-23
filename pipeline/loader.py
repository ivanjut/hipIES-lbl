# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/loader.py
# Compiled at: 2015-07-28 18:39:00
import fabio, numpy, pyfits, os, numpy as np
from nexpy.api import nexus as nx
import detectors, glob, re, time, scipy.ndimage, writer, nexpy.api.nexus.tree as tree
from hipies import debug
acceptableexts = [
 '.fits', '.edf', '.tif', '.nxs', '.tif', '.hdf']

def loadsingle(path):
    return (
     loadimage(path), loadparas(path))


def loadimage(path):
    data = None
    try:
        if os.path.splitext(path)[1] in acceptableexts:
            if os.path.splitext(path)[1] == '.gb':
                raise NotImplementedError('Format not yet implemented.')
            else:
                if os.path.splitext(path)[1] == '.fits':
                    data = pyfits.open(path)[2].data
                    return data
                if os.path.splitext(path)[1] in ('.nxs', '.hdf'):
                    nxroot = nx.load(path)
                    if hasattr(nxroot.data, 'signal'):
                        data = nxroot.data.signal
                        return data
                    return loadimage(str(nxroot.data.rawfile))
                else:
                    data = fabio.open(path).data
                    return data
    except IOError:
        print 'IO Error loading: ' + path

    return data


def readenergy(path):
    try:
        if os.path.splitext(path)[1] in acceptableexts:
            if os.path.splitext(path)[1] == '.fits':
                head = pyfits.open(path)
                paras = scanparaslines(str(head[0].header).split('\r'))
            elif os.path.splitext(path)[1] in ('.nxs', '.hdf'):
                pass
    except IOError:
        print 'IO Error reading energy: ' + path

    return


def readvariation(path):
    for i in range(20):
        try:
            nxroot = nx.load(path)
            print 'Attempt', i + 1, 'to read', path, 'succeeded; continuing...'
            return dict([ [int(index), int(value)] for index, value in nxroot.data.variation ])
        except IOError:
            print 'Could not load', path, ', trying again in 0.2 s'
            time.sleep(0.2)
        except nx.NeXusError:
            print 'No variation saved in file ' + path

    return


def loadparas(path):
    try:
        extension = os.path.splitext(path)[1]
        if extension == '.fits':
            head = pyfits.open(path)
            return head[0].header
        if extension == '.edf':
            txtpath = os.path.splitext(path)[0] + '.txt'
            if os.path.isfile(txtpath):
                return scanparas(txtpath)
            basename = os.path.splitext(path)[0]
            obj = re.search('_\\d+$', basename)
            if obj is not None:
                iend = obj.start()
                token = basename[:iend] + '*txt'
                txtpath = glob.glob(token)[0]
                return scanparas(txtpath)
            return
        else:
            if extension == '.gb':
                raise NotImplementedError('This format is not yet supported.')
            else:
                if extension in ('.nxs', '.hdf'):
                    nxroot = nx.load(path)
                    return nxroot
    except IOError:
        print 'Unexpected read error in loadparas'
    except IndexError:
        print 'No txt file found in loadparas'

    return


def scanparas(path):
    with open(path, 'r') as (f):
        lines = f.readlines()
    paras = scanparaslines(lines)
    return paras


def scanparaslines(lines):
    paras = dict()
    for line in lines:
        cells = filter(None, re.split('[=:]+', line))
        key = cells[0]
        if cells.__len__() == 2:
            cells[1] = cells[1].split('/')[0]
            paras[key] = cells[1]
        elif cells.__len__() == 1:
            paras[key] = cells[0]

    return paras


def loadstichted(filepath2, filepath1):
    data1, paras1 = loadsingle(filepath1)
    data2, paras2 = loadsingle(filepath2)
    positionY1 = float(paras1['Detector Vertical'])
    positionY2 = float(paras2['Detector Vertical'])
    positionX1 = float(paras1['Detector Horizontal'])
    positionX2 = float(paras2['Detector Horizontal'])
    deltaX = round((positionX2 - positionX1) / 0.172)
    deltaY = round((positionY2 - positionY1) / 0.172)
    padtop2 = 0
    padbottom1 = 0
    padtop1 = 0
    padbottom2 = 0
    padleft2 = 0
    padright1 = 0
    padleft1 = 0
    padright2 = 0
    if deltaY < 0:
        padtop2 = abs(deltaY)
        padbottom1 = abs(deltaY)
    else:
        padtop1 = abs(deltaY)
        padbottom2 = abs(deltaY)
    if deltaX < 0:
        padleft2 = abs(deltaX)
        padright1 = abs(deltaX)
    else:
        padleft1 = abs(deltaX)
        padright2 = abs(deltaX)
    d2 = numpy.pad(data2, ((padtop2, padbottom2), (padleft2, padright2)), 'constant')
    d1 = numpy.pad(data1, ((padtop1, padbottom1), (padleft1, padright1)), 'constant')
    mask2 = numpy.pad(1 - finddetector(data2.T)[1], ((padtop2, padbottom2), (padleft2, padright2)), 'constant')
    mask1 = numpy.pad(1 - finddetector(data1.T)[1], ((padtop1, padbottom1), (padleft1, padright1)), 'constant')
    with numpy.errstate(divide='ignore'):
        data = (d1 + d2) / (mask2 + mask1)
    return data


@debug.timeit
def finddetectorbyfilename(path):
    dimg = diffimage(filepath=path)
    return dimg.detector


def loadthumbnail(path):
    nxpath = pathtools.path2nexus(path)
    img = diffimage(filepath=path).thumbnail
    if img is not None:
        img = writer.thumbnail(img)
    return img


def loadpath(path):
    if '_lo_' in path:
        path2 = path.replace('_lo_', '_hi_')
        return (
         loadstichted(path, path2), None)
    if '_hi_' in path:
        path2 = path.replace('_hi_', '_lo_')
        return (
         loadstichted(path, path2), None)
    return loadsingle(path)
    return


import integration, remesh, center_approx, variation, pathtools
from fabio import file_series

class diffimage:

    def __init__(self, filepath=None, data=None, detector=None, experiment=None):
        """
        Image class for diffraction images that caches and validates cache
        :param filepath: str
        :param data: numpy.multiarray.ndarray
        :param detector: pyFAI.detectors.Detector
        :param experiment: hipies.config.experiment
        """
        print 'Loading ' + str(filepath) + '...'
        self._data = data
        self.filepath = filepath
        self._detector = detector
        self._params = None
        self._thumb = None
        self._variation = dict()
        self.experiment = experiment
        self.cache = dict()
        self.cachecheck = None
        return

    def updateexperiment(self):
        _ = self.detector
        if 'Beamline Energy' in self.params:
            self.experiment.setvalue('Energy', self.params['Beamline Energy'])

    def checkcache(self):
        pass

    def invalidatecache(self):
        self.cache = dict()

    def cachedata(self):
        if self._data is None:
            if self.filepath is not None:
                try:
                    self._data = loadimage(self.filepath)
                except IOError:
                    debug.frustration()
                    raise IOError('File moved, corrupted, or deleted. Load failed')

        return

    @property
    def mask(self):
        return self.experiment.mask

    @property
    def dataunrot(self):
        self.cachedata()
        return self._data

    @property
    def data(self):
        self.cachedata()
        return np.rot90(self._data, 3)

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def params(self):
        if self._params is None:
            self._params = loadparas(self.paths[0])
        return self._params

    @property
    def detector(self):
        if self._detector is None:
            if self.data is not None:
                name, detector = self.finddetector()
            else:
                return
            self.detectorname = name
            mask = detector.calc_mask()
            self._detector = detector
            if detector is not None:
                if mask is not None:
                    self.experiment.addtomask(np.rot90(mask, 3))
                self.experiment.setvalue('Pixel Size X', detector.pixel1)
                self.experiment.setvalue('Pixel Size Y', detector.pixel2)
                self.experiment.setvalue('Detector', name)
        return self._detector

    def finddetector(self):
        for name, detector in detectors.ALL_DETECTORS.iteritems():
            if hasattr(detector, 'MAX_SHAPE'):
                if detector.MAX_SHAPE == self.data.shape[::-1]:
                    detector = detector()
                    print 'Detector found: ' + name
                    return (
                     name, detector)
            if hasattr(detector, 'BINNED_PIXEL_SIZE'):
                if self.data.shape[::-1] in [ tuple(np.array(detector.MAX_SHAPE) / b) for b in detector.BINNED_PIXEL_SIZE.keys()
                                            ]:
                    detector = detector()
                    print 'Detector found with binning: ' + name
                    return (
                     name, detector)

        raise ValueError('Detector could not be identified!')

    @detector.setter
    def detector(self, value):
        if type(value) == str:
            try:
                self._detector = detectors.ALL_DETECTORS[value]
            except KeyError:
                try:
                    self._detector = getattr(detectors, value)
                except AttributeError:
                    raise KeyError('Detector not found in pyFAI registry: ' + value)

        else:
            self._detector = value

    @property
    def params(self):
        if self._params is None:
            self._params = loadparas(self.filepath)
        return self._params

    @property
    def thumbnail(self):
        if self._thumb is None:
            self._thumb = writer.thumbnail(self.data)
        return self._thumb

    def iscached(self, key):
        return key in self.cache

    def cachedetector(self):
        _ = self.detector

    @property
    def cake(self):
        self.cachedetector()
        if not self.iscached('cake'):
            cake, x, y = integration.cake(self.data, self.experiment)
            cakemask, _, _ = integration.cake(self.mask, self.experiment)
            cakemask = (cakemask > 0) * 255
            self.cache['cake'] = cake
            self.cache['cakemask'] = cakemask
            self.cache['cakeqx'] = x
            self.cache['cakeqy'] = y
        return self.cache['cake']

    @property
    def remesh(self):
        if not self.iscached('remesh'):
            remeshdata, x, y = remesh.remesh(np.rot90(self.data, 1).copy(), self.filepath, self.experiment.getGeometry())
            remeshmask, _, _ = remesh.remesh(np.rot90(self.mask, 1).copy(), self.filepath, self.experiment.getGeometry())
            self.cache['remesh'] = remeshdata
            self.cache['remeshmask'] = remeshmask
            self.cache['remeshqx'] = x
            self.cache['remeshqy'] = y
        return self.cache['remesh']

    def __del__(self):
        if self._data is not None:
            self.writenexus()
        return

    @debug.timeit
    def writenexus(self):
        nxpath = pathtools.path2nexus(self.filepath)
        w = writer.nexusmerger(img=self._data, thumb=self.thumbnail, path=nxpath, rawpath=self.filepath, variation=self._variation)
        w.run()

    def findcenter(self):
        x, y = center_approx.center_approx(self.data)
        self.experiment.setvalue('Center X', x)
        self.experiment.setvalue('Center Y', y)

    def variation(self, operationindex, roi):
        if operationindex not in self._variation or roi is not None:
            nxpath = pathtools.path2nexus(self.filepath)
            if os.path.exists(nxpath) and roi is None:
                v = readvariation(nxpath)
                print v
                if operationindex in v:
                    self._variation[operationindex] = v[operationindex]
                    print 'successful variation load!'
                else:
                    prv = pathtools.similarframe(self.filepath, -1)
                    nxt = pathtools.similarframe(self.filepath, +1)
                    self._variation[operationindex] = variation.filevariation(operationindex, prv, self.dataunrot, nxt)
            else:
                prv = pathtools.similarframe(self.filepath, -1)
                nxt = pathtools.similarframe(self.filepath, +1)
                if roi is None:
                    self._variation[operationindex] = variation.filevariation(operationindex, prv, self.dataunrot, nxt)
                else:
                    v = variation.filevariation(operationindex, prv, self.dataunrot, nxt, roi)
                    return v
        return self._variation[operationindex]

    def __getattr__(self, name):
        if name in self.cache:
            return self.cache[name]
        raise AttributeError('diffimage has no attribute: ' + name)


class imageseries:

    def __init__(self, paths, experiment):
        self.paths = dict()
        self.variation = dict()
        self.appendimages(paths)
        self.experiment = experiment
        self.roi = None
        return

    def __len__(self):
        return len(self.paths)

    def first(self):
        if len(self.paths) > 0:
            firstpath = sorted(list(self.paths.values()))[0]
            print firstpath
            return diffimage(filepath=firstpath, experiment=self.experiment)
        return diffimage(data=np.zeros((2, 2)), experiment=self.experiment)

    def getDiffImage(self, key):
        return diffimage(filepath=self.paths[key], experiment=self.experiment)

    def appendimages(self, paths):
        for path in paths:
            frame = self.path2frame(path)
            if frame is None:
                continue
            self.variation[frame] = None
            self.paths[frame] = path

        return

    def currentdiffimage(self):
        pass

    def scan(self, operationindex):
        if len(self.paths) < 3:
            return
        self.variation = dict()
        keys = self.paths.keys()
        for key in keys:
            variationx = self.path2frame(self.paths[key])
            self.variation[variationx] = self.getDiffImage(key).variation(operationindex, self.roi)

        return

    @staticmethod
    def path2frame(path):
        try:
            return int(os.path.splitext(os.path.basename(path).split('_')[-1])[0])
        except ValueError:
            print 'Path has no frame number:', path

        return
# okay decompiling loader.pyc
