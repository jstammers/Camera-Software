import os, os.path
basedir = os.path.dirname(__file__)
#path to acquired image
imagefilepath = os.path.join(basedir, 'img')

#full path to image file
#imagefile = os.path.join(imagefilepath, 'test.sis')
imagefile = os.path.join(imagefilepath, 'test.png')
testfile = os.path.join(imagefilepath, 'test.png')
absorbfile = os.path.join(imagefilepath,'absorb.png')
forefile = os.path.join(imagefilepath,'foreground.png')
backfile = os.path.join(imagefilepath,'background.png')

#full path to variable file
varfile = os.path.join(imagefilepath, 'Variables.txt')
#imagefile = r"W:/ocf/fit.sis" #direct access to acquired image on camera computer

#path where to save images
imagesavepath = r"C:/Data/" # with subdirs automagically created
#imagesavepath = r"y:/data/2008/" #direct access to cam computer

#path to dir where icon bitmap are stored
bitmappath = os.path.join(basedir, 'bitmaps')

##settings for cam computer
#imagefile = r"c:/fit/ocf/fit.sis" #on cam computer
#imagesavepath = r"c:/repository/data"

#for developing:
#imagefile = "W:/ocf/fit.sis"
#imagefile = r"c:/fit/ocf/fit.sis"
#imagefile = "img/test.sis"
#imagefile = "img/20061115_0.SIS" #bimodal


#settings for acquire
configfile = r"c:\Dokumente und Einstellungen\Gregor\Eigene Dateien\python\siscam\config_simulation.ccf"
usePseudoCam = False

useTheta   = False
useBluefox = False
useSony    = False
useAVT     = True

ImagingControlProgID = "IC.ICImagingControl3"
devicesettings = 'settings/cam bluefox device settings.txt'

#Vera
#ImagingControlProgID = "IC.ICImagingControl"
#devicesettings = 'settings/cam sony 1 device settings.txt'



configfiles_sony = ['settings/cam sony 0 device settings.txt',
                    'settings/cam sony 1 device settings.txt',
                    ]

#configfiles_sony = ['settings/cam bluefox device settings.txt',
#                    'settings/cam bluefox device settings.txt']

#real system
#configfile = r"c:\WinSIS6\py\config.ini" #real system
#usePseudoCam = False



templatedir = os.path.join(basedir, 'templates')


