#!/usr/bin/python

from pymba import * 
import time
import numpy as np

def spam_cameras():
    # start Vimba
    vimba = Vimba()
    vimba.startup()

    # get system object
    # system = vimba.getSystem()

    # list available cameras (after enabling discovery for GigE cameras)
    # if system.GeVTLIsPresent:
        # system.runFeatureCommand("GeVDiscoveryAllOnce")
        # time.sleep(0.2)
    cameraIds = vimba.getCameraIds()
    # if cameraIds is not None:
        # for cameraId in cameraIds:
            # print 'Camera ID:', cameraId
        # else:
            # print 'no camera found' 
    # get and open a camera
    camera0 = vimba.getCamera(cameraIds[0])
    camera0.openCamera()
    print 'camera0 ready'
    return camera0, vimba
    # list camera features
    # cameraFeatureNames = camera0.getFeatureNames()
    # f = open('features.txt','w')
    # for name in cameraFeatureNames:
        # print>>f, 'Camera feature:', name
    # f.close()
    # get the value of a feature
    # print camera0.AcquisitionMode
    # print 'Belichtungszeit:', camera0.ExposureTime
    # set the value of a feature
    # camera0.AcquisitionMode = 'MultiFrame'
##    print camera0.AcquisitionMode
    # create new frames for the camera
##    frame0 = camera0.getFrame()  # creates a frame
##    frame1 = camera0.getFrame()  # creates a second frame

    # announce frame
##    frame0.announceFrame()

    # capture a camera image
##    camera0.startCapture()
##    frame0.queueFrameCapture()
##    camera0.runFeatureCommand('AcquisitionStart')
##    camera0.runFeatureCommand('AcquisitionStop')
##    frame0.waitFrameCapture()
##
##    # get image data...
##    imgData = frame0.getBufferByteData()

    # ...or use NumPy for fast image display (for use with OpenCV, etc)

##
##    moreUsefulImgData = np.ndarray(buffer=frame0.getBufferByteData(),
##                                   dtype=np.uint8,
##                                   shape=(frame0.height,
##                                          frame0.width,
##                                          1))

    # clean up after capture
##    camera0.endCapture()
##    camera0.revokeAllFrames()
##
    # close camera
    # camera0.closeCamera()

    # shutdown Vimba
    # vimba.shutdown()
    # testimg = 'nur dieser teststring'


##    import matplotlib.pyplot as plt
##    import matplotlib.image as mpimg
    
##    bild = moreUsefulImgData.squeeze()
##    
##    plt.imshow(bild)
##    plt.show()

print 'module loaded, spam_cameras returns camera0, vimba' 
