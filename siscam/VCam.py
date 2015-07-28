#!/usr/bin/python
#-*- coding: latin-1 -*-
"""High level interface to Sony Cams with Imaging Control ActiveX interface.
Note: if started from IPython, behaves very slowly!
"""
from settings import ImagingControlProgID as ICID

import time, math

import numpy
import ctypes

from win32com.client.gencache import EnsureDispatch
from win32com.client import Dispatch


from camera import CamTimeoutError

class ICTimeoutError(CamTimeoutError):
    def __init__(self):
        super(ICTimeoutError, self).__init__(self)


#constants, taken from samples/vb6/common/VCDPropertyID.bas

VCDInterface_Range = "{99B44940-BFE1-4083-ADA1-BE703F4B8E03}"
VCDInterface_Switch = "{99B44940-BFE1-4083-ADA1-BE703F4B8E04}"
VCDInterface_Button = "{99B44940-BFE1-4083-ADA1-BE703F4B8E05}"
VCDInterface_MapStrings = "{99B44940-BFE1-4083-ADA1-BE703F4B8E06}"
VCDInterface_AbsoluteValue = "{99B44940-BFE1-4083-ADA1-BE703F4B8E08}"

#Standard Element IDs
VCDElement_Value = "{B57D3000-0AC6-4819-A609-272A33140ACA}"
VCDElement_Auto = "{B57D3001-0AC6-4819-A609-272A33140ACA}"
VCDElement_OnePush = "{B57D3002-0AC6-4819-A609-272A33140ACA}"

#Standard Property Item IDs
VCDID_Brightness = "{284C0E06-010B-45BF-8291-09D90A459B28}"
VCDID_Contrast = "{284C0E07-010B-45BF-8291-09D90A459B28}"
VCDID_Hue = "{284C0E08-010B-45BF-8291-09D90A459B28}"
VCDID_Saturation = "{284C0E09-010B-45BF-8291-09D90A459B28}"
VCDID_Sharpness = "{284C0E0A-010B-45BF-8291-09D90A459B28}"
VCDID_Gamma = "{284C0E0B-010B-45BF-8291-09D90A459B28}"
VCDID_ColorEnable = "{284C0E0C-010B-45BF-8291-09D90A459B28}"
VCDID_WhiteBalance = "{284C0E0D-010B-45BF-8291-09D90A459B28}"
VCDID_BacklightCompensation = "{284C0E0E-010B-45BF-8291-09D90A459B28}"
VCDID_Gain = "{284C0E0F-010B-45BF-8291-09D90A459B28}"

VCDID_Pan = "{90D5702A-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_Tilt = "{90D5702B-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_Roll = "{90D5702C-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_Zoom = "{90D5702D-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_Exposure = "{90D5702E-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_Iris = "{90D5702F-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_Focus = "{90D57030-E43B-4366-AAEB-7A7A10B448B4}"

VCDID_TriggerMode = "{90D57031-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_VCRCompatibilityMode = "{90D57032-E43B-4366-AAEB-7A7A10B448B4}"
VCDID_SignalDetected = "{90D57033-E43B-4366-AAEB-7A7A10B448B4}"

#TIS DCAM Property Item IDs
VCDID_TestPattern = "{F7EAA79E-90FA-4969-B05F-9BDAF1A4328F}"

VCDID_MultiSlope = "{630B1F3E-4A0A-4963-89B1-86BA8FDA2990}"

VCDElement_MultiSlope_SlopeValue0 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3090}"
VCDElement_MultiSlope_ResetValue0 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3091}"
VCDElement_MultiSlope_SlopeValue1 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3190}"
VCDElement_MultiSlope_ResetValue1 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3191}"
VCDElement_MultiSlope_SlopeValue2 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3290}"
VCDElement_MultiSlope_ResetValue2 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3291}"
VCDElement_MultiSlope_SlopeValue3 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3390}"
VCDElement_MultiSlope_ResetValue3 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3391}"
VCDElement_MultiSlope_SlopeValue4 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3490}"
VCDElement_MultiSlope_ResetValue4 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3491}"
VCDElement_MultiSlope_SlopeValue5 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3590}"
VCDElement_MultiSlope_ResetValue5 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3591}"
VCDElement_MultiSlope_SlopeValue6 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3690}"
VCDElement_MultiSlope_ResetValue6 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3691}"
VCDElement_MultiSlope_SlopeValue7 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3790}"
VCDElement_MultiSlope_ResetValue7 = "{630B1F3E-4A0A-4963-89B1-86BA8FDA3791}"


