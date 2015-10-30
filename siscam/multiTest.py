from pymba import *
import os
import numpy as np
import time
from png_writer import PngWriter
import AVTcam
reload(AVTcam)
VimbAcq = AVTcam.VimbAcq()
#if __name__ == '__main__':
VimbAcq.open()  ####AVT
Guppy = AVTcam.AVTcam(VimbAcq.ID(),VimbAcq) ###AVT
Guppy.open()
print Guppy.camera0.ExposureMode + ' before change'
Guppy.set_AutoMode(exposure = 10)
print Guppy.camera0.ExposureMode
print Guppy.camera0.ExposureTime
# Guppy.set_TriggerMode(True)
# images = Guppy.MultipleImages(3)

# print images
# Guppy.close()
# VimbAcq.close()
# i = 0
# for image in images:
# 	PngWriter(os.path.join(os.getcwd(),'image_' +str(i)+'.png'),image, bitdepth = 8)
# 	i+=1