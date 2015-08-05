#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Acquire images, display and save them."""
# -------------- LATEST STABLE VERSION 19022015 ---------------
#
# Allows passing between acquire and cam. 
#
#
# STATUS New Computer: Live view works smoothly. Crash-issue due to slow computer.
#
# RESOLVED ISSUES: Live view possible if called from IDLE, crashes at some point (runtime errors...); if called via standard shell crashes when image passed to queue in acqthread, or when image to be plotted. (see remarks at these points). Reason: Probably bad hardware, RESOLVED with new PC
#
#
# ------------------------------------------------------
# 09/01/2015: 	Try modifying GUI
#				Added IDs for buttons
#				Added queue - variable for AVT
#				Add 'import Pymba' - Section - DONE via import AVTcam
#				Added timing and mode menu - WORKS
#				Added Buttons
# 15/01/2015	Added Acquire and Consumer for AVT, plus all following functions
# 19/01/2015   	Correctly  (hopefully) implemented GUI functions concerning Timing.
#				.timing_AVT now exists and can be manipulated using GUI
# 20/01/2015	Coded temporary solution for Timing business: in AVTcam.open() set all modes correctly
# 19/02/2015    Stuff works with new computer
#               Added absorption mode (triple image consumer))	
#               Added saving to PNG-file (FOR NOW OK, NOT SURE)
# 23/02/2015    Added 'Apply Timing'-Button in TEST SECTION. Timing can be written to Guppy. Values remain on Guppy after closing and reopening Acquire. ATTENTION: crashes if integration set to value below 71, 
#               Modified TESTY TEST. Includes now camera diagnostics (--> AVTcam.py)
#
# 24/02/2015    Minor Changes. Trigger is now correctly given. Image Acquisition does not work.
# 25/02/2015    Added TriggerGiven - Event. Still not working.
# ----------------------
#(to do): Write functions for AVT instead of sony ; AVT with .set_timing(), 
# (to do): Define third mode? Semi-External = trigger, but then fixed exposure time.
# TO DO Double check PNG-stuff: 
#                Size (! is there ROI setting in Cam?) ----> seems that whole image is passed. only question of zoom / cutting ...
#                brightness 
#                Cam.py error messages 
#                Take care of metadata ?	
# TO DO: Make whole thing work with external triggers. (Mode-control, proper AVT-function, )
# TO DO: Proper Timing
# TO DO: Take default values for timing_AVT from Guppy.
# TO DO: Find out how to put Camera in right mode for triggering.
# TO DO: Write ONE function that prepares camera in correct mode, depending on desired use. 
# ---------------------------------------
#	NOTES:  
#		- timing: app.timing_sony = CamTiming-object , values changed via OnSetTiming -->CreateDialog -->TimingDialog --> GetResult
#		- runs until .stop is called. Intervall between Images ??
#		- AcquireThread : Opens, Sets timing, starts taking images, saves to queue, closes ('with closing')
#		
#
from __future__ import with_statement

import wx, wx.aui, wx.lib.newevent

import numpy as np

import os, os.path
import threading, Queue
from contextlib import closing

import time

import settings
import ImagePanel
import readsis
from png_writer import PngWriter

reload(settings)
reload(ImagePanel)
from camera import CamTimeoutError

import sys
#take over settings
from settings import useTheta, useBluefox, useSony, useAVT
usePseudoTheta = settings.usePseudoCam
imgFile = open(os.getcwd()+'imgValues.txt','w+')
if useAVT:
    try:
        import AVTcam
        reload(AVTcam)
        useAVT = True
        # Guppy = AVTcam.AVTcam() ### might be better this way. right now implemented in if __name__ = __main__ block.
        VimbAcq = AVTcam.VimbAcq()	
    except ImportError:
        useAVT = False
        print "AVT not available"

        # configfile_theta = settings.configfile ### What to do here?
    

if useTheta:
    try:
        import SIS
        reload(SIS)
        useTheta = True
        
    except ImportError:
        useTheta = False
        print "Theta not available"

    if not usePseudoTheta:
        configfile_theta = settings.configfile
        camtheta = SIS.Cam(config=configfile_theta)
    else:
        camtheta = SIS.PseudoCam()
        useTheta = True

if useBluefox:
    try:
        import IMPACT
        reload(IMPACT)
        useBluefox = True
    except ImportError:
        useBluefox = False
        print "Bluefox not available!"

if useSony:
    try:
        import VCam
        reload(VCam)
        useSony = True
        configfiles_sony = settings.configfiles_sony
        cam_sony = VCam.VCam()
    except ImportError:
        useSony = False
        print "Sony not available"
        
(AVTSingleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_SINGLE_AVT) = wx.lib.newevent.NewEvent() ####AVT
(AVTTripleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_TRIPLE_AVT) = wx.lib.newevent.NewEvent() ####AVT
(ThetaSingleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_SINGLE_THETA) = wx.lib.newevent.NewEvent()
(ThetaTripleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_TRIPLE_THETA) = wx.lib.newevent.NewEvent()
(BluefoxSingleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_SINGLE_BLUEFOX) = wx.lib.newevent.NewEvent()
(BluefoxTripleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_TRIPLE_BLUEFOX) = wx.lib.newevent.NewEvent()
(SonySingleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_SINGLE_SONY) = wx.lib.newevent.NewEvent()
(SonyTripleImageAcquiredEvent, EVT_IMAGE_ACQUIRE_TRIPLE_SONY) = wx.lib.newevent.NewEvent()

AVTTriggerGivenEvent = threading.Event() ####AVT

(StatusMessageEvent, EVT_STATUS_MESSAGE) = wx.lib.newevent.NewEvent()

class CamTiming(object):
    def __init__(self, exposure, repetition=None, trigger=False, live=True):
        self._exposure = exposure
        self._repetition = repetition
        self._live = live
        self._trigger = trigger

    def get_exposure(self):
        if self._live:
            return self._exposure
        else:
            return 0

    def set_exposure(self, value):
        self._exposure = value
        
    exposure = property(get_exposure, set_exposure)
    
    def get_repetition(self):
        if self._live:
            return self._repetition
        else:
            return 0
    def set_repetition(self, value):
        self._repetition = value



    def get_trigger(self):
        if self._live:
            return self._trigger
        else:
            return 0

    def set_trigger(self,value):
        self._trigger = value
    trigger = property(get_trigger,set_trigger)

    repetition = property(get_repetition, set_repetition)

    def get_live(self):
        return self._live
    
    def set_live(self, value=True):
        self._live = bool(value)

    live = property(get_live, set_live)
    
    def get_external(self):
        return not self.live
    
    def set_external(self, value):
        self.live = not value
        
    external = property(get_external, set_external)


class AcquireThread(threading.Thread):
    """Base class for image acquisition threads."""

    def __init__(self, app, cam, queue):
        threading.Thread.__init__(self)
        self.app = app
        self.cam = cam
        self.queue = queue

        self.running = False
        self.nr = 0

    def run(self):
        pass

    def stop(self):
        self.running = False


class AcquireThreadTheta(AcquireThread):

    def run(self):
        self.running = True
        with closing(self.cam.open()):

            if self.app.timing_theta.external:
                self.cam.set_timing(0, 0)
            else:
                self.cam.set_timing(integration=self.app.timing_theta.exposure,
                                    repetition=self.app.timing_theta.repetition)

            self.cam.start_live_acquisition()

            while self.running:
                try:
                    self.cam.wait(1)
                except CamTimeoutError:
                    pass
                except SIS.SislibError:
                    print "Error acquiring image from Theta"
                else:
                    img = self.cam.roidata
                    self.nr += 1
                    self.queue.put((self.nr, img.astype(np.float32))) #TODO: ????

            #put empty image to queue
            self.queue.put((- 1, None))

        print "SISImageProducerThread exiting"

    def stop(self):
        self.running = False
        try:
            self.cam.stop()
        except SIS.SislibError, e:
            print e
######AVT ----------- New AVT-section -------- added 15012015
class AcquireThreadAVT(AcquireThread): #To be used with app=ImgAcqApp (self), cam=Guppy, queue...

    def run(self):
        self.running = True
        with closing(self.cam.open()):
            ## TODO set_timing stuff
            if not self.app.timing_AVT.external:
                self.cam.set_timing(integration=self.app.timing_AVT.exposure,
                                    repetition=self.app.timing_AVT.repetition,trigger=self.app.timing_AVT.trigger)
            time0 =time.time()
            while self.running:
                try:
                    img = self.cam.SingleImage()
                    imTime = time.time()-time0
                    self.nr += 1

                    # print 'Acq Thread: Das ist nur ein Teststring. Hier sollte das Bild kommen.'
                    self.queue.put((self.nr, img.astype(np.uint16),imTime)) ##### BEST VERSION 19012015. python crashes here with standard interpreter. IDLE crashes after couple of images. With casting='safe', OR .astype(npuint8): exception raised.

                    # print 'DEBUG MODE! bitdepth after acq = ',img.dtype.itemsize
                    
                except:
                    print "Acq Thread: UNKNOWN ERROR"
                    break
            self.queue.put((-1, None,0))
        print '------------ AcquireThreadAVT finished --------- '
        self.running = False