#TIS DCAM Element IDs
VCDElement_WhiteBalanceBlue = "{6519038A-1AD8-4E91-9021-66D64090CC85}"
VCDElement_WhiteBalanceRed = "{6519038B-1AD8-4E91-9021-66D64090CC85}"
VCDElement_AutoReference = "{6519038C-1AD8-4E91-9021-66D64090CC85}"

VCDElement_TriggerPolarity = "{6519038D-1AD8-4E91-9021-66D64090CC85}"
VCDElement_TriggerMode = "{6519038E-1AD8-4E91-9021-66D64090CC85}"
VCDElement_ResetValue = "{B57D3003-0AC6-4819-A609-272A33140ACA}"


VCDID_GPIO = 			"{86D89D69-9880-4618-9BF6-DED5E8383449}"

VCDElement_GPIOIn =	"{7D006621-761D-4B88-9C5F-8B906857A500}"
VCDElement_GPIOOut =	"{7D006621-761D-4B88-9C5F-8B906857A501}"
VCDElement_GPIOWrite =	"{7D006621-761D-4B88-9C5F-8B906857A502}"
VCDElement_GPIORead =	"{7D006621-761D-4B88-9C5F-8B906857A503}"

VCDID_Strobe = 				"{DC320EDE-DF2E-4A90-B926-71417C71C57C}"
VCDElement_StrobePolarity = 	"{B41DB628-0975-43F8-A9D9-7E0380580ACA}"
VCDElement_StrobeDuration = 	"{B41DB628-0975-43F8-A9D9-7E0380580ACB}"
VCDElement_StrobeDelay = 		"{B41DB628-0975-43F8-A9D9-7E0380580ACC}"

