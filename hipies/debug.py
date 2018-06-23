# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/debug.py
# Compiled at: 2015-07-17 13:23:47
import time, matplotlib.pylab as plt, inspect

def timeit(method):
    """
    Use this as a decorator to time a function
    """

    def timed(*args, **kw):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        print 'Find peaks called from ' + calframe[1][3]
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '%r  %2.3f sec' % (
         method.__name__, te - ts)
        return result

    return timed


def frustration():
    print '(\xef\xbe\x89\xe0\xb2\xa5\xe7\x9b\x8a\xe0\xb2\xa5\xef\xbc\x89\xef\xbe\x89\xef\xbb\xbf \xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb'


def showimage(img):
    plt.imshow(img)
    plt.show()
    print 'Image displayed!'
# okay decompiling debug.pyc