######## ---------------------- End new section ------------------
######AVT ----------- New AVT-section -------- added 23022015
class AcquireThreadAVTTriggered(AcquireThread): #To be used with app=ImgAcqApp (self), cam=Guppy, queue...
## Cam is opened within OnArmButton. 
    def __init__(self, app, cam, queue, evt):
        AcquireThread.__init__(self, app, cam, queue)
        self.evt = evt

    def run(self):
        self.running = True
        
            ## TODO set_timing stuff
            
        while self.running:
            try:
                frame0 = self.cam.prepareFrame()
                print 'Acq Thread: WAITING FOR TRIGGER'
                self.evt.wait(4)
                frame0.waitFrameCapture() ## FOLGT DIREKT AUF EVENT
                img = np.ndarray(buffer=frame0.getBufferByteData(),
                        dtype=np.uint16,
                        shape=(frame0.height,
                                frame0.width))
                self.nr += 1
                print 'Acq Thread: pre q'
                # print 'Acq Thread: Das ist nur ein Teststring. Hier sollte das Bild kommen.'
                self.queue.put((self.nr, img.astype(np.uint16))) ##### BEST VERSION 19012015. python crashes here with standard interpreter. IDLE crashes after couple of images. With casting='safe', OR .astype(npuint8): exception raised.
                print 'Acq Thread: post q'
                # print 'DEBUG MODE! bitdepth after acq = ',img.dtype.itemsize
                time.sleep(1)
                self.queue.put((-1, None))
                print 'Acq Thread: Terminating ...'
                self.running = False
                print 'Acq Thread Terminating: hep1'
                self.cam.camera0.endCapture()
                print 'Acq Thread Terminating: hep2'
                self.cam.camera0.revokeAllFrames()
                print 'Acq Thread Terminating: hep3'
                self.cam.close()
                print 'Acq Thread: Ended Capture, Revoked Frames, Closed Guppy. All A-Ok!' 
                print '------------ AcquireThreadAVT finished REGULAR --------- '

            except:
                print "Acq Thread: UNKNOWN ERROR. Terminating thread ..."
                
                self.running = False
                # self.cam.camera0.endCapture()
                # self.cam.camera0.revokeAllFrames()
                self.cam.close()
                print 'Acq Thread: Closed Guppy via emergency exit.' 
                print '------------ AcquireThreadAVT finished EXCEPTION--------- '
######## ---------------------- End new section ------------------
class AcquireThreadBluefox(AcquireThread):

    def run(self):
        self.running = True
        with closing(self.cam.open()):

            if self.app.timing_bluefox.external:
                self.cam.set_timing(0, 0)
            else:
                self.cam.set_timing(integration=self.app.timing_bluefox.exposure,
                                    repetition=self.app.timing_bluefox.repetition)

            while self.running:
                try:
                    self.cam.wait(1000)
                except IMPACT.TimeoutError:
                    pass
                except Exception, e:
                    print "Exception happened in acquiring image from Bluefox"
                    print e
                    break
                else:
                    img = self.cam.data
                    self.nr += 1
                    self.queue.put((self.nr, img.astype(np.float32)))

            self.queue.put((- 1, None))

        print "AcquireThreadBluefox finished"
        
class AcquireThreadSony(AcquireThread):
    def __init__(self, app, cam, queue, configfile, nimg=1, ):
        super(AcquireThreadSony, self).__init__(app, cam, queue)
        self.nimg = nimg
        self.configfile = configfile
    
    def run(self):
        self.running = True
        with closing(self.cam.open(self.configfile)):
            if self.app.timing_sony.external:
                #TODO: set external trigger
                pass
            
            self.cam.set_timing(integration=self.app.timing_sony.exposure)
            
            while self.running:
                try:
                    imgs = self.cam.snap(self.nimg)
                except CamTimeoutError:
                    pass
                except Exception, e:
                    print "unknown exception in acquiring images from Sony"
                    print e
                    break
                else:
                    self.nr += self.nimg
                    #self.queue.put((self.nr, imgs))
                    self.queue.put((self.nr, [img.astype(np.float32) for img in imgs]))
            
            self.queue.put((- 1, None))
                
class ConsumerThread(threading.Thread):
    def __init__(self, app, queue):
        threading.Thread.__init__(self, name="ImageConsumerThread")
        self.queue = queue
        self.app = app
        self.running = False

    def run(self):
        pass

    def get_image(self, timeout=1):
        """get image from queue, skip empty images (nr<0)"""
        nr = - 1
        while nr < 0:
            nr, img = self.queue.get(block=True, timeout=timeout)
        return nr, img

    def message(self, msg):
        wx.PostEvent(self.app, StatusMessageEvent(data=msg))

    def save_abs_img(self, filename, img):
        rawimg = (1000 * (img + 1)).astype(np.uint16)

        # readsis.write_raw_image(filename, rawimg)
        # print 'DEBUG MODE! bitdepth before saving abs = ',rawimg.dtype.itemsize
        PngWriter(filename, rawimg)
        self.message('S')

    def save_raw_img(self, filename, img):
        rawimg = img.astype(np.uint16)
        # readsis.write_raw_image(filename, rawimg)
        # print 'DEBUG MODE! in save_raw_img, bitdepth before saving = ',rawimg.dtype.itemsize
        PngWriter(filename, rawimg)
        self.message('S')
    
    def stop(self):
        self.running = False
        #TODO: empty queue
  

class ConsumerThreadThetaSingleImage(ConsumerThread):

    def run(self):
        self.running = True
        while self.running:
            try:
                nr, img = self.queue.get(timeout=10)
                
            except Queue.Empty:
                self.message('R')

            else:
                if nr > 0:
                    wx.PostEvent(self.app, ThetaSingleImageAcquiredEvent(imgnr=nr, img=img))
                    self.message('I')

        self.message('E')
        print "ImageConsumerThread exiting!"

######AVT ----------- New AVT-section -------- added 15012015
class ConsumerThreadAVTSingleImage(ConsumerThread):

    def run(self):
        self.running = True
        print 'consumer thread started. live'
        while self.running:
            try:
                
                nr, img, imtime = self.queue.get()
                print 'got image'
            except Queue.Empty:
                print "timout in Image consumer, resetting"
                pass

            else:
                print "consumer: got image", nr
               
                if nr > 0:
                    wx.PostEvent(self.app, AVTSingleImageAcquiredEvent(imgnr=nr, img=img))
                    
                    #if nr%100 == 0:
                    # print 'DEBUG MODE! bitdepth before saving = ',img.dtype.itemsize
                    self.save_abs_img(settings.testfile, img) ###### NOTE: png image is much darker than display --> multiply by 1000 before saving to PNG??? not sure.... for now it works like this.
                # print 'Consumer: queue size', self.queue.qsize()
        print "ImageConsumerThread exiting!"
        self.message('E')

######## ---------------------- End new section ------------------

class ConsumerThreadBluefoxSingleImage(ConsumerThread):

    def run(self):
        self.running = True
        while self.running:
            try:
                nr, img = self.queue.get(timeout=10)

            except Queue.Empty:
                print "timout in Image consumer, resetting"
                pass

            else:
                #print "got image", nr
                if nr > 0:
                    wx.PostEvent(self.app, BluefoxSingleImageAcquiredEvent(imgnr=nr, img=img))
                    #if nr%100 == 0:
                    #    self.save_abs_img(settings.imagefile, np.vstack((img, img)))

        print "ImageConsumerThread exiting!"
        self.message('E')


class ConsumerThreadThetaTripleImage(ConsumerThread):
    """Acquire three images, calculate absorption image, save to file, display"""

    def run(self):
        self.running = True
        while self.running:
            try:
                nr1, img1 = self.get_image(timeout=5)
                self.message('1')
                if not self.running: break

                nr2, img2 = self.get_image(timeout=2)
                self.message('2')
                if not self.running: break

                nr3, img3 = self.get_image(timeout=2)
                self.message('3')
                if not self.running: break

            except Queue.Empty:
                self.message(None)
                self.message('W')

            else:
                #calculate absorption image
                img = - (np.log(img1 - img3) - np.log(img2 - img3))
                imga,  imgb  = self.app.imagesplit(img)
                img2a, img2b = self.app.imagesplit(img2)

                if self.app.imaging_theta_remove_background:
                    ma, sa = find_background(img2a)
                    mb, sb = find_background(img2b)
                    imga[img2a<ma+4*sa] = np.NaN
                    imgb[img2b<mb+4*sb] = np.NaN

                if self.app.imaging_theta_useROI:
                    #set all pixels in absorption image outside roi to NaN
                    r = self.app.marker_roi_theta.roi.ROI

                    imgR = np.empty_like(imga)
                    for timg in [imga, imgb]:
                        imgR[:] = np.NaN
                        imgR[r] = timg[r]
                        timg[:] = imgR[:]
                
                data = {'image1': img1,
                        'image2': img2,
                        'image3': img3,
                        'image_numbers': (nr1, nr2, nr3),
                        'absorption_image': img}
                wx.PostEvent(self.app, ThetaTripleImageAcquiredEvent(data=data))

                self.save_abs_img(settings.imagefile, img)


        self.message('E')
        print "ImageConsumerThread exiting!"
######AVT ----------- New AVT-section -------- added 19022015
class ConsumerThreadAVTTripleImage(ConsumerThread):

    def run(self):
        self.running = True
        print 'Consumer Thread started (Absorption)'
        while self.running:
            try:
                
                nr1, img1, time1 = self.queue.get(timeout=5)

                nr2, img2, time2 = self.queue.get(timeout=5)

                nr3, img3, time3 = self.queue.get(timeout=5)
       
            except Queue.Empty:
                print "timout in Image consumer, resetting"
                pass

            else:
                print "consumer: got image", nr1, nr2, nr3
                print "image times: ", time1, time2, time3
				#calculate absorption image
                img = - (np.log(img1 - img3) - np.log(img2 - img3))

                data = {'image1': img1,
                        'image2': img2,
                        'image3': img3,
                        'image_numbers': (nr1, nr2, nr3),
                        'absorption_image': img}
                wx.PostEvent(self.app, AVTTripleImageAcquiredEvent(data=data))

                self.save_abs_img(settings.testfile, img)
                # PngWriter(settings.testfile, img, bitdepth=8)
                # print 'Consumer: queue size', self.queue.qsize()
        print "ImageConsumerThread exiting!"
        self.message('E')

