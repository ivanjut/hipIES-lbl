# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/saxs_calibration.py
# Compiled at: 2015-07-17 13:23:47
import warnings, threading, numpy, scipy.optimize, pyFAI
FIT_PARAMETER = [
 'wavelength',
 'distance',
 'center_x',
 'center_y',
 'tilt',
 'rotation']
LN_2 = numpy.log(2)
x = []
y = []

def gauss(x_max, y_max, fwhm, x_array):
    return y_max * numpy.exp(-LN_2 * ((x_array - x_max) / fwhm * 2) ** 2)


def lorentz(x_max, y_max, fwhm, x_array):
    return y_max * 1.0 / (1 + ((x_array - x_max) / fwhm * 2) ** 2)


def pseudo_voigt(x_max, y_max, fwhm, eta, x_array):
    return eta * gauss(x_max, y_max, fwhm, x_array) + (1 - eta) * lorentz(x_max, y_max, fwhm, x_array)


def fit_maxima(x_data, y_data):
    err = lambda p, x, y: y - (p[0] + p[1] * x + pseudo_voigt(p[2], p[3], p[4], p[5], x))
    y_min = y_data.min()
    y_max = y_data.max() - y_min
    x_max = x_data[y_data.argmax()]
    parameter = [y_min, 1e-06, x_max, y_max, 1, 1]
    args = (x_data, y_data)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        parameter, info = scipy.optimize.leastsq(err, parameter, args)
    maxima = parameter[2]
    if info != 5 and maxima > x_data.min() and maxima < x_data.max():
        return parameter[2]
    return numpy.nan


def _error_function(parameter, arguments):
    """
    The error functions returns the distances using the current parameter.
    This is a helper function for the fitting process.
    """
    geometry, d_spacings, maxima, selected_parameter = arguments
    mask = [ sel in selected_parameter for sel in FIT_PARAMETER ]
    param = numpy.array(geometry.get_fit2d())
    param[numpy.array(mask)] = parameter
    geometry.set_fit2d(*param)
    return peak_distance(geometry, d_spacings, maxima)


def fit_geometry(geometry, maxima, d_spacings, selected_parameter):
    args = [
     geometry, d_spacings, maxima, selected_parameter]
    mask = numpy.array([ sel in selected_parameter for sel in FIT_PARAMETER ])
    start_parameter = numpy.array(geometry.get_fit2d())[mask]
    if len(start_parameter) >= len(maxima[0]):
        raise Exception('More variables then fit points.')
    _, cov_x, info, _, _ = scipy.optimize.leastsq(_error_function, start_parameter, args, full_output=True)
    fit_parameter = numpy.array(geometry.get_fit2d())[mask]
    dof = len(maxima[0]) - len(start_parameter)
    chisq = (info['fvec'] ** 2).sum()
    info_out = {'calls': info['nfev'], 'dof': dof, 
       'sum_chi_square': chisq}
    info_out['variance_residuals'] = chisq / float(dof)
    for i, name in enumerate(selected_parameter):
        if cov_x is not None:
            ase = numpy.sqrt(cov_x[(i, i)]) * numpy.sqrt(chisq / float(dof))
        else:
            ase = numpy.NAN
        info_out['ase_%s' % name] = ase
        percent_ase = round(ase / (abs(fit_parameter[i]) * 0.01), 3)
        info_out['percent_ase_%s' % name] = percent_ase
        info_out[name] = fit_parameter[i]

    return info_out


def radial_array(beam_center, shape):
    """
    Returns array with shape where every point is the radial distance to the
    beam center in pixel.
    """
    pos_x, pos_y = numpy.meshgrid(numpy.arange(shape[1]), numpy.arange(shape[0]))
    return numpy.sqrt((pos_x - beam_center[0]) ** 2 + (pos_y - beam_center[1]) ** 2)


def ring_maxima(geometry, d_spacing, image, radial_pos, step_size):
    """
    Returns x and y arrays of maximum positions [pixel] found on the ring
    defined by pyFAI geometry and d_spacing on the given image
    """
    tth = 2 * numpy.arcsin(geometry.get_wavelength() / (2e-10 * d_spacing))
    radius = geometry.get_dist() * numpy.tan(tth) / geometry.get_pixel1()
    center = (geometry.getFit2D()['centerX'], geometry.getFit2D()['centerY'])
    alpha = numpy.arange(0, numpy.pi * 2, step_size / float(radius))
    circle_x = numpy.round(center[0] + numpy.sin(alpha) * radius)
    circle_y = numpy.round(center[1] + numpy.cos(alpha) * radius)
    half_step = int(numpy.ceil(step_size / 2.0))
    x_0 = circle_x - half_step
    x_1 = circle_x + half_step
    y_0 = circle_y - half_step
    y_1 = circle_y + half_step
    mask = numpy.where((x_0 >= 0) & (y_0 >= 0) & (y_1 < image.shape[0]) & (x_1 < image.shape[1]))
    x_0 = x_0[mask]
    x_1 = x_1[mask]
    y_0 = y_0[mask]
    y_1 = y_1[mask]
    maxima_x = []
    maxima_y = []
    for i in range(len(x_0)):
        roi = image[y_0[i]:y_1[i], x_0[i]:x_1[i]]
        pos = radial_pos[y_0[i]:y_1[i], x_0[i]:x_1[i]]
        if roi.size < half_step ** 2:
            continue
        x_hist, y_hist, _, _ = pyFAI.histogram.histogram(pos, roi, step_size)
        maximum = fit_maxima(x_hist, y_hist)
        if maximum is numpy.nan:
            continue
        scale = float(maximum / radius)
        maxima_x.append(center[0] + (x_0[i] + half_step - center[0]) * scale)
        maxima_y.append(center[1] + (y_0[i] + half_step - center[1]) * scale)

    return (
     numpy.array(maxima_x), numpy.array(maxima_y), radial_pos)


