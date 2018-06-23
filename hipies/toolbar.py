# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/toolbar.py
# Compiled at: 2015-07-28 18:39:00
from PySide import QtGui
from PySide import QtCore

class difftoolbar(QtGui.QToolBar):

    def __init__(self):
        super(difftoolbar, self).__init__()
        self.actionCenterFind = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap('gui/icons_27.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCenterFind.setIcon(icon1)
        self.actionCenterFind.setObjectName('actionCenterFind')
        self.actionPolyMask = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap('gui/icons_05.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPolyMask.setIcon(icon2)
        self.actionPolyMask.setText('')
        self.actionPolyMask.setObjectName('actionPolyMask')
        self.actionOpen = QtGui.QAction(self)
        self.actionOpen.setObjectName('actionOpen')
        self.actionSaveExperiment = QtGui.QAction(self)
        self.actionSaveExperiment.setObjectName('actionSaveExperiment')
        self.actionLoadExperiment = QtGui.QAction(self)
        self.actionLoadExperiment.setObjectName('actionLoadExperiment')
        self.actionClose = QtGui.QAction(self)
        self.actionClose.setObjectName('actionClose')
        self.actionMasking = QtGui.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap('gui/icons_03.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMasking.setIcon(icon3)
        self.actionMasking.setObjectName('actionMasking')
        self.actionLog_Intensity = QtGui.QAction(self)
        self.actionLog_Intensity.setCheckable(True)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap('gui/icons_02.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLog_Intensity.setIcon(icon4)
        self.actionLog_Intensity.setObjectName('actionLog_Intensity')
        self.actionLog_Intensity.setChecked(True)
        self.actionCake = QtGui.QAction(self)
        self.actionCake.setCheckable(True)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap('gui/icons_04.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCake.setIcon(icon5)
        self.actionCake.setObjectName('actionCake')
        self.actionRemove_Cosmics = QtGui.QAction(self)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap('gui/icons_06.png'), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionRemove_Cosmics.setIcon(icon6)
        self.actionRemove_Cosmics.setText('')
        self.actionRemove_Cosmics.setObjectName('actionRemove_Cosmics')
        self.actionMaskLoad = QtGui.QAction(self)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap('gui/icons_08.png'), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionMaskLoad.setIcon(icon7)
        self.actionMaskLoad.setText('')
        self.actionMaskLoad.setObjectName('actionMaskLoad')
        self.actionMultiPlot = QtGui.QAction(self)
        self.actionMultiPlot.setCheckable(True)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap('gui/icons_07.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMultiPlot.setIcon(icon8)
        self.actionMultiPlot.setObjectName('actionMultiPlot')
        self.actionLibrary = QtGui.QAction(self)
        self.actionLibrary.setObjectName('actionLibrary')
        self.actionViewer = QtGui.QAction(self)
        self.actionViewer.setObjectName('actionViewer')
        self.actionAdd = QtGui.QAction(self)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap('gui/icons_11.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd.setIcon(icon9)
        self.actionAdd.setObjectName('actionAdd')
        self.actionSubtract = QtGui.QAction(self)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap('gui/icons_13.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSubtract.setIcon(icon10)
        self.actionSubtract.setObjectName('actionSubtract')
        self.actionAdd_with_coefficient = QtGui.QAction(self)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap('gui/icons_14.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_with_coefficient.setIcon(icon11)
        self.actionAdd_with_coefficient.setObjectName('actionAdd_with_coefficient')
        self.actionSubtract_with_coefficient = QtGui.QAction(self)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap('gui/icons_15.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSubtract_with_coefficient.setIcon(icon12)
        self.actionSubtract_with_coefficient.setObjectName('actionSubtract_with_coefficient')
        self.actionDivide = QtGui.QAction(self)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap('gui/icons_12.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDivide.setIcon(icon13)
        self.actionDivide.setObjectName('actionDivide')
        self.actionAverage = QtGui.QAction(self)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap('gui/icons_16.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAverage.setIcon(icon14)
        self.actionAverage.setObjectName('actionAverage')
        self.actionRadial_Symmetry = QtGui.QAction(self)
        self.actionRadial_Symmetry.setCheckable(True)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap('gui/icons_18.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRadial_Symmetry.setIcon(icon15)
        self.actionRadial_Symmetry.setObjectName('actionRadial_Symmetry')
        self.actionMirror_Symmetry = QtGui.QAction(self)
        self.actionMirror_Symmetry.setCheckable(True)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap('gui/icons_17.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMirror_Symmetry.setIcon(icon16)
        self.actionMirror_Symmetry.setObjectName('actionMirror_Symmetry')
        self.actionShow_Mask = QtGui.QAction(self)
        self.actionShow_Mask.setCheckable(True)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap('gui/icons_20.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon17.addPixmap(QtGui.QPixmap('gui/icons_19.png'), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionShow_Mask.setIcon(icon17)
        self.actionShow_Mask.setObjectName('actionShow_Mask')
        self.actionPolygon_Cut = QtGui.QAction(self)
        self.actionPolygon_Cut.setCheckable(True)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap('gui/icons_21.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPolygon_Cut.setIcon(icon18)
        self.actionPolygon_Cut.setObjectName('actionPolygon_Cut')
        self.actionVertical_Cut = QtGui.QAction(self)
        self.actionVertical_Cut.setCheckable(True)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap('gui/icons_22.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionVertical_Cut.setIcon(icon19)
        self.actionVertical_Cut.setObjectName('actionVertical_Cut')
        self.actionHorizontal_Cut = QtGui.QAction(self)
        self.actionHorizontal_Cut.setCheckable(True)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap('gui/icons_23.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHorizontal_Cut.setIcon(icon20)
        self.actionHorizontal_Cut.setObjectName('actionHorizontal_Cut')
        self.actionLine_Cut = QtGui.QAction(self)
        self.actionLine_Cut.setCheckable(True)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap('gui/icons_24.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLine_Cut.setIcon(icon21)
        self.actionLine_Cut.setObjectName('actionLine_Cut')
        self.actionTimeline = QtGui.QAction(self)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap('gui/icons_26.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionTimeline.setIcon(icon22)
        self.actionTimeline.setObjectName('actionTimeline')
        self.actionRemeshing = QtGui.QAction(self)
        self.actionRemeshing.setCheckable(True)
        icon23 = QtGui.QIcon()
        icon23.addPixmap(QtGui.QPixmap('gui/icons_25.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRemeshing.setIcon(icon23)
        self.actionRemeshing.setObjectName('actionRemeshing')
        self.actionExport_Image = QtGui.QAction(self)
        self.actionExport_Image.setObjectName('actionExport_Image')
        self.actionRefine_Center = QtGui.QAction(self)
        icon24 = QtGui.QIcon()
        icon24.addPixmap(QtGui.QPixmap('gui/icons_28.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefine_Center.setIcon(icon24)
        self.actionRefine_Center.setObjectName('actionRefine_Center')
        self.actionCalibrate_AgB = QtGui.QAction(self)
        icon25 = QtGui.QIcon()
        icon25.addPixmap(QtGui.QPixmap('gui/icons_29.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCalibrate_AgB.setIcon(icon25)
        self.actionCalibrate_AgB.setObjectName('actionCalibrate_AgB')
        menu = QtGui.QMenu()
        menu.addAction(self.actionPolyMask)
        menu.addAction(self.actionRemove_Cosmics)
        menu.addAction(self.actionMaskLoad)
        toolbuttonMasking = QtGui.QToolButton()
        toolbuttonMasking.setDefaultAction(self.actionMasking)
        toolbuttonMasking.setMenu(menu)
        toolbuttonMasking.setPopupMode(QtGui.QToolButton.InstantPopup)
        toolbuttonMaskingAction = QtGui.QWidgetAction(self)
        toolbuttonMaskingAction.setDefaultWidget(toolbuttonMasking)
        self.setIconSize(QtCore.QSize(32, 32))
        self.addAction(self.actionCalibrate_AgB)
        self.addAction(self.actionCenterFind)
        self.addAction(self.actionRefine_Center)
        self.addAction(self.actionShow_Mask)
        self.addAction(toolbuttonMaskingAction)
        self.addAction(self.actionCake)
        self.addAction(self.actionRemeshing)
        self.addAction(self.actionLine_Cut)
        self.addAction(self.actionVertical_Cut)
        self.addAction(self.actionHorizontal_Cut)
        self.addAction(self.actionLog_Intensity)
        self.addAction(self.actionRadial_Symmetry)
        self.addAction(self.actionMirror_Symmetry)

    def connecttriggers(self, calibrate, centerfind, refine, showmask, cake, remesh, linecut, vertcut, horzcut, logint, radialsym, mirrorsym, roi):
        self.actionCalibrate_AgB.triggered.connect(calibrate)
        self.actionCenterFind.triggered.connect(centerfind)
        self.actionRefine_Center.triggered.connect(refine)
        self.actionShow_Mask.triggered.connect(showmask)
        self.actionCake.triggered.connect(cake)
        self.actionRemeshing.triggered.connect(remesh)
        self.actionLine_Cut.triggered.connect(linecut)
        self.actionVertical_Cut.triggered.connect(vertcut)
        self.actionHorizontal_Cut.triggered.connect(horzcut)
        self.actionLog_Intensity.triggered.connect(logint)
        self.actionRadial_Symmetry.triggered.connect(radialsym)
        self.actionMirror_Symmetry.triggered.connect(mirrorsym)
# okay decompiling toolbar.pyc
