from SIS import Cam, SislibError, PseudoCam

import time

#import numpy
#from pylab import imshow, show, figure, subplot, colorbar, clf
#import shelve



#def testcam():
    

configfile = r"c:\Dokumente und Einstellungen\Gregor\Eigene Dateien\python\siscam\config_simulation.ccf"

#configfile = r"c:\WinSIS6\py\config.ini" #real system

try:
    #cam = PseudoCam()
    cam = Cam(config = configfile)
    cam.open()
    print "opened cam"

    #cam.set_timing(10, 1000) #use with real system

    print "ROI: ", cam.getROI()

    #cam.setROI((0,0,100, 100))
    cam.ROI = (100,400,500,600)
    print "changed ROI"
    print "ROI: ", cam.ROI    

    #print "resetting ROI"
    ##cam.ROI = None
    #del cam.ROI
    #print "ROI: ", cam.ROI
    
    print "binning enabled:", cam.binning_enabled
    print "driver revision:", cam.driver_revision
    print "actual width/height:", cam.actual_width, cam.actual_height
    print "actual ROI:", cam.actual_ROI
    print "debug info: ", cam.debug_info[0:30]
    print "frame width/height:", cam.frame_width, cam.frame_height
    print "acquisition mode: ", cam.acquisition_mode

    cam.start_singleshot()

    print "started single shot acquisition"
    print "acquisition mode: ", cam.acquisition_mode
    print "frame count: ",cam.frame_count


    cam.wait(1000)
    print "completed waiting for end of data acquisition"

    print "frame count: ",cam.frame_count

    img = cam.data
    print "got data"

    cam.stop()
    print "stopped acquistion"

    print "started live acquisition"
    cam.start_live_acquisition()
    cam.wait(1500)
    img2 = cam.roidata
    extent2 = cam.ROI
    cam.stop()
    print "stopped acquisition"

    #cam.start_sequence(2)
    #cam.wait(2000)
    #img1 = cam.get_data()
    #img2 = cam.get_data(1)
    
    print cam.frame_count
    
    #cam.set_timing(integration = 50)


    


except SislibError, error:
    print error
else:
    print "succeded"

finally:
    try:
        cam.close()
        print "closed"
    except:
        print "error closing"



#         storage = shelve.open('img1.pkl', protocol=2)
#         storage['img1'] = data1 storage.close()
        
#         sislib().sis_StartAcq(h, SIS_ACQ_SINGLESHOT)
#         sislib().sis_WaitAcqEnd(h, 5000)
#         data1 = getData()

#         sislib().sis_StartAcq(h, SIS_ACQ_SINGLESHOT)
#         sislib().sis_WaitAcqEnd(h, 5000)
#         data2 = getData()

#         sislib().sis_StartAcq(h, SIS_ACQ_SINGLESHOT)
#         sislib().sis_WaitAcqEnd(h, 5000)
#         data3 = getData()

        
#         storage = shelve.open('img1.pkl', protocol=2)
#         storage['img1'] = data1
#         storage['img2'] = data2
#         storage['img3'] = data3
#         storage.close()


#imshow(img2, extent2)


#         figure(1)
#         clf()
#         subplot(1,2,1)
#         imshow(data1)
#         colorbar()
#         subplot(1,2,2)
#         imshow(data2)
#         colorbar()
#         show()

        
        

    
    


#if __name__ == '__main__':
#    testcam()

