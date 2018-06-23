# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 29 2018, 20:59:26) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/ivanjut333/PycharmProjects/HipIES/hipies/viewer.py
# Compiled at: 2015-07-28 18:39:00
import os
from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import Qt
import pyqtgraph as pg, numpy as np
from pipeline import detectors
from fabio import edfimage
import debug, pipeline

class imageTabTracker(QtGui.QWidget):

    def __init__(self, paths, experiment, parent, operation=None):
        """
        A collection of references that can be used to make an imageTab dynamically and dispose of it when unneeded
        :type paths: list[str]
        :type experiment: config.experiment
        :type parent: main.MyMainWindow
        :type operation:
        :return:
        """
        super(imageTabTracker, self).__init__()
        self.paths = paths
        self.experiment = experiment
        self.parent = parent
        self.operation = operation
        self.tab = None
        self.layout = None
        parent.listmodel.widgetchanged()
        self.isloaded = False
        return

    def load(self):
        """
        load this tab; rebuild the viewer
        """
        if not self.isloaded:
            if self.operation is None and len(self.paths) == 1:
                self.parent.ui.filenamelabel.setText(self.paths[0])
                dimg = pipeline.loader.diffimage(filepath=self.paths[0], experiment=self.experiment)
            else:
                imgdata = [ pipeline.loader.loadimage(path) for path in self.paths ]
                imgdata = self.operation(imgdata)
                dimg = pipeline.loader.diffimage(filepath=self.paths[0], data=imgdata, experiment=self.experiment)
            self.layout = QtGui.QHBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.tab = imageTab(dimg, self.parent, self.paths)
            self.layout.addWidget(self.tab)
            self.isloaded = True
            self.tab.cache1Dintegration.connect(self.cache1Dintegration)
            self.tab.send1Dintegration()
        return

    def cache1Dintegration(self, q, I):
        self.q = q
        self.I = I

    def unload(self):
        """
        orphan the tab widgets and queue them for deletion. Mwahahaha.
        """
        if self.isloaded:
            for child in self.children():
                if type(child) is imageTab:
                    self.layout.removeWidget(child)
                    child.deleteLater()
                if type(child) is QtGui.QHBoxLayout:
                    child.parent = None
                    child.deleteLater()

            self.tab = None
            self.layout = None
            self.isloaded = False
        return

    def replotassecondary(self):
        self.parent.integration.plot(self.q, self.I, pen=pg.mkPen('#555555'))


