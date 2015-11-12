# Camera-Software
Collection of software for analysing images from cameras for use in atomic physics experiments. At present, this is designed for Python 2.7. Due to compatibility issues with Python 3 of some dependent modules, there are no immediate plans to support this.

# Acquire
acquire is a GUI designed to acquire images from a CCD camera. It currently supports Allied Vision Technologies (AVT) cameras, with some functionality for other brands, such as Sony.

## Live Acquisition
Under Live mode, acquire continuously grabs image frames from the camera. The exposure time of each image is set under Settings in Timing AVT, in units of us.

## Triggered Acquisition
Choosing Absorption or Fluorescence mode will set the camera to wait for a trigger input before acquiring. Here, the trigger duration sets the exposure time. After three or two images are acquired, the absorption or flourescence image is displayed along with the others. This calculated image is written to img/test.png for use with Cam.

##Saving Images
By default, the images are saved into a folder img located in the same directory as the source code. This can be modified in the settings.py file. Add this file to .gitignore if any settings are changed from the default.

#Cam
Two versions of Cam exist. Cam is the original version, designed for analysis of Rb and K dual-species experiments. Cam_stripdown analyses a single image at a time. Upon loading, Cam_stripdown searches for a "test.png" image and a "Variables.txt" file. This variables file should be a comma-separated file with each line corresponding to a variable name and the value it had for the corresponding image. If it cannot find these, the program will exit

## Fitting to the image
The region of interest can be selected using the yellow markers and the program will perform a 2D Gaussian fit. The results of this fit will be displayed in a table. Mathematical functions of these can also be displayed, as well as user-defined values or those from the Variables file.

## Plotting results
Selecting a column will allow the field to be set as the X ordinate or Y ordinate for a scatter plot. This can be dynamicallyplotted as a sequence of images is loaded and calculated. Rows can be omitted using the omit check box.

## Saving results
Both plots and the raw data can be saved. The defualt location is again determined by the setttings file with a subdirectory of the form "/Year/Month/Day". Refer to the settings file if changes are to be made

## Imaging Parameters
The imaging parameters, in particular the pixel size is given in the imagingpars.py module. This needs to be modified to extract a physical length scale for the images
