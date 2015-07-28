/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        VimbaHelper.cs

  Description: Implementation file for the VimbaHelper class that demonstrates
               how to implement a synchronous single image acquisition with
               VimbaNET.

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

namespace SynchronousGrab
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

    //Delegate for our callback
    public delegate void CameraListChangedHandler(object sender, EventArgs args);

    //A helper class as a wrapper around Vimba
    public class VimbaHelper
    {
        private Vimba                       m_Vimba = null;                     //Main Vimba API entry object
        private CameraListChangedHandler    m_CameraListChangedHandler = null;  //Camera list changed handler

        public VimbaHelper()
        {
        }

        ~VimbaHelper()
        {
            //Release Vimba API if user forgot to call Shutdown
            ReleaseVimba();
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

            //Convert raw frame data into image (for image display)
            Image image = null;
            switch(frame.PixelFormat)
            {
            case VmbPixelFormatType.VmbPixelFormatMono8:
                {
                    Bitmap bitmap = new Bitmap((int)frame.Width, (int)frame.Height, PixelFormat.Format8bppIndexed);

                    //Set greyscale palette
                    ColorPalette palette = bitmap.Palette;
                    for(int i = 0; i < palette.Entries.Length; i++)
                    {
                        palette.Entries[i] = Color.FromArgb(i, i, i);
                    }
                    bitmap.Palette = palette;

                    //Copy image data
                    BitmapData bitmapData = bitmap.LockBits(    new Rectangle(  0,
                                                                                0,
                                                                                (int)frame.Width,
                                                                                (int)frame.Height),
                                                                ImageLockMode.WriteOnly,
                                                                PixelFormat.Format8bppIndexed);
                    try
                    {
                        //Copy image data line by line
                        for(int y = 0; y < (int)frame.Height; y++)
                        {
                            System.Runtime.InteropServices.Marshal.Copy(    frame.Buffer,
                                                                            y * (int)frame.Width,
                                                                            new IntPtr(bitmapData.Scan0.ToInt64() + y * bitmapData.Stride),
                                                                            (int)frame.Width);
                        }
                    }
                    finally
                    {
                        bitmap.UnlockBits(bitmapData);
                    }

                    image = bitmap;
                }
                break;

            case VmbPixelFormatType.VmbPixelFormatBgr8:
                {
                    Bitmap bitmap = new Bitmap((int)frame.Width, (int)frame.Height, PixelFormat.Format24bppRgb);

                    //Copy image data
                    BitmapData bitmapData = bitmap.LockBits(    new Rectangle(  0,
                                                                                0,
                                                                                (int)frame.Width,
                                                                                (int)frame.Height),
                                                                ImageLockMode.WriteOnly,
                                                                PixelFormat.Format24bppRgb);
                    try
                    {
                        //Copy image data line by line
                        for(int y = 0; y < (int)frame.Height; y++)
                        {
                            System.Runtime.InteropServices.Marshal.Copy(    frame.Buffer,
                                                                            y * ((int)frame.Width) * 3,
                                                                            new IntPtr(bitmapData.Scan0.ToInt64() + y * bitmapData.Stride),
                                                                            ((int)(frame.Width) * 3));
                        }
                    }
                    finally
                    {
                        bitmap.UnlockBits(bitmapData);
                    }

                    image = bitmap;
                }
                break;

            default:
                throw new Exception("Current pixel format is not supported by this example (only Mono8 and BRG8Packed are supported).");
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
                        if(null != m_CameraListChangedHandler)
                        {
                            m_Vimba.OnCameraListChanged -= this.OnCameraListChange;
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
        //Get vimba version as string
        public String GetVersion()
        {
            //Check if API has been started up at all
            if (null == m_Vimba)
            {
                throw new Exception("Vimba has not been started.");
            }
            return String.Format("{0:D}.{1:D}.{2:D}",m_Vimba.Version.major, m_Vimba.Version.minor, m_Vimba.Version.patch);
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

        public Image AcquireSingleImage(string id)
        {
            //Check parameter
            if(null == id)
            {
                throw new ArgumentNullException("id");
            }

            //Check if API has been started up at all
            if(null == m_Vimba)
            {
                throw new Exception("Vimba is not started.");
            }

            //Open camera
            Camera camera = m_Vimba.OpenCameraByID(id, VmbAccessModeType.VmbAccessModeFull);
            if(null == camera)
            {
                throw new NullReferenceException("No camera retrieved.");
            }

            // Set the GeV packet size to the highest possible value
            // (In this example we do not test whether this cam actually is a GigE cam)
            try
            {
                camera.Features["GVSPAdjustPacketSize"].RunCommand();
                while (false == camera.Features["GVSPAdjustPacketSize"].IsCommandDone()) { }
            }
            catch { }

            Frame frame = null;
            try
            {
                //Set a compatible pixel format
                AdjustPixelFormat(camera);

                //Acquire an image synchronously (snap)
                camera.AcquireSingleImage(ref frame, 2000);
            }
            finally
            {
                camera.Close();
            }

            return ConvertFrame(frame);
        }
    }
}
