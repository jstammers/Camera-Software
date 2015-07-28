#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Improved implementation of NavigationToolbar for matplotlib."""

import os
import wx
from matplotlib.backend_bases import NavigationToolbar2

from matplotlib.backends.backend_wx import FigureManager, FigureCanvasWx, SubplotTool
from matplotlib.figure import Figure
from matplotlib import rcParams
from matplotlib.backends.backend_wx import cursord

def _load_bitmap(filename):
    """
    Load a bitmap file from the backends/images subdirectory in which the
    matplotlib library is installed. The filename parameter should not
    contain any path information as this is determined automatically.

    Returns a wx.Bitmap object
    """

    basedir = os.path.join(rcParams['datapath'],'images')

    bmpFilename = os.path.normpath(os.path.join(basedir, filename))
    if not os.path.exists(bmpFilename):
        raise IOError('Could not find bitmap file "%s"; dying'%bmpFilename)

    bmp =wx.Bitmap(bmpFilename, wx.BITMAP_TYPE_PNG)
    return bmp

def error_msg_wx(msg, parent=None):
    """
    Signal an error condition -- in a GUI, popup a error dialog
    """
    dialog =wx.MessageDialog(parent = parent,
                             message = msg,
                             caption = 'Matplotlib backend_wx error',
                             style=wx.OK | wx.CENTRE)
    dialog.ShowModal()
    dialog.Destroy()
    return None 

