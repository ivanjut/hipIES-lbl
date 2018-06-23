# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/pipeline/cosmics.py
# Compiled at: 2015-07-17 13:23:47
"""
About
=====

cosmics.py is a small and simple python module to detect and clean cosmic ray hits on images (numpy arrays or FITS), using scipy, and based on Pieter van Dokkum's L.A.Cosmic algorithm.

L.A.Cosmic = Laplacian cosmic ray detection

U{http://www.astro.yale.edu/dokkum/lacosmic/}

(article : U{http://arxiv.org/abs/astro-ph/0108003})


Additional features
===================

I pimped this a bit to suit my needs :

        - Automatic recognition of saturated stars, including their full saturation trails.
        This avoids that such stars are treated as big cosmics.
        Indeed saturated stars tend to get even uglier when you try to clean them. Plus they
        keep L.A.Cosmic iterations going on forever.
        This feature is mainly for pretty-image production. It is optional, requires one more parameter (a CCD saturation level in ADU), and uses some 
        nicely robust morphology operations and object extraction.
        
        - Scipy image analysis allows to "label" the actual cosmic ray hits (i.e. group the pixels into local islands).
        A bit special, but I use this in the scope of visualizing a PSF construction.

But otherwise the core is really a 1-to-1 implementation of L.A.Cosmic, and uses the same parameters.
Only the conventions on how filters are applied at the image edges might be different.

No surprise, this python module is much faster then the IRAF implementation, as it does not read/write every step to disk.

Usage
=====

Everything is in the file cosmics.py, all you need to do is to import it. You need pyfits, numpy and scipy.
See the demo scripts for example usages (the second demo uses f2n.py to make pngs, and thus also needs PIL).

Your image should have clean borders, cut away prescan/overscan etc.



Todo
====
Ideas for future improvements :

        - Add something reliable to detect negative glitches (dust on CCD or small traps)
        - Top level functions to simply run all this on either numpy arrays or directly on FITS files
        - Reduce memory usage ... easy
        - Switch from signal to ndimage, homogenize mirror boundaries


Malte Tewes, January 2010
"""
__version__ = '0.4'
import os, numpy as np, scipy.signal as signal, scipy.ndimage as ndimage, pyfits
laplkernel = np.array([[0.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 0.0]])
growkernel = np.ones((3, 3))
dilstruct = np.ones((5, 5))
dilstruct[(0, 0)] = 0
dilstruct[(0, 4)] = 0
dilstruct[(4, 0)] = 0
dilstruct[(4, 4)] = 0