def peak_distance(geometry, d_spacings, (x_peaks, y_peaks)):
    """
    Returns the minimum distances in 2*theta between given peaks in pixel and a 
    d_spacings in angstrom using the pyFAI geometry.
    """
    wavelength = geometry.get_wavelength()
    tth_rings = 2 * numpy.arcsin(wavelength / (2e-10 * d_spacings))
    distance = [ numpy.abs(tth_rings - tth).min() for tth in geometry.tth(y_peaks, x_peaks)
               ]
    return numpy.array(distance)


def circle_center_distance(center, x_array, y_array):
    """
    Returns the algebraic distances between the 2D points in x_array, y_array
    and the mean circle center.
    """
    r_array = numpy.sqrt((x_array - center[0]) ** 2 + (y_array - center[1]) ** 2)
    return r_array - r_array.mean()


def fit_circle(x_array, y_array):
    """
    Returns the center (x, y) and the radius of the fitted circle defined by
    the points in x_array and y_array.
    """
    xc_m = numpy.mean(x_array)
    yc_m = numpy.mean(y_array)
    center, _ = scipy.optimize.leastsq(circle_center_distance, (
     xc_m, yc_m), (
     x_array, y_array))
    radius = numpy.sqrt((x_array - center[0]) ** 2 + (y_array - center[1]) ** 2).mean()
    return (
     center, radius)


def quick_calibration(wavelength, pixel_size, d_spacing, x_array, y_array):
    """
    Returns pyFAI geometry by fitting a circle to a d-spacing ring.  
    """
    center, radius = fit_circle(x_array, y_array)
    tth = 2 * numpy.arcsin(wavelength / (2e-10 * d_spacing))
    sdd = pixel_size[0] * radius * numpy.cos(tth) * 1.0 / numpy.sin(tth)
    return PyFAIGeometry(sdd, center[1] * pixel_size[1], center[0] * pixel_size[0], 1e-06, 1e-06, 1e-06, pixel_size[0], pixel_size[1], wavelength=wavelength)


def set_PyFAIGeometry(agb):
    wave = agb.wavelength_ * 1e-10
    a = PyFAIGeometry(agb.sdd_, agb.center_[1] * agb.pixel_size_[1], agb.center_[0] * agb.pixel_size_[0], 1e-06, 1e-06, 1e-06, agb.pixel_size_[0], agb.pixel_size_[1], wavelength=wave)
    return a


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


class FitThread(threading.Thread):

    def __init__(self, geometry, d_spacings, image, selected_parameter, step_size):
        threading.Thread.__init__(self)
        self.geometry = geometry
        self.d_spacings = d_spacings
        self.image = image
        self.selected_paramter = selected_parameter
        self.step_size = step_size
        self.status = [0, len(d_spacings)]
        self.info = {}
        self.circle_patches = []

    def run(self):
        center = (
         self.geometry.getFit2D()['centerX'],
         self.geometry.getFit2D()['centerY'])
        radial_pos = radial_array(center, self.image.shape)
        x_data, y_data = [], []
        for d_spacing in self.d_spacings:
            maxima_x, maxima_y, radial_pos = ring_maxima(self.geometry, d_spacing, self.image, radial_pos, self.step_size)
            x_data.extend(maxima_x)
            y_data.extend(maxima_y)
            self.status[0] += 1

        try:
            info = fit_geometry(self.geometry, (
             numpy.array(x_data), numpy.array(y_data)), self.d_spacings, self.selected_paramter)
            info.update({'error': False, 'error_msg': ''})
            self.info = info
        except Exception as e:
            self.info = {'error': True, 'error_msg': e.message}

    def get_status(self):
        return tuple(self.status)

    def get_info(self):
        return self.info

    def get_circle_patches(self):
        return self.circle_patches


def dpdak_saxs_calibration(img, geometry, d_spacings, fit_param, step_size):
    fit_thread = FitThread(geometry, d_spacings, img, fit_param, step_size)
    fit_thread.start()
    params = geometry.get_fit2d()
    return (
     params[1] / 1000.0, [params[2], params[3]])


def saxs_calibration(img, agb):
    max_iter = 10
    tol = 0.001
    d_spacings = numpy.array([58.367, 29.1835, 19.45567, 14.59175,
     11.6734, 9.72783, 8.33814, 7.29587])
    step_size = 49
    geometry = set_PyFAIGeometry(agb)
    fit_param = [
     'distance', 'center_x', 'center_y', 'tilt']
    for i in range(10):
        fit_thread = FitThread(geometry, d_spacings, img, fit_param, step_size)
        fit_thread.start()
        fit_thread.join()

    params = geometry.get_fit2d()
    agb.setSDD(params[1] / 1000.0)
    agb.setCenter(params[2:4])
    return agb
# okay decompiling saxs_calibration.pyc
