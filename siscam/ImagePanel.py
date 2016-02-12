#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Display images.

This module contains several custom wxWidgets for displaying images.
@group Bitmap displays: BitmapDisplay BitmapDisplayOverlay
@group Image displays: ImageDisplay ImageDisplayWithMarkers ImageDisplayWithMarkersOverlayed
@group Camera image displays: CamImageDisplay
@group Camera image panels (with toolbar, ...): ImagePanel CamImagePanel CamImageMarkersPanel
@group Some Camera image panel prototypes with different contrast settings: CamAbsImagePanel CamRawSisImagePanel CamRawFoxImagePanel

"""

import wx
from wx.lib.scrolledpanel import ScrolledPanel

import numpy
import pylab
import readsis
import roi

from ImageTree import TreeModel, ImageTreePanel
import settings
import os.path

from observer import Subject, changes_state
import imagefile

from time import clock as time

def Nmin(a,b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a,b)

def Nmax(a,b):
    if a is None:
        return b
    if b is None:
        return a
    return max(a,b)

class MyScrolledPanel(ScrolledPanel):
    """Avoid scrolling when Image Panel gets focus."""
    def OnChildFocus(self, evt):
        pass

class BitmapDisplay(wx.PyControl):
    """Display static bitmap."""

    def __init__(self, parent, bitmap = None, size = wx.DefaultSize):
        wx.PyControl.__init__(self, parent, -1, size = size, style = wx.BORDER_NONE)
        self.EmptyBitmap = wx.BitmapFromBufferRGBA(1,1, '\x00\x00\x00\x00')
        if bitmap is not None:
            self.bitmap = bitmap
        else:
            self.bitmap = self.EmptyBitmap
        self.InheritAttributes()
        self.SetInitialSize(size)
        
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CHAR, self.OnKey)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouse)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouse)
        self.Bind(wx.EVT_MOTION, self.OnMouse)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouse)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

    def DoGetBestSize(self):
        return wx.Size( self.bitmap.Width + 4, self.bitmap.Height + 4)

    def AcceptsFocus(self):
        return True
    
    def SetBitmap(self, bitmap):
        self.bitmap = bitmap
        self.SetInitialSize( (bitmap.Width + 4, bitmap.Height + 4) )
        self.Refresh()

    def OnEraseBackground(self, event):
        pass

    def OnPaint(self, event):
        #dc = wx.PaintDC(self)
        dc = wx.BufferedPaintDC(self, style = wx.BUFFER_VIRTUAL_AREA)
        self.do_paint(dc)
        del dc

    def do_paint(self, dc):
        source = wx.MemoryDC()
        source.SelectObject(self.bitmap)
        r = wx.RegionIterator(self.UpdateRegion)
        while r.HaveRects():
            dc.Blit( r.X, r.Y, r.W, r.H, source, r.X, r.Y)
            r.Next()
        source.SelectObject(wx.NullBitmap)

    def OnKey(self, event):
        event.ResumePropagation(-1)
        event.Skip()

    def OnMouse(self, mouse):
        if mouse.LeftDown():
            self.active = True
            self.CaptureMouse()

        elif mouse.LeftUp():
            self.active = False
            if self.HasCapture(): self.ReleaseMouse()
        mouse.ResumePropagation(-1)
        mouse.Skip()

class BitmapDisplayOverlay(BitmapDisplay):
    """Display static bitmap with support for overlays (markers, ...) drawn on it. """

    def __init__(self, *args, **kwargs):
        super(BitmapDisplayOverlay, self).__init__(*args, **kwargs)
        self.paint_hooks = set([])

    def add_paint_hook(self, hook):
        self.paint_hooks.add(hook)

    def remove_paint_hook(self, hook):
        self.paint_hooks.discard(hook)
        
    def do_paint(self, dc):
        #BitmapDisplay.do_paint(self, dc)
        super(BitmapDisplayOverlay, self).do_paint(dc)
        for paint_hook in self.paint_hooks:
            paint_hook(dc)
            

class ImageDisplay(wx.PyControl):
    """Displays image (with scaling).  Uses L{BitmapDisplayOverlay}."""

    def __init__(self, parent, image = None, scale = 1):
        wx.PyControl.__init__(self, parent, -1)
        self.do_init(image, scale)

    def do_init(self, image, scale = 1):
        self.EmptyBitmap = wx.BitmapFromBufferRGBA(1,1, '\x00\x00\x00\x00')
        self.EmptyImage = wx.ImageFromBitmap(self.EmptyBitmap)
        self._scale = None
        if image is None:
            self._image = self.EmptyImage
        else:
            self._image = image
        self.image_scaled = self.EmptyImage
        self._bitmap = self.EmptyBitmap
        self.imgview = BitmapDisplayOverlay(self)
        self.set_scale(scale)
        
    def AcceptsFocus(self):
        return False

    def DoGetBestSize(self):
        return self.imgview.DoGetBestSize()

    def set_image(self, image, scale = None):
        """set image to display. Apply current scaling to
        image. Optionally change scale."""
        self._image = image
        if scale is not None:
            self.set_scale(scale)
        else:
            self.do_scale()
            self.draw()

    def do_scale(self):
        scale = self._scale
        if self._image.Ok():
            if scale < 1:
                quality = wx.IMAGE_QUALITY_HIGH
            else:
                quality = wx.IMAGE_QUALITY_NORMAL
                
            self.image_scaled = self._image.Scale(self._image.Width * scale,
                                                  self._image.Height * scale,
                                                  quality)
            
    def set_scale(self, scale):
        """set scale factor, scale image, display scaled image."""
        if self._scale == scale:
            return
        
        self._scale = scale
        self.do_scale()
        self.draw()

    def get_scale(self):
        return self._scale

    scale = property(get_scale, set_scale)

    def draw(self):
        if self.image_scaled.Ok():
            self._bitmap = wx.BitmapFromImage(self.image_scaled)
            self.imgview.SetBitmap(self._bitmap)


    

class Marker(Subject):
    """Base class for markers. Derived from L{Subject} to support observer
    pattern, i.e., notify observers if marker has changed."""
    
    def __init__(self, linecolor = wx.Colour(255,255,255,128), linestyle = wx.SOLID):
        self._linecolor = linecolor
        self._linestyle = linestyle

    def get_linecolor(self):
        """color of marker."""
        return self._linecolor

    @changes_state
    def set_linecolor(self, color):
        self._linecolor = linecolor

    linecolor = property(get_linecolor, set_linecolor)

    def get_linestyle(self):
        """linestyle of marker"""
        return self._linestyle

    @changes_state
    def set_linestyle(self, linestyle):
        self._linestyle = linestyle

    linestyle = property(get_linestyle, set_linestyle)

    def mouseover(self,x,y,radius):
        pass
    def change(self,x,y,change):
        pass
    def cleanup(self):
        pass
    def get_info(self):
        pass
        
class Point(Subject):
    def __init__(self, x, y):
        self._x = x
        self._y = y

        self._xold = x
        self._yold = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def get_xy(self):
        return (self._x, self._y)

    @changes_state
    def set_xy(self, xy):
        self._xold, self._yold = self.xy
        self._x, self._y = xy

    xy = property(get_xy, set_xy)

    def is_hit(self,x,y,r):
        return (x-self.x)**2 + (y-self.y)**2 < r**2

class CrossMarker(Marker):
    cursordict = {0: wx.CURSOR_CROSS}

    def __init__(self, x,y, linecolor = wx.WHITE, linestyle = wx.SOLID):
        super(CrossMarker, self).__init__(linecolor, linestyle)
        self.point = Point(x,y)
        self.point.add_observer(self)

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.point.add_observer(self)

    @changes_state
    def update(self, subject):
        pass
        
    def mouseover(self, x,y,radius):
        if self.point.is_hit(x,y,radius):
            return (True, 0)
        else:
            return (False, 0)

    #@changes_state #note point member marked as changes_state, calls
    #update, which is tagged changes_state, ...
    def change(self, x,y,kind):
        self.point.xy = (x,y)

    def draw(self, dc, scale, size):

        #dc = wx.GCDC(dc)
        pen = wx.Pen(colour = self.linecolor,
                     width = max(1, scale))
        pen.Style = self.linestyle
        dc.Pen = pen

        sx, sy = size

        x = int((self.point.x+0.5)*scale)
        y = int((self.point.y+0.5)*scale)

        x = min(x, sx-1)
        y = min(y, sy-1)

        dc.DrawLine(x, 0, x, sy)
        dc.DrawLine(0, y, sx, y)


    def get_invalidate_regions(self, scale, size):

        sx, sy = size
        r = []
        
        wh = int(round(max(1, scale))/2)
        w  = 2*wh + 1

        if self.point._xold != self.point.x:
            x    = min(sx-1, int((self.point.x+0.5)    *scale))
            oldx = min(sx-1, int((self.point._xold+0.5)*scale))

            r.append(wx.Rect(x-wh,   0,  w, sy))
            r.append(wx.Rect(oldx-wh,0,  w, sy))

        if self.point._yold != self.point.y:
            y    = min(sy-1, int((self.point.y+0.5)    *scale))
            oldy = min(sy-1, int((self.point._yold+0.5)*scale))

            r.append(wx.Rect(0, oldy-wh, sx, w))
            r.append(wx.Rect(0, y-wh,    sx, w))

        return r

    def get_info(self):
        return "(%4d, %4d)"%(self.point.x, self.point.y)
            
class RectMarker(Marker):

    cursordict =  {'left'       : wx.CURSOR_SIZEWE,
                   'right'      : wx.CURSOR_SIZEWE,
                   'top'        : wx.CURSOR_SIZENS,
                   'bottom'     : wx.CURSOR_SIZENS,
                   'topleft'    : wx.CURSOR_SIZENWSE,
                   'bottomright': wx.CURSOR_SIZENWSE,
                   'topright'   : wx.CURSOR_SIZENESW,
                   'bottomleft' : wx.CURSOR_SIZENESW,
                   }

    def __init__(self, x1,y1, x2,y2, linecolor = wx.WHITE, linestyle = wx.SOLID):
        super(RectMarker, self).__init__(linecolor, linestyle)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = x2
        self.r = []

    def mouseover(self, x, y, radius):
        x1,x2 = min(self.x1,self.x2), max(self.x1,self.x2)
        y1,y2 = min(self.y1,self.y2), max(self.y1,self.y2)
        
        kind = ''
        if (x-x1)**2 + (y-y1)**2 < radius**2:
            kind = 'topleft'
        elif (x-x2)**2 + (y-y2)**2 < radius**2:
            kind = 'bottomright'
        elif (x-x1)**2 + (y-y2)**2 < radius**2:
            kind = 'bottomleft'
        elif (x-x2)**2 + (y-y1)**2 < radius**2:
            kind = 'topright'
        elif abs(y-y1) < radius and x1<x<x2:
            kind = 'top'
        elif abs(y-y2) < radius and x1<x<x2:
            kind = 'bottom'
        elif abs(x-x1) < radius and y1<y<y2:
            kind = 'left'
        elif abs(x-x2) < radius and y1<y<y2:
            kind = 'right'

        if kind:
            return (True, kind)
        else:
            return (False, kind)

    @changes_state
    def change(self, x,y,kind):
        self.r = []
        l,r,b,t = None, None, None, None
        
        if kind == 'topleft': #top left
            l, t = x, y
        elif kind == 'bottomright': #bottom right
            r, b = x, y
        elif kind == 'bottomleft':
            l, b = x, y
        elif kind == 'topright':
            r, t = x, y
        elif kind == 'top':
            t = y
        elif kind == 'bottom':
            b = y
        elif kind == 'left':
            l = x
        elif kind == 'right':
            r = x

        lo, ro, to, bo = self.x1, self.x2, self.y1, self.y2

        if l is not None:
            self.x1 = l
            self.inval([lo, Nmin(t,to), lo, Nmax(b,bo)])
            self.inval([l,  Nmin(t,to), l,  Nmax(b,bo)])
            self.inval([Nmin(l,lo), to, Nmax(l,lo), to])
            self.inval([Nmin(l,lo), bo, Nmax(l,lo), bo])
        if r is not None:
            self.x2 = r
            self.inval([ro, Nmin(t,to), ro, Nmax(b,bo)])
            self.inval([r,  Nmin(t,to), r,  Nmax(b,bo)])
            self.inval([Nmin(r,ro), to, Nmax(r,ro), to])
            self.inval([Nmin(r,ro), bo, Nmax(r,ro), bo])

        if t is not None:
            self.y1 = t
            self.inval([Nmin(l,lo), to, Nmax(r,ro), to])
            self.inval([Nmin(l,lo), t,  Nmax(r,ro), t ])
            self.inval([lo, Nmin(t,to), lo, Nmax(t,to)])
            self.inval([ro, Nmin(t,to), ro, Nmax(t,to)])
        if b is not None:
            self.y2 = b
            self.inval([Nmin(l,lo), bo, Nmax(r,ro), bo])
            self.inval([Nmin(l,lo), b,  Nmax(r,ro), b ])
            self.inval([lo, Nmin(b,bo), lo, Nmax(b,bo)])
            self.inval([ro, Nmin(b,bo), ro, Nmax(b,bo)])


    def draw(self, dc, scale, size):
        #dc = wx.GCDC(dc)
        pen = wx.Pen(colour = self.linecolor,
                     width = max(1, scale))
        pen.Cap = wx.CAP_PROJECTING
        pen.Style = self.linestyle
        dc.Pen = pen
        dc.Brush = wx.TRANSPARENT_BRUSH

        l = int((self.x1+0.5)*scale)
        t = int((self.y1+0.5)*scale)
        r = int((self.x2+0.5)*scale)
        b = int((self.y2+0.5)*scale)

        dc.DrawLine(l, t, r, t)
        dc.DrawLine(r, t, r, b)
        dc.DrawLine(r, b, l, b)
        dc.DrawLine(l, b, l, t)

    def inval(self, r):
        self.r.append(r)

    def get_invalidate_regions(self, scale, size):
        sx,sy = size

        w = int(round(max(1, scale))/2)
        rects = []

        for rect in self.r:
            
            l = int((rect[0]+0.5)*scale)
            t = int((rect[1]+0.5)*scale)
            r = int((rect[2]+0.5)*scale)
            b = int((rect[3]+0.5)*scale)

            rects.append(wx.Rect( l-w, t-w, r-l+2*w+1, b-t+2*w+1))

        #self.r = []
        return rects
        
    def cleanup(self):
        self.x1,self.x2 = min(self.x1,self.x2), max(self.x1,self.x2)
        self.y1,self.y2 = min(self.y1,self.y2), max(self.y1,self.y2)

    def get_info(self):
        return "(%d, %d, %d, %d)"%(self.x1, self.y1, self.x2, self.y2)

    @property
    def roi(self):
        self.cleanup()
        return roi.ROI(self.x1, self.x2, self.y1, self.y2)

class ImageDisplayWithMarkers(ImageDisplay):
    """(Obsolete) Image display with markers overlayed."""


class ImageDisplayWithMarkersOverlayed(ImageDisplay):
    """Image display with markers overlayed. Just implements
    draw_markers and registered them as paint_hook of
    L{BitmapDisplayOverlay}.
    """
    
    def __init__(self, parent, image = None, scale = 1):
        ImageDisplay.__init__(self, parent, image, scale)

        self._markers = set([])
        self.imgview.add_paint_hook(self.draw_markers)
        
    def update(self, marker):
        """This method gets called if any marker has changed. Updates
        marker on screen. For this, just invalidate regions containing
        old and new marker. Repainting will repair region hidden by
        marker before and draw markers in new position (this is done
        by the paint_hook). This is more efficient than refreshing all
        the window or even recreating the whole bitmap and drawing the
        markers.
        """
        size = (self._bitmap.Width, self._bitmap.Height)
        regions = marker.get_invalidate_regions(self._scale, size)
        for rect in regions:
            self.RefreshRect(rect)
                
    def draw_markers(self, dc):
        """Draw cross shaped marker on top of (scaled) bitmap. Gets
        called in OnPaint handler of L{BitmapDisplayOverlay}"""
        
        for marker in self._markers:
            marker.draw(dc, self._scale, (self._bitmap.Width, self._bitmap.Height))
            
    def add_marker(self, marker):
        self._markers.add(marker)
        marker.add_observer(self)

    def remove_marker(self, marker):
        self._markers.discard(marker)
        marker.remove_observer(self)


class CamImageDisplay(ImageDisplayWithMarkersOverlayed):
    """Displays Camera Image. Provides application of colormap, color
    scaling. (Image size scaling inherited.)
    """
    def __init__(self, parent, camimage = None,
                 scale = 1,
                 colormap = pylab.cm.jet,
                 vmin = -0.1,
                 vmax = 1.5):
        
        super(CamImageDisplay, self).__init__(parent)
        self._colormap = colormap
        self.vmin = vmin
        self.vmax = vmax 
        self.set_camimage(camimage)
        self.set_scale(scale)
        #self.do_scale()
        #self.draw()

    def set_camimage(self, camimg, scale = None):
        """sets camimage. Convert camimage to wxImage by applying colormap"""
        self._camimg = camimg
        if camimg is None:
            return
        self.render()

    set_image = set_camimage

    def get_camimage(self):
        """return original camera image"""
        return self._camimg

    def set_colormap(self, colormap):
        self._colormap = colormap
        self.render()

    def set_clim(self, vmin = None, vmax = None):
        if vmax is not None:
            self.vmax = vmax

        if vmin is not None:
            self.vmin = vmin

        self.render()
    
    def render(self):
        camimg = self._camimg
        if camimg is None:
            return

        #tic = time()
        #color scaling
        scale = (255.0/(self.vmax - self.vmin))
        ci = numpy.empty_like(camimg)
        numpy.subtract(camimg, self.vmin, ci)
        #ci = (camimg - self.vmin)
        numpy.multiply(ci, scale, ci)
        #print "render scale: ", time()-tic #180ms

        #tic = time()
        #convert to color image, apply colormap
        ci.clip(0, 255, ci)
        #print "render clip:", time()-tic #40ms

        #tic = time()
        ci = ci.astype(numpy.uint8)
        #print "render convert to uint8:", time()-tic #15ms

        #tic = time()
        lut = self._colormap(numpy.arange(256), bytes = True)
        lut = lut[:, :-1]
        imgrgb = lut.take(ci, axis = 0)
        #print "apply colormap: ", time()-tic #21ms

        #tic = time()
        wximg = wx.ImageFromBuffer(imgrgb.shape[1],
                                   imgrgb.shape[0],
                                   imgrgb.data)
        self._image = wximg
        #print "convert to wximg", time()-tic #0ms
        
        #tic = time()
        self.do_scale()
        #print "scale: ", time()-tic
        self.draw()

    def get_value(self, x, y):
        try:
            return self._camimg[y, x]
        except IndexError:
            return 0

class ImagePanel(wx.Panel):
    """Base class for image panel with Toolbar, status bar, and
    L{ImageDisplay} (support scaling), handles mouse interaction
    (panning)."""

    zoomlevels = [4,
                  3,
                  2,
                  1,
                  2/3.0,
                  0.5,
                  1/3.0,
                  0.25,
                  0.125,
                  0.0625]

    def __init__(self, parent, image = None, scale = 1):
        wx.Panel.__init__(self, parent, -1)

        #init member variables
        self._zoom = 3
        self._mpos = None

        ##create controls 
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #toolbar
        self.toolbar = self.create_toolbar(parent = self)
        self.toolbar.Realize()
        self.sizer.Add(self.toolbar, 0, wx.EXPAND | wx.FIXED_MINSIZE)

        #scrolled image view
        self.scrolledpanel = MyScrolledPanel(self, -1, style = wx.BORDER_NONE)
        self.imgview = self.create_imageview(parent = self.scrolledpanel,
                                             image = image,
                                             scale = scale)
        imagesizerbox = wx.BoxSizer(wx.VERTICAL)
        imagesizerbox.Add((0,0), 1)
        imagesizerbox.Add(self.imgview, 0, wx.ALIGN_CENTER)
        imagesizerbox.Add((0,0), 1)
        self.scrolledpanel.SetSizer(imagesizerbox)
        self.scrolledpanel.SetAutoLayout(1)
        self.scrolledpanel.SetupScrolling(rate_x = 1,  rate_y = 1)
        self.sizer.Add(self.scrolledpanel, 1, wx.EXPAND)
        
        #status bar
        self.statusbar = wx.StatusBar(self)
        self.statusbar.FieldsCount = 3
        self.statusbar.SetStatusWidths([50, 200, -1])
        self.sizer.Add(self.statusbar, 0, wx.EXPAND)

        #finalize
        self.SetSizer(self.sizer)
        self.update_statusbar()

        #bindings
        self.Bind(wx.EVT_TOOL, self.OnTool)
        self.Bind(wx.EVT_CHAR, self.OnKey)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        #Bind all mouse events coming from BitmapDisplay
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse, self.imgview.imgview)

    def create_toolbar(self, parent):
        return ZoomToolbar(parent)

    def create_imageview(self, parent, image, scale):
        return ImageDisplay(parent, image, scale)

    @property
    def scale(self):
        return self.zoomlevels[self._zoom]

    def OnMouse(self, mouse):
        #catch mouse events propagated from subwindows
        if mouse.ShouldPropagate():
            mouse.StopPropagation()
        
        mouse.Skip() #to get focus

        if mouse.LeftDown():
            #start pan

            self._mpos = mouse.Position
            self.statusbar.SetStatusText('Pan',1)
            
        elif mouse.Dragging() and mouse.LeftIsDown() and self._mpos is not None:
            #panning
            offset = self.scrolledpanel.ViewStart
            mpos = self._mpos
            apos = mouse.Position
            self.scrolledpanel.Scroll( offset[0] - apos[0] + mpos[0],
                                       offset[1] - apos[1] + mpos[1])
        elif mouse.LeftUp():
            #stop panning
            self._mpos = None

        elif mouse.Leaving():
            self.statusbar.SetStatusText('', 1)

        else:
            #display position and value
            px = int(mouse.Position[0]/self.scale)
            py = int(mouse.Position[1]/self.scale)
            val = self.imgview.get_value(px, py)
            self.statusbar.SetStatusText("(%4d, %4d): %+6.2f"%(px, py, val), 1)

    def OnEraseBackground(self, event):
        pass

    def show_image(self, image, scale = None, description = ""):
        self.imgview.set_image(image, scale)
        self.scrolledpanel.FitInside()
        self.statusbar.SetStatusText(description, 2)
        self.update_statusbar()

    def OnTool(self, event):
        Id = event.GetId()
        if Id == self.toolbar._ZOOM_IN:
            self.zoom_in()
        if Id == self.toolbar._ZOOM_OUT:
            self.zoom_out()
        else:
            event.Skip()

    def OnKey(self, event):
        if event.KeyCode == ord('+'):
            self.zoom_in()
        elif event.KeyCode == ord('-'):
            self.zoom_out()
        else:
            event.Skip()

    def update_statusbar(self):
        self.statusbar.StatusText = "%3.0f%%"%(self.scale*100)

    def get_zoomstep(self):
        return self._zoom

    def zoom_to(self, zoomstep):
        oldscale = self.scale
        offset = self.scrolledpanel.ViewStart
        size = self.scrolledpanel.ClientSize.Get()
        oldcenter = [(offset[0] + size[0]/2.0)/oldscale,
                     (offset[1] + size[1]/2.0)/oldscale
                     ]

        self.scrolledpanel.Freeze()

        self._zoom = zoomstep
        self.imgview.scale = self.scale
        self.scrolledpanel.FitInside()

        newcenter = (oldcenter[0]*self.scale,
                     oldcenter[1]*self.scale)
        size = self.scrolledpanel.ClientSize.Get()
        self.scrolledpanel.Scroll( newcenter[0] - size[0]/2,
                                   newcenter[1] - size[1]/2)

        self.scrolledpanel.Thaw()
        self.update_statusbar()
        self.Update()
        
    def zoom_in(self):
        self.zoom_to( max(self._zoom - 1, 0) )
        
    def zoom_out(self):
        self.zoom_to( min(self._zoom + 1, len(self.zoomlevels)-1) )

    zoomstep = property(get_zoomstep, zoom_to)

class ZoomToolbar(wx.ToolBar):
    """Toolbar with + and - tools for zooming"""
    
    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, -1)
        
        self._ZOOM_IN = wx.NewId()
        self._ZOOM_OUT = wx.NewId()

        self.SetToolBitmapSize(wx.Size(24, 24))

        self.AddLabelTool(self._ZOOM_IN,
                          'zoom in',
                          wx.Bitmap(os.path.join(settings.bitmappath,
                                                 'zoomin.png'),
                                    wx.BITMAP_TYPE_PNG),
                          shortHelp = 'Zoom in',
                          longHelp = 'Zool in')

        self.AddLabelTool(self._ZOOM_OUT,
                          'zoom out',
                          wx.Bitmap(os.path.join(settings.bitmappath,
                                                 'zoomout.png'),
                                    wx.BITMAP_TYPE_PNG),
                          shortHelp = 'Zoom out',
                          longHelp = 'Zoom out')

class CamImagePanel(ImagePanel):
    """Image panel with Toolbar, status bar, and L{CamImageDisplay}
    (supports scaling, colormaps), handles mouse interaction
    (panning)."""


    contrast = [ ['low',   300],
                 ['normal', 520],
                 ['high',   1024],
                 ]

    contrast_default = 1 #default entry of table before
    
    def __init__(self, parent, camimg = None, scale = 1):
        super(CamImagePanel, self).__init__(parent, image = camimg)

        self.contrast_choice = self.contrast_default

    def create_imageview(self, parent, image, scale):
        return CamImageDisplay(parent, image, scale)

    def create_toolbar(self, parent):
        toolbar = ZoomToolbar(parent)
        toolbar.ID_COLORMAP = wx.NewId()
        toolbar.ID_CONTRAST = wx.NewId()
        
        toolbar.AddSeparator()
        toolbar.AddControl(wx.StaticText(toolbar, -1, "Contrast: "))
        colormap_contrast = wx.ComboBox(toolbar,
                                        toolbar.ID_CONTRAST,
                                        #value = self.contrast[self.contrast_default][0],
                                        size = (75,-1),
                                        choices = [c[0] for c in self.contrast],
                                        style = wx.CB_READONLY
                                        )
        toolbar.AddControl(colormap_contrast)

        toolbar.AddSeparator()
        toolbar.AddControl(wx.StaticText(toolbar, -1, "Colormap: "))
        #choices = pylab.cm.cmapnames,
        choices = ['jet', 'gray', 'bone', 'hsv', 'binary','raw']
        colormap_choice = wx.ComboBox(toolbar,
                                      toolbar.ID_COLORMAP,
                                      value = "jet",
                                      size = (75, -1),
                                      choices = choices,
                                      style = wx.CB_READONLY | wx.CB_SORT,
                                      )
        toolbar.AddControl(colormap_choice)

        self.Bind(wx.EVT_COMBOBOX, self.OnSelectColormap, colormap_choice)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectContrast, colormap_contrast)

        self._contrast_combobox = colormap_contrast
        self._colormap_combobox = colormap_choice

        return toolbar

    def OnSelectColormap(self, event):
        self.colormap_choice = event.Int

    def OnSelectContrast(self, event):
        self.contrast_choice = event.Int
        
    def set_contrast_choice(self, n):
        self._contrast_combobox.SetSelection(n)
        vmax = self.contrast[n][1]
        self.imgview.set_clim(vmax = vmax)

    def get_contrast_choice(self):
        return self._contrast_combobox.Selection

    contrast_choice = property(get_contrast_choice,
                               set_contrast_choice)

    def set_colormap_choice(self, n):
        self._colormap_combobox.Selection = n
        if self._colormap_combobox.GetString(n) != 'raw':
            cm = pylab.cm.__getattribute__(self._colormap_combobox.GetString(n))
            self.imgview.set_colormap(cm)
        self.Refresh()
        self.Update()

    def get_colormap_choice(self):
        return self._colormap_combobox.Selection

    colormap_choice = property(get_colormap_choice,
                               set_colormap_choice)

        
class CamImageMarkersPanel(CamImagePanel):
    """Image panel with Toolbar, status bar, and L{CamImageDisplay}
    (supports scaling, colormaps), implements full mouse interaction
    (panning and marker selection)."""

    def __init__(self, *args, **kwargs):
        super(CamImageMarkersPanel, self).__init__(*args, **kwargs)
        self._markers = self.imgview._markers

    #def create_imageview(self, parent, image, scale):
    #    return CamImageDisplay(parent, image, scale)

    def OnMouse(self, mouse):
        #catch mouse events propagated from subwindows
        if mouse.ShouldPropagate():
            mouse.StopPropagation()

        mouse.Skip() #to get focus

        #mouse position in unscaled units
        px = int((mouse.Position[0])/self.scale + 0.5)
        py = int((mouse.Position[1])/self.scale + 0.5)

        if mouse.LeftDown():
            if self.marker_hit is not None:
                #self.statusbar.SetStatusText('Move Marker', 1)
                #
                pass
            else: #start pan
                #self._mouse_ignore_next_drag = True
                self._mpos = mouse.Position
                self.statusbar.SetStatusText('Pan',1)
                self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
            
        elif mouse.Dragging() and mouse.LeftIsDown():
            if self._mpos is not None:
                #panning
                offset = self.scrolledpanel.ViewStart
                mpos = self._mpos
                apos = mouse.Position
                self.scrolledpanel.Scroll( offset[0] - apos[0] + mpos[0],
                                           offset[1] - apos[1] + mpos[1])
            elif self.marker_hit is not None:
                #drag marker
                px = max(0, px)
                px = min(self.imgview._image.Width-1, px)

                py = max(0, py)
                py = min(self.imgview._image.Height-1, py)

                self.marker_hit.change(px, py, self.marker_hit_kind)

                self.statusbar.SetStatusText('Marker: '+self.marker_hit.get_info(),1)

        elif mouse.LeftUp():
            #stop panning/marker dragging
            if self._mpos:
                self._mpos = None
                
            if self.marker_hit:
                self.marker_hit.cleanup()
                self.marker_hit = None
                self.marker_hit_kind = None
                self.SetCursor(wx.STANDARD_CURSOR)

        elif mouse.Leaving():
            self.statusbar.SetStatusText('', 1)
            #self.SetCursor(wx.STANDARD_CURSOR)

        else:
            #check for markers
            self.marker_hit = None
            for m in self._markers:
                (hit, kind) = m.mouseover(px, py, (3.0/min(1.0 ,self.scale)))
                if hit:
                    self.marker_hit = m
                    self.marker_hit_kind = kind

                
            if self.marker_hit is not None:
                self.SetCursor(wx.StockCursor(
                    self.marker_hit.cursordict[self.marker_hit_kind]))
            else:
                self.SetCursor(wx.STANDARD_CURSOR)

            #display position and value
            val = self.imgview.get_value(px, py)
            self.statusbar.SetStatusText("(%4d, %4d): %+6.2f"%(px, py, val), 1)


    def add_marker(self, marker):
        self.imgview.add_marker(marker)

    def remove_marker(self, marker):
        self.imgview.remove_marker(marker)

class CamAbsImagePanel(CamImageMarkersPanel):
    contrast = [ ['low',    64],
             ['normal', 128],
             ['high',   256],
             ]

class CamRawSisImagePanel(CamImageMarkersPanel):
    contrast = [
        ['low',    5000],
        ['normal', 1200],
        ['high',   500],
        ]

class CamRawFoxImagePanel(CamImageMarkersPanel):
    contrast = [
        ['standard', 255],
        ['high',     127],
        ]
    contrast_default = 0

class ImgPanelApp(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None,
                              title = "Image Panel Test Application",
                              size = (600, 400),
                              )
        filename = "img/20061115_0.sis"
        img1, img2 = loadimg(filename)

        self.panel = CamImageMarkersPanel(self.frame, camimg = img2)

        for m in [CrossMarker(300, 300, linecolor = wx.Colour(255,255,255,128)),
                  CrossMarker(400, 400, linecolor = wx.Colour(255,255,  0,128),
                              linestyle = wx.SOLID),
                  RectMarker(100, 100, 200, 200,
                             linecolor = wx.Colour(255,0,255,128),
                             linestyle = wx.SOLID),
                  ]:
            self.panel.add_marker(m)

        
        
        self.frame.Show(True)
        return True

def loadimg(file):
    """load sis image
    @param file: filename
    @rtype: (wx.Image, wx.Image)
    """
    #img1, img2 = readsis.loadimg(file)
    #return img1, img2
    return imagefile.load_image(file)

def run_showimage():
    gui = ImgPanelApp(redirect = False)

    gui.MainLoop()
    return gui
        
if __name__ == '__main__':
    gui = run_showimage()

