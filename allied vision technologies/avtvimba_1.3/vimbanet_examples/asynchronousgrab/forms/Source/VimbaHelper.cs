/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        VimbaHelper.cs

  Description: Implementation file for the VimbaHelper class that demonstrates
               how to implement an asynchronous, continuous image acquisition
               with VimbaNET.

-------------------------------------------------------------------------------

  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE,
  NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR  PURPOSE ARE
  DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
  AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=============================================================================*/

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using System.Drawing.Imaging;
using AVT.VmbAPINET;

namespace AsynchronousGrab
{
    
    //A simple container class for infos (name and ID) about a camera
    public class CameraInfo
    {
        private string m_Name = null;
        private string m_ID = null;

        public CameraInfo(string name, string id)
        {
            if(null == name)
            {
                throw new ArgumentNullException("name");
            }
            if(null == name)
            {
                throw new ArgumentNullException("id");
            }

            m_Name = name;
            m_ID = id;
        }

        public string Name
        {
            get
            {
                return m_Name;
            }
        }

        public string ID
        {
            get
            {
                return m_ID;
            }
        }

        public override string ToString()
        {
            return m_Name;
        }
    }

    //Event args class that will contain a single image
    public class FrameEventArgs : EventArgs
    {
        private Image       m_Image = null;
        private Exception   m_Exception = null;

        public FrameEventArgs(Image image)
        {
            if(null == image)
            {
                throw new ArgumentNullException("image");
            }

            m_Image = image;
        }

        public FrameEventArgs(Exception exception)
        {
            if(null == exception)
            {
                throw new ArgumentNullException("exception");
            }

            m_Exception = exception;
        }

        public Image Image
        {
            get
            {
                return m_Image;
            }
        }

        public Exception Exception
        {
            get
            {
                return m_Exception;
            }
        }
    }

    //Delegates for our callbacks
    public delegate void CameraListChangedHandler(object sender, EventArgs args);
    public delegate void FrameReceivedHandler(object sender, FrameEventArgs args);

    //A helper class as a wrapper around Vimba
    public class VimbaHelper
    {
        private Vimba                       m_Vimba = null;                     //Main Vimba API entry object
        private CameraListChangedHandler    m_CameraListChangedHandler = null;  //Camera list changed handler
        private Camera                      m_Camera = null;                    //Camera object if camera is open
        private bool                        m_Acquiring = false;                //Flag to remember if acquisition is running
        private FrameReceivedHandler        m_FrameReceivedHandler = null;      //Frames received handler
        private const int                   m_RingBitmapSize = 2;               //Amount of Bitmaps in RingBitmap
        private static RingBitmap           m_RingBitmap = null;                //Bitmaps to display images
        private static readonly object      m_ImageInUseSyncLock = new object();//Protector for m_ImageInUse
        private static bool                 m_ImageInUse = true;                //Signal of picture box that image is used

        public VimbaHelper()
        {
            m_RingBitmap = new RingBitmap(m_RingBitmapSize);
        }

        ~VimbaHelper()
        {
            //Release Vimba API if user forgot to call Shutdown
            ReleaseVimba();
        }

        //set/get flag, signals a displayed image
        public static bool ImageInUse
        {
            set
            {
                lock (m_ImageInUseSyncLock)
                {
                    m_ImageInUse = value;
                }
            }
            get
            {
                lock (m_ImageInUseSyncLock)
                {
                    return m_ImageInUse;
                }
            }
        }

        //Convert frame to displayable image
        private static Image ConvertFrame(Frame frame)
        {
            if(null == frame)
            {
                throw new ArgumentNullException("frame");
            }

            //Check if the image is valid
            if(VmbFrameStatusType.VmbFrameStatusComplete != frame.ReceiveStatus)
            {
                throw new Exception("Invalid frame received. Reason: " + frame.ReceiveStatus.ToString());
            }

            //define return variable
            Image image = null;
            
            //check if current image is in use,
            //if not we drop the frame to get not in conflict with GUI
            if (ImageInUse)
            {
                //Convert raw frame data into image (for image display)
                switch (frame.PixelFormat)
                {
                    case VmbPixelFormatType.VmbPixelFormatMono8:
                        {
                            m_RingBitmap.CopyToNextBitmap_8bppIndexed((int)frame.Width,
                                                                      (int)frame.Height,
                                                                      frame.Buffer);

                            image = m_RingBitmap.Image;
                            ImageInUse = false;
                        }
                        break;

                    case VmbPixelFormatType.VmbPixelFormatBgr8:
                        {
                            m_RingBitmap.CopyToNextBitmap_24bppRgb((int)frame.Width,
                                                                    (int)frame.Height,
                                                                    frame.Buffer);

                            image = m_RingBitmap.Image;
                            ImageInUse = false;
                        }
                        break;

                    default:
                        throw new Exception("Current pixel format is not supported by this example (only Mono8 and BRG8Packed are supported).");
                }
            }
                    
            return image;
        }