class cosmicsimage():

    def __init__(self, rawarray, pssl=0.0, gain=2.2, readnoise=10.0, sigclip=5.0, sigfrac=0.3, objlim=5.0, satlevel=50000.0, verbose=True):
        """
        
        sigclip : increase this if you detect cosmics where there are none. Default is 5.0, a good value for earth-bound images.
        objlim : increase this if normal stars are detected as cosmics. Default is 5.0, a good value for earth-bound images.
        
        Constructor of the cosmic class, takes a 2D numpy array of your image as main argument.
        sigclip : laplacian-to-noise limit for cosmic ray detection
        objlim : minimum contrast between laplacian image and fine structure image. Use 5.0 if your image is undersampled, HST, ...
        
        satlevel : if we find agglomerations of pixels above this level, we consider it to be a saturated star and
        do not try to correct and pixels around it. A negative satlevel skips this feature.
        
        pssl is the previously subtracted sky level !
        
        real   gain    = 1.8          # gain (electrons/ADU)    (0=unknown)
        real   readn   = 6.5                  # read noise (electrons) (0=unknown)
        ##gain0  string statsec = "*,*"       # section to use for automatic computation of gain
        real   skyval  = 0.           # sky level that has been subtracted (ADU)
        real   sigclip = 3.0          # detection limit for cosmic rays (sigma)
        real   sigfrac = 0.5          # fractional detection limit for neighbouring pixels
        real   objlim  = 3.0           # contrast limit between CR and underlying object
        int    niter   = 1            # maximum number of iterations
        
        """
        self.rawarray = rawarray + pssl
        self.cleanarray = self.rawarray.copy()
        self.mask = np.cast['bool'](np.zeros(self.rawarray.shape))
        self.gain = gain
        self.readnoise = readnoise
        self.sigclip = sigclip
        self.objlim = objlim
        self.sigcliplow = sigclip * sigfrac
        self.satlevel = satlevel
        self.verbose = verbose
        self.pssl = pssl
        self.backgroundlevel = None
        self.satstars = None
        return

    def __str__(self):
        """
        Gives a summary of the current state, including the number of cosmic pixels in the mask etc.
        """
        stringlist = [
         'Input array : (%i, %i), %s' % (self.rawarray.shape[0], self.rawarray.shape[1], self.rawarray.dtype.name),
         'Current cosmic ray mask : %i pixels' % np.sum(self.mask)]
        if self.pssl != 0.0:
            stringlist.append('Using a previously subtracted sky level of %f' % self.pssl)
        if self.satstars != None:
            stringlist.append('Saturated star mask : %i pixels' % np.sum(self.satstars))
        return ('\n').join(stringlist)

    def labelmask(self, verbose=None):
        """
        Finds and labels the cosmic "islands" and returns a list of dicts containing their positions.
        This is made on purpose for visualizations a la f2n.drawstarslist, but could be useful anyway.
        """
        if verbose == None:
            verbose = self.verbose
        if verbose:
            print 'Labeling mask pixels ...'
        dilmask = ndimage.morphology.binary_dilation(self.mask, structure=dilstruct, iterations=1, mask=None, output=None, border_value=0, origin=0, brute_force=False)
        labels, n = ndimage.measurements.label(dilmask)
        slicecouplelist = ndimage.measurements.find_objects(labels)
        if len(slicecouplelist) != n:
            raise RuntimeError, 'Mega error in labelmask !'
        centers = [ [(tup[0].start + tup[0].stop) / 2.0, (tup[1].start + tup[1].stop) / 2.0] for tup in slicecouplelist ]
        sizes = ndimage.measurements.sum(self.mask.ravel(), labels.ravel(), np.arange(1, n + 1, 1))
        retdictlist = [ {'name': '%i' % size, 'x': center[0], 'y': center[1]} for size, center in zip(sizes, centers) ]
        if verbose:
            print 'Labeling done'
        return retdictlist

    def getdilatedmask(self, size=3):
        """
        Returns a morphologically dilated copy of the current mask.
        size = 3 or 5 decides how to dilate.
        """
        if size == 3:
            dilmask = ndimage.morphology.binary_dilation(self.mask, structure=growkernel, iterations=1, mask=None, output=None, border_value=0, origin=0, brute_force=False)
        else:
            if size == 5:
                dilmask = ndimage.morphology.binary_dilation(self.mask, structure=dilstruct, iterations=1, mask=None, output=None, border_value=0, origin=0, brute_force=False)
            else:
                dismask = self.mask.copy()
        return dilmask

    def clean(self, mask=None, verbose=None):
        """
        Given the mask, we replace the actual problematic pixels with the masked 5x5 median value.
        This mimics what is done in L.A.Cosmic, but it's a bit harder to do in python, as there is no
        readymade masked median. So for now we do a loop...
        Saturated stars, if calculated, are also masked : they are not "cleaned", but their pixels are not
        used for the interpolation.
        
        We will directly change self.cleanimage. Instead of using the self.mask, you can supply your
        own mask as argument. This might be useful to apply this cleaning function iteratively.
        But for the true L.A.Cosmic, we don't use this, i.e. we use the full mask at each iteration.
        
        """
        if verbose == None:
            verbose = self.verbose
        if mask == None:
            mask = self.mask
        if verbose:
            print 'Cleaning cosmic affected pixels ...'
        cosmicindices = np.argwhere(mask)
        self.cleanarray[mask] = np.Inf
        w = self.cleanarray.shape[0]
        h = self.cleanarray.shape[1]
        padarray = np.zeros((w + 4, h + 4)) + np.Inf
        padarray[2:w + 2, 2:h + 2] = self.cleanarray.copy()
        if self.satstars != None:
            padarray[2:w + 2, 2:h + 2][self.satstars] = np.Inf
        for cosmicpos in cosmicindices:
            x = cosmicpos[0]
            y = cosmicpos[1]
            cutout = padarray[x:x + 5, y:y + 5].ravel()
            goodcutout = cutout[cutout != np.Inf]
            if np.alen(goodcutout) >= 25:
                raise RuntimeError, 'Mega error in clean !'
            else:
                if np.alen(goodcutout) > 0:
                    replacementvalue = np.median(goodcutout)
                else:
                    print 'OH NO, I HAVE A HUUUUUUUGE COSMIC !!!!!'
                    replacementvalue = self.guessbackgroundlevel()
            self.cleanarray[(x, y)] = replacementvalue

        if verbose:
            print 'Cleaning done'
        return

    def findsatstars(self, verbose=None):
        """
        Uses the satlevel to find saturated stars (not cosmics !), and puts the result as a mask in self.satstars.
        This can then be used to avoid these regions in cosmic detection and cleaning procedures.
        Slow ...
        """
        if verbose == None:
            verbose = self.verbose
        if verbose:
            print 'Detecting saturated stars ...'
        satpixels = self.rawarray > self.satlevel
        m5 = ndimage.filters.median_filter(self.rawarray, size=5, mode='mirror')
        largestruct = m5 > self.satlevel / 2.0
        satstarscenters = np.logical_and(largestruct, satpixels)
        if verbose:
            print 'Building mask of saturated stars ...'
        dilsatpixels = ndimage.morphology.binary_dilation(satpixels, structure=dilstruct, iterations=2, mask=None, output=None, border_value=0, origin=0, brute_force=False)
        dilsatlabels, nsat = ndimage.measurements.label(dilsatpixels)
        if verbose:
            print 'We have %i saturated stars.' % nsat
        outmask = np.zeros(self.rawarray.shape)
        for i in range(1, nsat + 1):
            thisisland = dilsatlabels == i
            overlap = np.logical_and(thisisland, satstarscenters)
            if np.sum(overlap) > 0:
                outmask = np.logical_or(outmask, thisisland)

        self.satstars = np.cast['bool'](outmask)
        if verbose:
            print 'Mask of saturated stars done'
        return

    def getsatstars(self, verbose=None):
        """
        Returns the mask of saturated stars after finding them if not yet done.
        Intended mainly for external use.
        """
        if verbose == None:
            verbose = self.verbose
        if not self.satlevel > 0:
            raise RuntimeError, 'Cannot determine satstars : you gave satlevel <= 0 !'
        if self.satstars == None:
            self.findsatstars(verbose=verbose)
        return self.satstars

    def getmask(self):
        return self.mask

    def getrawarray(self):
        """
        For external use only, as it returns the rawarray minus pssl !
        """
        return self.rawarray - self.pssl

    def getcleanarray(self):
        """
        For external use only, as it returns the cleanarray minus pssl !
        """
        return self.cleanarray - self.pssl

    def guessbackgroundlevel(self):
        """
        Estimates the background level. This could be used to fill pixels in large cosmics.
        """
        if self.backgroundlevel == None:
            self.backgroundlevel = np.median(self.rawarray.ravel())
        return self.backgroundlevel

    def lacosmiciteration(self, verbose=None):
        """
        Performs one iteration of the L.A.Cosmic algorithm.
        It operates on self.cleanarray, and afterwards updates self.mask by adding the newly detected
        cosmics to the existing self.mask. Cleaning is not made automatically ! You have to call
        clean() after each iteration.
        This way you can run it several times in a row to to L.A.Cosmic "iterations".
        See function lacosmic, that mimics the full iterative L.A.Cosmic algorithm.
        
        Returns a dict containing
            - niter : the number of cosmic pixels detected in this iteration
            - nnew : among these, how many were not yet in the mask
            - itermask : the mask of pixels detected in this iteration
            - newmask : the pixels detected that were not yet in the mask
        
        If findsatstars() was called, we exclude these regions from the search.
        
        """
        if verbose == None:
            verbose = self.verbose
        if verbose:
            print 'Convolving image with Laplacian kernel ...'
        subsam = subsample(self.cleanarray)
        conved = signal.convolve2d(subsam, laplkernel, mode='same', boundary='symm')
        cliped = conved.clip(min=0.0)
        lplus = rebin2x2(cliped)
        if verbose:
            print 'Creating noise model ...'
        m5 = ndimage.filters.median_filter(self.cleanarray, size=5, mode='mirror')
        m5clipped = m5.clip(min=1e-05)
        noise = 1.0 / self.gain * np.sqrt(self.gain * m5clipped + self.readnoise * self.readnoise)
        if verbose:
            print 'Calculating Laplacian signal to noise ratio ...'
        s = lplus / (2.0 * noise)
        sp = s - ndimage.filters.median_filter(s, size=5, mode='mirror')
        if verbose:
            print 'Selecting candidate cosmic rays ...'
        candidates = sp > self.sigclip
        nbcandidates = np.sum(candidates)
        if verbose:
            print '  %5i candidate pixels' % nbcandidates
        if self.satstars != None:
            if verbose:
                print 'Masking saturated stars ...'
            candidates = np.logical_and(np.logical_not(self.satstars), candidates)
            nbcandidates = np.sum(candidates)
            if verbose:
                print '  %5i candidate pixels not part of saturated stars' % nbcandidates
        if verbose:
            print 'Building fine structure image ...'
        m3 = ndimage.filters.median_filter(self.cleanarray, size=3, mode='mirror')
        m37 = ndimage.filters.median_filter(m3, size=7, mode='mirror')
        f = m3 - m37
        f = f / noise
        f = f.clip(min=0.01)
        if verbose:
            print 'Removing suspected compact bright objects ...'
        cosmics = np.logical_and(candidates, sp / f > self.objlim)
        nbcosmics = np.sum(cosmics)
        if verbose:
            print '  %5i remaining candidate pixels' % nbcosmics
        if verbose:
            print 'Finding neighboring pixels affected by cosmic rays ...'
        growcosmics = np.cast['bool'](signal.convolve2d(np.cast['float32'](cosmics), growkernel, mode='same', boundary='symm'))
        growcosmics = np.logical_and(sp > self.sigclip, growcosmics)
        finalsel = np.cast['bool'](signal.convolve2d(np.cast['float32'](growcosmics), growkernel, mode='same', boundary='symm'))
        finalsel = np.logical_and(sp > self.sigcliplow, finalsel)
        if self.satstars != None:
            if verbose:
                print 'Masking saturated stars ...'
            finalsel = np.logical_and(np.logical_not(self.satstars), finalsel)
        nbfinal = np.sum(finalsel)
        if verbose:
            print '  %5i pixels detected as cosmics' % nbfinal
        newmask = np.logical_and(np.logical_not(self.mask), finalsel)
        nbnew = np.sum(newmask)
        self.mask = np.logical_or(self.mask, finalsel)
        return {'niter': nbfinal, 'nnew': nbnew, 'itermask': finalsel, 'newmask': newmask}

    def findholes(self, verbose=True):
        """
        Detects "negative cosmics" in the cleanarray and adds them to the mask.
        This is not working yet.
        """
        pass

    def run(self, maxiter=4, verbose=False):
        """
        Full artillery :-)
            - Find saturated stars
            - Run maxiter L.A.Cosmic iterations (stops if no more cosmics are found)
        
        Stops if no cosmics are found or if maxiter is reached.
        """
        if self.satlevel > 0 and self.satstars == None:
            self.findsatstars(verbose=True)
        print 'Starting %i L.A.Cosmic iterations ...' % maxiter
        for i in range(1, maxiter + 1):
            print 'Iteration %i' % i
            iterres = self.lacosmiciteration(verbose=verbose)
            print '%i cosmic pixels (%i new)' % (iterres['niter'], iterres['nnew'])
            self.clean(verbose=verbose)
            if iterres['niter'] == 0:
                break

        return


