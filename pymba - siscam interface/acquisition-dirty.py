class AcquireThreadTheta(AcquireThread):

    def run(self):
        self.running = True
	vimba.startup()  ####### nicht vergessen: vimba = Vimba() ; evtl. an anderer Stelle ? z.B. wenn AcquireThread aufgerufen wird ???
        with closing(self.cam.open()):   ###### obacht, rather closeCamera!! evtl. neue Klasse schreiben. cam = vimba.getCamera(Id)
## brauchen wir wohl nicht
            # if self.app.timing_theta.external:         
                # self.cam.set_timing(0, 0)
            # else:
                # self.cam.set_timing(integration=self.app.timing_theta.exposure,
                                    # repetition=self.app.timing_theta.repetition)
##
			frame0 = self.cam.getFrame()
			frame0.announceFrame()
			self.cam.startCapture()
			frame0.queueFrameCapture()
			self.cam.runFeatureCommand('AcquisitionStart')
			self.cam.runFeatureCommand('AcquisitionStop')
			frame0.waitFrameCapture()
			
			img = frame0.getBufferByteData()
			
			self.cam.endCapture()
			self.cam.revokeAllFrames()
			self.nr += 1
			self.queue.put((self.nr, img.astype(np.float32)))

##
            # while self.running:
                # try:
                    # self.cam.wait(1)
                # except CamTimeoutError:
                    # pass
                # except SIS.SislibError:
                    # print "Error acquiring image from Theta"
## Wozu ist das gut?
## das loesen wir dann anders, mit frames
				# else:
                    # img = self.cam.roidata
                    # self.nr += 1
                    # self.queue.put((self.nr, img.astype(np.float32))) 
## 
			
            #put empty image to queue
            self.queue.put((- 1, None))
	vimba.shutdown()  ####### evtl. an anderer Stelle ? z.B. wenn AcquireThread aufgerufen wird ???
        print "AVTImageProducerThread exiting"