/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of UserSet example of VimbaNET.

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
        Unknown         = 0,
        Save            = 1,
        Load            = 2,
        Count           = 3,
        Index           = 4,
        MakeDefault     = 5,
        IsDefault       = 6,
        ShowData        = 7,
        OperationResult = 8,
        OperationStatus = 9
    };

    static void Main( string[] args )
    {
        string  cameraID = null;
        string  controlIndex = null;
        Mode    usersetMode = Mode.Unknown; 
        bool    printHelp = false;

        try
        {
            Console.WriteLine("//////////////////////////////////////");
            Console.WriteLine("/// AVT Vimba API User Set Example ///");
            Console.WriteLine("//////////////////////////////////////");
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
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.Save;
                    }
                    else if(string.Compare(parameter, "/l", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.Load;
                    }
                    else if (string.Compare(parameter, "/n", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.Count;
                    }
                    else if (string.Compare(parameter, "/i", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.Index;
                    }
                    else if (parameter.StartsWith("/i:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        controlIndex = parameter.Substring(3);

                        if (controlIndex.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }
                    }
                    else if(string.Compare(parameter, "/m", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.MakeDefault;
                    }
                    else if (string.Compare(parameter, "/d", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.IsDefault;
                    }
                    else if (string.Compare(parameter, "/or", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.OperationResult;
                    }
                    else if (string.Compare(parameter, "/os", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != usersetMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        usersetMode = Mode.OperationStatus;
                    }
                    else if (string.Compare(parameter, "/h", StringComparison.Ordinal) == 0)
                    {
                        if ((null != cameraID)
                            || (Mode.Unknown != usersetMode)
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
            Console.WriteLine("Usage: UserSet.exe [CameraID] [/i:Index] [/h] [/{s|l|i|m|d|or|os|n}]");
            Console.WriteLine("Parameters:   CameraID       ID of the camera to use");
            Console.WriteLine("                             (using first camera if not specified)");
            Console.WriteLine("              /i:Index       Set user set index");
            Console.WriteLine("              /h             Print out help");
            Console.WriteLine("              /s             Save user set to flash");
            Console.WriteLine("              /l             Load user set from flash");
            Console.WriteLine("                             (default if not specified)");
            Console.WriteLine("              /i             Get selected user set index");
            Console.WriteLine("              /m             Make user set default");
            Console.WriteLine("              /d             Is user set default");
            Console.WriteLine("              /or            Get user set operation result");
            Console.WriteLine("              /os            Get user set operation status");
            Console.WriteLine("              /n             Get user set count");

            return;
        }

        try
        {
            //Create a new Vimba entry object
            Vimba vimbaSystem = new Vimba();

            //Startup API
            vimbaSystem.Startup();

            try
            {
                Console.WriteLine("Vimba Version V{0:D}.{1:D}.{2:D}",vimbaSystem.Version.major, vimbaSystem.Version.minor, vimbaSystem.Version.patch);
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

                    Examples.UserSetCollection collection = new Examples.UserSetCollection(camera);

                    Int64 nIndex = 0;

                    if(null != controlIndex)
                    {
                        nIndex = Int64.Parse(controlIndex);
                    }
                    else
                    {
                        nIndex = Examples.UserSetCollection.SelectedIndex;
                    }

                    UserSetControl control = null;

                    if ((Mode.Count != usersetMode) && (Mode.Index != usersetMode))
                    {
                        control = collection[nIndex];
                    }

                    switch (usersetMode)
                    {
                    default:
                    case Mode.Load:
                        {
                            //Load user set from flash
                            control.LoadFromFlash();
                            
                            Console.WriteLine("User set successfully loaded from flash.");
                        }
                        break;

                    case Mode.Save:
                        {
                            //Save user set to flash
                            control.SaveToFlash();

                            Console.WriteLine("User set successfully saved to flash.");
                        }
                        break;

                    case Mode.Count:
                        {
                            Int64 nCount = 0;

                            //Clear flash
                            nCount = Examples.UserSetCollection.Count;

                            Console.WriteLine("Get user set count was successful. Count = " + nCount);
                        }
                        break;
                    case Mode.Index:
                        {
                            Int64 nSelectedIndex = 0;

                            //Get selected user set index
                            nSelectedIndex = Examples.UserSetCollection.SelectedIndex;

                            Console.WriteLine("Get selected user set was successful. Index = " + nSelectedIndex);

                        }
                        break;

                    case Mode.MakeDefault:
                        {
                            //Make user set default
                            control.MakeDefault();

                            Console.WriteLine("Make user set default was successful.");                        
                        }
                        break;

                    case Mode.IsDefault:
                        {
                            bool bValue = false;

                            //Is user set default
                            bValue = control.IsDefault;

                            Console.WriteLine("Is user set default was successful. Result = "  + bValue);
                        }
                        break;

                    case Mode.OperationResult:
                        {
                            Int64 nValue = 0;

                            //Get user set operation result
                            nValue = control.OperationResult;

                            Console.WriteLine("Get look up table operation result was successful. Operation Result = " + nValue);
                        }
                        break;

                    case Mode.OperationStatus:
                        {
                            Int64 nValue = 0;

                            //Get user set operation status
                            nValue = control.OperationStatus;

                            Console.WriteLine("Get look up table operation status was successful. Operation Status = " + nValue);
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
