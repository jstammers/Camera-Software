from pymba import *
import os
import numpy as np
import time
from png_writer import PngWriter
i=0
time0 = time.time()
vimba = Vimba()
vimba.startup()
cameraIds = vimba.getCameraIds()
cam0 = vimba.getCamera(cameraIds[0])
cam0.openCamera()
for i in range(3):
	
	frame0 = cam0.getFrame()
	frame1 = cam0.getFrame()
	frame2 = cam0.getFrame()
	frame0.announceFrame()
	cam0.startCapture()
	frame0.queueFrameCapture()
	cam0.runFeatureCommand('AcquisitionStart')
	time.sleep(5.0/10.0)
	cam0.runFeatureCommand('AcquisitionStop')
	acqTime = time.time()
	cam0.endCapture()
	startTime = time.time()
	imdNp = np.ndarray(buffer = frame0.getBufferByteData(), dtype = np.uint8, shape = (frame0.height,frame0.width))
	
	PngWriter(os.path.join(os.getcwd(),'testImage.png'),imdNp, bitdepth = 8)
	writeTime = time.time()
	cam0.revokeAllFrames()
	i+=1
	print 'acquired at' + str(acqTime-time0)
	print 'ended at' + str(startTime-acqTime)
	print 'wrote image at' + str(writeTime-acqTime)  
cam0.closeCamera()
vimba.shutdown()