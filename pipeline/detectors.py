# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/detectors.py
# Compiled at: 2015-07-17 13:23:47
import pyFAI.detectors, fabio, logging

class PrincetonMTE(pyFAI.detectors.Detector):
    """
    Princeton Instrument, PI-MTE CCD
    """
    force_pixel = True
    MAX_SHAPE = (2048, 2048)
    BINNED_PIXEL_SIZE = {1: 1.35e-05, 2: 2.7e-05}

    def __init__(self):
        pixel1 = 2.7e-05
        pixel2 = 2.7e-05
        super(PrincetonMTE, self).__init__(pixel1=pixel1, pixel2=pixel2)

    def get_binning(self):
        return self._binning

    def set_binning(self, bin_size=(1, 1)):
        """
        Set the "binning" of the detector,
        @param bin_size: set the binning of the detector
        @type bin_size: int or (int, int)
        """
        if '__len__' in dir(bin_size) and len(bin_size) >= 2:
            bin_size = (
             int(round(float(bin_size[0]))), int(round(float(bin_size[1]))))
        else:
            b = int(round(float(bin_size)))
            bin_size = (b, b)
        if bin_size != self._binning:
            if bin_size[0] in self.BINNED_PIXEL_SIZE and bin_size[1] in self.BINNED_PIXEL_SIZE:
                self._pixel1 = self.BINNED_PIXEL_SIZE[bin_size[0]]
                self._pixel2 = self.BINNED_PIXEL_SIZE[bin_size[1]]
            else:
                self._pixel1 = self.BINNED_PIXEL_SIZE[1] / float(bin_size[0])
                self._pixel2 = self.BINNED_PIXEL_SIZE[1] / float(bin_size[1])
            self._binning = bin_size
            self.shape = (self.max_shape[0] // bin_size[0],
             self.max_shape[1] // bin_size[1])

    binning = property(get_binning, set_binning)

    def __repr__(self):
        return 'Detector %s\t PixelSize= %.3e, %.3e m' % (
         self.name, self._pixel1, self._pixel2)

    def guess_binning(self, data):
        """
        Guess the binning/mode depending on the image shape
        @param data: 2-tuple with the shape of the image or the image with a .shape attribute.
        """
        if 'shape' in dir(data):
            shape = data.shape
        else:
            shape = tuple(data[:2])
        bin1 = self.MAX_SHAPE[0] // shape[0]
        bin2 = self.MAX_SHAPE[1] // shape[1]
        self._binning = (bin1, bin2)
        self.shape = shape
        self.max_shape = shape
        self._pixel1 = self.BINNED_PIXEL_SIZE[bin1]
        self._pixel2 = self.BINNED_PIXEL_SIZE[bin2]
        self._mask = False
        self._mask_crc = None
        return


ALL_DETECTORS = {'princetonMTE': PrincetonMTE}
ALL_DETECTORS.update(pyFAI.detectors.ALL_DETECTORS)
# okay decompiling detectors.pyc
