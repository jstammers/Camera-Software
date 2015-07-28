#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Contains imaging parameters like effective pixelsize, absorption
coefficient, ..."""

class ImagingPars(object):
    """Base class for parameters of imaging system.

    @cvar description: descriptive name of settings, used for GUI selection.
    @cvar pixelsize: Size of area (in µm) which is imaged to one pixel of the cam.
    @cvar sigma0: cross section for light absorption
    """
    description = None
    pixelsize = 1
    sigma0 = 1.5/3.14*(780e-9)**2
    expansion_time = 0
    mass = 0
    ODmax = 0 #maximum optical density

    def __str__(self):
        s = "%s, t_exp = %.1fms, OD_max = %.1f"%(
            self.description,
            self.expansion_time,
            self.ODmax)
        return s

class ImagingParsHorizontal(ImagingPars):
    description = "horizontal"
    pixelsize = 6.45e-6/2 * 1e6 #pixelsize in µm
    
class ImagingParsVertical(ImagingPars):
    description = "vertical"
    pixelsize = 6.45e-6/2.5 * 1e6 #pixelsize in µm

class ImagingParsBlueFox(ImagingPars):
    description = 'BlueFox'
    pixelsize = 7.4 #pixelsize in µm
