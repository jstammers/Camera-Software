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
import sys

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

	def open(self, mode = 'absorption',pixel=np.uint8): # see comments on vim.open() for cam.open() ; Prepare camera already here for triggered Acquisition			
		self.camera0.openCamera()
		print 'AVTcam: Guppy open'
		if mode == 'absorption':
			self.camera0.ExposureMode = 'TriggerWidth'
			self.camera0.TriggerSelector = 'ExposureActive'
			self.camera0.AcquisitionMode = 'SingleFrame'
			self.camera0.TriggerActivation = 'LevelHigh'
			if pixel == np.uint8:
			    self.camera0.PixelFormat = 'Mono8'
			elif pixel == np.uint16:
			    self.camera0.PixelFormat = 'Mono16'
			print 'AVTcam: Camera set on Absorption mode'
		elif mode == 'live':
			self.camera0.ExposureMode = 'Timed'
			self.camera0.TriggerMode = 'On'
			self.camera0.AcquisitionMode = 'SingleFrame'
			if pixel == np.uint8:
			    self.camera0.PixelFormat = 'Mono8'
			elif pixel == np.uint16:
			    self.camera0.PixelFormat = 'Mono16'
			print 'AVTcam: Camera set on Live mode'
		else:
			print 'AVTcam: Invalid mode specified'
		print'AVTcam: Pixel Mode set to', self.camera0.PixelFormat
		return self
		
	def close(self):
		self.camera0.closeCamera()
		print 'Guppy closed'

	def set_TriggerMode(self,gated=True):
		if not gated:
			self.camera0.TriggerMode = 'On'
			self.camera0.TriggerActivation = 'RisingEdge'
			self.camera0.ExposureMode = 'Timed'
			print 'AVTCam: Switched to timed trigger mode'
		else:
			self.camera0.ExposureMode = 'TriggerWidth'
			if self.camera0.TriggerMode == 'Off':
				self.camera0.TriggerMode = 'On'

			self.camera0.TriggerActivation = 'LevelHigh'
			self.camera0.TriggerSelector = 'ExposureActive'



	def set_AutoMode(self,exposure=40):
		self.camera0.ExposureMode = 'Timed'
		self.camera0.ExposureTime = int(round(exposure*1000))
		if self.camera0.TriggerMode == 'On':
			self.camera0.TriggerMode = 'Off'
		print 'AVTCam: Switched to auto mode'


	def set_timing(self, integration = 40, repetition = 60, trigger = False,gated=True):
		exposure_time_us = int(round(integration*1000)) ### TODO: Make sure that integer
		repetition_time_us = int(round(repetition)) ### TODO: Make sure that integer
		if trigger:
			self.set_TriggerMode(gated)
		else:
			self.set_AutoMode()
		if not gated:
			self.camera0.ExposureTime = exposure_time_us ##### TODO: Double check definitions


	def getImageDepth(self):
		if self.camera0.PixelFormat == 'Mono8':
			return np.uint8
		elif self.camera0.PixelFormat == 'Mono16':
			return np.uint16
	

	def SingleImage(self,wait=10000000): 
        #For some reason, the trigger mode needs both waits, but the live stream will not acquire if it waits before the queue. The simplest solution is to hard code a wait time based on the acquisition mode
		self.camera0.AcquisitionMode = 'SingleFrame'
		frame0 = self.camera0.getFrame()
		frame0.announceFrame()
		self.camera0.startCapture()
		frame0.queueFrameCapture() 
		self.camera0.runFeatureCommand('AcquisitionStart')
		frame0.waitFrameCapture(110)
		frame0.queueFrameCapture()
        #This next wait needs to be commented for the live acquisition and very long for absorption
		frame0.waitFrameCapture(wait)

		imgData = np.ndarray(buffer=frame0.getBufferByteData(),
							dtype=self.getImageDepth(),
							shape=(frame0.height,
									frame0.width))	#####BEST VERSION 19012015
									# 1))
		

			
		self.camera0.flushCaptureQueue()

		self.camera0.revokeAllFrames()
		self.camera0.runFeatureCommand('AcquisitionStop')
		self.camera0.endCapture()
		print 'AVTcam: SingleImage done, returning data'
		newImage = np.ndarray(shape = (frame0.height,frame0.width))
		newImage = np.copy(imgData)
		return newImage
        