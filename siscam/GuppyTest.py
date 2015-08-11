
from AVTcam import *
VimbAcq = VimbAcq()
VimbAcq.open()
Guppy = AVTcam(VimbAcq.ID(),VimbAcq)
Guppy.open()
Guppy.SingleImage()

Guppy.close()
VimbAcq.close()