class NavigationToolbar2Wx(NavigationToolbar2, wx.ToolBar):

    def __init__(self, canvas):
        wx.ToolBar.__init__(self, canvas.GetParent(), -1)
        NavigationToolbar2.__init__(self, canvas)
        self.canvas = canvas
        self._idle = True
        self.statbar = None

    def get_canvas(self, frame, fig):
        return FigureCanvasWx(frame, -1, fig)

    def _init_toolbar(self):
        self._parent = self.canvas.GetParent()

        self._NTB2_HOME    = wx.NewId()
        self._NTB2_BACK    = wx.NewId()
        self._NTB2_FORWARD = wx.NewId()
        self._NTB2_PAN     = wx.NewId()
        self._NTB2_ZOOM    = wx.NewId()
        self._NTB2_SAVE    = wx.NewId()
        self._NTB2_SUBPLOT = wx.NewId()

        self.SetToolBitmapSize(wx.Size(24,24))

        self.AddLabelTool(self._NTB2_HOME,
                          'home',
                          _load_bitmap('home.png'),
                          shortHelp = 'Home',
                          longHelp = 'Reset original view')
        self.AddLabelTool(self._NTB2_BACK,
                          'back',
                          _load_bitmap('back.png'),
                          shortHelp = 'Back',
                          longHelp = 'Back navigation view')
        self.AddLabelTool(self._NTB2_FORWARD,
                          'forward',
                          _load_bitmap('forward.png'),
                          shortHelp = 'Forward',
                          longHelp = 'Forward navigation view')
        self.AddCheckLabelTool(self._NTB2_PAN,
                          'pan',
                          _load_bitmap('move.png'),
                          shortHelp='Pan',
                          longHelp='Pan with left, zoom with right')
        self.AddCheckLabelTool(self._NTB2_ZOOM,
                          'zoom',
                          _load_bitmap('zoom_to_rect.png'),
                          shortHelp='Zoom',
                          longHelp='Zoom to rectangle')

        self.AddSeparator()
        self.AddLabelTool(self._NTB2_SUBPLOT,
                          'configure',
                          _load_bitmap('subplots.png'),
                          shortHelp = 'Configure subplots',
                          longHelp = 'Configure subplot parameters')

        self.AddLabelTool(self._NTB2_SAVE,
                          'save',
                          _load_bitmap('filesave.png'),
                          shortHelp = 'Save',
                          longHelp = 'Save plot contents to file')
        
        wx.EVT_TOOL(self, self._NTB2_HOME, self.home)
        wx.EVT_TOOL(self, self._NTB2_FORWARD, self.forward)
        wx.EVT_TOOL(self, self._NTB2_BACK, self.back)
        wx.EVT_TOOL(self, self._NTB2_ZOOM, self.zoom)
        wx.EVT_TOOL(self, self._NTB2_PAN, self.pan)
        wx.EVT_TOOL(self, self._NTB2_SUBPLOT, self.configure_subplot)
        wx.EVT_TOOL(self, self._NTB2_SAVE, self.save)

        self.Realize()


    def zoom(self, *args):
        self.ToggleTool(self._NTB2_PAN, False)
        NavigationToolbar2.zoom(self, *args)

    def pan(self, *args):
        self.ToggleTool(self._NTB2_ZOOM, False)
        NavigationToolbar2.pan(self, *args)

    def configure_subplot(self, evt):
        frame = wx.Frame(None, -1, "Configure subplots")

        toolfig = Figure((6,3))
        canvas = self.get_canvas(frame, toolfig)

        # Create a figure manager to manage things
        figmgr = FigureManager(canvas, 1, frame)

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        frame.SetSizer(sizer)
        frame.Fit()
        tool = SubplotTool(self.canvas.figure, toolfig)
        frame.Show()

    def save(self, evt):
        # Fetch the required filename and file type.
        filetypes, exts, filter_index = self.canvas._get_imagesave_wildcards()
        default_file = "image." + self.canvas.get_default_filetype()
        dlg = wx.FileDialog(self._parent, "Save to file", "", default_file,
                            filetypes,
                            wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
        dlg.SetFilterIndex(filter_index)
        if dlg.ShowModal() == wx.ID_OK:
            dirname  = dlg.GetDirectory()
            filename = dlg.GetFilename()
            format = exts[dlg.GetFilterIndex()]
            
            #Explicitly pass in the selected filetype to override the
            # actual extension if necessary
            try:
                self.canvas.print_figure(
                    str(os.path.join(dirname, filename)), format=format)
            except Exception, e:
                error_msg_wx(str(e))
            
    def set_cursor(self, cursor):
        cursor =wx.StockCursor(cursord[cursor])
        self.canvas.SetCursor( cursor )

    def release(self, event):
        try: del self.lastrect
        except AttributeError: pass

    def dynamic_update(self):
        d = self._idle
        self._idle = False
        if d:
            self.canvas.draw()
            self._idle = True

    def draw_rubberband(self, event, x0, y0, x1, y1):
        'adapted from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/189744'
        canvas = self.canvas
        dc =wx.ClientDC(canvas)

        # Set logical function to XOR for rubberbanding
        dc.SetLogicalFunction(wx.XOR)

        # Set dc brush and pen
        # Here I set brush and pen to white and grey respectively
        # You can set it to your own choices

        # The brush setting is not really needed since we
        # dont do any filling of the dc. It is set just for
        # the sake of completion.

        wbrush =wx.Brush(wx.Colour(255,255,255), wx.TRANSPARENT)
        wpen =wx.Pen(wx.Colour(200, 200, 200), 1, wx.SOLID)
        dc.SetBrush(wbrush)
        dc.SetPen(wpen)


        dc.ResetBoundingBox()
        dc.BeginDrawing()
        height = self.canvas.figure.bbox.height()
        y1 = height - y1
        y0 = height - y0

        if y1<y0: y0, y1 = y1, y0
        if x1<y0: x0, x1 = x1, x0

        w = x1 - x0
        h = y1 - y0

        rect = int(x0), int(y0), int(w), int(h)
        try: lastrect = self.lastrect
        except AttributeError: pass
        else: dc.DrawRectangle(*lastrect)  #erase last
        self.lastrect = rect
        dc.DrawRectangle(*rect)
        dc.EndDrawing()

    def set_status_bar(self, statbar):
        self.statbar = statbar

    def set_message(self, s):
        if self.statbar is not None: self.statbar.set_function(s)

    def set_history_buttons(self):
        can_backward = (self._views._pos > 0)
        can_forward = (self._views._pos < len(self._views._elements) - 1)
        self.EnableTool(self._NTB2_BACK, can_backward)
        self.EnableTool(self._NTB2_FORWARD, can_forward)

