/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of ShadingData example of VimbaNET.

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
    enum Mode
    {
        Unknown     = 0,
        Save        = 1,
        Load        = 2,
        Clear       = 3,
        Build       = 4,
        Enable      = 5,
        IsEnabled   = 6,
        ShowData    = 7,
        IsDataShown = 8
    };

    static void Main( string[] args )
    {
        string  cameraID = null;
        Int64   nValue = 0;
        bool    bValue = false;
        string  cmdParam = null;
        Mode    shadingMode = Mode.Unknown; 
        bool    printHelp = false;

        try
        {
            Console.WriteLine("//////////////////////////////////////////");
            Console.WriteLine("/// AVT Vimba API Shading Data Example ///"); 
            Console.WriteLine("//////////////////////////////////////////");
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
                        if(Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        shadingMode = Mode.Save;
                    }
                    else if(string.Compare(parameter, "/l", StringComparison.Ordinal) == 0)
                    {
                        if(Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        shadingMode = Mode.Load;
                    }
                    else if (string.Compare(parameter, "/c", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        shadingMode = Mode.Clear;
                    }
                    else if (parameter.StartsWith("/b:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        cmdParam = parameter.Substring(3);

                        if (cmdParam.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        nValue = Int64.Parse(cmdParam);
                        
                        shadingMode = Mode.Build;
                    }
                    else if (parameter.StartsWith("/e:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        cmdParam = parameter.Substring(3);

                        if (cmdParam.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        if (cmdParam == "on")
                        {
                            bValue = true;
                        }
                        else if (cmdParam == "off")
                        {
                            bValue = false;
                        }
                        else
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        shadingMode = Mode.Enable;
                    }
                    else if(string.Compare(parameter, "/e", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        shadingMode = Mode.IsEnabled;
                    }
                    else if (parameter.StartsWith("/p:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        cmdParam = parameter.Substring(3);

                        if (cmdParam.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        if (cmdParam == "on")
                        {
                            bValue = true;
                        }
                        else if (cmdParam == "off")
                        {
                            bValue = false;
                        }
                        else
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        shadingMode = Mode.ShowData;
                    }
                    else if(string.Compare(parameter, "/p", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != shadingMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }
                        
                        shadingMode = Mode.IsDataShown;
                    }
                    else if (string.Compare(parameter, "/h", StringComparison.Ordinal) == 0)
                    {
                        if ((null != cameraID)
                            || (Mode.Unknown != shadingMode)
                            || (true == printHelp))
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        printHelp = true;
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
            Console.WriteLine("Usage: ShadingData.exe [CameraID] [/h] [/{s|l|c|b:ImageCount|e(:Enable)|v(:ShowData)}]");
            Console.WriteLine("Parameters:   CameraID       ID of the camera to use");
            Console.WriteLine("                             (using first camera if not specified)");
            Console.WriteLine("              /h             Print out help");
            Console.WriteLine("              /s             Save shading data to flash");
            Console.WriteLine("              /l             Load shading data from flash");
            Console.WriteLine("                             (default if not specified)");
            Console.WriteLine("              /c             Clear shading data from flash");
            Console.WriteLine("              /b:ImageCount  Build shading data with image count");
            Console.WriteLine("              /e             Is shading data enabled");
            Console.WriteLine("              /e:Enable      Enable shading data [on/off]");
            Console.WriteLine("              /p             Is shading data shown");
            Console.WriteLine("              /p:ShowData    Show shading data [on/off]");

            return;
        }

        try
        {
            //Create a new Vimba entry object
            Vimba vimbaSystem = new Vimba();

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
                        CameraCollection cameras = vimbaSystem.Cameras;
                        if(cameras.Count < 0)
                        {
                            throw new Exception("No camera available.");
                        }

                        foreach(Camera currentCamera in cameras)
                        {
                            //Check if we can open the camera in full mode
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

                    Console.WriteLine("Camera ID: " + cameraID);
                    Console.WriteLine();

                    Examples.ShadingDataControl control = new Examples.ShadingDataControl(camera);

                    switch(shadingMode)
                    {
                    default:
                    case Mode.Load:
                        {
                            //Load shading data from flash
                            Examples.ShadingDataControl.LoadFromFlash();
                            
                            Console.WriteLine("Shading data successfully loaded from flash.");
                        }
                        break;

                    case Mode.Save:
                        {
                            //Save settings to flash
                            Examples.ShadingDataControl.SaveToFlash();

                            Console.WriteLine("Shading data successfully saved to flash.");
                        }
                        break;

                    case Mode.Clear:
                        {
                            //Clear flash
                            Examples.ShadingDataControl.ClearFlash();

                            Console.WriteLine("Shading data successfully cleared from flash.");
                        }
                        break;
                    case Mode.Build:
                        {
                            //Build shading data with image count
                            Examples.ShadingDataControl.BuildImages(nValue);

                            Console.WriteLine("Shading data successfully built.");

                        }
                        break;

                    case Mode.IsEnabled:
                        {
                            //Is shading data enabled
                            bValue = Examples.ShadingDataControl.IsEnabled;

                            Console.WriteLine("Shading data enable state requested successfully. Enable = " + bValue);                        
                        }
                        break;

                    case Mode.Enable:
                        {
                            //Enable shading data
                            Examples.ShadingDataControl.Enable = bValue;

                            Console.WriteLine("Shading data enable state was set successfully.");
                        }
                        break;

                    case Mode.IsDataShown:
                        {
                            //Is shading data data shown
                            bValue = Examples.ShadingDataControl.IsDataShown;

                            Console.WriteLine("Shading data shown state requested successfully. DataShown = " + bValue);
                        }
                        break;

                    case Mode.ShowData:
                        {
                            //Show shading data
                            Examples.ShadingDataControl.ShowData = bValue;

                            Console.WriteLine("Shading data show state was set successfully.");
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
        catch (VimbaException ex)
        {
            Console.WriteLine("VimbaException: " + ex.ReturnCode + " = " + ex.MapReturnCodeToString());
        }
        catch(Exception exception)
        {
            Console.WriteLine(exception.Message);
        }
    }
}

}}} // Namespace AVT.VmbAPINET.Examples
