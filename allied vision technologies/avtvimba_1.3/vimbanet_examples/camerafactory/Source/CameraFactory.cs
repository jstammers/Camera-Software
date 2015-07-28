/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        CameraFactory.cs

  Description: The CameraFactory example will create a suitable object for
               each known interface. The user can create his own factory and 
               camera classes for customisation.

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

using AVT.VmbAPINET;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

public class FirewireCamera: Camera
{
    public FirewireCamera(  string cameraID,
                            string cameraName,
                            string cameraModel,
                            string cameraSerialNumber,
                            string interfaceID,
                            VmbInterfaceType interfaceType,
                            string interfaceName,
                            string interfaceSerialNumber,
                            VmbAccessModeType interfacePermittedAccess)
        : base( cameraID,
                cameraName,
                cameraModel,
                cameraSerialNumber,
                interfaceID,
                interfaceType,
                interfaceName,
                interfaceSerialNumber,
                interfacePermittedAccess)
    {
    }

    public void addonFirewire(string info)  // custom camera function
    {
        info = "1394 interface connection detected";
    }
};  

class GigECamera: Camera
{
    public GigECamera(  string cameraID,
                        string cameraName,
                        string cameraModel,
                        string cameraSerialNumber,
                        string interfaceID,
                        VmbInterfaceType interfaceType,
                        string interfaceName,
                        string interfaceSerialNumber,
                        VmbAccessModeType interfacePermittedAccess)
        : base( cameraID,
                cameraName,
                cameraModel,
                cameraSerialNumber,
                interfaceID,
                interfaceType,
                interfaceName,
                interfaceSerialNumber,
                interfacePermittedAccess)
    {
    }

    public void addonGigE(string info)  // custom camera function
    {
        info = "ethernet interface connection detected";
    }
};  

class USBCamera: Camera
{
    public USBCamera(   string cameraID,
                        string cameraName,
                        string cameraModel,
                        string cameraSerialNumber,
                        string interfaceID,
                        VmbInterfaceType interfaceType,
                        string interfaceName,
                        string interfaceSerialNumber,
                        VmbAccessModeType interfacePermittedAccess)
        : base( cameraID,
                cameraName,
                cameraModel,
                cameraSerialNumber,
                interfaceID,
                interfaceType,
                interfaceName,
                interfaceSerialNumber,
                interfacePermittedAccess)
    {
    }

    public void addonUSB(string info)  // custom camera function
    {
        info = "usb interface connection detected";
    }
}

// class to give possiblility to create standart camera
class DefaultCamera : Camera
{
    public DefaultCamera(string cameraID,
                         string cameraName,
                         string cameraModel,
                         string cameraSerialNumber,
                         string interfaceID,
                         VmbInterfaceType interfaceType,
                         string interfaceName,
                         string interfaceSerialNumber,
                         VmbAccessModeType interfacePermittedAccess)
            : base( cameraID,
                    cameraName,
                    cameraModel,
                    cameraSerialNumber,
                    interfaceID,
                    interfaceType,
                    interfaceName,
                    interfaceSerialNumber,
                    interfacePermittedAccess)
    {
    }
}

public class UserCameraFactory
{
    static public Camera MyCameraFactory(   string cameraID,
                                            string cameraName,
                                            string cameraModel,
                                            string cameraSerialNumber,
                                            string interfaceID,
                                            VmbInterfaceType interfaceType,
                                            string interfaceName,
                                            string interfaceSerialNumber,
                                            VmbAccessModeType interfacePermittedAccess)
    {
        // create camera class, depending on camera interface type
        if (VmbInterfaceType.VmbInterfaceFirewire == interfaceType)
        {
            return new FirewireCamera(cameraID, 
                                      cameraName, 
                                      cameraModel, 
                                      cameraSerialNumber, 
                                      interfaceID, 
                                      interfaceType, 
                                      interfaceName, 
                                      interfaceSerialNumber, 
                                      interfacePermittedAccess);
        }
        else if (VmbInterfaceType.VmbInterfaceEthernet == interfaceType)
        {
            return new GigECamera(cameraID, 
                                  cameraName, 
                                  cameraModel, 
                                  cameraSerialNumber, 
                                  interfaceID, 
                                  interfaceType, 
                                  interfaceName, 
                                  interfaceSerialNumber, 
                                  interfacePermittedAccess);
        }
        else if (VmbInterfaceType.VmbInterfaceUsb == interfaceType)
        {
            return new USBCamera(cameraID, 
                                 cameraName, 
                                 cameraModel, 
                                 cameraSerialNumber, 
                                 interfaceID, 
                                 interfaceType, 
                                 interfaceName, 
                                 interfaceSerialNumber, 
                                 interfacePermittedAccess);
        }
        else // unknown camera interface
        {
            // use default camera class
            return new DefaultCamera(cameraID, 
                                     cameraName, 
                                     cameraModel, 
                                     cameraSerialNumber, 
                                     interfaceID, 
                                     interfaceType, 
                                     interfaceName, 
                                     interfaceSerialNumber, 
                                     interfacePermittedAccess);
        }   
    }
}

}}} // Namespace AVT::Vimba::Exanples