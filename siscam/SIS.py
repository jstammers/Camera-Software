"""
High level interface for Theta-System cameras.
"""

import SISlib
import numpy
import ctypes

from SISlib import SislibError, SislibTimeoutError

import random
import time

from camera import CamTimeoutError

class Cam(object):
    """High level representation of Theta-Systems Cam."""
    
    def __init__(self, path = None, config = 'config.ccf', handle = 0):
        """Create Camera object.
        @param path: path of SisApi.dll (optional)
        @param config: (full) path to config file (default: 'config.ccf')
        @param handle: index of acquisition board (default 0)
        """
    
        lib = SISlib.SisLibrary()
        lib.load_library(path)
        self.__sislib = lib()
        self.handle = handle
        self.config_file = config

    def open(self):
        """Open and initialize SIS camera system"""
        print "open SIS"
        self.__sislib.sis_Open(self.handle, self.config_file)
        return self
        
    def close(self):
        """Close cam."""
        self.__sislib.sis_Close(self.handle)
        
    def reset(self):
        """reset DMA controller of interface board. Should be called if
        image acquisition has been aborted."""
        self.__sislib.sis_Reset(self.handle)
        
    def getROI(self):
        """Give Region of interest.
        @return: region of interest
        @rtype: (left, right, top, bottom)
        """
        ROI = SISlib.RECT(0,0,0,0);
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_ROI, ctypes.byref(ROI))
        return (ROI.left, ROI.right, ROI.top, ROI.bottom)
    
    def setROI(self, roi):
        """Set Region of interest.
        @param roi: region of interest. If None, reset ROI
        @type roi: (left, right, top, bottom)
        """
        if roi is None:
            self.clearROI()
        else:
            ROI = SISlib.RECT()
            ROI.left, ROI.right, ROI.top, ROI.bottom = roi
            self.__sislib.sis_SetROI(self.handle, ctypes.byref(ROI))

    def clearROI(self):
        """Reset region of interest to default (complete frame)"""
        self.__sislib.sis_SetROI(self.handle, 0)

    ROI = property(getROI, setROI, clearROI)

    @property
    def binning_enabled(self):
        """Return true value if binning is enabled."""
        arg = ctypes.c_int()
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_BINNINGENABLE, ctypes.byref(arg))
        return arg.value

    @property
    def driver_revision(self):
        """driver revision and firmware revision. If value
        contains $, then debug mode is active.
        @rtype: string"""
        s = ctypes.create_string_buffer(20)
        self.__sislib.sis_GetDriverRevision(s)
        return s.value

    @property
    def actual_width(self):
        """width of image (read only)
        @return: width of image in pixels, including binning"""
        actwidth = ctypes.c_int()
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_ACTWIDTH, ctypes.byref(actwidth))
        return actwidth.value

    @property
    def actual_height(self):
        """height of image (readonly)
        @return: height of image in pixels, including binning"""
        actheight = ctypes.c_int()
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_ACTHEIGHT, ctypes.byref(actheight))
        return actheight.value

    @property
    def debug_info(self):
        """debug information (read only).
        @rtype: string
        @return: complete debug information"""
        s = ctypes.create_string_buffer(5000)
        self.__sislib.sis_TextOutSisData(self.handle, s, SISlib.SIS_DIAG_ALL)
        return s.value

    @property
    def frame_width(self):
        """frame width (maximum image width) in pixels (read only)"""
        val = ctypes.c_int()
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_FRAMEWIDTH, ctypes.byref(val))
        return val.value

    @property
    def frame_height(self):
        """frame height (maximum image height) in pixels (read only)"""
        val = ctypes.c_int()
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_FRAMEHEIGHT, ctypes.byref(val))
        return val.value

    @property
    def actual_ROI(self):
        """region of interest, including binning (read only).
        @rtype: (left, right, top, bottom)"""
        ROI = SISlib.RECT(0,0,0,0);
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_ACTROI, ctypes.byref(ROI))
        return (ROI.left, ROI.right, ROI.top, ROI.bottom)

    @property
    def frame_count(self):
        """number of acquired frames (read only)"""
        val = ctypes.c_int()
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_ACQFRAMECOUNT, ctypes.byref(val))
        return val.value

    @property
    def acquisition_mode(self):
        """actual acquisition mode (read only). See L{SISlib}, SIS_ACQ_*"""
        val = ctypes.c_int()
        self.__sislib.sis_Get(self.handle, SISlib.SISGET_ACQMODE, ctypes.byref(val))
        return val.value
    
    def get_data(self, frame = 0):
        """Give raw image data.
        @param frame: frame number (only for sequence aquisition, otherwise 0)
        @rtype: ndarray (L{actual_width} x L{actual_height}, uint16)"""
        width = self.actual_width
        height = self.actual_height
        img = numpy.empty(shape = (height, width), dtype = numpy.uint16)
        self.__sislib.sis_CopyAcqData(self.handle, frame, img)
        return img

    @property
    def data(self):
        """give raw image data (read only). short for L{get_data(frame =
        0)<get_data>}."""
        return self.get_data()

    @property
    def roidata(self):
        """Give image data."""
        img = self.data
        left, right, top, bottom = self.ROI
        nx = right-left
        ny = bottom-top
        d = img.reshape(-1)[0:(nx*ny)].copy()
        d.shape = (ny, nx)
        return d

    def start_singleshot(self):
        """Start acquistion of single image"""
        self.__sislib.sis_StartAcq(self.handle, SISlib.SIS_ACQ_SINGLESHOT)

    def start_live_acquisition(self):
        """start of continuous image acquisition"""
        self.__sislib.sis_StartAcq(self.handle, SISlib.SIS_ACQ_CONTINOUS)

    def start_sequence(self, Nframes):
        """start acquisition of N consecutive frames.
        @param Nframes: number of frames."""
        self.__sislib.sis_StartAcq(self.handle, Nframes)

    def stop(self):
        """stop image acquisition after current image is completely acquired."""
        self.__sislib.sis_StopAcq(self.handle)


    def wait(self, timeout):
        """wait for end of data acquisition, timeout in ms"""
        try:
            self.__sislib.sis_WaitAcqEnd(self.handle, timeout)
        except SislibTimeoutError:
            raise CamTimeoutError

    def set_timing(self, integration = 20, repetition = 1000):
        """Set image timing information. Set params to zero for external exposure control.
        @param: integration time in ms
        @param: repetition time in ms.
        """
        integration_time_us = int(round(integration*1000))
        repetition_time_us =  int(round(repetition*1000))
        self.__sislib.sis_SetTiming(self.handle, integration_time_us, repetition_time_us)
        
        
