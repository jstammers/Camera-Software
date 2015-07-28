/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        FindCameras.cs

  Description: Find and print a custom string for each known customised camera.

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

namespace AVT {
namespace VmbAPINET {
namespace Examples {

class FindCameras
{
    public static void Print()
    {
        Vimba sys = new Vimba();                // Create a VimbaSystem object. This will be our entry point for everything else
        CameraCollection cameras;               // A list of tracking handles of AVT::VmbAPINET::Camera objects

        string strName;                         // The name of the cam
        string strInfo;                         // The custom information
        VmbInterfaceType interfaceType = VmbInterfaceType.VmbInterfaceUnknown; // The interface type of the cam
        
        try
        {
            sys.Startup();                      // Initialize the Vimba API
            Console.WriteLine("Vimba Version V{0:D}.{1:D}.{2:D}", sys.Version.major,sys.Version.minor,sys.Version.patch);
            sys.CreateCamera += new Vimba.CreateCameraHandler( UserCameraFactory.MyCameraFactory );  // register the CreateCamera function
            cameras = sys.Cameras;              // Fetch all cameras known to Vimba

            Console.WriteLine( "Cameras found: " + cameras.Count );
            Console.WriteLine();

            // Query the name and interface of all known cameras and print them out.
            // We don't have to open the cameras for that.
            foreach (Camera camera in cameras)
            {
                try
                {
                    strName = camera.Name;
                }
                catch ( VimbaException ve )
                {
                    strName = ve.Message;
                }

                try
                {
                    interfaceType = camera.InterfaceType;
                
                    strInfo = "none";
                    switch (interfaceType)
                    {
                        case VmbInterfaceType.VmbInterfaceFirewire:
                        {
                            FirewireCamera fcam = (FirewireCamera)camera;
                            fcam.addonFirewire(strInfo);
                            break;
                        }
                        case VmbInterfaceType.VmbInterfaceEthernet:
                        {
                            GigECamera gcam = (GigECamera)camera;
                            gcam.addonGigE(strInfo);
                            break;
                        }
                        case VmbInterfaceType.VmbInterfaceUsb:
                        {
                            USBCamera ucam = (USBCamera)camera;
                            ucam.addonUSB(strInfo);
                            break;
                        }
                        default:
                        {
                            break;
                        }
                    }
                }
                catch (Exception ve)
                {
                    strInfo = ve.Message;
                }

                Console.WriteLine( "/// Camera Name: " + strName );
                Console.WriteLine( "/// Custom Info: " + strInfo );
                Console.WriteLine();
            }
        }
        finally
        {
            sys.Shutdown();
        }
    }
}

}}} // Namespace AVT::Vimba::Exanples