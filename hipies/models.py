# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/models.py
# Compiled at: 2015-07-17 13:23:47
from PySide.QtCore import Qt
from PySide import QtCore

class openfilesmodel(QtCore.QAbstractListModel):
    """
    This model creates modelitems for each open tab for navigation
    """

    def __init__(self, tabwidget):
        QtCore.QAbstractListModel.__init__(self)
        self.tabwidget = tabwidget

    def widgetchanged(self):
        self.dataChanged.emit(0, 0)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.tabwidget.count()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.tabwidget.tabText(index.row())
        return
        return
# okay decompiling models.pyc