        //Adjust pixel format of given camera to match one that can be displayed
        //in this example.
        private void AdjustPixelFormat(Camera camera)
        {
            if(null == camera)
            {
                throw new ArgumentNullException("camera");
            }

            string[] supportedPixelFormats = new string[] { "BGR8Packed", "Mono8" };
            //Check for compatible pixel format
            Feature pixelFormatFeature = camera.Features["PixelFormat"];

            //Determine current pixel format
            string currentPixelFormat = pixelFormatFeature.EnumValue;

            //Check if current pixel format is supported
            bool currentPixelFormatSupported = false;
            foreach(string supportedPixelFormat in supportedPixelFormats)
            {
                if(string.Compare(currentPixelFormat, supportedPixelFormat, StringComparison.Ordinal) == 0)
                {
                    currentPixelFormatSupported = true;
                    break;
                }
            }

            //Only adjust pixel format if we not already have a compatible one.
            if(false == currentPixelFormatSupported)
            {
                //Determine available pixel formats
                string[] availablePixelFormats = pixelFormatFeature.EnumValues;
                    
                //Check if there is a supported pixel format
                bool pixelFormatSet = false;
                foreach(string supportedPixelFormat in supportedPixelFormats)
                {
                    foreach(string availablePixelFormat in availablePixelFormats)
                    {
                        if(     (string.Compare(supportedPixelFormat, availablePixelFormat, StringComparison.Ordinal) == 0)
                            &&  (pixelFormatFeature.IsEnumValueAvailable(supportedPixelFormat) == true))
                        {
                            //Set the found pixel format
                            pixelFormatFeature.EnumValue = supportedPixelFormat;
                            pixelFormatSet = true;
                            break;
                        }
                    }

                    if(true == pixelFormatSet)
                    {
                        break;
                    }
                }

                if(false == pixelFormatSet)
                {
                    throw new Exception("None of the pixel formats that are supported by this example (Mono8 and BRG8Packed) can be set in the camera.");
                }
            }
        }

        private void OnCameraListChange(VmbUpdateTriggerType reason)
        {
            switch(reason)
            {
            case VmbUpdateTriggerType.VmbUpdateTriggerPluggedIn:
            case VmbUpdateTriggerType.VmbUpdateTriggerPluggedOut:
                {
                    CameraListChangedHandler cameraListChangedHandler = m_CameraListChangedHandler;
                    if(null != cameraListChangedHandler)
                    {
                        cameraListChangedHandler(this, EventArgs.Empty);
                    }
                }
                break;

            default:
                break;
            }
        }

        private void OnFrameReceived(Frame frame)
        {
            try
            {
                //Convert frame into displayable image
                Image image = ConvertFrame(frame);

                FrameReceivedHandler frameReceivedHandler = m_FrameReceivedHandler;
                if (null != frameReceivedHandler && null != image)
                {
                    //Report image to user
                    frameReceivedHandler(this, new FrameEventArgs(image));
                }
            }
            catch(Exception exception)
            {
                FrameReceivedHandler frameReceivedHandler = m_FrameReceivedHandler;
                if(null != frameReceivedHandler)
                {
                    //Report an error to the user
                    frameReceivedHandler(this, new FrameEventArgs(exception));
                }
            }
            finally
            {
                //We make sure to always return the frame to the API
                m_Camera.QueueFrame(frame);
            }
        }

        //Release Camera
        private void ReleaseCamera()
        {
            if(null != m_Camera)
            {
                //We can use cascaded try-finally blocks to release the
                //camera step by step to make sure that every step is executed.
                try
                {
                    try
                    {
                        try
                        {
                            if(null != m_FrameReceivedHandler)
                            {
                                m_Camera.OnFrameReceived -= this.OnFrameReceived;
                            }
                        }
                        finally
                        {
                            m_FrameReceivedHandler = null;
                            if(true == m_Acquiring)
                            {
                                m_Camera.StopContinuousImageAcquisition();
                            }
                        }
                    }
                    finally
                    {
                        m_Acquiring = false;
                        m_Camera.Close();
                    }
                }
                finally
                {
                    m_Camera = null;
                }
            }
        }

