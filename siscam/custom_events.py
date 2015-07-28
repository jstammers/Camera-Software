#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Define custom wx events"""

import wx.lib.newevent


#(ReloadImageEvent, EVT_RELOAD_IMAGE) = wx.lib.newevent.NewCommandEvent()

#Note: NewCommandEvent unnecessarily forces signature of new event
#class to contain id
class ReloadImageEvent(wx.PyCommandEvent):
    evttype = wx.NewEventType()
    def __init__(self, filename = None, target = None, **kw):
        wx.PyCommandEvent.__init__(self, self.evttype)
        self.filename = filename
        self.target = target
        self.__dict__.update(kw)
EVT_RELOAD_IMAGE = wx.PyEventBinder(ReloadImageEvent.evttype, 1)

(FitCompletedEvent, EVT_FIT_COMPLETED) = wx.lib.newevent.NewEvent()
(FitResultsEvent, EVT_FIT_RESULTS) = wx.lib.newevent.NewCommandEvent()
(SaveImageEvent, EVT_SAVE_IMAGE) = wx.lib.newevent.NewEvent()