######## ---------------------- End new section ------------------        
class ConsumerThreadSony(ConsumerThread):
    
    def run(self):
        self.running = True
        while self.running:
            try:
                nr, imgs = self.queue.get(timeout = 5)
            except Queue.Empty:
                self.message('R')
                
            else:
                if nr>0 and len(imgs)==1:
                #got single image
                    wx.PostEvent(self.app, SonySingleImageAcquiredEvent(imgnr=nr, img = imgs[0]))
                    self.message('I')
                elif nr>0 and len(imgs)==3:
                    #got three images
                    img =   np.log(imgs[1] - imgs[2]) - np.log(imgs[0] - imgs[2])
                    
                    data = {'image1': imgs[0],
                            'image2': imgs[1],
                            'image3': imgs[2],
                            'image_numbers': (nr, nr+1, nr+2), #TODO: nr-2, nr-1, nr?
                            'absorption_image': img,
                            }
                    wx.PostEvent(self.app, SonyTripleImageAcquiredEvent(data=data))
                    self.save_abs_img(settings.imagefile, np.vstack((img,img)))
        self.message('E')
        print "Consumer thread sony finished"
                    


class AcquireSplashScreen(wx.SplashScreen):
    def __init__(self):
        bitmap = wx.Image(os.path.join(settings.bitmappath, 'acquire_splash.png'),
                          wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        wx.SplashScreen.__init__(self,
                                 bitmap,
                                 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                 5000, None, - 1)


class ImgAcquireApp(wx.App):
    """Application to acquire, display and save images."""

    def OnInit(self):

        #IDs
        self.ID_ShowAll = wx.NewId()
        self.ID_AcquireAVTButton = wx.NewId()  #####AVT
        self.ID_AcquireThetaButton = wx.NewId()
        self.ID_AcquireBlueFoxButton = wx.NewId()
        self.ID_AcquireSonyButton = wx.NewId()

        self.ID_TimingAVTInternal = wx.NewId()  #####AVT
        self.ID_TimingAVTExternal = wx.NewId()  #####AVT
        self.ID_TimingAVTSettings = wx.NewId()  #####AVT
		
        self.ID_TimingThetaInternal = wx.NewId()
        self.ID_TimingThetaExternal = wx.NewId()
        self.ID_TimingThetaSettings = wx.NewId()

        self.ID_TimingBlueFoxInternal = wx.NewId()
        self.ID_TimingBlueFoxExternal = wx.NewId()
        self.ID_TimingBlueFoxSettings = wx.NewId()
        
        self.ID_TimingSonyInternal = wx.NewId()
        self.ID_TimingSonyExternal = wx.NewId()
        self.ID_TimingSonySettings = wx.NewId()
        
        self.ID_SonyCam1 = wx.NewId()
        self.ID_SonyCam2 = wx.NewId()
		
        self.ID_ImagingModeAVT_Live = wx.NewId()  #####AVT
        self.ID_ImagingModeAVT_Absorption = wx.NewId()  #####AVT
        self.ID_ImagingAVT_RemoveBackground = wx.NewId()  #####AVT
        self.ID_ImagingAVT_UseROI = wx.NewId()  #####AVT
		
        self.ID_ImagingModeTheta_Live = wx.NewId()
        self.ID_ImagingModeTheta_Absorption = wx.NewId()
        self.ID_ImagingTheta_RemoveBackground = wx.NewId()
        self.ID_ImagingTheta_UseROI = wx.NewId()

        self.ID_ImagingModeSony_Live = wx.NewId()
        self.ID_ImagingModeSony_Absorption = wx.NewId()

        self.ID_SettingsLoad = wx.NewId()
        self.ID_SettingsSave = wx.NewId()

        self.ID_HelpMenu = wx.NewId()
        self.ID_AboutMenu = wx.NewId()

        #Queues for image acquisition
        self.imagequeue_AVT = Queue.Queue(3)  ####AVT ; ATTENTION Argument of .queue() not clear
        self.imagequeue_theta = Queue.Queue(3)
        self.imagequeue_bluefox = Queue.Queue(2)
        self.imagequeue_sony = Queue.Queue(2)

        #splash screen
        splash = AcquireSplashScreen()
        splash.Show()
        self.SetAppName("Acquire")

        self.frame = wx.Frame(None,
                              title="Acquire - modified",
                              size=(1000, 800),
                              )

        #set main icon
        icons = wx.IconBundle()
        for icon in ['acquire16.png',
                     'acquire24.png',
                     'acquire32.png',
                     'acquire48.png']:
            icons.AddIconFromFile(os.path.join(settings.bitmappath, icon),
                                  wx.BITMAP_TYPE_PNG)
        self.frame.SetIcons(icons)

        #aui-manager
        self.manager = wx.aui.AuiManager(self.frame,
                                     wx.aui.AUI_MGR_RECTANGLE_HINT | 
                                     wx.aui.AUI_MGR_ALLOW_FLOATING
                                     )

        self.manager.SetDockSizeConstraint(0.5, 0.75)

        #member variables  
        self.imaging_mode_theta = 'live' #'live', 'absorption'
        self.imaging_mode_sony  = 'live'
        self.imaging_mode_AVT =  'live' #######AVT
		
        #self.external_timing_theta = True
        #self.external_timing_bluefox = True
        #self.external_timing_sony = False

        self.timing_AVT = CamTiming(exposure=40, repetition=605, live=False, trigger = False) ####AVT units: both times in ms, bot exposure later displated converted to us 
        self.timing_theta = CamTiming(exposure=0.1, repetition=600, live=True)
        self.timing_bluefox = CamTiming(exposure=20, repetition=None, live=True)
        self.timing_sony = CamTiming(exposure=1, repetition=None, live=True)
        
        #self.timing_exposure_theta = 100 #µs
        #self.timing_repetition_theta = 600 #ms
        #self.timing_exposure_bluefox = 20000 #µs
        #self.timing_repetition_bluefox = 20 #ms
        
        self.acquiring_theta = False
        self.acquiring_bluefox = False
        self.acquiring_sony = False
        self.acquiring_AVT = False

        self.busy = 0

        ##Menu
        #view menu
        view_menu = wx.Menu()
        view_menu.Append(self.ID_ShowAll, 'Show All')
        self.frame.Bind(wx.EVT_MENU, self.OnMenuShowAll, id = self.ID_ShowAll)
######AVT ----------- New AVT-section -------- added 09012015
	#imaging menu AVT
        menu_imaging_mode_AVT = wx.Menu()
        menu_imaging_mode_AVT.AppendRadioItem(self.ID_ImagingModeAVT_Live, 'Live')
        menu_imaging_mode_AVT.AppendRadioItem(self.ID_ImagingModeAVT_Absorption, 'Absorption')
        # menu_imaging_mode_AVT.AppendCheckItem(self.ID_ImagingAVT_RemoveBackground, 'Remove Background')
        # menu_imaging_mode_AVT.AppendCheckItem(self.ID_ImagingAVT_UseROI, 'Use Region of Interest')  ##### this one we might not need later ???
        
        self.imaging_AVT_remove_background = False
        self.imaging_AVT_useROI = False
        
        if self.imaging_mode_AVT == 'live':  ####### Maybe rather use continuous, multiframe, single frame ???
            menu_imaging_mode_AVT.Check(self.ID_ImagingModeAVT_Live, True)
        elif self.imaging_mode_AVT == 'absorption':
            menu_imaging_mode_AVT.Check(self.ID_ImagingModeAVT_Absorption, True)

        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnMenuImagingModeAVT,
                        id=self.ID_ImagingModeAVT_Live,
                        id2=self.ID_ImagingModeAVT_Absorption)
                        # id2=self.ID_ImagingTheta_UseROI) ### ATTENTION For the moment the functions stay linked to the Theta Functions. Only want to create GUI-objects, not functions
######## ---------------------- End new section ------------------
        #imaging menu theta
        menu_imaging_mode_theta = wx.Menu()
        menu_imaging_mode_theta.AppendRadioItem(self.ID_ImagingModeTheta_Live, 'Live')
        menu_imaging_mode_theta.AppendRadioItem(self.ID_ImagingModeTheta_Absorption, 'Absorption')
        menu_imaging_mode_theta.AppendCheckItem(self.ID_ImagingTheta_RemoveBackground, 'Remove Background')
        menu_imaging_mode_theta.AppendCheckItem(self.ID_ImagingTheta_UseROI, 'Use Region of Interest')
        
        self.imaging_theta_remove_background = False
        self.imaging_theta_useROI = False
        
        if self.imaging_mode_theta == 'live':
            menu_imaging_mode_theta.Check(self.ID_ImagingModeTheta_Live, True)
        elif self.imaging_mode_theta == 'absorption':
            menu_imaging_mode_theta.Check(self.ID_ImagingModeTheta_Absorption, True)

        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnMenuImagingModeTheta,
                        id=self.ID_ImagingModeTheta_Live,
                        id2=self.ID_ImagingTheta_UseROI)
        
        #imaging menu sony
        menu_imaging_mode_sony = wx.Menu()
        menu_imaging_mode_sony.AppendRadioItem(self.ID_ImagingModeSony_Live,       'Live')
        menu_imaging_mode_sony.AppendRadioItem(self.ID_ImagingModeSony_Absorption, 'Absorption')
        
        if self.imaging_mode_sony == 'live':
            menu_imaging_mode_sony.Check(self.ID_ImagingModeSony_Live, True)
        elif self.imaging_mode_sony == 'absorption':
            menu_imaging_mode_sony.Check(self.ID_ImagingModeSony_Absorption, True)

        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnMenuImagingModeSony,
                        id=self.ID_ImagingModeSony_Live,
                        id2=self.ID_ImagingModeSony_Absorption)
        
        menu_imaging_mode_sony.AppendSeparator()
        menu_imaging_mode_sony.AppendRadioItem(self.ID_SonyCam1, 'Sony Cam 1')
        menu_imaging_mode_sony.AppendRadioItem(self.ID_SonyCam2, 'Sony Cam 2')
        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnMenuCamSony,
                        id = self.ID_SonyCam1,
                        id2 = self.ID_SonyCam2)