def fromfits(infilename, hdu=0, verbose=True):
    """
    Reads a FITS file and returns a 2D numpy array of the data.
    Use hdu to specify which HDU you want (default = primary = 0)
    """
    pixelarray, hdr = pyfits.getdata(infilename, hdu, header=True)
    pixelarray = np.asarray(pixelarray).transpose()
    pixelarrayshape = pixelarray.shape
    if verbose:
        print 'FITS import shape : (%i, %i)' % (pixelarrayshape[0], pixelarrayshape[1])
        print 'FITS file BITPIX : %s' % hdr['BITPIX']
        print 'Internal array type :', pixelarray.dtype.name
    return (
     pixelarray, hdr)


def tofits(outfilename, pixelarray, hdr=None, verbose=True):
    """
    Takes a 2D numpy array and write it into a FITS file.
    If you specify a header (pyfits format, as returned by fromfits()) it will be used for the image.
    You can give me boolean numpy arrays, I will convert them into 8 bit integers.
    """
    pixelarrayshape = pixelarray.shape
    if verbose:
        print 'FITS export shape : (%i, %i)' % (pixelarrayshape[0], pixelarrayshape[1])
    if pixelarray.dtype.name == 'bool':
        pixelarray = np.cast['uint8'](pixelarray)
    if os.path.isfile(outfilename):
        os.remove(outfilename)
    if hdr == None:
        hdu = pyfits.PrimaryHDU(pixelarray.transpose())
    else:
        hdu = pyfits.PrimaryHDU(pixelarray.transpose(), hdr)
    hdu.writeto(outfilename)
    if verbose:
        print 'Wrote %s' % outfilename
    return


