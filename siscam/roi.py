#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Region Of Interest."""

class ROI(object):
    "class for handling information about region of interest ROI"
    def __init__(self, xmin = 0, xmax = 1392, ymin = 0, ymax = 1040):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    @property
    def xrange(self):
        return range(self.xmin, self.xmax)

    @property
    def yrange(self):
        return range(self.ymin, self.ymax)

    def xrange_clipped(self, img):
        return range( max(self.xmin, 0),
                      min(self.xmax, img.shape[1])
                      )

    def yrange_clipped(self, img):
        return range( max(self.ymin, 0),
                      min(self.ymax, img.shape[0])
                      )

    @property
    def ROI(self):
        return slice(self.ymin, self.ymax), slice(self.xmin, self.xmax)

    @property
    def x(self):
        return slice(self.xmin, self.xmax)

    @property
    def y(self):
        return slice(self.ymin, self.ymax)

    def setx(self, val, num):
        if num==0:
            self.xmin = int(val)
        elif num==1:
            self.xmax = int(val)

    def getx(self, num):
        return [self.xmin, self.xmax][num] #TODO: range checking of num

    def gety(self, num):
        return [self.ymin, self.ymax][num] #TODO: range checking of num

    def sety(self, val, num):
        if num==0:
            self.ymin = int(val)
        elif num==1:
            self.ymax = int(val)