        //Release Vimba API
        private void ReleaseVimba()
        {
            if(null != m_Vimba)
            {
                //We can use cascaded try-finally blocks to release the
                //Vimba API step by step to make sure that every step is executed.
                try
                {
                    try
                    {
                        try
                        {
                            //First we release the camera (if there is one)
                            ReleaseCamera();
                        }
                        finally
                        {
                            if(null != m_CameraListChangedHandler)
                            {
                                m_Vimba.OnCameraListChanged -= this.OnCameraListChange;
                            }
                        }
                    }
                    finally
                    {
                        //Now finally shutdown the API
                        m_CameraListChangedHandler = null;
                        m_Vimba.Shutdown();
                    }
                }
                finally
                {
                    m_Vimba = null;
                }
            }
        }

        //Start up Vimba API
        public void Startup(CameraListChangedHandler cameraListChangedHandler)
        {
            //Instanciate main Vimba object
            Vimba vimba = new Vimba();

            //Start up Vimba API
            vimba.Startup();
            m_Vimba = vimba;

            bool bError = true;
            try
            {
                //Register camera list change delegate
                if(null != cameraListChangedHandler)
                {
                    m_Vimba.OnCameraListChanged += this.OnCameraListChange;
                    m_CameraListChangedHandler = cameraListChangedHandler;
                }

                bError = false;
            }
            finally
            {
                //Release Vimba API if an error occured
                if(true == bError)
                {
                    ReleaseVimba();
                }
            }
        }

        //Shutdown API
        public void Shutdown()
        {
            //Check if API has been started up at all
            if(null == m_Vimba)
            {
                throw new Exception("Vimba has not been started.");
            }

            ReleaseVimba();
        }
        public String GetVersion()
        {
            if (null == m_Vimba)
            {
                throw new Exception("Vimba has not been started.");
            }
            VmbVersionInfo_t version_info = m_Vimba.Version;
            return String.Format("{0:D}.{1:D}.{2:D}",version_info.major,version_info.minor,version_info.patch);
        }
        //Property to get the current camera list
        public List<CameraInfo> CameraList
        {
            get
            {
                //Check if API has been started up at all
                if(null == m_Vimba)
                {
                    throw new Exception("Vimba is not started.");
                }

                List<CameraInfo> cameraList = new List<CameraInfo>();
                CameraCollection cameras = m_Vimba.Cameras;
                foreach(Camera camera in cameras)
                {
                    cameraList.Add(new CameraInfo(camera.Name, camera.Id));
                }

                return cameraList;
            }
        }

        public void StartContinuousImageAcquisition(string id, FrameReceivedHandler frameReceivedHandler)
        {
            //Check parameters
            if(null == id)
            {
                throw new ArgumentNullException("id");
            }

            //Check if API has been started up at all
            if(null == m_Vimba)
            {
                throw new Exception("Vimba is not started.");
            }

            //Check if a camera is already open
            if(null != m_Camera)
            {
                throw new Exception("A camera is already open.");
            }

            //Open camera
            m_Camera = m_Vimba.OpenCameraByID(id, VmbAccessModeType.VmbAccessModeFull);
            if(null == m_Camera)
            {
                throw new NullReferenceException("No camera retrieved.");
            }

            // Set the GeV packet size to the highest possible value
            // (In this example we do not test whether this cam actually is a GigE cam)
            try
            {
                m_Camera.Features["GVSPAdjustPacketSize"].RunCommand();
                while (false == m_Camera.Features["GVSPAdjustPacketSize"].IsCommandDone()) {}
            }
            catch {}

            bool bError = true;
            try
            {
                //Set a compatible pixel format
                AdjustPixelFormat(m_Camera);

                //Register frame callback
                if(null != frameReceivedHandler)
                {
                    m_Camera.OnFrameReceived += this.OnFrameReceived;
                    m_FrameReceivedHandler = frameReceivedHandler;
                }

                //Reset member variables
                m_RingBitmap = new RingBitmap(m_RingBitmapSize);
                m_ImageInUse = true;
                m_Acquiring = true;

                //Start synchronous image acquisition (grab)
                m_Camera.StartContinuousImageAcquisition(3);
                
                bError = false;
            }
            finally
            {
                //Close camera already if there was an error
                if(true == bError)
                {
                    ReleaseCamera();
                }
            }
        }

        public void StopContinuousImageAcquisition()
        {
            //Check if API has been started up at all
            if(null == m_Vimba)
            {
                throw new Exception("Vimba is not started.");
            }

            //Check if no camera is open
            if(null == m_Camera)
            {
                throw new Exception("No camera open.");
            }

            //Close camera
            ReleaseCamera();
        }
    }
}