class imageTab(QtGui.QWidget):
    cache1Dintegration = QtCore.Signal(np.ndarray, np.ndarray)

    def __init__(self, dimg, parent, paths=None):
        """
        A tab containing an imageview. Also manages functionality connected to a specific tab (masking/integration)
        :param imgdata:
        :param experiment:
        :return:
        """
        super(imageTab, self).__init__()
        self.region = None
        self.maskROI = None
        self.istimeline = False
        self.layout = QtGui.QStackedLayout(self)
        if paths is not None:
            self.path = paths[0]
        else:
            self.path = None
        self.dimg = dimg
        self.parentwindow = parent
        self.dimg.experiment.addtomask(self.dimg.data < 0)
        self.activeaction = None
        self.viewbox = pg.ViewBox()
        self.imageitem = pg.ImageItem()
        self.viewbox.addItem(self.imageitem)
        self.graphicslayoutwidget = pg.GraphicsLayoutWidget()
        self.graphicslayoutwidget.addItem(self.viewbox)
        self.viewbox.setAspectLocked(True)
        self.imghistLUT = pg.HistogramLUTItem(self.imageitem)
        self.graphicslayoutwidget.addItem(self.imghistLUT, 0, 1)
        linepen = pg.mkPen('#FFA500')
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=linepen)
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=linepen)
        self.vLine.setVisible(False)
        self.hLine.setVisible(False)
        self.viewbox.addItem(self.vLine, ignoreBounds=True)
        self.viewbox.addItem(self.hLine, ignoreBounds=True)
        self.imageitem.border = pg.mkPen('w')
        self.coordslabel = QtGui.QLabel('')
        self.layout.addWidget(self.coordslabel)
        self.coordslabel.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.coordslabel.setStyleSheet('background-color: rgba(0,0,0,0%)')
        self.graphicslayoutwidget.scene().sigMouseMoved.connect(self.mouseMoved)
        self.layout.setStackingMode(QtGui.QStackedLayout.StackAll)
        self.coordslabel.mouseMoveEvent = self.graphicslayoutwidget.mouseMoveEvent
        self.coordslabel.mousePressEvent = self.graphicslayoutwidget.mousePressEvent
        self.coordslabel.mouseReleaseEvent = self.graphicslayoutwidget.mouseReleaseEvent
        self.coordslabel.mouseDoubleClickEvent = self.graphicslayoutwidget.mouseDoubleClickEvent
        self.coordslabel.mouseGrabber = self.graphicslayoutwidget.mouseGrabber
        self.coordslabel.wheelEvent = self.graphicslayoutwidget.wheelEvent
        self.coordslabel.leaveEvent = self.graphicslayoutwidget.leaveEvent
        self.coordslabel.enterEvent = self.graphicslayoutwidget.enterEvent
        self.coordslabel.setMouseTracking(True)
        self.centerplot = None
        backwidget = QtGui.QWidget()
        self.layout.addWidget(backwidget)
        self.backlayout = QtGui.QHBoxLayout(backwidget)
        self.backlayout.setContentsMargins(0, 0, 0, 0)
        self.backlayout.addWidget(self.graphicslayoutwidget)
        self.maskimage = pg.ImageItem(opacity=0.25)
        self.viewbox.addItem(self.maskimage)
        if self.dimg.data is not None:
            self.redrawimage()
            self.q, self.radialprofile = pipeline.integration.radialintegrate(self.dimg)
            if self.dimg.experiment.iscalibrated:
                self.replot()
                self.drawcenter()
        return

    def send1Dintegration(self):
        self.cache1Dintegration.emit(self.q, self.radialprofile)

    def mouseMoved(self, evt):
        """
        when the mouse is moved in the viewer, translate the crosshair, recalculate coordinates
        """
        pos = evt
        if self.viewbox.sceneBoundingRect().contains(pos):
            mousePoint = self.viewbox.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            if (0 < mousePoint.x() < self.dimg.data.shape[0]) & (0 < mousePoint.y() < self.dimg.data.shape[1]):
                if self.dimg.experiment.iscalibrated:
                    x = mousePoint.x()
                    y = mousePoint.y()
                    iscake = self.parentwindow.difftoolbar.actionCake.isChecked()
                    isremesh = self.parentwindow.difftoolbar.actionRemeshing.isChecked()
                    if iscake:
                        q = pixel2cake(x, y, self.dimg)
                    else:
                        if isremesh:
                            return
                        q = pixel2q(x, y, self.dimg.experiment)
                    self.coordslabel.setText(u"<span style='font-size: 12pt;background-color:black;'>x=%0.1f,   <span style=''>y=%0.1f</span>,   <span style=''>I=%0.0f</span>,  q=%0.3f \u212b\u207b\xb9,  q<sub>z</sub>=%0.3f \u212b\u207b\xb9,  q<sub>\u2225\u2225</sub>=%0.3f \u212b\u207b\xb9</span>,  r=%0.1f" % (
                     mousePoint.x(),
                     mousePoint.y(),
                     self.dimg.data[(int(mousePoint.x()),
                      int(mousePoint.y()))],
                     q,
                     pixel2q(None, mousePoint.y(), self.dimg.experiment),
                     pixel2q(mousePoint.x(), None, self.dimg.experiment),
                     np.sqrt((mousePoint.x() - self.dimg.experiment.getvalue('Center X')) ** 2 + (mousePoint.y() - self.dimg.experiment.getvalue('Center Y')) ** 2)))
                else:
                    self.coordslabel.setText(u"<span style='font-size: 12pt;background-color:black;'>x=%0.1f,   <span style=''>y=%0.1f</span>,   <span style=''>I=%0.0f</span>,  Calibration Required..." % (
                     mousePoint.x(),
                     mousePoint.y(),
                     self.dimg.data[(int(mousePoint.x()),
                      int(mousePoint.y()))]))
                self.coordslabel.setVisible(True)
            else:
                self.coordslabel.setVisible(False)
            self.parentwindow.qLine.setPos(pixel2q(mousePoint.x(), mousePoint.y(), self.dimg.experiment))
        return

    def leaveEvent(self, evt):
        """
        hide crosshair and coordinates when mouse leaves viewer
        """
        self.hLine.setVisible(False)
        self.vLine.setVisible(False)
        self.coordslabel.setVisible(False)
        self.parentwindow.qLine.setVisible(False)

    def enterEvent(self, evt):
        """
        show crosshair and coordinates when mouse enters viewer
        """
        self.hLine.setVisible(True)
        self.vLine.setVisible(True)
        self.parentwindow.qLine.setVisible(True)

    def redrawimageLowRes(self):
        self.redrawimage(forcelow=True)

    def redrawimage(self, forcelow=False):
        """
        redraws the diffraction image, checking drawing modes (log, symmetry, mask, cake)
        """
        if self.parentwindow.ui.viewmode.currentIndex() == 1 or not self.istimeline:
            toolbar = self.parentwindow.difftoolbar
        else:
            if self.parentwindow.ui.viewmode.currentIndex() == 2 or self.istimeline:
                toolbar = self.parentwindow.timelinetoolbar
            else:
                print 'Redraw somehow activated from wrong tab'
                debug.frustration()
                toolbar = None
        islogintensity = toolbar.actionLog_Intensity.isChecked()
        isradialsymmetry = toolbar.actionRadial_Symmetry.isChecked()
        ismirrorsymmetry = toolbar.actionMirror_Symmetry.isChecked()
        ismaskshown = toolbar.actionShow_Mask.isChecked()
        iscake = toolbar.actionCake.isChecked()
        isremesh = toolbar.actionRemeshing.isChecked()
        if forcelow:
            img = self.dimg.thumbnail.copy()
            scale = 10
        else:
            img = self.dimg.data
            scale = 1
        if isradialsymmetry:
            centerx = self.dimg.experiment.getvalue('Center X')
            centery = self.dimg.experiment.getvalue('Center Y')
            symimg = np.rot90(img.copy(), 2)
            xshift = -(img.shape[0] - 2 * centerx)
            yshift = -(img.shape[1] - 2 * centery)
            symimg = np.roll(symimg, int(xshift), axis=0)
            symimg = np.roll(symimg, int(yshift), axis=1)
            marginmask = 1 - self.dimg.experiment.mask
            x, y = np.indices(img.shape)
            padmask = (yshift < y) & (y < yshift + img.shape[1]) & (xshift < x) & (x < xshift + img.shape[0])
            img = img * marginmask + symimg * padmask * (1 - marginmask)
        else:
            if ismirrorsymmetry:
                centery = self.dimg.experiment.getvalue('Center Y')
                symimg = np.fliplr(img.copy())
                yshift = -(img.shape[1] - 2 * centery)
                symimg = np.roll(symimg, int(yshift), axis=1)
                marginmask = 1 - self.dimg.experiment.mask
                x, y = np.indices(img.shape)
                padmask = (yshift < y) & (y < yshift + img.shape[1])
                img = img * marginmask + symimg * padmask * (1 - marginmask)
        mask = self.dimg.experiment.mask
        if iscake:
            img = self.dimg.cake
            mask = self.dimg.cakemask
        else:
            if isremesh:
                img = self.dimg.remesh
                mask = self.dimg.remeshmask
        if iscake or isremesh:
            if self.centerplot is not None:
                self.centerplot.clear()
        else:
            self.drawcenter()
        if ismaskshown:
            self.maskimage.setImage(np.dstack((mask, np.zeros_like(mask), np.zeros_like(mask), mask)), opacity=0.25)
        else:
            self.maskimage.clear()
        if islogintensity:
            img = np.log(img * (img > 0) + (img < 1))
        self.imageitem.setImage(img, scale=scale)
        if not iscake and not isremesh:
            self.imageitem.setRect(QtCore.QRect(0, 0, self.dimg.data.shape[0], self.dimg.data.shape[1]))
        return

    def linecut(self):
        """
        toggles the line cut
        """
        self.viewbox.removeItem(self.region)
        self.parentwindow.difftoolbar.actionVertical_Cut.setChecked(False)
        self.parentwindow.difftoolbar.actionHorizontal_Cut.setChecked(False)
        if self.parentwindow.difftoolbar.actionLine_Cut.isChecked():
            self.region = pg.LineSegmentROI([
             [
              self.dimg.experiment.getvalue('Center X'), self.dimg.experiment.getvalue('Center Y')],
             [
              self.dimg.experiment.getvalue('Center X'), self.dimg.data.shape[0]]])
            self.viewbox.addItem(self.region)
            self.replot()
            self.region.sigRegionChanged.connect(self.replot)
        else:
            self.region = None
            self.replot()
        return

    def verticalcut(self):
        self.viewbox.removeItem(self.region)
        self.parentwindow.difftoolbar.actionLine_Cut.setChecked(False)
        self.parentwindow.difftoolbar.actionHorizontal_Cut.setChecked(False)
        if self.parentwindow.difftoolbar.actionVertical_Cut.isChecked():
            try:
                self.viewbox.removeItem(self.region)
            except AttributeError:
                print 'Attribute error in verticalcut'

            self.region = pg.LinearRegionItem(orientation=pg.LinearRegionItem.Vertical, brush=pg.mkBrush('#00FFFF32'), bounds=[
             0, self.dimg.data.shape[1]], values=[
             self.dimg.experiment.getvalue('Center X') - 10,
             10 + self.dimg.experiment.getvalue('Center X')])
            for line in self.region.lines:
                line.setPen(pg.mkPen('#00FFFF'))

            self.region.sigRegionChangeFinished.connect(self.replot)
            self.viewbox.addItem(self.region)
        else:
            self.region = None
        self.replot()
        return

    def horizontalcut(self):
        self.parentwindow.difftoolbar.actionVertical_Cut.setChecked(False)
        self.parentwindow.difftoolbar.actionLine_Cut.setChecked(False)
        self.viewbox.removeItem(self.region)
        if self.parentwindow.difftoolbar.actionHorizontal_Cut.isChecked():
            try:
                self.viewbox.removeItem(self.region)
            except AttributeError:
                print 'Attribute error in horizontalcut'

            self.region = pg.LinearRegionItem(orientation=pg.LinearRegionItem.Horizontal, brush=pg.mkBrush('#00FFFF32'), bounds=[
             0, self.dimg.data.shape[0]], values=[
             self.dimg.experiment.getvalue('Center Y') - 10,
             10 + self.dimg.experiment.getvalue('Center Y')])
            for line in self.region.lines:
                line.setPen(pg.mkPen('#00FFFF'))

            self.region.sigRegionChangeFinished.connect(self.replot)
            self.viewbox.addItem(self.region)
        else:
            self.region = None
        self.replot()
        return

    def removecosmics(self):
        c = pipeline.cosmics.cosmicsimage(self.dimg.data)
        c.run(maxiter=4)
        self.dimg.experiment.addtomask(c.mask)

    @debug.timeit
    def findcenter(self):
        self.dimg.findcenter()
        self.drawcenter()
        self.replot()

    def drawcenter(self):
        if self.centerplot is not None:
            self.centerplot.clear()
        self.centerplot = pg.ScatterPlotItem([self.dimg.experiment.getvalue('Center X')], [
         self.dimg.experiment.getvalue('Center Y')], pen=None, symbol='o', brush=pg.mkBrush('#FFA500'))
        self.viewbox.addItem(self.centerplot)
        return

    def calibrate(self):
        self.dimg.experiment.iscalibrated = False
        _ = self.dimg.detector
        self.findcenter()
        radialprofile = pipeline.integration.pixel_2Dintegrate(self.dimg)
        peaks = np.array(pipeline.peakfinding.findpeaks(np.arange(len(radialprofile)), radialprofile)).T
        peaks = peaks[peaks[:, 1].argsort()[::-1]]
        for peak in peaks:
            if peak[0] > 25 and not np.isinf(peak[1]):
                bestpeak = peak[0]
                break

        tth = 2 * np.arcsin(0.5 * self.dimg.experiment.getvalue('Wavelength') / 5.8367e-09)
        tantth = np.tan(tth)
        sdd = bestpeak * self.dimg.experiment.getvalue('Pixel Size X') / tantth
        print 'Best AgB peak gives sdd: ' + str(sdd)
        self.dimg.experiment.setvalue('Detector Distance', sdd)
        self.refinecenter()
        self.dimg.experiment.iscalibrated = True
        self.replot()

    @debug.timeit
    def refinecenter(self):
        cen = pipeline.center_approx.refinecenter(self.dimg)
        self.dimg.experiment.setcenter(cen)
        self.drawcenter()

    def replot(self):
        self.parentwindow.integration.clear()
        self.replotprimary()
        self.parentwindow.qLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#FFA500'))
        self.parentwindow.qLine.setVisible(False)
        self.parentwindow.integration.addItem(self.parentwindow.qLine)

    def replotprimary(self):
        if not self.dimg.experiment.iscalibrated:
            return
        cut = None
        if self.parentwindow.difftoolbar.actionMultiPlot.isChecked():
            for tabtracker in self.parentwindow.ui.findChildren(imageTabTracker):
                if self.parentwindow.ui.findChild(QtGui.QTabWidget, 'tabWidget').currentWidget() is not tabtracker:
                    tabtracker.replotassecondary()

        if self.parentwindow.difftoolbar.actionLine_Cut.isChecked():
            iscake = self.parentwindow.difftoolbar.actionCake.isChecked()
            isremesh = self.parentwindow.difftoolbar.actionRemeshing.isChecked()
            if iscake:
                data = self.dimg.cake
            else:
                if isremesh:
                    data = self.dimg.remesh
                else:
                    data = self.dimg.data
            cut = self.region.getArrayRegion(data, self.imageitem)
            x = np.linspace(self.viewbox.mapSceneToView(self.region.getSceneHandlePositions(0)[1]).x(), self.viewbox.mapSceneToView(self.region.getSceneHandlePositions(1)[1]).x(), cut.__len__())
            y = np.linspace(self.viewbox.mapSceneToView(self.region.getSceneHandlePositions(0)[1]).y(), self.viewbox.mapSceneToView(self.region.getSceneHandlePositions(1)[1]).y(), cut.__len__())
            q = pixel2q(x, y, self.dimg.experiment)
            qmiddle = q.argmin()
            leftq = -q[0:qmiddle]
            rightq = q[qmiddle:]
            if leftq.__len__() > 1:
                self.parentwindow.integration.plot(leftq, cut[:qmiddle])
            if rightq.__len__() > 1:
                self.parentwindow.integration.plot(rightq, cut[qmiddle:])
        else:
            if self.parentwindow.difftoolbar.actionHorizontal_Cut.isChecked():
                regionbounds = self.region.getRegion()
                cut = np.zeros_like(self.dimg.data)
                cut[:, regionbounds[0]:regionbounds[1]] = 1
            if self.parentwindow.difftoolbar.actionVertical_Cut.isChecked():
                regionbounds = self.region.getRegion()
                cut = np.zeros_like(self.dimg.data)
                cut[regionbounds[0]:regionbounds[1], :] = 1
            self.q, self.radialprofile = pipeline.integration.radialintegrate(self.dimg, cut=cut)
            self.cache1Dintegration.emit(self.q, self.radialprofile)
            self.peaktooltip = pipeline.peakfinding.peaktooltip(self.q, self.radialprofile, self.parentwindow.integration)
            self.parentwindow.integration.plot(self.q, self.radialprofile)
        return

    def polymask(self):
        if self.activeaction is None:
            self.activeaction = 'polymask'
            left = self.dimg.experiment.getvalue('Center X') - 100
            right = self.dimg.experiment.getvalue('Center X') + 100
            up = self.dimg.experiment.getvalue('Center Y') - 100
            down = self.dimg.experiment.getvalue('Center Y') + 100
            self.maskROI = pg.PolyLineROI([[left, up], [left, down], [right, down], [right, up]], pen=(6,
                                                                                                       9), closed=True)
            self.viewbox.addItem(self.maskROI)

            def checkPointMove(handle, pos, modifiers):
                p = self.viewbox.mapToView(pos)
                if 0 < p.y() < self.dimg.data.shape[0] and 0 < p.x() < self.dimg.data.shape[1]:
                    return True
                return False

            self.maskROI.checkPointMove = checkPointMove
        else:
            if self.activeaction == 'polymask':
                self.activeaction = None
                maskedarea = self.maskROI.getArrayRegion(np.ones_like(self.dimg.data.T), self.imageitem, returnMappedCoords=True)
                boundrect = self.viewbox.itemBoundingRect(self.maskROI)
                leftpad = boundrect.x()
                toppad = boundrect.y()
                maskedarea = np.pad(maskedarea, ((int(leftpad), 0), (int(toppad), 0)), mode='constant')
                maskedarea = np.pad(maskedarea, (
                 (
                  0, self.dimg.data.shape[0] - maskedarea.shape[0]), (0, self.dimg.data.shape[1] - maskedarea.shape[1])), mode='constant')
                self.dimg.experiment.addtomask(maskedarea)
                self.viewbox.removeItem(self.maskROI)
                self.replot()
        return

    def maskoverlay(self):
        self.maskimage.setImage(np.dstack((
         self.dimg.experiment.mask.T, np.zeros_like(self.dimg.experiment.mask).T,
         np.zeros_like(self.dimg.experiment.mask).T,
         self.dimg.experiment.mask.T)), opacity=0.25)

    def exportimage(self):
        fabimg = edfimage.edfimage(np.rot90(self.imageitem.image))
        dialog = QtGui.QFileDialog(parent=self.parentwindow.ui, caption='blah', directory=os.path.dirname(self.path), filter=u'EDF (*.edf)')
        dialog.selectFile(os.path.basename(self.path))
        filename, _ = dialog.getSaveFileName()
        fabimg.write(filename)


