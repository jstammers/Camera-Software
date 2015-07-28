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

namespace AsynchronousGrabConsole
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Imaging;
    using AVT.VmbAPINET;

    /// <summary>
    /// A helper class as a wrapper around Vimba
    /// </summary>
    public class VimbaHelper
    {
        private Vimba m_Vimba = null;                     // Main Vimba API entry object
        private Camera m_Camera = null;                    // Camera object if camera is open

        /// <summary>
        /// Initializes a new instance of the VimbaHelper class
        /// </summary>
        public VimbaHelper()
        {
        }

        /// <summary>
        /// Finalizes an instance of the VimbaHelper class
        /// </summary>
        ~VimbaHelper()
        {
            // Release Vimba API if user forgot to call Shutdown
            ReleaseVimba();
        }

        /// <summary>
        /// Gets the current camera list
        /// </summary>
        public List<Camera> CameraList
        {
            get
            {
                // Check if API has been started up at all
                if (null == m_Vimba)
                {
                    throw new Exception("Vimba is not started.");
                }

                List<Camera> cameraList = new List<Camera>();
                CameraCollection cameras = m_Vimba.Cameras;
                foreach (Camera camera in cameras)
                {
                    cameraList.Add(camera);
                }

                return cameraList;
            }
        }

        /// <summary>
        /// // Start up Vimba API
        /// </summary>
        public void Startup()
        {
            // Instantiate main Vimba object
            Vimba vimba = new Vimba();

            // Start up Vimba API
            vimba.Startup();
            m_Vimba = vimba;
        }

        /// <summary>
        /// Shutdown API
        /// </summary>
        public void Shutdown()
        {
            // Check if API has been started up at all
            if (null == m_Vimba)
            {
                throw new Exception("Vimba has not been started.");
            }

            ReleaseVimba();
        }
        /// <summary>
        /// get Vimba Version as String
        /// </summary>
        /// <returns>vimba version as string</returns>
        public String GetVersion()
        {
            if (null == m_Vimba)
            {
                throw new Exception("Vimba has not been started.");
            }
            return String.Format("{0:D}.{1:D}.{2:D}",m_Vimba.Version.major, m_Vimba.Version.minor, m_Vimba.Version.patch);
        }
        /// <summary>
        /// Acquire a Single Image
        /// </summary>
        /// <param name="cameraID">The Camera ID</param>
        /// <returns>The acquired image</returns>
        public Image AcquireSingleImage(string cameraID)
        {
            // Check parameter
            if (null == cameraID)
            {
                throw new ArgumentNullException("id");
            }

            // Check if API has been started up at all
            if (null == m_Vimba)
            {
                throw new Exception("Vimba is not started.");
            }

            // Open camera
            Camera camera = m_Vimba.OpenCameraByID(cameraID, VmbAccessModeType.VmbAccessModeFull);
            if (null == camera)
            {
                throw new NullReferenceException("No camera retrieved.");
            }

            // Set the GeV packet size to the highest possible value
            // (In this example we do not test whether this cam actually is a GigE cam)
            try
            {
                camera.Features["GVSPAdjustPacketSize"].RunCommand();
                while (false == camera.Features["GVSPAdjustPacketSize"].IsCommandDone())
                {
                    // Do nothing
                }
            }
            catch
            {
                // Do nothing
            }

            Frame frame = null;
            try
            {
                // Set a compatible pixel format
                AdjustPixelFormat(camera);

                // Acquire an image synchronously (snap)
                camera.AcquireSingleImage(ref frame, 2000);
            }
            finally
            {
                camera.Close();
            }

            return ConvertFrame(frame);
        }

        /// <summary>
        /// Convert frame to displayable or savable image
        /// </summary>
        /// <param name="frame">The received frame</param>
        /// <returns>The taken Image</returns>
        private static Image ConvertFrame(Frame frame)
        {
            if (null == frame)
            {
                throw new ArgumentNullException("frame");
            }

            // Check if the image is valid
            if (VmbFrameStatusType.VmbFrameStatusComplete != frame.ReceiveStatus)
            {
                throw new Exception("Invalid frame received. Reason: " + frame.ReceiveStatus.ToString());
            }

            // Convert raw frame data into
            Bitmap bitmap = null;

            bitmap = new Bitmap((int)frame.Width, (int)frame.Height, PixelFormat.Format24bppRgb);

            frame.Fill(ref bitmap);

            return bitmap;
        }

        /// <summary>
        /// Adjust pixel format of given camera to match one that can be displayed in this example.
        /// </summary>
        /// <param name="camera">The camera</param>
        private void AdjustPixelFormat(Camera camera)
        {
            if (null == camera)
            {
                throw new ArgumentNullException("camera");
            }

            string[] supportedPixelFormats = new string[] { "BayerRG8", "Mono8" };

            // Check for compatible pixel format
            Feature pixelFormatFeature = camera.Features["PixelFormat"];

            // Determine current pixel format
            string currentPixelFormat = pixelFormatFeature.EnumValue;

            // Check if current pixel format is supported
            bool currentPixelFormatSupported = false;
            foreach (string supportedPixelFormat in supportedPixelFormats)
            {
                if (string.Compare(currentPixelFormat, supportedPixelFormat, StringComparison.Ordinal) == 0)
                {
                    currentPixelFormatSupported = true;
                    break;
                }
            }

            // Only adjust pixel format if we not already have a compatible one.
            if (false == currentPixelFormatSupported)
            {
                // Determine available pixel formats
                string[] availablePixelFormats = pixelFormatFeature.EnumValues;

                // Check if there is a supported pixel format
                bool pixelFormatSet = false;
                foreach (string supportedPixelFormat in supportedPixelFormats)
                {
                    foreach (string availablePixelFormat in availablePixelFormats)
                    {
                        if ((string.Compare(supportedPixelFormat, availablePixelFormat, StringComparison.Ordinal) == 0)
                            && (pixelFormatFeature.IsEnumValueAvailable(supportedPixelFormat) == true))
                        {
                            // Set the found pixel format
                            pixelFormatFeature.EnumValue = supportedPixelFormat;
                            pixelFormatSet = true;
                            break;
                        }
                    }

                    if (true == pixelFormatSet)
                    {
                        break;
                    }
                }

                if (false == pixelFormatSet)
                {
                    throw new Exception("None of the pixel formats that are supported by this example (Mono8 and BRG8Packed) can be set in the camera.");
                }
            }
        }

        /// <summary>
        ///  Release Camera
        /// </summary>
        private void ReleaseCamera()
        {
            if (null != m_Camera)
            {
                // Close Camera
                try
                {
                    m_Camera.Close();
                }
                finally
                {
                    m_Camera = null;
                }
            }
        }

        /// <summary>
        ///  Release Vimba API
        /// </summary>
        private void ReleaseVimba()
        {
            if (null != m_Vimba)
            {
                // We can use cascaded try-finally blocks to release the
                // Vimba API step by step to make sure that every step is executed.
                try
                {
                    try
                    {
                        // First we release the camera (if there is one)
                        ReleaseCamera();
                    }
                    finally
                    {
                        // Now finally shutdown the API
                        m_Vimba.Shutdown();
                    }
                }
                finally
                {
                    m_Vimba = null;
                }
            }
        }
    }
}