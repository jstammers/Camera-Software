
from AVTcam import *
VimbAcq = VimbAcq()
VimbAcq.open()
Guppy = AVTcam(VimbAcq.ID(),VimbAcq)
Guppy.open()
print Guppy.SingleImage()

Guppy.close()
VimbAcq.close()

