/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        ListCameras.cs

  Description: The ListCameras example will list all available cameras that
               are found by VimbaNET.

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

class ListCameras
{
    public static void Print()
    {
        Vimba sys = new Vimba();                // Create a VimbaSystem object. This will be our entry point for everything else
        CameraCollection cameras;               // A list of tracking handles of AVT::VmbAPINET::Camera objects

        string strID;                           // The ID of the cam
        string strName;                         // The name of the cam
        string strModelname;                    // The model name of the cam
        string strSerialNumber;                 // The serial number of the cam
        string strInterfacaeID;                 // The ID of the interface the cam is connected to

        try
        {
            sys.Startup();                      // Initialize the Vimba API
            Console.WriteLine("Vimba Version V{0:D}.{1:D}.{2:D}",sys.Version.major,sys.Version.minor,sys.Version.patch);
            cameras = sys.Cameras;              // Fetch all cameras known to Vimba

            Console.WriteLine( "Cameras found: " + cameras.Count );
            Console.WriteLine();

            // Query all static details of all known cameras and print them out.
            // We don't have to open the cameras for that.
            foreach (Camera camera in cameras)
            {
                try
                {
                    strID = camera.Id;
                }
                catch ( VimbaException ve )
                {
                    strID = ve.Message;
                }

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
                    strModelname = camera.Model;
                }
                catch ( VimbaException ve )
                {
                    strModelname = ve.Message;
                }

                try
                {
                    strSerialNumber = camera.SerialNumber;
                }
                catch ( VimbaException ve )
                {
                    strSerialNumber = ve.Message;
                }

                try
                {
                    strInterfacaeID = camera.InterfaceID;
                }
                catch ( VimbaException ve )
                {
                    strInterfacaeID = ve.Message;
                }

                Console.WriteLine( "/// Camera Name: " + strName );
                Console.WriteLine( "/// Model Name: " + strModelname );
                Console.WriteLine( "/// Camera ID: " + strID );
                Console.WriteLine( "/// Serial Number: " + strSerialNumber );
                Console.WriteLine( "/// @ Interface ID: " + strInterfacaeID );
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