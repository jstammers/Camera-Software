/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of LoadSaveSettings example of VimbaNET.

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
using System.Collections.Specialized;

using AVT.VmbAPINET;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

class Program
{
    enum SettingsMode
    {
        Unknown = 0,
        Save    = 1,
        Load    = 2
    };

    static void Main( string[] args )
    {
        string cameraID = null;
        string fileName = null;
        SettingsMode settingsMode = SettingsMode.Unknown; 
        bool printHelp = false;
        bool ignoreStreamable = false;

        try
        {
            Console.WriteLine("/////////////////////////////////////////////");
            Console.WriteLine("/// AVT Vimba API Manage Settings Example ///");
            Console.WriteLine("/////////////////////////////////////////////");
            Console.WriteLine();

            //////////////////////
            //Parse command line//
            //////////////////////

            foreach(string parameter in args)
            {
                if(parameter.Length <= 0)
                {
                    throw new ArgumentException("Invalid parameter found.");
                }

                if(parameter.StartsWith("/"))
                {
                    if(string.Compare(parameter, "/s", StringComparison.Ordinal) == 0)
                    {
                        if(SettingsMode.Unknown != settingsMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        settingsMode = SettingsMode.Save;
                    }
                    else if(string.Compare(parameter, "/l", StringComparison.Ordinal) == 0)
                    {
                        if(SettingsMode.Unknown != settingsMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        settingsMode = SettingsMode.Load;
                    }
                    else if(parameter.StartsWith("/f:", StringComparison.Ordinal))
                    {
                        if(null != fileName)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        fileName = parameter.Substring(3);
                        if(fileName.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }
                    }
                    else if(string.Compare(parameter, "/h", StringComparison.Ordinal) == 0)
                    {
                        if(true == printHelp)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        printHelp = true;
                    }
                    else if(string.Compare(parameter, "/i", StringComparison.Ordinal) == 0)
                    {
                        if(true == ignoreStreamable)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        ignoreStreamable = true;
                    }
                    else
                    {
                        throw new ArgumentException("Invalid parameter found.");
                    }
                }
                else
                {
                    if(null != cameraID)
                    {
                        throw new ArgumentException("Invalid parameter found.");
                    }

                    cameraID = parameter;
                }
            }

            if(     (       (null != cameraID)
                        ||  (null != fileName)
                        ||  (SettingsMode.Unknown != settingsMode)
                        ||  (true == ignoreStreamable))
                &&  (true == printHelp))
            {
                throw new ArgumentException("Invalid parameter found.");
            }
        }
        catch(Exception exception)
        {
            Console.WriteLine(exception.Message);
            Console.WriteLine();
            printHelp = true;
        }

        //Print out help and end program
        if(true == printHelp)
        {
            Console.WriteLine("Usage: LoadSaveSettings.exe [CameraID] [/h] [/{s|l}] [/f:FileName] [/i]");
            Console.WriteLine("Parameters:   CameraID    ID of the camera to use (using first camera if not specified)");
            Console.WriteLine("              /h          Print out help");
            Console.WriteLine("              /s          Save settings to file (default if not specified)");
            Console.WriteLine("              /l          Load settings from file");
            Console.WriteLine("              /f:FileName File name for operation");
            Console.WriteLine("                          (default is \"CameraSettings.xml\" if not specified)");
            Console.WriteLine("              /i          Ignore streamable property of features");
            Console.WriteLine();
            Console.WriteLine("For example to load user set 0 (factory set) from flash in order to\nactivate it call\n");
            Console.WriteLine("UserSet.exe /i:0 /l\n");
            Console.WriteLine("To save the current settings to user set 1 call\n");
            Console.WriteLine("UserSet.exe /i:1 /s");
            Console.WriteLine();

            return;
        }

        try
        {
            if(null == fileName)
            {
                fileName = "CameraSettings.xml";
            }

            //Create a new Vimba entry object
            AVT.VmbAPINET.Vimba vimbaSystem = new AVT.VmbAPINET.Vimba();

            //Startup API
            vimbaSystem.Startup();
            Console.WriteLine("Vimba Version V{0:D}.{1:D}.{2:D}",vimbaSystem.Version.major,vimbaSystem.Version.minor,vimbaSystem.Version.patch);
            try
            {
                //Open camera
                AVT.VmbAPINET.Camera camera = null;
                try
                {
                    if(null == cameraID)
                    {
                        //Open first available camera

                        //Fetch all cameras known to Vimba
                        AVT.VmbAPINET.CameraCollection cameras = vimbaSystem.Cameras;
                        if(cameras.Count < 0)
                        {
                            throw new Exception("No camera available.");
                        }

                        foreach(AVT.VmbAPINET.Camera currentCamera in cameras)
                        {
                            //Check if we can open the camere in full mode
                            VmbAccessModeType accessMode = currentCamera.PermittedAccess;
                            if(VmbAccessModeType.VmbAccessModeFull == (VmbAccessModeType.VmbAccessModeFull & accessMode))
                            {
                                //Now get the camera ID
                                cameraID = currentCamera.Id;
                                
                                //Try to open the camera
                                try
                                {
                                    currentCamera.Open(VmbAccessModeType.VmbAccessModeFull);
                                }
                                catch
                                {
                                    //We can ignore this exception because we simply try
                                    //to open the next camera.
                                    continue;
                                }

                                camera = currentCamera;
                                break;
                            }
                        }

                        if(null == camera)
                        {
                            throw new Exception("Could not open any camera.");
                        }
                    }
                    else
                    {
                        //Open specific camera
                        camera = vimbaSystem.OpenCameraByID(cameraID, VmbAccessModeType.VmbAccessModeFull);
                    }

                    Console.WriteLine("File name: " + fileName);
                    Console.WriteLine("Camera ID: " + cameraID);
                    Console.WriteLine();

                    switch(settingsMode)
                    {
                    default:
                    case SettingsMode.Save:
                        {
                            //Save settings to file
                            AVT.VmbAPINET.Examples.LoadSaveSettings.SaveToFile(camera, fileName, ignoreStreamable);
                            
                            Console.WriteLine("Settings successfully written to file.");
                        }
                        break;

                    case SettingsMode.Load:
                        {
                            //Load settings from file
                            StringCollection loadedFeatures = null;
                            StringCollection missingFeatures = null;
                            AVT.VmbAPINET.Examples.LoadSaveSettings.LoadFromFile(camera, fileName, out loadedFeatures, out missingFeatures, ignoreStreamable);
                            
                            //Even if we don't get an error there may be features missing
                            //that haven't been restored. Let's print them out.
                            if(missingFeatures.Count > 0)
                            {
                                Console.WriteLine("Settings loaded from file but not all features have be restored.");
                                Console.Write("Missing features: ");

                                bool first = true;
                                foreach(string feature in missingFeatures)
                                {
                                    if(true == first)
                                    {
                                        first = false;
                                    }
                                    else
                                    {
                                        Console.Write(", ");
                                    }

                                    Console.Write(feature);
                                }

                                Console.WriteLine();
                            }
                            else
                            {
                                Console.WriteLine("Settings successfully loaded from file.");
                            }
                        }
                        break;
                    }
                }
                finally
                {
                    if(null != camera)
                    {
                        camera.Close();
                    }
                }
            }
            finally
            {
                vimbaSystem.Shutdown();
            }
        }
        catch(Exception exception)
        {
            Console.WriteLine(exception.Message);
        }
    }
}

}}} // Namespace AVT.VmbAPINET.Examples
