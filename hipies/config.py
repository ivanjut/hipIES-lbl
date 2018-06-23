# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/config.py
# Compiled at: 2015-07-17 13:23:47
import pickle, pyFAI
from pyFAI import geometry
from pipeline import detectors
from pyqtgraph.parametertree import Parameter
import numpy as np

class PyFAIGeometry(pyFAI.geometry.Geometry):

    def set_fit2d(self, wavelength, distance, center_x, center_y, tilt, rotation):
        self.set_wavelength(wavelength * 1e-10)
        self.setFit2D(distance, center_x, center_y, tilt, rotation)

    def get_fit2d(self):
        param_dict = self.getFit2D()
        return [
         self.get_wavelength() * 10000000000.0,
         param_dict['directDist'],
         param_dict['centerX'],
         param_dict['centerY'],
         param_dict['tilt'],
         param_dict['tiltPlanRotation']]


class experiment(Parameter):

    def __init__(self, path=None):
        self.iscalibrated = False
        if path is None:
            config = [{'name': 'Name', 'type': 'str', 'value': 'New Experiment'}, {'name': 'Detector', 'type': 'str', 'value': 'Unknown'},
             {'name': 'Pixel Size X', 'type': 'float', 'value': 0, 'siPrefix': True, 'suffix': 'm', 'step': 1e-06},
             {'name': 'Pixel Size Y', 'type': 'float', 'value': 0, 'siPrefix': True, 'suffix': 'm', 'step': 1e-06}, {'name': 'Center X', 'type': 'int', 'value': 0, 'suffix': ' px'}, {'name': 'Center Y', 'type': 'int', 'value': 0, 'suffix': ' px'},
             {'name': 'Detector Distance', 'type': 'float', 'value': 1, 'siPrefix': True, 'suffix': 'm', 'step': 0.001}, {'name': 'Energy', 'type': 'float', 'value': 10000, 'siPrefix': True, 'suffix': 'eV'}, {'name': 'Wavelength', 'type': 'float', 'value': 1, 'siPrefix': True, 'suffix': 'm'}, {'name': 'Notes', 'type': 'text', 'value': ''}]
            super(experiment, self).__init__(name='Experiment Properties', type='group', children=config)
            EnergyParam = self.param('Energy')
            WavelengthParam = self.param('Wavelength')
            EnergyParam.sigValueChanged.connect(self.EnergyChanged)
            WavelengthParam.sigValueChanged.connect(self.WavelengthChanged)
            self._mask = None
            self.EnergyChanged()
        else:
            with open(path, 'r') as (f):
                self.config = pickle.load(f)
        return

    @property
    def mask(self):
        """I'm the 'mask' property."""
        return self._mask

    @mask.setter
    def mask(self, value):
        self._mask = value

    @mask.deleter
    def mask(self):
        del self._mask

    def addtomask(self, maskedarea):
        if self._mask is None:
            self._mask = maskedarea.astype(np.int)
        else:
            if self._mask.shape == maskedarea.shape:
                self._mask = np.bitwise_or(self._mask, maskedarea.astype(np.int))
        return

    def EnergyChanged(self):
        self.param('Wavelength').setValue(1.239842e-06 / self.param('Energy').value(), blockSignal=self.WavelengthChanged)

    def WavelengthChanged(self):
        self.param('Energy').setValue(1.239842e-06 / self.param('Wavelength').value(), blockSignal=self.EnergyChanged)

    def save(self):
        with open(self.getvalue('Name') + '.exp', 'w') as (f):
            pickle.dump(self.saveState(), f)
        with open(self.getvalue('Name') + '.expmask', 'w') as (f):
            np.save(f, self.mask)

    def getvalue(self, name):
        return self.child(name).value()

    def setvalue(self, name, value):
        self.child(name).setValue(value)

    def setcenter(self, cen):
        self.setvalue('Center X', cen[0])
        self.setvalue('Center Y', cen[1])

    def getAI(self):
        """
        :rtype : pyFAI.AzimuthalIntegrator
        """
        AI = pyFAI.AzimuthalIntegrator(dist=self.getvalue('Detector Distance'), poni1=self.getvalue('Pixel Size X') * self.getvalue('Center Y'), poni2=self.getvalue('Pixel Size Y') * self.getvalue('Center X'), rot1=0, rot2=0, rot3=0, pixel1=self.getvalue('Pixel Size Y'), pixel2=self.getvalue('Pixel Size X'), detector=self.getDetector(), wavelength=self.getvalue('Wavelength'))
        return AI

    def getGeometry(self):
        """
        :rtype : pyFAI.Geometry
        """
        geo = PyFAIGeometry(dist=self.getvalue('Detector Distance'), poni1=self.getvalue('Pixel Size X') * self.getvalue('Center Y'), poni2=self.getvalue('Pixel Size Y') * self.getvalue('Center X'), rot1=0, rot2=0, rot3=0, pixel1=self.getvalue('Pixel Size Y'), pixel2=self.getvalue('Pixel Size X'), detector=self.getDetector(), wavelength=self.getvalue('Wavelength'))
        return geo

    def getDetector(self):
        key = self.getvalue('Detector')
        if key in detectors.ALL_DETECTORS:
            return detectors.ALL_DETECTORS[self.getvalue('Detector')]()

    def edit(self):
        pass
# okay decompiling config.pyc
