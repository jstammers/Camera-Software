#!/usr/bin/python
"""Needs methods: 
.snap() --> captures image on trigger, puts image to queue ; 
.open() 
.close() 
.set_timing() ; which also sets trigger mode etc. """
from pymba import * 
import numpy as np
import matplotlib.pyplot as plt
import time
import sys#

# from contextlib import closing ## pretty sure we don't need this, because already imported in acquire.

class VimbAcq(Vimba):  # this class only defines open / close methods to use ' with closing ' 
	
# 'with closing(thing)' calls 'thing.close()' in the end. 
# Want to use with closing(vim.open()) later. So vim.open() has to return vim.
	def open(self):  
		self.startup()
		print 'Opened Vimba'
		return self 
		
	def close(self):
		self.shutdown()
		print 'Closed Vimba'
		
	def ID(self):
		id = self.getCameraIds()
		if id is None:
			print 'No Camera found'
			id[0] = 'NotFound'
		else:
			pass
		return id[0]

class AVTcam(object): # only works inside VimbAcq.open() / .close() , 
	
	def __init__(self, cameraID, vimba):
		self.camera0 = vimba.getCamera(cameraID)
		# if cameraID is not None:      ##### TODO: Proper Exception Handling
			# try:
				# self.camera0 = vimba.getCamera(cameraID)
			# except:
				# print 'Weird Error'
				
		# else:
			# print 'no camera found' 

	def open(self): # see comments on vim.open() for cam.open() ; Prepare camera already here for triggered Acquisition			
		self.camera0.openCamera()
		print 'AVTcam: Guppy open'
		# self.camera0.ExposureMode = 'TriggerWidth' ######### ATTENTION uncomment these lines for final version.
		print 'AVTcam: ExposureMode set on ', self.camera0.ExposureMode
		# self.camera0.TriggerSelector = 'ExposureActive'
		print 'AVTcam: TriggerSelector set on ', self.camera0.TriggerSelector
		# self.camera0.AcquisitionMode = 'SingleFrame'
		print 'AVTcam: AcquisitionMode set on', self.camera0.AcquisitionMode
		return self
		
	def close(self):
		self.camera0.closeCamera()
		print 'Guppy closed'
	
	def set_timing(self, integration = 40, repetition = 60):
		expTime = integration*1000 ### TODO: Make sure that integer
		frameRate = 1000/60 ### TODO: Make sure that integer
		if self.camera0.ExposureMode is not 'Timed': ##### TODO: Re-check properly for modes (Timing vs trigger!)
			print 'AVTcam: Cam in triggered mode. No use setting timings.'
		else:
			self.camera0.ExposureTime = expTime ##### TODO: Double check definitions
			self.camera0.AcquisitionFrameRate = frameRate
	
	def SingleImagePlot(self):  # make and plot image.
		self.camera0.AcquisitionMode = 'SingleFrame'
		print 'changed Acq mode to singleframe'
		frame0 = self.camera0.getFrame()
		frame0.announceFrame()
		self.camera0.startCapture()
		frame0.queueFrameCapture() 
		self.camera0.runFeatureCommand('AcquisitionStart')
		time.sleep(1.1/10.0)
		self.camera0.runFeatureCommand('AcquisitionStop')
		frame0.waitFrameCapture()
		imgData = np.ndarray(buffer=frame0.getBufferByteData(),
							dtype=np.uint8,
							shape=(frame0.height,
									frame0.width))
									# 1))
		print len(imgData)
		# imgData = frame0.getBufferByteData()
		self.camera0.endCapture()
		self.camera0.revokeAllFrames()
		#self.close()
		print 'cam closed, vimba still open!'
		plt.imshow(imgData)
		plt.show() ### instead of printing later. Works this way.
		print 'type plt.show, if not plotted' ### instead of the plt.show() line above. Crashes however
	
	def SingleImage(self):  # image blurred, when plotted with matplotlib, probably some
                         # numpy-array-print problem.
		self.camera0.AcquisitionMode = 'SingleFrame'
		print 'changed Acq mode to singleframe'
		frame0 = self.camera0.getFrame()
		frame0.announceFrame()
		self.camera0.startCapture()
		frame0.queueFrameCapture() 
		self.camera0.runFeatureCommand('AcquisitionStart')
		time.sleep(1.1/10.0) 
		self.camera0.runFeatureCommand('AcquisitionStop')
		frame0.waitFrameCapture()
		imgData = np.ndarray(buffer=frame0.getBufferByteData(),
							dtype=np.uint8,
							shape=(frame0.height,
									frame0.width))	#####BEST VERSION 19012015
									# 1))
		
		self.camera0.flushCaptureQueue()
		self.camera0.endCapture()
		self.camera0.revokeAllFrames()
		print 'AVTcam: SingleImage done, returning data'
		#self.camera0.close()
		newImage = np.ndarray(shape = (frame0.height,frame0.width))
		for i in range(frame0.height):
				for j in range(frame0.width):
						newImage[i][j]=imgData[i][j]
		print 'Added something else'
		return newImage
        

	def ContinuousStream(self):
		#This needs to be able to continuously return images to be put in the queue by the AVT live AcquireThread
		self.camera0.AcquisitionMode='ContinuousStream'
		print 'changed Acq mode to continuousstream'
		frame0 = self.camera0.getFrame()
		frame0.announceFrame()
		self.camera0.startCapture()
		framecount = 0
		droppedFrames = []

		while 1:
			try:
				frame0.queueFrameCapture()
				success = True
			except:
				droppedFrames.append(framecount)
				success = False
			camera0.runFeatureCommand('AcquisitionStart')
			camera0.runFeatureCommand('AcquisitionStop')
			frame0.waitFrameCapture(1000)

# Crashes when user tries to print off matrix values. (only if function value is passed to a variable.) 

def set_timing(self,exposure):
    ###
	# self.camera0.ExposureTime = exposure

def set_trigger_mode(self,mode):
	# self.camera0.TriggerMode = mode