### TIMING MENU ###
######AVT ----------- New AVT-section -------- added 09012015
        menu_timing_AVT = wx.Menu()
        menu_timing_AVT.AppendRadioItem(self.ID_TimingAVTInternal, 'Internal')
        menu_timing_AVT.AppendRadioItem(self.ID_TimingAVTExternal, 'External') ### ATTENTION adapt to AVT features

        if self.timing_AVT.external:
            menu_timing_AVT.Check(self.ID_TimingAVTExternal, True)
        else:
            menu_timing_AVT.Check(self.ID_TimingAVTInternal, True)
        
        menu_timing_AVT.Append(self.ID_TimingAVTSettings, 'Settings...')
        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnSetTiming,
                        id=self.ID_TimingAVTInternal,
                        id2=self.ID_TimingAVTSettings) ### ATTENTION For the moment the functions stay linked to the Theta Functions. Only want to create GUI-objects, not functions
######## ---------------------- End new section ------------------
						
        #timing Theta menu
        menu_timing_theta = wx.Menu()
        menu_timing_theta.AppendRadioItem(self.ID_TimingThetaInternal, 'Internal')
        menu_timing_theta.AppendRadioItem(self.ID_TimingThetaExternal, 'External')

        if self.timing_theta.external:
            menu_timing_theta.Check(self.ID_TimingThetaExternal, True)
        else:
            menu_timing_theta.Check(self.ID_TimingThetaInternal, True)
        
        menu_timing_theta.Append(self.ID_TimingThetaSettings, 'Settings...')
        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnSetTiming,
                        id=self.ID_TimingThetaInternal,
                        id2=self.ID_TimingThetaSettings) 


        #timing blue fox menu
        menu_timing_bluefox = wx.Menu()
        menu_timing_bluefox.AppendRadioItem(self.ID_TimingBlueFoxInternal, 'Internal')
        menu_timing_bluefox.AppendRadioItem(self.ID_TimingBlueFoxExternal, 'External')

        if self.timing_bluefox.external:
            menu_timing_bluefox.Check(self.ID_TimingBlueFoxExternal, True)
        else:
            menu_timing_bluefox.Check(self.ID_TimingBlueFoxInternal, True)

        menu_timing_bluefox.Append(self.ID_TimingBlueFoxSettings, 'Settings...')
        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnSetTiming,
                        id=self.ID_TimingBlueFoxInternal,
                        id2=self.ID_TimingBlueFoxSettings)

        #timing menu sony
        menu_timing_sony = wx.Menu()
        menu_timing_sony.AppendRadioItem(self.ID_TimingSonyInternal, 'Internal')
        menu_timing_sony.AppendRadioItem(self.ID_TimingSonyExternal, 'External')
        if self.timing_sony.external:
            menu_timing_sony.Check(self.ID_TimingSonyExternal, True)
        else:
            menu_timing_sony.Check(self.ID_TimingSonyInternal, True)
        
        menu_timing_sony.Append(self.ID_TimingSonySettings, 'Settings...')
        self.frame.Bind(wx.EVT_MENU_RANGE,
                        self.OnSetTiming,
                        id=self.ID_TimingSonyInternal,
                        id2=self.ID_TimingSonySettings)

        #settings menu
        settings_menu = wx.Menu()
        settings_menu.Append(self.ID_SettingsLoad, 'Load')
        settings_menu.Append(self.ID_SettingsSave, 'Save')
        self.frame.Bind(wx.EVT_MENU, self.OnSettingsLoad, id=self.ID_SettingsLoad)
        self.frame.Bind(wx.EVT_MENU, self.OnSettingsSave, id=self.ID_SettingsSave)

        #help menu
        help_menu = wx.Menu()
        help_menu.Append(self.ID_HelpMenu, 'Help')
        help_menu.Append(self.ID_AboutMenu, 'About')
        self.frame.Bind(wx.EVT_MENU, self.OnMenuHelp, id=self.ID_HelpMenu)
        self.frame.Bind(wx.EVT_MENU, self.OnMenuAbout, id=self.ID_AboutMenu)

        #main menu
        self.menu = wx.MenuBar()
        self.menu.Append(view_menu, "Show")
        if useAVT:  ####AVT
            self.menu.Append(menu_imaging_mode_AVT, "Imaging AVT") ####AVT
            self.menu.Append(menu_timing_AVT, 'Timing AVT') ####AVT
        if useTheta:
            self.menu.Append(menu_imaging_mode_theta, "Imaging Theta")
            self.menu.Append(menu_timing_theta, 'Timing Theta')
        if useBluefox:
            self.menu.Append(menu_timing_bluefox, 'Timing Bluefox')
        if useSony:
            self.menu.Append(menu_imaging_mode_sony, "Imaging Sony")
            self.menu.Append(menu_timing_sony, 'Timing Sony')
            self.configfile_sony = configfiles_sony[0]
            
        self.menu.Append(settings_menu, 'Settings')
        self.menu.Append(help_menu, 'Help')

        self.frame.SetMenuBar(self.menu)
        
        #for disabling timing menu entry ...
        self.ID_TimingTheta = self.menu.FindMenu('Timing Theta')


        ##toolbar
        self.toolbar = wx.ToolBar(self.frame, - 1,
                                  wx.DefaultPosition,
                                  wx.DefaultSize,
                                  style=wx.TB_FLAT | wx.TB_NODIVIDER | 
                                  wx.TB_HORZ_TEXT,
                                  )
        self.toolbar.SetToolBitmapSize(wx.Size(24, 24))

        #create bitmaps
        self.bitmap_stop = wx.Bitmap(os.path.join(settings.bitmappath,
                                             'stop.png'),
                                wx.BITMAP_TYPE_PNG)
        
        self.bitmap_go = wx.Bitmap(os.path.join(settings.bitmappath,
                                           'go.png'),
                              wx.BITMAP_TYPE_PNG)
        self.bitmap_save = wx.Bitmap(os.path.join(settings.bitmappath,
                                                  'save.png'))
        
         

        #go-buttons
        if useTheta:
            self.acquire_theta_button = self.toolbar.AddCheckLabelTool(
                self.ID_AcquireThetaButton,
                label="Acquire Theta",
                bitmap=self.bitmap_stop,
                shortHelp="Acquire",
                longHelp="aquire images"
                )
    
            self.Bind(wx.EVT_TOOL,
                      self.OnAcquireThetaButton,
                      id=self.ID_AcquireThetaButton)
            
            #save image button
            #TODO: which image to save?
            self.ID_SaveImageTheta = wx.NewId()
            self.toolbar.AddLabelTool(self.ID_SaveImageTheta,
                                      label='save image',
                                      bitmap=self.bitmap_save,
                                      shortHelp='save image')
            self.Bind(wx.EVT_TOOL, self.OnSaveImageTheta, id=self.ID_SaveImageTheta)
                
        if useBluefox:
            self.acquire_bluefox_button = self.toolbar.AddCheckLabelTool(
                self.ID_AcquireBlueFoxButton,
                label="Acquire BlueFOX",
                bitmap=self.bitmap_stop,
                shortHelp="Acquire",
                longHelp="aquire images from BlueFOX camera"
                )
    
            self.Bind(wx.EVT_TOOL,
                      self.OnAcquireBlueFoxButton,
                      id=self.ID_AcquireBlueFoxButton)

            self.ID_SaveImageBluefox = wx.NewId()
            self.toolbar.AddLabelTool(self.ID_SaveImageBluefox,
                                      label='save image',
                                      bitmap=self.bitmap_save,
                                      shortHelp='save image')
            self.Bind(wx.EVT_TOOL, self.OnSaveImageBluefox, id=self.ID_SaveImageBluefox)
        
        if useSony:
            self.acquire_sony_button = self.toolbar.AddCheckLabelTool(
                self.ID_AcquireSonyButton,
                label="Acquire Sony",
                bitmap=self.bitmap_stop,
                shortHelp="Acquire",
                longHelp="acquire images"
                )
            self.Bind(wx.EVT_TOOL, self.OnAcquireSonyButton, id=self.ID_AcquireSonyButton)
            
            self.ID_SaveImageSony = wx.NewId()
            self.toolbar.AddLabelTool(self.ID_SaveImageSony,
                                      label='save image',
                                      bitmap=self.bitmap_save,
                                      shortHelp='save image')
            self.Bind(wx.EVT_TOOL, self.OnSaveImageSony, id=self.ID_SaveImageSony)

######AVT ----------- New AVT-section -------- added 09012015
        if useAVT:
            self.acquire_AVT_button = self.toolbar.AddCheckLabelTool(
                self.ID_AcquireAVTButton,
                label="Acquire AVT",
                bitmap=self.bitmap_stop,
                shortHelp="Acquire",
                longHelp="aquire images"
                )
    
            self.Bind(wx.EVT_TOOL,
                      self.OnAcquireAVTButton,
                      id=self.ID_AcquireAVTButton)
            
            #save image button
            #TODO: which image to save?
            self.ID_SaveImageAVT = wx.NewId()
            self.toolbar.AddLabelTool(self.ID_SaveImageAVT,
                                      label='save image',
                                      bitmap=self.bitmap_save,
                                      shortHelp='save image')
            self.Bind(wx.EVT_TOOL, self.OnSaveImageAVT, id=self.ID_SaveImageAVT)#### ATTENTION still bound to theta functions