def subsample(a):
    """
    Returns a 2x2-subsampled version of array a (no interpolation, just cutting pixels in 4).
    The version below is directly from the scipy cookbook on rebinning :
    U{http://www.scipy.org/Cookbook/Rebinning}
    There is ndimage.zoom(cutout.array, 2, order=0, prefilter=False), but it makes funny borders.
    
    """
    newshape = (
     2 * a.shape[0], 2 * a.shape[1])
    slices = [ slice(0, old, float(old) / new) for old, new in zip(a.shape, newshape) ]
    coordinates = np.mgrid[slices]
    indices = coordinates.astype('i')
    return a[tuple(indices)]


def rebin(a, newshape):
    """
    Auxiliary function to rebin an ndarray a.
    U{http://www.scipy.org/Cookbook/Rebinning}
    
            >>> a=rand(6,4); b=rebin(a,(3,2))
        """
    shape = a.shape
    lenShape = len(shape)
    factor = np.asarray(shape) / np.asarray(newshape)
    evList = [
     'a.reshape('] + [ 'newshape[%d],factor[%d],' % (i, i) for i in xrange(lenShape) ] + [')'] + [ '.sum(%d)' % (i + 1) for i in xrange(lenShape) ] + [ '/factor[%d]' % i for i in xrange(lenShape) ]
    return eval(('').join(evList))


def rebin2x2(a):
    """
    Wrapper around rebin that actually rebins 2 by 2
    """
    inshape = np.array(a.shape)
    if not (inshape % 2 == np.zeros(2)).all():
        raise RuntimeError, 'I want even image shapes !'
    return rebin(a, inshape / 2)
# okay decompiling cosmics.pyc
