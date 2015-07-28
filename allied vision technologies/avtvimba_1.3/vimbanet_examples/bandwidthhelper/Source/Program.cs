/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of BandwidthHelper example of VimbaNET.

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
using System.Globalization;

using AVT.VmbAPINET;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

enum SettingsMode
{
    Unknown = 0,
    Get = 1,
    Set = 2,
    GetMin = 3,
    GetMax = 4
};

class Program
{
    static void Main( string[] args )
    {
        string cameraID = null;
        double fValue = 0.0;
        SettingsMode settingsMode = SettingsMode.Unknown;
        bool printHelp = false;

        Console.WriteLine();
        Console.WriteLine( "//////////////////////////////////////////////" );
        Console.WriteLine( "/// AVT Vimba API Bandwidth Helper Example ///" );
        Console.WriteLine( "//////////////////////////////////////////////" );
        Console.WriteLine();

        #region ParseCommandLine        
        //////////////////////
        //Parse command line//
        //////////////////////
        try
        {
            if ( 3 < args.Length )
            {
                printHelp = true;
                throw new ArgumentException("Invalid parameter found.");
            }

            foreach(string parameter in args)
            {
                if(parameter.Length <= 0)
                {
                    throw new ArgumentException("Invalid parameter found.");
                }

                if(parameter.StartsWith("/"))
                {
                    if(string.Compare(parameter, "/g", StringComparison.Ordinal) == 0)
                    {
                        if(SettingsMode.Unknown != settingsMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        settingsMode = SettingsMode.Get;
                    }
                    else if(parameter.StartsWith("/s:"))
                    {
                        if(SettingsMode.Unknown != settingsMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }
                        settingsMode = SettingsMode.Set;
                        fValue = Double.Parse(parameter.Substring(3), CultureInfo.InvariantCulture) / 100;
                    }
                    else if(string.Compare(parameter, "/h", StringComparison.Ordinal) == 0)
                    {
                        if( true == printHelp )
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        printHelp = true;
                    }
                    else if(string.Compare(parameter, "/min", StringComparison.Ordinal) == 0)
                    {
                        if(SettingsMode.Unknown != settingsMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        settingsMode = SettingsMode.GetMin;
                    }
                    else if(string.Compare(parameter, "/max", StringComparison.Ordinal) == 0)
                    {
                        if(SettingsMode.Unknown != settingsMode)
                        {
                            throw new ArgumentException("Invalid parameter found.");
                        }

                        settingsMode = SettingsMode.GetMax;
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

        // Print out help and exit
        if(true == printHelp)
        {
            Console.WriteLine("Gets or sets the current bandwidth as percentage of the theoretically possible bandwidth.");
            Console.WriteLine("Usage: BandwidthHelper.exe [CameraID] [/h] [/{g|s:val|min|max}]");
            Console.WriteLine("Parameters:   CameraID    ID of the camera to use (using first camera if not specified)");
            Console.WriteLine("              /h          Print out help");
            Console.WriteLine("              /g          Get bandwidth usage (default if not specified)");
            Console.WriteLine("              /s:val      Set bandwidth usage to <val> % of the maximum bandwidth");
            Console.WriteLine("              /min        Get minimal possible bandwidth usage");
            Console.WriteLine("              /max        Get maximal possible bandwidth usage");
            Console.WriteLine();

            return;
        }
        #endregion

        try
        {
            // Get a reference to the VimbaSystem singleton
            Vimba system = new Vimba();

            // Startup API
            system.Startup();
            Console.WriteLine("Vimba Version V{0:D}.{1:D}.{2:D}",system.Version.major,system.Version.minor,system.Version.patch);
            try
            {
                // Open camera
                Camera camera = null;
                try
                {
                    // Open first available camera
                    if ( null == cameraID )
                    {
                        // Fetch all cameras known to Vimba
                        CameraCollection cameras = system.Cameras;

                        if(0 >= cameras.Count)
                        {
                            throw new Exception("No camera available.");
                        }
                    
                        foreach ( Camera c in cameras )
                        {
                            // Check if we can open the camera in full mode
                            VmbAccessModeType accessMode = VmbAccessModeType.VmbAccessModeNone;
                            accessMode = c.PermittedAccess;
                            
                            if(VmbAccessModeType.VmbAccessModeFull == (accessMode & VmbAccessModeType.VmbAccessModeFull))
                            {
                                // Now get the camera ID
                                cameraID = c.Id;

                                //Try to open the camera
                                try
                                {
                                    c.Open(VmbAccessModeType.VmbAccessModeFull);
                                }
                                catch
                                {
                                    //We can ignore this exception because we simply try
                                    //to open the next camera.
                                    continue;
                                }

                                camera = c;
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
                        camera = system.OpenCameraByID(cameraID, VmbAccessModeType.VmbAccessModeFull);
                    }

                    try
                    {
                        // Get camera name and interface type
                        Console.WriteLine("Successfully opened " + camera.InterfaceType + " camera " + camera.Name + " (" + camera.Id + ") ");
                    }
                    catch
                    {
                        // If we cannot get the name and interface type we simply print out the ID
                        Console.WriteLine("Successfully opened camera ( " + camera.Id + ") ");
                    }

                    switch( settingsMode )
                    {
                        default:
                        case SettingsMode.Get:
                        {
                            // Get bandwidth
                            fValue = BandwidthHelper.GetBandwidthUsage(camera);
                            Console.WriteLine("Bandwidth usage: " + (fValue * 100).ToString(CultureInfo.InvariantCulture) + "%" );
                        }
                        break;

                        case SettingsMode.Set:
                        {
                            // Set bandwidth
                            BandwidthHelper.SetBandwidthUsage( camera, fValue );
                            // Read written value back
                            fValue = BandwidthHelper.GetBandwidthUsage(camera);
                            Console.WriteLine("Bandwidth usage successfully set to: " + (fValue * 100).ToString(CultureInfo.InvariantCulture) + "%");
                        }
                        break;

                        case SettingsMode.GetMin:
                        {
                            // Get bandwidth
                            fValue = BandwidthHelper.GetMinPossibleBandwidthUsage(camera);
                            Console.WriteLine("Minimal possible bandwidth usage: " + (fValue * 100).ToString(CultureInfo.InvariantCulture) + "%" );
                        }
                        break;

                        case SettingsMode.GetMax:
                        {
                            // Get bandwidth
                            fValue = BandwidthHelper.GetMaxPossibleBandwidthUsage(camera);
                            Console.WriteLine("Maximal possible bandwidth usage: " + (fValue * 100).ToString(CultureInfo.InvariantCulture) + "%" );
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
                system.Shutdown();
            }
        }
        catch (VimbaException ve)
        {
            Console.WriteLine(ve.Message);
            Console.Write("Return Code: " + ve.ReturnCode.ToString() + " (" + ve.MapReturnCodeToString() + ")");            
        }
        catch (Exception e)
        {
            Console.WriteLine(e.Message);
        }

        Console.WriteLine();
    }
}

}}} // Namespace AVT::Vimba::Exanples