###### ----------- End new section --------        

#### ---------- TEST SECTION
        self.ID_TestButton = wx.NewId()
        self.toolbar.AddCheckLabelTool(self.ID_TestButton,
                                       label="TESTY TEST",
                                       bitmap=self.bitmap_go,
                                       shortHelp="Testy testy test")
        self.Bind(wx.EVT_TOOL, self.OnTestButton, id=self.ID_TestButton)
        
        self.ID_TimingButton = wx.NewId()
        self.toolbar.AddCheckLabelTool(self.ID_TimingButton,
                                       label="Apply Timings",
                                       bitmap=self.bitmap_go,
                                       shortHelp="Timings will be written to camera")
        self.Bind(wx.EVT_TOOL, self.OnTimingButton, id=self.ID_TimingButton)
        
        self.ID_ArmButton = wx.NewId()
        self.toolbar.AddCheckLabelTool(self.ID_ArmButton,
                                       label="Arm Guppy",
                                       bitmap=self.bitmap_go,
                                       shortHelp="Calls arm_triggers")
        self.Bind(wx.EVT_TOOL, self.OnArmButton, id=self.ID_ArmButton)
        
        
        self.ID_OpenButton = wx.NewId()
        self.toolbar.AddCheckLabelTool(self.ID_OpenButton,
                                       label="Open Guppy",
                                       bitmap=self.bitmap_go,
                                       shortHelp="Opens Guppy")
        self.Bind(wx.EVT_TOOL, self.OnOpenButton, id=self.ID_OpenButton)
        
        self.ID_CloseButton = wx.NewId()
        self.toolbar.AddCheckLabelTool(self.ID_CloseButton,
                                       label="Close Guppy",
                                       bitmap=self.bitmap_go,
                                       shortHelp="Closes Guppy if still open")
        self.Bind(wx.EVT_TOOL, self.OnCloseButton, id=self.ID_CloseButton)
