#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Custom Editors and Renderers for grid entries."""

import wx, wx.grid

class FloatRenderer(wx.grid.PyGridCellRenderer):
    """FloatRenderer renders float value into grid table
    entry. Similar to GridCellFloatRenderer, but shows empty entry if
    value is None or empty string"""

    def __init__(self, width = -1, precision = -1):
        """
        @param width: total number of digits
        @param precision: number of digits after comma
        """
        wx.grid.PyGridCellRenderer.__init__(self)

        self.width = width
        self.precision = precision
        
    def SetParameters(self, format):
        "@param format: format string, e.g., '4,1' for width = 4, precision = 1"
        self.width, self.precision = map(int, format.split(','))

    @property
    def format(self):
        """
        read property for dynamically created format string
        @return: format string
        """
        w,p = self.width, self.precision
        if w==-1 and p==-1:
            return '%f'

        f = '%'
        if w>-1:
            f+= "%d"%w
            
        if p>-1:
            f+= ".%d"%p

        f += 'f'
        return f
        
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        """
        Implements rendering into grid entry.
        """
        #paint background
        if isSelected:
            dc.Brush = wx.Brush(grid.SelectionBackground)
        else:
            dc.Brush = wx.Brush(attr.BackgroundColour)    
        dc.BackgroundMode = wx.SOLID
        dc.Pen = wx.TRANSPARENT_PEN
        dc.DrawRectangleRect(rect)

        #create string, applying format to value
        value = grid.Table.GetValue(row, col)
        empty = grid.Table.IsEmptyCell(row, col)
        if not empty:
            s = (self.format%float(value)).lstrip()
        else:
            s = '-'
    
        #draw text        
        dc.BackgroundMode = wx.TRANSPARENT
        dc.Font = attr.Font
        dc.TextForeground = attr.TextColour
        dc.ClippingRect = rect
        tw, th = dc.GetTextExtent(s)
        dc.DrawText(s, rect.x + rect.width - tw - 2, rect.y + 2)
        dc.DestroyClippingRegion()
        
    def GetBestSize(self, grid, attr, dc, row, col):
        """Calculate size of entry"""
        #TODO: calculate width from text or self.width
        return wx.Size(50, 10)

    def Clone(self):
        return FloatRenderer(self.width, self.precision)


class BoolRenderer(wx.grid.PyGridCellRenderer):
    """
    Custom renderer for boolean values. Use native renderer for
    checkbox.
    """

    def __init__(self):
        wx.grid.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        """
        Implements rendering into grid entry.
        """
        #paint background
        if isSelected:
            dc.Brush = wx.Brush(grid.SelectionBackground)
        else:
            dc.Brush = wx.Brush(attr.BackgroundColour)
        dc.Pen = wx.TRANSPARENT_PEN
        dc.DrawRectangleRect(rect)

        #get state of checkbox
        value = grid.Table.GetValue(row, col)
        if value:
            style = wx.CONTROL_CHECKED
        else:
            style = 0

        #draw Checkbox
        dc.ClippingRect = rect
        render = wx.RendererNative.Get()        
        render.DrawCheckBox(grid, dc, (rect.x, rect.y, 16, rect.height), style)
        dc.DestroyClippingRegion()

    def GetBestSize(self, grid, attr, dc, row, col):
        return wx.Size(16, 16)

    def Clone(self):
        return BoolEditor()


class BoolEditor(wx.grid.PyGridCellEditor):
    """
    Custom Bool Cell Editor. Use native checkbox.
    """
    def __init__(self):
        wx.grid.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        self.checkbox = wx.CheckBox(parent, id, "")

        self.SetControl(self.checkbox)
        if evtHandler:
            self.checkbox.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        self.checkbox.SetPosition((rect.x+1, rect.y+2))
        self.checkbox.SetSize((rect.width-2, rect.height-2))

    def Show(self, show, attr):
        super(BoolEditor, self).Show(show, attr)

    def BeginEdit(self, row, col, grid):
        self.startValue = bool(grid.Table.GetValue(row, col))
        self.checkbox.Value = self.startValue
        self.checkbox.SetFocus()

    def EndEdit(self, row, col, grid):
        value = self.checkbox.Value
        grid.Table.SetValue(row, col, value)
        return True

    def Reset(self):
        self.checkbox.Value = self.startValue

    def StartingClick(self):
        """
        Gets called after the first click. Toggle state of checkbox.
        """
        self.checkbox.Value = not self.checkbox.Value

    def Destroy(self):
        super(BoolEditor, self).Destroy()

    def Clone(self):
        return BoolEditor()
