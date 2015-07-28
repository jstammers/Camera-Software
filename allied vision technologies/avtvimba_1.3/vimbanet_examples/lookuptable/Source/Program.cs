/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of LookUpTable example of VimbaNET.

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
        SaveCSV         = 3,
        LoadCSV         = 4,
        Enable          = 7,
        IsEnabled       = 8,
        SetValue        = 9,
        GetValue        = 10,
        BitIn           = 11,
        BitOut          = 12,
        Count           = 13
    };

    static void Main( string[] args )
    {
        string  cameraID = null;
        string  fileName = null;
        string  controlIndex = null;
        Int64   nValue = 0;
        bool    bValue = false;
        string  cmdParam = null;
        Mode    lutMode = Mode.Unknown; 
        bool    printHelp = false;

        try
        {
            Console.WriteLine("///////////////////////////////////////////");
            Console.WriteLine("/// AVT Vimba API Look Up Table Example ///");
            Console.WriteLine("///////////////////////////////////////////");
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
                    if(string.Compare(parameter, "/sc", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.SaveCSV;
                    }
                    else if (parameter.StartsWith("/lc:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        cmdParam = parameter.Substring(4);

                        if (cmdParam.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        nValue = Int64.Parse(cmdParam);

                        lutMode = Mode.LoadCSV;
                    }
                    else if (string.Compare(parameter, "/s", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.Save;
                    }
                    else if (string.Compare(parameter, "/l", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.Load;
                    }
                    else if (string.Compare(parameter, "/bi", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.BitIn;
                    }
                    else if (string.Compare(parameter, "/bo", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.BitOut;
                    }
                    else if (string.Compare(parameter, "/n", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.Count;
                    }
                    else if (parameter.StartsWith("/e:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != lutMode)
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

                        lutMode = Mode.Enable;
                    }
                    else if (string.Compare(parameter, "/e", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.IsEnabled;
                    }
                    else if (parameter.StartsWith("/v:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        cmdParam = parameter.Substring(3);

                        if (cmdParam.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        nValue = Int64.Parse(cmdParam);

                        lutMode = Mode.SetValue;
                    }
                    else if (string.Compare(parameter, "/v", StringComparison.Ordinal) == 0)
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        lutMode = Mode.GetValue;
                    }
                    else if (parameter.StartsWith("/f:", StringComparison.Ordinal))
                    {
                        if ((Mode.Unknown != lutMode) &&
                            (Mode.SaveCSV != lutMode) &&
                            (Mode.LoadCSV != lutMode))
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        fileName = parameter.Substring(3);

                        if (fileName.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                    }
                    else if (parameter.StartsWith("/i:", StringComparison.Ordinal))
                    {
                        if (Mode.Unknown != lutMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        controlIndex = parameter.Substring(3);

                        if (controlIndex.Length <= 0)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }
                    }
                    else if (string.Compare(parameter, "/h", StringComparison.Ordinal) == 0)
                    {
                        if ((null != cameraID)
                            || (Mode.Unknown != lutMode)
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

            Console.WriteLine("Usage: LookUpTable.exe [CameraID] [/i:Index] [/h] [/{s|l|sc|lc:Column|u|d|v(:Value)|e(:Enable)|bi|bo|n}] [/f:FileName]");
            Console.WriteLine("Parameters:   CameraID       ID of the camera to use");
            Console.WriteLine("                             (using first camera if not specified)");
            Console.WriteLine("              /i:Index       Set look up table index");
            Console.WriteLine("              /h             Print out help");
            Console.WriteLine("              /s             Save look up table to flash");
            Console.WriteLine("              /l             Load look up table from flash");
            Console.WriteLine("              /sc            Save look up table to Csv");
            Console.WriteLine("                             (Look up table previously downloaded)");
            Console.WriteLine("              /lc:Column     Load look up table from Csv using specified column");
            Console.WriteLine("                             (Look up table uploaded afterwards)");
            Console.WriteLine("              /e:Enable      Set look up table enable [on/off]");
            Console.WriteLine("              /e             Get look up table enable");
            Console.WriteLine("                             (default if not specified)");
            Console.WriteLine("              /v:Value       Set look up table value");
            Console.WriteLine("              /v             Get look up table value");
            Console.WriteLine("              /bi            Get look up table bit depth in");
            Console.WriteLine("              /bo            Get look up table bit depth out");
            Console.WriteLine("              /n             Get look up table count");
            Console.WriteLine("              /f:FileName    File name for operation");
            Console.WriteLine();
            Console.WriteLine("For example to load a look up table from the csv file C:\\lut.csv and \nwrite it to the camera's flash as LUT1 call\n");
            Console.WriteLine("LookUpTable.exe /i:0 /lc:0 /f:\"C:\\lut.csv\"\n");
            Console.WriteLine("To load the look up table LUT2 from the camera and write it \nto the csv file C:\\lut.csv call\n");
            Console.WriteLine("LookUpTable.exe /i:1 /sc /f:\"C:\\lut.csv\"\n");
            Console.WriteLine();

            return;
        }

        try
        {
            //Create a new Vimba entry object
            Vimba vimbaSystem = new Vimba();

            //Startup API
            vimbaSystem.Startup();
            Console.WriteLine("Vimba Version V{0:D}.{1:D}.{2:D}",vimbaSystem.Version.major, vimbaSystem.Version.minor, vimbaSystem.Version.patch);
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

                    Examples.LookUpTableCollection collection = new Examples.LookUpTableCollection(camera);

                    Int64 nIndex = 0;

                    if(null != controlIndex)
                    {
                        nIndex = Int64.Parse(controlIndex);
                    }
                    else
                    {
                        nIndex = Examples.LookUpTableCollection.ActiveIndex;
                    }

                    LookUpTableControl control = collection[nIndex];

                    switch(lutMode)
                    {
                    default:
                    case Mode.IsEnabled:
                        {
                            //Is look up table enabled
                            bool bEnable;
                            bEnable = control.IsEnabled;

                            Console.WriteLine("Get look up table enable was successful. Enable = " + bEnable);
                        }
                        break;

                    case Mode.Save:
                        {
                            //Save look up table to flash
                            control.SaveToFlash();

                            Console.WriteLine("Look up table successfully saved to flash.");
                        }
                        break;

                    case Mode.Load:
                        {
                            //Load look up table from flash
                            control.LoadFromFlash();

                            Console.WriteLine("Look up table successfully loaded from flash.");
                        }
                        break;

                    case Mode.SaveCSV:
                        {
                            //Download LUT        
                            control.Download();

                            //Save look up table to CSV
                            control.SaveToCsv(fileName);

                            Console.WriteLine("Look up table successfully saved to CSV.");
                        }
                        break;

                    case Mode.LoadCSV:
                        {
                            //Load look up table from CSV
                            control.LoadFromCsv(fileName, (int)nValue);

                            //Upload LUT        
                            control.Upload();

                            Console.WriteLine("Look up table successfully loaded from CSV.");
                        }
                        break;

                    case Mode.Enable:
                        {
                            //Set look up table enable
                            control.Enable(bValue);

                            Console.WriteLine("Look up table was successfully enabled.");
                        }
                        break;

                    case Mode.BitIn:
                        {
                            //Get bit depth in of look up table
                            Int64 nBitDepthIn;
                            nBitDepthIn = control.BitDepthIn;

                            Console.WriteLine("Get look up table 'bit depth in' was successful. BitDepthIn = " + nBitDepthIn);
                        }
                        break;

                    case Mode.BitOut:
                        {
                            //Get bit depth out of look up table
                            Int64 nBitDepthOut;
                            nBitDepthOut = control.BitDepthOut;

                            Console.WriteLine("Get look up table 'bit depth out' was successful. BitDepthOut = " + nBitDepthOut);
                        }
                        break;

                    case Mode.SetValue:
                        {
                            //Set look up table value
                            control.Value = nValue;

                            Console.WriteLine("Look up table value was set successfully.");
                        }
                        break;

                    case Mode.GetValue:
                        {
                            //Get look up table value
                            nValue = control.Value;

                            Console.WriteLine("Get look up table value was successful. Value = " + nValue);
                        }
                        break;

                    case Mode.Count:
                        {
                            //Get look up table count
                            Int64 nCount = 0;
                            nCount = Examples.LookUpTableCollection.Count;

                            Console.WriteLine("Get look up table count was successful. Count = " + nCount);
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
