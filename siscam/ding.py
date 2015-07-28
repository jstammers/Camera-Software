#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Play a (random) sound."""

import wx
import os, os.path
import random

class Ding:
    def __init__(self):
        self.soundpath = os.path.join(os.getcwd(), 'sounds') #TODO: might fail
        self.soundfiles = os.listdir(self.soundpath)

    def play(self):
        soundfile = os.path.join(self.soundpath,
                                 random.choice(self.soundfiles))

        wx.Sound.PlaySound(soundfile, wx.SOUND_ASYNC)
        wx.YieldIfNeeded() #necessary?
    
