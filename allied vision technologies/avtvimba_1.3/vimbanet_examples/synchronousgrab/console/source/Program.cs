/*=============================================================================
  Copyright (C) 2013 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: The main entry point of the AsynchronousGrabConsole example of VimbaNET.

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

    using AVT.VmbAPINET;

    /// <summary>
    /// The Program class 
    /// </summary>
    internal static class Program
    {
       /// <summary>
        /// The main entry point for the application.
       /// </summary>
       /// <param name="args">The command line arguments</param>
        private static void Main(string[] args)
        {
            string fileName = string.Empty;        // The FileName to store the image
            bool printHelp = false;                // Output help?
            string cameraID = null;                // The camera ID

            Console.WriteLine();
            Console.WriteLine("///////////////////////////////////////////////");
            Console.WriteLine("/// AVT Vimba API Synchronous Grab Example ///");
            Console.WriteLine("//////////////////////////////////////////////");
            Console.WriteLine();

            try
            {
                ParseCommandLine(args, ref fileName, ref printHelp, ref cameraID);

                if (fileName == string.Empty)
                {
                    fileName = "SynchronousGrab.bmp";
                }

                // Print out help and end program
                if (printHelp)
                {
                    Console.WriteLine("Usage: AsynchronousGrab [CameraID] [/i] [/h]");
                    Console.WriteLine("Parameters:   CameraID    ID of the camera to use (using first camera if not specified)");
                    Console.WriteLine("              /f          FileName to save the image");
                    Console.WriteLine("              /h          Print out help");
                }
                else
                {
                    // Create a new Vimba entry object
                    // AVT.VmbAPINET.Vimba vimbaSystem = new AVT.VmbAPINET.Vimba();
                    VimbaHelper vimbaHelper = new VimbaHelper();
                    vimbaHelper.Startup(); // Startup API
                    // Open camera
                    try
                    {
                        Console.WriteLine("Vimba Version V{0}", vimbaHelper.GetVersion());
                        if (null == cameraID)
                        {
                            // Open first available camera

                            // Fetch all cameras known to Vimba
                            List<Camera> cameras = vimbaHelper.CameraList;
                            if (cameras.Count < 0)
                            {
                                throw new Exception("No camera available.");
                            }

                            foreach (Camera currentCamera in cameras)
                            {
                                // Check if we can open the camera in full mode
                                VmbAccessModeType accessMode = currentCamera.PermittedAccess;
                                if (VmbAccessModeType.VmbAccessModeFull == (VmbAccessModeType.VmbAccessModeFull & accessMode))
                                {
                                    // Now get the camera ID
                                    cameraID = currentCamera.Id;
                                }
                            }

                            if (null == cameraID)
                            {
                                throw new Exception("Could not open any camera.");
                            }
                        }

                        Console.WriteLine("Opening camera with ID: " + cameraID);

                        System.Drawing.Image img = vimbaHelper.AcquireSingleImage(cameraID);

                        img.Save(fileName); 

                        Console.WriteLine("Image is saved as: " + fileName); 
                    }
                    finally
                    {
                        // shutdown the vimba API
                        vimbaHelper.Shutdown(); 
                    }
                }
            }
            catch (VimbaException ve)
            {
                // Output in case of a vimba Exception 
                Console.WriteLine(ve.Message);
                Console.Write("Return Code: " + ve.ReturnCode.ToString() + " (" + ve.MapReturnCodeToString() + ")");
            }
            catch (Exception e)
            {
                // Output in case of a System.Exception
                Console.WriteLine(e.Message);
            }

            Console.WriteLine("Press any Key to exit!");
            Console.ReadKey();
        }

        /// <summary>
        /// Parses the Command Line Arguments
        /// </summary>
        /// <param name="args">The command line arguments</param>
        /// <param name="fileName">Holds the optional fileName</param>
        /// <param name="printHelp">Flag to decide if help information is shown</param>
        /// <param name="cameraID">The camera ID</param>
        private static void ParseCommandLine(string[] args, ref string fileName, ref bool printHelp, ref string cameraID)
        {
            // Parse command line
            foreach (string parameter in args)
            {
                if (parameter.Length < 0)
                {
                    throw new ArgumentException("Invalid parameter found.");
                }

                if (parameter.StartsWith("/"))
                {
                    if (parameter.StartsWith("/f:"))
                    {
                        if (string.Empty != fileName)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        fileName = parameter.Substring(3);
                        if (fileName.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }
                    }
                    else 
                        if (string.Compare(parameter, "/h", StringComparison.Ordinal) == 0)
                        {
                            if (true == printHelp)
                            {
                                throw new ArgumentException("Invalid parameter found.");
                            }

                            printHelp = true;
                        }
                }
                else
                {
                    if (null != cameraID)
                    {
                        throw new ArgumentException("Invalid parameter found.");
                    }

                    cameraID = parameter;
                }
            }
        }
    }
}