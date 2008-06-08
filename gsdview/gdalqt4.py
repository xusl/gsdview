### Copyright (C) 2008 Antonio Valentino <a_valentino@users.sf.net>

### This file is part of GSDView.

### GSDView is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; either version 2 of the License, or
### (at your option) any later version.

### GSDView is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.

### You should have received a copy of the GNU General Public License
### along with GSDView; if not, write to the Free Software
### Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.

'''Helper tools and custom components for binding GDAL and PyQt4.'''

__author__  = 'Antonio Valentino <a_valentino@users.sf.net>'
__date__    = '$Date$'
__revision__ = '$Revision$'


import logging

import numpy

try:
    from osgeo import gdal
    from osgeo.gdal_array import GDALTypeCodeToNumericTypeCode
except ImportError:
    import gdal
    from gdalsupport import GDALTypeCodeToNumericTypeCode

from PyQt4 import QtCore, QtGui
from PyQt4 import Qwt5 as Qwt

import gdalsupport
import gsdtools


# @TODO: move GraphicsView here
# @TODO: treeview showing GDAL datasets/bands attributes and metadata (read only)

class GdalGraphicsItem(QtGui.QGraphicsItem):
    # @TODO:
    #   * child class that uses the quicklook image as a low resolution cache
    #     to speedup scrolling
    def __init__(self, band, parent=None, scene=None):
        QtGui.QGraphicsItem.__init__(self, parent, scene)
        self.band = band
        #~ self._boundingRect = QtCore.QRectF(-self.band.XSize/2.,
                                           #~ -self.band.YSize/2.,
                                           #~ self.band.XSize,
                                           #~ self.band.YSize)
        # @TODO: check (work like QPixmap)
        self._boundingRect = QtCore.QRectF(0, 0,
                                           self.band.XSize,
                                           self.band.YSize)

        self._lut = self.compute_default_LUT()

        #~ if band.DataType in (gdal.GDT_CInt16, gdal.GDT_CInt32):
            #~ logging.warning('complex integer dataset')

        dtype = GDALTypeCodeToNumericTypeCode(band.DataType)
        if isinstance(dtype, basestring):
            dtype = numpy.typeDict[dtype]
        if numpy.iscomplexobj(dtype()):
            logging.warning('extract module from complex data')

    def compute_default_LUT(self):
        # @TOOD: fix flags (approx, force)
        #min_, max_, mean, stddev = self.band.GetStatistics(False, True)
        min_, max_, mean, stddev = self.band.GetStatistics(True, True)

        #~ lower = 0
        #~ upper = round(max_)

        #N = 3
        N = 1
        lower = round(max(mean - N * stddev, 0))
        upper = round(min(mean + N * stddev, max_))

        return gsdtools.compute_lin_LUT(min_, max_, lower, upper)

    def boundingRect(self):
        return self._boundingRect

    # @overrideCursor
    def paint(self, painter, option, widget):
        '''options.levelOfDetail:
        This simple metric provides an easy way to determine the level of
        detail for an item. Its value represents the maximum value of the
        height and width of a unity rectangle, mapped using the complete
        transformation matrix of the painter used to draw the item.
        By default, if no transformations are applied, its value is 1.
        If zoomed out 1:2, the level of detail will be 0.5, and if zoomed
        in 2:1, its value is 2.

        '''

        rect = option.exposedRect.toAlignedRect()

        x = int(numpy.floor(rect.x() - self._boundingRect.x()))
        y = int(numpy.floor(rect.y() - self._boundingRect.y()))
        width = rect.width() + 1        # @TODO: check
        height = rect.height() + 1      # @TODO: check

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + width > self._boundingRect.width():
            width = int(self._boundingRect.width()) - x
        if y + height > self._boundingRect.height():
            height = int(self._boundingRect.height()) - y

        data = self.band.ReadAsArray(x, y, width, height)

        if numpy.iscomplexobj(data):
            data = numpy.abs(data)
        try:
            data = gsdtools.apply_LUT(data, self._lut)
        except IndexError:
            # Is use the gdal approx stats evaluation it is possible thet the
            # image maximum is under-estimated. Fix the LUT.
            new_max = int(numpy.ceil(data.max()))
            assert new_max >= len(self._lut)
            new_lut = numpy.ndarray(new_max+1, dtype=numpy.uint8)
            new_lut[:len(self._lut)] = self._lut
            new_lut[len(self._lut)] = 255
            self._lut = new_lut
            data = gsdtools.apply_LUT(data, self._lut)

        image = Qwt.toQImage(data.transpose())
        # @TODO: SIP v4.7.5
        #image = QtGui.QImage(data.data, height, width, QtGui.QImage.Format_Indexed8)

        painter.drawImage(rect.x(), rect.y(), image)
        #drawPixmap(self, QRectF targetRect, QPixmap pixmap, QRectF sourceRect)
        #drawPixmap(self, QRect targetRect, QPixmap pixmap, QRect sourceRect)
        #drawPixmap(self, QPointF p, QPixmap pm)
        #drawPixmap(self, QPoint p, QPixmap pm)
        #drawPixmap(self, QRect r, QPixmap pm)
        #drawPixmap(self, int x, int y, QPixmap pm)
        #drawPixmap(self, int x, int y, int w, int h, QPixmap pm)
        #drawPixmap(self, int x, int y, int w, int h, QPixmap pm, int sx, int sy, int sw, int sh)
        #drawPixmap(self, int x, int y, QPixmap pm, int sx, int sy, int sw, int sh)
        #drawPixmap(self, QPointF p, QPixmap pm, QRectF sr)
        #drawPixmap(self, QPoint p, QPixmap pm, QRect sr)
        #painter->drawTiledPixmap()


#class GdalDatasetBrowser(object):
#    pass