class previewwidget(pg.GraphicsLayoutWidget):
    """
    top-left preview
    """

    def __init__(self, model):
        super(previewwidget, self).__init__()
        self.model = model
        self.view = self.addViewBox(lockAspect=True)
        self.imageitem = pg.ImageItem()
        self.view.addItem(self.imageitem)
        self.imgdata = None
        return

    def loaditem(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.imgdata = pipeline.loader.loadimage(path)
            self.imageitem.setImage(np.rot90(np.log(self.imgdata * (self.imgdata > 0) + (self.imgdata < 1)), 3), autoLevels=True)


def pixel2cake(x, y, dimg):
    cakeqx = dimg.cakeqx
    cakeqy = dimg.cakeqy
    return np.sqrt(cakeqx[x] ** 2 + cakeqy[y] ** 2)


def pixel2q(x, y, experiment):
    if x is None:
        x = experiment.getvalue('Center X')
    if y is None:
        y = experiment.getvalue('Center Y')
    r = np.sqrt((x - experiment.getvalue('Center X')) ** 2 + (y - experiment.getvalue('Center Y')) ** 2)
    theta = np.arctan2(r * experiment.getvalue('Pixel Size X'), experiment.getvalue('Detector Distance'))
    wavelength = experiment.getvalue('Wavelength')
    return 4 * np.pi / wavelength * np.sin(theta / 2) * 1e-10
# okay decompiling viewer.pyc
