#!/usr/bin/python
#-*- coding: latin-1 -*-
"""High level interface to Matrix Vision cams (mvBlueFOX)."""

import numpy
import ctypes
import mvIMPACT.acquire as MV

#hack to releas GIL during wait
MVll = ctypes.windll.mvDeviceManager

llWait = MVll.DMR_ImageRequestWaitFor
llWait.argtypes = [ctypes.c_int,
                   ctypes.c_int,
                   ctypes.c_int,
                   ctypes.POINTER(ctypes.c_int)]
llWait.restype = ctypes.c_int
#


class TimeoutError(Exception):
    def __init__(self):
        Exception.__init__(self, 'Timeout')

class Cam(object):
    """High level represantion of Theta-Systems Cam."""

    def __init__(self):
        print 'init'
        self._data = None
        self._device_manager = MV.DeviceManager()
        self.device = self._device_manager.getDeviceByProduct('mvBlueFOX-120AG')

    def open(self):
        print 'open bluefox'
        self.device.open()
        
        self.cam = MV.FunctionInterface(self.device)
        self.cam.ensureRequests(1)
        return self

    def close(self):
        print 'close bluefox'
        self.device.close()

    def wait(self, timeout=1000):
        """wait for next image to acquired. timeout in ms"""
        #TODO: set timeout property!!
        self.cam.imageRequestSingle()

        nr = self.cam.imageRequestWaitFor(-1)

        ##hack to release GIL during wait, instead of imageRequestWaitFor()
        #nr = ctypes.c_int(0)
        #errorcode = llWait(self.device.hDrv(),
        #                   #timeout,
        #                   -1,
        #                   0,
        #                   ctypes.byref(nr))
        #nr = nr.value
        #-----------

        self._data = None

        if not self.cam.isRequestNrValid(nr):
            print "request is not valid (perhaps timeout in RequestWaitFor"
            self.cam.imageRequestUnlock(nr)
            raise TimeoutError

        request = self.cam.getRequest(nr)

        if not self.cam.isRequestOK(request):
            print "Error in acquired image, possibly timeout"

            reason = request.requestResult.readS()
            reasonid = request.requestResult.read()

            if reason == 'Timeout':
                self.cam.imageRequestUnlock(nr)
                raise TimeoutError
            else:
                self.cam.imageRequestUnlock(nr)
                raise Exception('Error acquiring image #%d: %s'%(reasonid, reason))

        imgbuf = request.getImageBuffer()
        cbuf = (ctypes.c_char*(imgbuf.iSize)).from_address(long(imgbuf.vpData))
        img = numpy.fromstring(cbuf, dtype = numpy.uint8)
        img.shape = (imgbuf.iHeight, imgbuf.iWidth)

        self._data = img
        self.cam.imageRequestUnlock(nr)

    @property
    def data(self):
        return self._data

    def set_timing(self, integration = 20,
                   repetition = 1000):

        p = MV.CameraSettingsBlueFOX(self.device)

        if integration == 0 and repetition == 0:
            p.triggerMode.writeS('OnHighExpose')

        else:
            p.expose_us.write(int(integration*1000))



if __name__ == '__main__':
    cam = Cam()

    cam.open()
    cam.wait()
    img = cam.data
    cam.close()
        
        


        
        
        

        


        
        
    