class VCam(object):
    """High level represantion of Sony Cams."""

    def __init__(self):
        print 'init'
        self._data = None
        self.cam = EnsureDispatch(ICID)
        
        print 'init done'

    def open(self, config):
        print 'open sony'

        #self.cam = EnsureDispatch(ICID)
        #self.cam = Dispatch(ICID)

        #load settings, created by SaveDeviceStateToFile
        self.cam.LoadDeviceStateFromFile(config, True)

        #get image extends
        self.w = self.cam.ImageWidth
        self.h = self.cam.ImageHeight
        self.d = self.cam.ImageBitsPerPixel / 8

        #initialize cam
        self.cam.MemorySnapTimeout = 1000
        self.cam.ImageRingBufferSize = 6
        self.cam.LiveDisplay = False #True
        self.cam.LiveCaptureLastImage=False

        self.cam.LiveStart()
        
        return self

    def start(self):
        if not self.cam.LiveVideoRunning:
            self.cam.LiveStart()

    def stop(self):
        if self.cam.LiveVideoRunning:
            self.cam.LiveStop() 

    def close(self):
        print 'close'
        self.stop()
        del self.cam

    def snap(self, n=1):
        """acquire sequence of n images"""

        if n>self.cam.ImageRingBufferSize:
            raise ValueError('sequence length too large')
        
        try:
            tic = time.clock()
            self.cam.MemorySnapImageSequence(n)
            #print "got %d pictures after %.3f ms"%(n, 1e3*(time.clock() - tic))
        except Exception, e:
            #print "didn't get all (or any) pictures"
            raise ICTimeoutError(0, self.wait)

        imgbufs = self.cam.ImageBuffers
        for b in imgbufs:
            b.Lock()
            
        sampletimes = [buf.SampleEndTime for buf in imgbufs]
        buforder = [t[0] for t in sorted([x for x in enumerate(sampletimes)],
                                         key = lambda t:t[1])]
        print "used buffers nr ",buforder[-n:]
        print "sample times:", sampletimes

        imgs = [self._get_img(n) for n in buforder[-n:]]
        
        for b in imgbufs:
            b.ForceUnlock()

        return imgs

    def _get_img(self, n):
        b = self.cam.ImageBuffers[n]
        b.Lock()

        ptr = b.ImageDataPtr
        cbuf = (ctypes.c_char*(abs(self.w*self.h*self.d))).from_address(long(ptr))
        img = numpy.fromstring(cbuf, dtype = numpy.uint8)
        b.Unlock()

        img.shape = (self.h, self.w, self.d)
        return img[:,:,0].copy()


    def wait(self, timeout=1000):
        """DEPRECATED. Use snap instead.
        wait for next image to acquired. timeout in ms"""

        starttime = self.cam.ImageBuffers[0].SampleEndTime
        try:
            self.cam.MemorySnapImage()
        except Exception, e:
            #print "Exception happened", e
            print "timeout"
            raise ICTimeoutError(0,self.wait)
        
        self._data = None
        
        

        b = self.cam.ImageBuffers[0]

        if b.SampleEndTime <= starttime:
            #raise TimeoutError
            print b.SampleEndTime, starttime
        
        b.Lock()

        ptr = b.ImageDataPtr
        cbuf = (ctypes.c_char*(abs(self.w*self.h*self.d))).from_address(long(ptr))
        img = numpy.fromstring(cbuf, dtype = numpy.uint8)
        b.Unlock()

        img.shape = (self.h, self.w, self.d)
        self._data = img[:,:,0]

    @property
    def data(self):
        return self._data

    def set_timing(self,
                   integration = 20,
                   repetition = 0):
        print "set timing:", integration, repetition

        

        self.stop()
        if integration==0 and repetition==0:
            if self.cam.DeviceTriggerAvailable:
                self.cam.DeviceTrigger=True 
        else:
            if self.cam.DeviceTriggerAvailable:
                self.cam.DeviceTrigger=False

            t = integration/1000.0
            logt = round(math.log(t,2))
            if self.cam.ExposureAvailable:
                self.cam.ExposureAuto = False
                self.cam.Exposure = logt
            

        #TODO: set integration
        self.start()


if __name__ == '__main__':
    cam = VCam()

    try:
        cam.open(settings.devicesettings)
        c = cam.cam

        #take picture
        cam.wait()
        img1 = cam.data
        print "got image 1"

        cam.wait()
        img2 = cam.data
        print "got image 2"

        img3 = cam.snap(3)
        print "got image sequence"

        cam.wait()

        cam.snap(2)

        #c.LiveStop()
        #c.DeviceTrigger = True
        #c.LiveStart()

        #c.LiveStop()
        #c.LiveDisplay = False
        #c.LiveStart()
        
        props = c.VCDPropertyItems
        print "Properties:"
        for prop in props:
            print prop.Name
            for e in prop.Elements:
                print " -  ", e.Name


        Exposure = c.VCDPropertyItems.FindItem(VCDID_Exposure)
        if Exposure:
            ExposureSwitch = Exposure.Elements.FindInterface(VCDElement_Auto + ":" + VCDInterface_Switch)
            ExposureRange = Exposure.Elements.FindInterface(VCDElement_Value+":"+VCDInterface_Range)
            ExpsoureMap = Exposure.Elements.FindInterface(VCDElement_Value+":"+VCDInterface_MapStrings)
            
        
    except CamTimeoutError:
        print "timeout occured!"
        cam.close()
    else:
        cam.close()
        pass
        


        
        
        

        


        
        
    