##### ---------- END TEST SECTION
        
        #fullscreen button
        self.ID_fullscreen = wx.NewId()
        self.toolbar.AddCheckLabelTool(self.ID_fullscreen,
                                       label="fullscreen",
                                       bitmap=self.bitmap_go,
                                       shortHelp="Fullscreen")
        self.Bind(wx.EVT_TOOL, self.OnFullscreenButton, id=self.ID_fullscreen)

 
        #finalize toolbar
        self.toolbar.Realize()
        self.manager.AddPane(self.toolbar,
                             wx.aui.AuiPaneInfo().
                             Name('toolbar').
                             ToolbarPane().Top().Row(1).Position(1))

        #status bar
        self.statusbar = wx.StatusBar(self.frame)
        self.statusbar.FieldsCount = 4
        self.statusbar.SetStatusWidths([50, 200, 150, - 1])
        self.frame.SetStatusBar(self.statusbar)

        self._status = ''

        #main panel
        self.mainpanel = wx.Panel(self.frame)
        self.mainpanel.SetBestFittingSize = wx.Size(400, 20)
        self.mainpanel.SetMinSize(wx.Size(100, 10))
        
        self.manager.AddPane(self.mainpanel,
                             wx.aui.AuiPaneInfo().
                             Name('Acquire').
                             CenterPane().
                             BestSize(wx.Size(600, 50))
                             )
                             
        ##Image displays
        size_recommended = wx.Size(300, 300)
    
        #absorption image
        if useTheta:
            self.imageA = ImagePanel.CamAbsImagePanel(self.frame)
            self.imageB = ImagePanel.CamAbsImagePanel(self.frame)
    
            
            self.manager.AddPane(self.imageA,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image A').
                                 Caption('Image A').
                                 Left().Position(0).Layer(1).
                                 MaximizeButton(1).
                                 BestSize(wx.Size(600, 300))
                                 )
            
            self.manager.AddPane(self.imageB,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image B').
                                 Caption('Image B').
                                 Left().Position(1).Layer(1).
                                 MaximizeButton(1).
                                 BestSize(wx.Size(600, 300))
                                 )
            #raw images
            
            self.image1a = ImagePanel.CamRawSisImagePanel(self.frame)
            self.image1b = ImagePanel.CamRawSisImagePanel(self.frame)
            self.manager.AddPane(self.image1a,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 1 A').
                                 Caption('Image 1 A').
                                 Left().Position(0).Layer(3).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
    
            self.manager.AddPane(self.image1b,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 1 B').
                                 Caption('Image 1 B').
                                 Left().Position(0).Layer(2).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
    
            self.image2a = ImagePanel.CamRawSisImagePanel(self.frame)
            self.image2b = ImagePanel.CamRawSisImagePanel(self.frame)
            self.manager.AddPane(self.image2a,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 2 A').
                                 Caption('Image 2 A').
                                 Left().Position(1).Layer(3).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
    
            self.manager.AddPane(self.image2b,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 2 B').
                                 Caption('Image 2 B').
                                 Left().Position(1).Layer(2).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
    
            self.image3a = ImagePanel.CamRawSisImagePanel(self.frame)
            self.image3b = ImagePanel.CamRawSisImagePanel(self.frame)
            self.manager.AddPane(self.image3a,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 3 A').
                                 Caption('Image 3 A').
                                 Left().Position(2).Layer(3).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
    
            self.manager.AddPane(self.image3b,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 3 B').
                                 Caption('Image 3 B').
                                 Left().Position(2).Layer(2).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
            #organize panels into lists
            self.image_panels_theta = [self.image1a,
                                       self.image1b,
                                       self.image2a,
                                       self.image2b,
                                       self.image3a,
                                       self.image3b,
                                       self.imageA,
                                       self.imageB]
        else:
            self.image_panels_theta = []
        
        if useBluefox:
            self.imageBluefoxA = ImagePanel.CamRawFoxImagePanel(self.frame)
            self.imageBluefoxB = ImagePanel.CamRawFoxImagePanel(self.frame)
            self.manager.AddPane(self.imageBluefoxA,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 0 A').
                                 Caption('Image BlueFOX A').
                                 Left().Position(3).Layer(3).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )

            self.manager.AddPane(self.imageBluefoxB,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image 0 B').
                                 Caption('Image BlueFOX B').
                                 Left().Position(3).Layer(2).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )

        
            self.image_panels_bluefox = [self.imageBluefoxA,
                                         self.imageBluefoxB, ]
        else:
            self.image_panels_bluefox = []
            
        if useSony:
            self.imageSonyA = ImagePanel.CamAbsImagePanel(self.frame)
                        
            self.manager.AddPane(self.imageSonyA,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image Sony A').
                                 Caption('Image Sony A').
                                 Left().Position(0).Layer(1).
                                 MaximizeButton(1).
                                 BestSize(wx.Size(600, 300))
                                 )
            
            #raw images
            size_recommended = wx.Size(300, 300)
    
            self.imageSony1 = ImagePanel.CamRawFoxImagePanel(self.frame)
            self.manager.AddPane(self.imageSony1,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image Sony 1').
                                 Caption('Image Sony 1').
                                 Left().Position(0).Layer(3).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
    
            self.imageSony2 = ImagePanel.CamRawFoxImagePanel(self.frame)
            self.manager.AddPane(self.imageSony2,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image Sony 2').
                                 Caption('Image 2 A').
                                 Left().Position(1).Layer(3).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
    
            self.imageSony3 = ImagePanel.CamRawFoxImagePanel(self.frame)
            self.manager.AddPane(self.imageSony3,
                                 wx.aui.AuiPaneInfo().
                                 Name('Image Sony 3').
                                 Caption('Image Sony 3').
                                 Left().Position(2).Layer(3).
                                 MaximizeButton(1).
                                 BestSize(size_recommended)
                                 )
            #organize panels into lists
            self.image_panels_sony = [self.imageSony1,
                                      self.imageSony2,
                                      self.imageSony3,
                                      self.imageSonyA,
                                      ]
        else:
            self.image_panels_sony = []
			
######AVT ----------- New AVT-section -------- added 15012015
        if useAVT:
            self.imageAVT = ImagePanel.CamAbsImagePanel(self.frame)
                        
            self.manager.AddPane(self.imageAVT,
                                 wx.aui.AuiPaneInfo().
                                 Name('Absorption/Live Image').
                                 Caption('Absorption/Live Image').
                                 Left().Position(0).Layer(1).
                                 MaximizeButton(1).
                                 BestSize(wx.Size(600, 300))
                                 )
            #if self.imaging_mode_AVT == 'absorption':
            self.imageAVT_foreground = ImagePanel.CamImagePanel(self.frame)
            self.imageAVT_background = ImagePanel.CamImagePanel(self.frame)

            self.manager.AddPane(self.imageAVT_foreground,wx.aui.AuiPaneInfo().Name('Foreground').Caption('Foreground Image').Right().Position(0).Layer(1).MaximizeButton(1).BestSize(wx.Size(400,400)))
            self.manager.AddPane(self.imageAVT_background,wx.aui.AuiPaneInfo().Name('Background').Caption('Background Image').Right().Position(1).Layer(1).MaximizeButton(1).BestSize(wx.Size(400,400)))
                #organize panels into lists
            self.image_panels_AVT = [self.imageAVT]
			
        else:
            self.image_panels_sony = []
######## ---------------------- End new section ------------------
								 
        #perspectives
        self.perspective_full = self.manager.SavePerspective()
    
        #shared markers
        self.marker_roi_theta = ImagePanel.RectMarker(140, 140, 300, 300,
                                                      linecolor=wx.NamedColour('Magenta'),
                                                      linestyle=wx.SOLID)
        self.markers_shared_theta = [
            self.marker_roi_theta,
            ImagePanel.CrossMarker(100, 100,
                                   linecolor=wx.NamedColour('Red'),
                                   linestyle=wx.LONG_DASH),
            ImagePanel.CrossMarker(120, 120,
                                   linecolor=wx.NamedColour('Cyan'),
                                   linestyle=wx.SHORT_DASH),
            ]
        self.set_shared_markers_theta()
        
        self.markers_shared_sony = [ImagePanel.RectMarker(100, 100, 200, 200,
                                                          linecolor = wx.NamedColour('Yellow'),
                                                          linestyle=wx.SOLID),
                                    ImagePanel.CrossMarker(150, 150,
                                                           linecolor = wx.NamedColour('Blue'),
                                                           linestyle = wx.SOLID)
                                    ]
        self.roi_sony = self.markers_shared_sony[0]
        self.set_shared_markers_sony()
        

        #shared statusbar
        for panel in self.image_panels:
            panel.statusbar.Hide()
            panel.statusbar = self.statusbar #TODO: ugly hijacking!
            
        #initialize
        
        #Setup bindings for Events created from acquire threads
        self.Bind(EVT_IMAGE_ACQUIRE_SINGLE_THETA, self.OnSingleImageAcquiredTheta)
        self.Bind(EVT_IMAGE_ACQUIRE_SINGLE_BLUEFOX, self.OnSingleImageAcquiredBluefox)
        self.Bind(EVT_IMAGE_ACQUIRE_SINGLE_SONY, self.OnSingleImageAcquiredSony)
        self.Bind(EVT_IMAGE_ACQUIRE_SINGLE_AVT, self.OnSingleImageAcquiredAVT)
		
		
        self.Bind(EVT_IMAGE_ACQUIRE_TRIPLE_THETA, self.OnTripleImageAcquiredTheta)
        self.Bind(EVT_IMAGE_ACQUIRE_TRIPLE_SONY, self.OnTripleImageAcquiredSony)
        self.Bind(EVT_IMAGE_ACQUIRE_TRIPLE_AVT, self.OnTripleImageAcquiredAVT)
        #status messages
        self.Bind(EVT_STATUS_MESSAGE, self.OnStatusMessage)

        #self.Bind(wx.EVT_CLOSE, self.onclose, self.frame)
        wx.EVT_CLOSE(self.frame, self.onclose) #TODO: why this?

        self.Bind(wx.EVT_IDLE, self.OnIdle)

        #statistics, used in OnImageAcquiredSingle
        #self._skipped = 0
        #self._acquired = 0
        #self._tic = time.clock()

        #finalize
        self.manager.Update()
        self.frame.Show(True)

        return True

    @property
    def image_panels(self):
        return self.image_panels_theta + self.image_panels_bluefox + self.image_panels_sony
    def OnTestButton(self, event):##### ATTENTION TODO remove this function
        print 'Acquire: AVT imaging mode', self.imaging_mode_AVT
        print 'Acquire: AVT exposure', self.timing_AVT.exposure
        print 'Acquire: AVT timing external', self.timing_AVT.external
        with closing(Guppy.open()):
            Guppy.diagnostics()
        print 'testbutton over'
        
    def OnTimingButton(self, event): ##### ATTENTION TODO move to its right place. Values remain on Guppy after closing and reopening Acquire. ATTENTION: crashes if integration set to value below 71
        print 'Acquire: timings are written to Guppy.'
        with closing(Guppy.open()):
            Guppy.set_timing(external = self.timing_AVT.external, integration = self.timing_AVT.exposure, repetition = self.timing_AVT.repetition)
        print 'Acquire: Timing Button done.'
    
    def OnArmButton(self,event):
        print 'Acquire: Let s arm the guppy.'
        print 'Acquire: Open Guppy.'
        Guppy.open()
        print 'Acquire: run arm_triggers'
        Guppy.arm_triggers()
        print 'Acquire: Arming done. TAKE CARE OF CLOSING GUPPY!!'
        
        print 'Acquire: Launch Threads'
        self.acquiring_AVT = True
        self.imgproducer_AVT = AcquireThreadAVTTriggerd(self,
													cam=Guppy,
													queue=self.imagequeue_AVT,
                                                    evt = AVTTriggerGivenEvent)
        
        # if self.imaging_mode_AVT == 'live':
        self.imgconsumer_AVT = ConsumerThreadAVTSingleImage(self, self.imagequeue_AVT)
        # if self.imaging_mode_AVT == 'absorption':
            # self.imgconsumer_AVT = ConsumerThreadAVTTripleImage(self, self.imagequeue_AVT)
        self.imgconsumer_AVT.start()
        self.imgproducer_AVT.start()
        print 'Acquire: Threads running, OnArmButton over.'
    def OnFireButton(self,event):
        
        print 'Acquire Fire Button: T -0.5' 
        time.sleep(0.5)
        try:
            Guppy.give_trigger()
            AVTTriggerGivenEvent.set()
        except:
            print 'Acquire Fire Button: TRIGGER FAILED'
            pass
        time.sleep(1)
        print 'Acquire Fire Button: All shutting down. T +1' 
        self.imgproducer_AVT.stop()
        self.imgconsumer_AVT.stop()
    def OnOpenButton(self,event):
        Guppy.open()
        print 'Acquire: Guppy opened.'
    def OnCloseButton(self,event):
        
        self.imgproducer_AVT.stop()
        self.imgconsumer_AVT.stop()
        Guppy.close()
        print 'Acquire: Guppy closed.' 
        
    def set_shared_markers_theta(self):
        for image in self.image_panels_theta:
            map(image.add_marker, self.markers_shared_theta)
            
    def clear_shared_markers_theta(self):
        for image in self.image_panels_theta:
            map(image.remove_marker, self.markers_shared_theta)
            
    def set_shared_markers_sony(self):
        for image in self.image_panels_sony:
            map(image.add_marker, self.markers_shared_sony)
        
    def OnFullscreenButton(self, event):
        if event.Checked():
            self.frame.ShowFullScreen(True,
                                      wx.FULLSCREEN_NOBORDER
                                      )
        else:
            self.frame.ShowFullScreen(False)

    def OnSaveImageTheta(self, event):
        #TODO: needs rework, which image to save?
        print "save image"
        imgA = self.image1a.imgview.get_camimage()
        imgB = self.image1b.imgview.get_camimage()
        readsis.write_raw_image(settings.imagefile, np.vstack((imgA, imgB)))
        wx.PostEvent(self, StatusMessageEvent(data='s'))
        
    def OnSaveImageBluefox(self, event):
        print "save image"
        imgA = self.imageBluefoxA.imgview.get_camimage()
        readsis.write_raw_image(settings.imagefile, np.vstack((imgA, imgA)))
        wx.PostEvent(self, StatusMessageEvent(data='s'))
    
    def OnSaveImageSony(self, event):
        print "save image"
        imgA = self.imageSony1.imgview.get_camimage()
        readsis.write_raw_image(settings.imagefile, np.vstack((imgA, imgA)))
        wx.PostEvent(self, StatusMessageEvent(data='s'))
    def OnSaveImageAVT(self, event):
        # Need to add viewers for each image used in aborption. For now, this just saves the image displayed in the viewer
        print "save image"
        img = self.imageAVT.imgview.get_camimage()
        if self.imaging_mode_AVT == 'absorption':
                img_fore = self.imageAVT_foreground.imgview.get_camimage()
                img_back = self.imageAVT_background.imgview.get_camimage()
                PngWriter(settings.absorbfile, img, bitdepth = 8)
                PngWriter(settings.forefile, img_fore, bitdepth = 8)
                PngWriter(settings.backfile, img_back, bitdepth = 8)
        else:
                PngWriter(settings.imagefile, img,  bitdepth = 8)
    def OnIdle(self, event):
        self.busy = 0

    def OnSingleImageAcquiredTheta(self, event):

        if event.img is not None:
            #cut image into halves
            h, w = event.img.shape
            img1 = event.img[0:h / 2, :]
            img2 = event.img[h / 2: - 1, :]

            #avoid deadlock if too many images to process
            if self.Pending():
                self.busy += 1
            else:
                self.busy = 0
                
            if self.busy > 3:
                print "I am busy, skip displaying"
                self.show_status_message('.')
            else:
                self.image1a.show_image(img1, description="image #%d" % event.imgnr)
                self.image1b.show_image(img2, description="image #%d" % event.imgnr)
######AVT ----------- New AVT-section -------- added 15012015            
    def OnSingleImageAcquiredAVT(self, event):
        if not self.Pending():
            self.imageAVT.show_image(event.img, description="image #%d" % event.imgnr) ### CRASH at this point
######## ---------------------- End new section ------------------
    def OnSingleImageAcquiredBluefox(self, event):
        """Display image if not too busy"""
        if not self.Pending(): #TODO: implement like Theta, use self.busy
            self.imageBluefoxA.show_image(event.img, description="image #%d" % event.imgnr)
        
        #self._acquired += 1
        #TODO: implement like for Theta
        
        #else:
        #    self._skipped += 1
        #
        #if self._acquired % 10 == 0:
        #    print "%.1f"%(10/(time.clock() - self._tic)), "fps", self._skipped, "skipped"
        #    self._skipped = 0
        #    self._tic = time.clock()
        
    def OnSingleImageAcquiredSony(self, event):
        if event.img is not None:   
        #avoid deadlock if too many images to process
            if self.Pending():
                self.busy += 1
            else:
                self.busy = 0
                
            if self.busy > 4:
                #print "I am busy, skip displaying"
                self.show_status_message('.')
            else:
                self.imageSony1.show_image(event.img, description="image #%d" % event.imgnr)
                
                img = event.img
                l,r,b,t = (self.roi_sony.x1,
                           self.roi_sony.x2,
                           self.roi_sony.y1,
                           self.roi_sony.y2)
                imgroi = img[b:t, l:r]
                imgroisum = imgroi.sum()
                imgroisumscaled = 100.0/255*float(imgroisum)/abs( (r-l)*(t-b) )
                self.statusbar.SetStatusText('%.4f'%imgroisumscaled,0)

    def OnTripleImageAcquiredTheta(self, event):
        #print "TripleImageAcquired...", event.data['image_numbers']
        img1a, img1b = self.imagesplit(event.data['image1'])
        img2a, img2b = self.imagesplit(event.data['image2'])
        img3a, img3b = self.imagesplit(event.data['image3'])
        img_a, img_b = self.imagesplit(event.data['absorption_image'])

        self.image1a.show_image(img1a)
        self.image1b.show_image(img1b)

        self.image2a.show_image(img2a)
        self.image2b.show_image(img2b)

        self.image3a.show_image(img3a)
        self.image3b.show_image(img3b)
        
        self.imageA.show_image(img_a, description='')
        self.imageB.show_image(img_b, description='')

        
##### ----------- New AVT - Section ---------------- Added on 19022015
    def OnTripleImageAcquiredAVT(self, event):
        #print "TripleImageAcquired...", event.data['image_numbers']
        img1 = event.data['image1']
        img2 = event.data['image2']
        img3 = event.data['image3']
        imgA = event.data['absorption_image']
        
        if not self.Pending():
            # self.imageSony1.show_image(img1)
            # self.imageSony2.show_image(img2)
            # self.imageSony3.show_image(img3)
            self.imageAVT.show_image(imgA)
            self.imageAVT_foreground.show_image(img1)
            self.imageAVT_background.show_image(img2)        
        
##### ----------- End New Section ---------------- Added on 19022015
        
    def OnTripleImageAcquiredSony(self, event):
        img1 = event.data['image1']
        img2 = event.data['image2']
        img3 = event.data['image3']
        imgA = event.data['absorption_image']
        
        if not self.Pending():
            self.imageSony1.show_image(img1)
            self.imageSony2.show_image(img2)
            self.imageSony3.show_image(img3)
            self.imageSonyA.show_image(imgA)

    def OnStatusMessage(self, event):
        message = event.data
        self.show_status_message(message)
        
    def show_status_message(self, message=None):
        if message is None:
            self._status = ''
        else:
            self._status += message
            
        self._status = self._status[ - 6:]
        self.statusbar.SetStatusText(self._status, 3)

    def imagesplit(self, img):
        h, w = img.shape
        return img[:h/2],img[h/2:]
        
    def do_toggle_button(self, state, id):
        """Change visual appearance of toolbar buttons."""

        self.toolbar.ToggleTool(id, state)
        self.toolbar.SetToolNormalBitmap(id,
                                         self.bitmap_go if state else
                                         self.bitmap_stop)

######AVT ----------- New AVT-section -------- added 15012015
    def OnAcquireAVTButton(self, event):
        if event.Checked():
            self.start_acquisition_AVT()
        else:
            self.stop_acquisition_AVT()

        self.do_toggle_button(event.Checked(), self.ID_AcquireAVTButton)
######## ---------------------- End new section ------------------	
	
    def OnAcquireThetaButton(self, event):
        if event.Checked():
            self.start_acquisition_theta()
        else:
            self.stop_acquisition_theta()

        self.do_toggle_button(event.Checked(), self.ID_AcquireThetaButton)

    def OnAcquireBlueFoxButton(self, event):
        if event.Checked():
            self.start_acquisition_bluefox()
        else:
            self.stop_acquisition_bluefox()

        self.do_toggle_button(event.Checked(), self.ID_AcquireBlueFoxButton)

    def OnAcquireSonyButton(self, event):
        if event.Checked():
            self.start_acquisition_sony()
        else:
            self.stop_acquisition_sony()
        
        self.do_toggle_button(event.Checked(), self.ID_AcquireSonyButton)
######AVT ----------- New AVT-section -------- added 15012015
    def start_acquisition_AVT(self):
        self.acquiring_AVT = True
        self.imgproducer_AVT = AcquireThreadAVT(self,
													cam=Guppy,
													queue=self.imagequeue_AVT)
        
        if self.imaging_mode_AVT == 'live':
            self.imgconsumer_AVT = ConsumerThreadAVTSingleImage(self, self.imagequeue_AVT)
        if self.imaging_mode_AVT == 'absorption':
            self.imgconsumer_AVT = ConsumerThreadAVTTripleImage(self, self.imagequeue_AVT)
        self.imgconsumer_AVT.start()
        self.imgproducer_AVT.start()
	
    def stop_acquisition_AVT(self):
        
        self.imgproducer_AVT.stop()
        self.imgconsumer_AVT.stop()

        self.imgproducer_AVT.join(2)
        self.imgconsumer_AVT.join(2)

        if self.imgproducer_AVT.isAlive():
            print "could not stop AVT producer thread."
        if self.imgconsumer_AVT.isAlive():
            print "could not stop AVT consumer threads!"

        self.acquiring_AVT = False
	
######## ---------------------- End new section ------------------
    def start_acquisition_theta(self):
        self.acquiring_theta = True
        self.menu.EnableTop(self.ID_TimingTheta, False)
        
        self.imgproducer_theta = AcquireThreadTheta(self,
                                                       camtheta,
                                                       self.imagequeue_theta
                                                       )

        if self.imaging_mode_theta == 'live':
            self.imgconsumer_theta = ConsumerThreadThetaSingleImage(self, self.imagequeue_theta)
        elif self.imaging_mode_theta == 'absorption':
            self.imgconsumer_theta = ConsumerThreadThetaTripleImage(self, self.imagequeue_theta)
        
        self.imgconsumer_theta.start()
        self.imgproducer_theta.start()

    def start_acquisition_bluefox(self):
        self.acquiring_bluefox = True
        self.imgproducer_bluefox = AcquireThreadBluefox(self,
                                                             cam=IMPACT.Cam(),
                                                             queue=self.imagequeue_bluefox)
        self.imgconsumer_bluefox = ConsumerThreadBluefoxSingleImage(self, self.imagequeue_bluefox)
        self.imgconsumer_bluefox.start()
        self.imgproducer_bluefox.start()
        
    def start_acquisition_sony(self):
        self.acquiring_sony = True
        if self.imaging_mode_sony == 'live':
            nimg = 1
        elif self.imaging_mode_sony == 'absorption':
            nimg = 3
            
        self.imgproducer_sony = AcquireThreadSony(self,
                                                  cam=VCam.VCam(),
                                                  queue=self.imagequeue_sony,
                                                  configfile = self.configfile_sony,
                                                  nimg=nimg)
        self.imgconsumer_sony = ConsumerThreadSony(self, self.imagequeue_sony)
        
        self.imgproducer_sony.start()
        self.imgconsumer_sony.start()

    def stop_acquisition_theta(self):
        self.imgproducer_theta.stop()
        self.imgconsumer_theta.stop()
        
        self.imgproducer_theta.join(6)
        self.imgconsumer_theta.join(2)
            
        if self.imgproducer_theta.isAlive() or self.imgconsumer_theta.isAlive():
            print "could not stop theta acquisition threads!", threading.enumerate()

        self.acquiring_theta = False
        self.menu.EnableTop(self.ID_TimingTheta, True)

    def stop_acquisition_bluefox(self):
        self.imgproducer_bluefox.stop()
        self.imgconsumer_bluefox.stop()

        self.imgproducer_bluefox.join(2)
        self.imgconsumer_bluefox.join(2)

        if self.imgproducer_bluefox.isAlive() \
           or self.imgconsumer_bluefox.isAlive():
            print "could not stop bluefox acquisition threads!"
		
        self.acquiring_bluefox = False

    def stop_acquisition_sony(self):
        self.imgproducer_sony.stop()
        self.imgconsumer_sony.stop()
        
        self.imgproducer_sony.join(2)
        self.imgconsumer_sony.join(2)
        
        if self.imgproducer_sony.isAlive() or self.imgconsumer_sony.isAlive():
            print "could not stop sony acquisition threads!"
        
        self.acquiring_sony = False
        
    def OnSetTiming(self, event):
        if event.Id == self.ID_TimingAVTExternal:####AVT
            self.timing_AVT.external = True
            
        if event.Id == self.ID_TimingAVTInternal:####AVT
            self.timing_AVT.external = False
            
        if event.Id == self.ID_TimingThetaExternal:
            self.timing_theta.external = True
            
        if event.Id == self.ID_TimingThetaInternal:
            self.timing_theta.external = False
            
        if event.Id == self.ID_TimingBlueFoxExternal:
            self.timing_bluefox.external = True
            
        if event.Id == self.ID_TimingBlueFoxInternal:
            self.timing_bluefox_external = False
            
        if event.Id == self.ID_TimingSonyExternal:
            self.timing_sony.external = True
            
        if event.Id == self.ID_TimingSonyInternal:
            self.timing_sony.external = False
            
        if event.Id == self.ID_TimingAVTSettings:
            dialog = self.create_timing_dialog(exposure=self.timing_AVT.exposure,
                                               repetition=self.timing_AVT.repetition,trigger = self.timing_AVT.trigger)
            res = dialog.ShowModal()
            if res == wx.ID_OK:
                exp, rep, trig = dialog.GetResults()
                self.timing_AVT.exposure, self.timing_AVT.repetition, self.timing_AVT.trigger = exp, rep, trig
               
            dialog.Destroy()

        if event.Id == self.ID_TimingThetaSettings:
            dialog = self.create_timing_dialog(exposure=self.timing_theta.exposure,
                                               repetition=self.timing_theta.repetition)
            res = dialog.ShowModal()
            if res == wx.ID_OK:
                exp, rep = dialog.GetResults()
                self.timing_theta.exposure, self.timing_theta.repetition = exp, rep
            dialog.Destroy()

        if event.Id == self.ID_TimingBlueFoxSettings:
            dialog = self.create_timing_dialog(exposure=self.timing_bluefox.exposure)
            res = dialog.ShowModal()
            if res == wx.ID_OK:
                self.timing_bluefox.exposure = dialog.GetResults()
            dialog.Destroy()
            
        if event.Id == self.ID_TimingSonySettings:
            dialog = self.create_timing_dialog(exposure=self.timing_sony.exposure)
            res = dialog.ShowModal()
            if res == wx.ID_OK:
                self.timing_sony.exposure = dialog.GetResults()
            dialog.Destroy()

    def OnSettingsSave(self, event):
        import shelve

        setting = shelve.open(os.path.join(settings.basedir,
                                            'settings/settings_acquire'))
        try:
            #window layout
            setting['perspective'] = self.manager.SavePerspective()

            #markers
            setting['markers_shared_theta'] = self.markers_shared_theta

            #get nonshared markers
            self.clear_shared_markers_theta() #remove shared
            markers_theta = []
            for panel in self.image_panels_theta: #collect nonshared
                markers_theta.append(panel._markers.copy())
            self.set_shared_markers_theta() #restore shared
            setting['markers_nonshared_theta'] = markers_theta

            setting['zoomsteps'] = [i.zoomstep for i in self.image_panels]
            setting['contrast_choices'] = [i.contrast_choice for i in self.image_panels]
            setting['colormap_choices'] = [i.colormap_choice for i in self.image_panels]
            
            setting['timing_theta']   = self.timing_theta
            setting['timing_bluefox'] = self.timing_bluefox
            setting['timing_sony']    = self.timing_sony
            

        finally:
            setting.close()
        print "settings saved"
        self.frame.Refresh()

    def OnSettingsLoad(self, event):
        import shelve

        setting = shelve.open(os.path.join(settings.basedir,
                                            'settings/settings_acquire'))
        try:
            self.manager.LoadPerspective(setting['perspective'])

            markers_shared = setting['markers_shared_theta']
            markers_theta = setting['markers_nonshared_theta']
            zoomsteps = setting['zoomsteps']
            colormap_choices = setting['colormap_choices']
            contrast_choices = setting['contrast_choices']
            
        finally:
            setting.close()

        #remove shared markers from image panels    
        self.clear_shared_markers_theta()
        self.markers_shared_theta = markers_shared

        for k, markers in enumerate(markers_theta):
            panel = self.image_panels_theta[k]

            #remove remaining markers from panels (assume: they are nonshared)
            for m in panel._markers.copy():
                panel.remove_marker(m)

            #add loaded markers
            for m in markers:
                panel.add_marker(m)
        
        #restore shared markers
        self.set_shared_markers_theta()

        #restore scalings, contrast, colormap
        for k, panel in enumerate(self.image_panels):
            panel.zoomstep = zoomsteps[k]
            panel.colormap_choice = colormap_choices[k]
            panel.contrast_choice = contrast_choices[k]
            
        self.frame.Refresh()
        
        print "settings loaded"

    def OnMenuShowAll(self, event):
        self.manager.LoadPerspective(self.perspective_full)

        
    def OnMenuImagingModeTheta(self, event):
        if event.Id == self.ID_ImagingModeTheta_Live:
            print "Live imaging Theta"
            self.imaging_mode_theta = 'live'

        elif event.Id == self.ID_ImagingModeTheta_Absorption:
            print "Absorption imaging Theta"
            self.imaging_mode_theta = 'absorption'

        elif event.Id == self.ID_ImagingTheta_RemoveBackground:
            self.imaging_theta_remove_background = event.IsChecked()

        elif event.Id == self.ID_ImagingTheta_UseROI:
            self.imaging_theta_useROI = event.IsChecked()
####AVT ------------New AVT-section --------------- 19012015
    def OnMenuImagingModeAVT(self, event):
        if event.Id == self.ID_ImagingModeAVT_Live:
            self.imaging_mode_AVT = 'live'
            print 'set to',self.imaging_mode_AVT
        elif event.Id == self.ID_ImagingModeAVT_Absorption:
            self.imaging_mode_AVT = 'absorption'
            print 'set to',self.imaging_mode_AVT
#### ---------- End new section ----------------			
    def OnMenuImagingModeSony(self, event):
        if event.Id == self.ID_ImagingModeSony_Live:
            self.imaging_mode_sony = 'live'
        elif event.Id == self.ID_ImagingModeSony_Absorption:
            self.imaging_mode_sony = 'absorption'

    def OnMenuCamSony(self, event):
        if event.Id == self.ID_SonyCam1:
            self.configfile_sony = configfiles_sony[0]
        elif event.Id == self.ID_SonyCam2:
            self.configfile_sony = configfiles_sony[1]

    def OnMenuHelp(self, event):
        pass
    
    def OnMenuAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = 'Acquire'
        info.Version = '$Id: acquire.py 435 2009-02-01 13:08:46Z Gregor $'
        info.Description = """
        Have fun and take images!"""
        info.Copyright = "(c) 2008 Gregor Thalhammer"
        info.Icon = wx.Icon(os.path.join(settings.bitmappath, 'acquire_splash.png'),
                            wx.BITMAP_TYPE_ANY)

        wx.AboutBox(info)

    def create_timing_dialog(self, exposure, repetition=None,trigger=False):
        dialog = TimingDialog(self.frame, - 1,
                              "Set Timing",
                              exposure=exposure,
                              repetition=repetition,trigger=trigger
                              )
        dialog.CenterOnScreen()
        return dialog

    def OnExit(self):
        pass

    def stop_threads(self):
        print "shutting down"
        if self.acquiring_theta:
            print "stopping threads theta"
            self.stop_acquisition_theta()
        if self.acquiring_bluefox:
            print "stopping threads bluefox"
            self.stop_acquisition_bluefox()
        if self.acquiring_AVT:
            print "stopping threads AVT"
            self.stop_acquisition_AVT()
        print "finished"

        
        
    def onclose(self, event):
        print "onclose"

        self.stop_threads()
        #self.ToggleGoButton(False)
        print "threads stopped"
            
        #if event.CanVeto():
        #    print "you are not serious"
        #    event.Veto()
        #else:
        #    print "I am convinced, I have to go!"
        #    self.frame.Destroy()
        self.frame.Destroy()

class TimingDialog(wx.Dialog):
    def __init__(self, parent, ID, title,
                 size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE,
                 exposure=100,
                 repetition=600,
                 repetition_min=600, trigger = False):
        
        self.repetition_shown = (repetition is not None)
        
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, - 1, "Set camera timings")
        sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        #entry exposure time
        #TODO: enable float entry
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, - 1, "Exposure time (µs)")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        entry = wx.SpinCtrl(self, - 1, "", (50, - 1))
        #entry = wx.SpinButton(self, -1, style = wx.SP_VERTICAL)
        entry.SetRange(0, 1000000)
        entry.SetValue(int(exposure*1000))
        box.Add(entry, 1, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.exposure_time_entry = entry

        if self.repetition_shown:
            #entry repetition time
            box = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, - 1, "Repetition time (ms)")
            box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            entry = wx.SpinCtrl(self, - 1, "", (50, - 1))
            entry.SetRange(repetition_min, 5000)
            entry.SetValue(repetition)
            box.Add(entry, 1, wx.ALIGN_CENTRE | wx.ALL, 5)
            sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
            self.repetition_time_entry = entry

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self,-1,"Trigger Mode")
        box.Add(label,0,wx.ALIGN_CENTRE | wx.ALL,5)
        entry = wx.CheckBox(self,-1,"")
        entry.SetValue(trigger)
        box.Add(entry,1,wx.ALIGN_CENTRE | wx.ALL,5)
        sizer.Add(box,0,wx.GROW | wx.ALIGN_CENTRE_VERTICAL | wx.ALL,5)
        self.trigger_mode_entry = entry

        line = wx.StaticLine(self, - 1, size=(20, - 1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        btn = wx.Button(self, wx.ID_OK)
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def GetResults(self):
        if self.repetition_shown:
            return (self.exposure_time_entry.Value / 1000.0,
                    self.repetition_time_entry.Value, self.trigger_mode_entry.Value)
        else:
            return (self.exposure_time_entry.Value / 1000.0, self.trigger_mode_entry.Value)

def find_background(img, r = 10.0):

    bins = np.linspace(0, 500, 501)
    db   = np.mean(np.diff(bins)) #width of bins

    #calculate histogram
    h, b = np.histogram(img, bins-0.5*db, new = True)
    
    mx = h.argmax() #find peak of histogram, take this as first estimate
    sel = slice(max(0, mx-int(r/db)), min(len(h),mx+int(r/db))) #select range around maximum

    nrm = sum(h[sel]) #norm of selected part
    m = sum(h[sel]*b[sel])/nrm #calculate mean value
    s = np.sqrt(sum((h[sel]*((b[sel]-m)**2)))/nrm) #and standard deviation

    return m, s
    
    
def run_acquire():
    gui = ImgAcquireApp(redirect=False)
    gui.MainLoop()
    return gui

if __name__ == '__main__':
	VimbAcq.open()  ####AVT
	Guppy = AVTcam.AVTcam(VimbAcq.ID(),VimbAcq) ###AVT
	gui = run_acquire()
	VimbAcq.close() ####AVT