# Pseudo Cams for testing purposes    
class PseudoCam(object):
    def __init__(self, path = None, config = 'config.ccf', handle = 0):
        self.binning_enabled = True
        self.driver_revision = "PseudoCam 0.0 $"
        #self.actual_width = 1392
        #self.actual_height = 1040*2
        self.actual_width = 600
        self.actual_height = 400*2
        self.debug_info = "PseudoCam"
        self.frame_width = 1392
        self.frame_height = 2*1040
        self.acquisition_mode = 0
        
        self.frame_count = 0
        self.clearROI()

        self._image_nr = 0

        self.exposure = 0
        self.repetition = 0

    def open(self):
        print "open PseudoCam"
        return self

    def close(self):
        print "close PseudoCam"
        pass
    
    def reset(self):
        pass

    def getROI(self):
        return self.roi

    def setROI(self, roi):
        self.roi = roi

    def clearROI(self):
        self.roi = (0, 0, 1392, 1040)

    ROI = property(getROI, setROI, clearROI)

    @property
    def actual_ROI(self):
        return self.roi

    def get_data(self, frame = 0):
        img = self.create_image()
        self._image_nr += 1
        self.slow_down()
        return img
    
    @property
    def data(self):
        return self.get_data()

    @property
    def roidata(self):
        return self.get_data()

    def start_singleshot(self):
        pass

    def start_live_acquisition(self):
        self._image_nr = 0
        pass

    def stop(self):
        pass

    def wait(self, timeout):
        import time
        time.sleep(timeout/1000.0)

    def set_timing(self, integration, repetition):
        self.exposure = integration
        self.repetition = repetition

    def create_image(self):
        if self.exposure or self.repetition:
            return self.create_image_live()
        else:
            return self.create_image_absorption()
        
    def create_image_live(self):
        width = self.actual_width
        height = self.actual_height / 2
        
        x = numpy.arange(width, dtype = numpy.float_)
        x.shape = (1, -1)
        y = numpy.arange(height, dtype = numpy.float_)
        y.shape = (-1, 1)

        mx1 = random.gauss(200, 10)
        my1 = random.gauss(250, 10)

        mx2 = random.gauss(200, 10)
        my2 = random.gauss(250, 10)

        sx1 = random.gauss(20, 5)
        sy1 = sx1

        sx2 = random.gauss(20, 5)
        sy2 = sx2

        img1 = numpy.exp( -(x - mx1)**2/sx1**2) * \
               numpy.exp( -(y - mx1)**2/sy1**2) \
               + numpy.random.random((height, width))*0.2

        img2 = numpy.exp( -(x - mx2)**2/sx2**2) * \
               numpy.exp( -(y - mx2)**2/sy2**2) \
               + 0.3

        img1 *= 1000
        img2 *= 1000

        return numpy.vstack((img1, img2,))

    def slow_down(self):
        time.sleep(0.5)

    def slow_down(self):
        time.sleep(1)

    def create_image_absorption(self):
        width = self.actual_width
        height = self.actual_height / 2

        x = numpy.arange(width, dtype = numpy.float_)
        x.shape = (1, -1)
        y = numpy.arange(height, dtype = numpy.float_)
        y.shape = (-1, 1)

        mx1 = random.gauss(200, 10)
        my1 = random.gauss(250, 10)

        mx2 = random.gauss(200, 10)
        my2 = random.gauss(250, 10)

        sx1 = random.gauss(20, 5)
        sy1 = sx1

        sx2 = random.gauss(20, 5)
        sy2 = sx2

        A   = random.random()
        B   = random.random()

        step = self._image_nr%3

        if step == 0:
            import fitting
            import imagingpars
            fit = fitting.Bimodal2d(imagingpars.ImagingPars())

            fit.cache.clear()
            pars1 = [A, mx1, my1, sx1, sy1, 0.0, B, sx1/1.0, sy1/1.0]
            img1 = 1000*numpy.exp(-fit.bimodal2d(pars1, x, y, 0)) +\
                   numpy.random.random((height, width))*100

            fit.cache.clear()
            pars2 = [0, mx1, my1, sx1, sy1, 0.0, B, sx1/1.0, sy1/1.0]
            img2 = 1000*numpy.exp(-fit.bimodal2d(pars2, x, y, 0)) +\
                   numpy.random.random((height, width))*100
            
            time.sleep(3)
            
        elif step == 1:
            img1 = numpy.zeros((height, width))
            img1[100:-100, 100:-100] = 1000.0 + numpy.random.random((height-200, width-200))*100
            
            img2 = numpy.zeros((height, width))
            img2[100:-100, 100:-100] = 1000.0

        elif step == 2:
            img1 = 00*numpy.ones((height, width), dtype = numpy.float64)
            img2 = 00* numpy.ones_like(img1)

        return numpy.vstack((img1, img2))


        

        
