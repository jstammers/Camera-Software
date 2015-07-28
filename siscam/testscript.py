#!/usr/bin/python

from AVTcam import *
from contextlib import closing
import matplotlib.pyplot as plt
import numpy as np


vim = VimbAcq()
vim.open()
cam = AVTcam(vim.ID(),vim)
cam.open()

##with closing(cam.open()):
##	print 'try setting to SingleFrame'
##	cam.camera0.AcquisitionMode = 'SingleFrame'
##	print 'AcqMode = ',cam.camera0.AcquisitionMode
##vim.close()
##print 'Vimba closed, end of program'

# def spam_image():
	# print 'Start imaging'
	# frame0 = cam.camera0.getFrame()
	# frame1 = cam.camera0.getFrame()
	# frame2 = cam.camera0.getFrame()

	# frame0.announceFrame()
	# frame1.announceFrame()
	# frame2.announceFrame()
	# print 'Frames ready. Starting Capture.'

	# cam.camera0.startCapture()

	# frame0.queueFrameCapture() 
	# cam.camera0.runFeatureCommand('AcquisitionStart')
	# time.sleep(1)
	# cam.camera0.runFeatureCommand('AcquisitionStop')
	# frame0.waitFrameCapture()
	# img0 = np.ndarray(buffer=frame0.getBufferByteData(),
						# dtype=np.uint8,
						# shape=(frame0.height,
							# frame0.width,))

	# print 'img0 Acquired'

	# frame1.queueFrameCapture() 
	# cam.camera0.runFeatureCommand('AcquisitionStart')
	# time.sleep(1)
	# cam.camera0.runFeatureCommand('AcquisitionStop')
	# frame1.waitFrameCapture()
	# img1 = np.ndarray(buffer=frame1.getBufferByteData(),
						# dtype=np.uint8,
						# shape=(frame1.height,
							# frame1.width,))

	# print 'img1 Acquired'

	# frame2.queueFrameCapture() 
	# cam.camera0.runFeatureCommand('AcquisitionStart')
	# time.sleep(1)
	# cam.camera0.runFeatureCommand('AcquisitionStop')
	# frame2.waitFrameCapture()
	# img2 = np.ndarray(buffer=frame2.getBufferByteData(),
						# dtype=np.uint8,
						# shape=(frame2.height,
							# frame2.width,))

	# print 'img2 Acquired'
							
	# cam.camera0.endCapture()
	# cam.camera0.revokeAllFrames()

	# print 'Capture terminated, Frames revoked. CAM STILL OPEN!!!'
	# return img0, img1, img2

# print 'Start imaging'
# frame0 = cam.camera0.getFrame()
# frame1 = cam.camera0.getFrame()
# frame2 = cam.camera0.getFrame()

# frame0.announceFrame()
# frame1.announceFrame()
# frame2.announceFrame()
# print 'Frames ready. Starting Capture.'

# cam.camera0.startCapture()

# frame0.queueFrameCapture() 
# cam.camera0.runFeatureCommand('AcquisitionStart')
# time.sleep(1)
# cam.camera0.runFeatureCommand('AcquisitionStop')
# frame0.waitFrameCapture()
# img0 = np.ndarray(buffer=frame0.getBufferByteData(),
					# dtype=np.uint8,
					# shape=(frame0.height,
						# frame0.width,))

# print 'img0 Acquired'

# frame1.queueFrameCapture() 
# cam.camera0.runFeatureCommand('AcquisitionStart')
# time.sleep(1)
# cam.camera0.runFeatureCommand('AcquisitionStop')
# frame1.waitFrameCapture()
# img1 = np.ndarray(buffer=frame1.getBufferByteData(),
					# dtype=np.uint8,
					# shape=(frame1.height,
						# frame1.width,))

# print 'img1 Acquired'

# frame2.queueFrameCapture() 
# cam.camera0.runFeatureCommand('AcquisitionStart')
# time.sleep(1)
# cam.camera0.runFeatureCommand('AcquisitionStop')
# frame2.waitFrameCapture()
# img2 = np.ndarray(buffer=frame2.getBufferByteData(),
					# dtype=np.uint8,
					# shape=(frame2.height,
						# frame2.width,))

# print 'img2 Acquired'
						
# cam.camera0.endCapture()
# cam.camera0.revokeAllFrames()

# print 'Capture terminated, Frames revoked. CAM STILL OPEN!!!'

# print 'Start imaging, once more!'
# frame3 = cam.camera0.getFrame()
# frame4 = cam.camera0.getFrame()
# frame5 = cam.camera0.getFrame()

# frame3.announceFrame()
# frame4.announceFrame()
# frame5.announceFrame()
# print 'Frames ready. Starting Capture.'

# cam.camera0.startCapture()

# frame3.queueFrameCapture() 
# cam.camera0.runFeatureCommand('AcquisitionStart')
# time.sleep(1)
# cam.camera0.runFeatureCommand('AcquisitionStop')
# frame3.waitFrameCapture()
# img3 = np.ndarray(buffer=frame3.getBufferByteData(),
					# dtype=np.uint8,
					# shape=(frame3.height,
						# frame3.width,))

# print 'img3 Acquired'

# frame4.queueFrameCapture() 
# cam.camera0.runFeatureCommand('AcquisitionStart')
# time.sleep(1)
# cam.camera0.runFeatureCommand('AcquisitionStop')
# frame4.waitFrameCapture()
# img1 = np.ndarray(buffer=frame4.getBufferByteData(),
					# dtype=np.uint8,
					# shape=(frame4.height,
						# frame4.width,))

# print 'img4 Acquired'

# frame5.queueFrameCapture() 
# cam.camera0.runFeatureCommand('AcquisitionStart')
# time.sleep(1)
# cam.camera0.runFeatureCommand('AcquisitionStop')
# frame5.waitFrameCapture()
# img5 = np.ndarray(buffer=frame5.getBufferByteData(),
					# dtype=np.uint8,
					# shape=(frame5.height,
						# frame5.width,))

# print 'img5 Acquired'
						
# cam.camera0.endCapture()
# cam.camera0.revokeAllFrames()

# print 'Capture terminated, Frames revoked. CAM STILL OPEN!!!'
# cam.close()
# print 'cam closed'
# vim.close()
# print 'vimba closed'

# plt.imshow(img0)
# plt.show()
# plt.imshow(img1)
# plt.show()
# plt.imshow(img2)
