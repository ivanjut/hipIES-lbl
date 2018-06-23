# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/watcher.py
# Compiled at: 2015-07-17 13:23:47
from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import Qt
import os

class newfilewatcher(QtCore.QFileSystemWatcher):
    newFilesDetected = QtCore.Signal(str, list)

    def __init__(self):
        super(newfilewatcher, self).__init__()
        self.childrendict = dict()
        self.directoryChanged.connect(self.checkdirectory)

    def addPath(self, path):
        super(newfilewatcher, self).addPath(path)
        self.childrendict[path] = set(os.listdir(path))

    def checkdirectory(self, path):
        updatedchildren = set(os.listdir(path))
        newchildren = updatedchildren - self.childrendict[path]
        self.childrendict[path] = updatedchildren
        self.newFilesDetected.emit(path, list(newchildren))
# okay decompiling watcher.pyc
