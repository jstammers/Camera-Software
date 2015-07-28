/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        ListFeatures.cs

  Description: The ListFeatures example will list all available features of a
               camera that are found by VimbaNET.

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

class ListFeatures
{
    public static void Print( string strID )
    {
        Vimba sys = new Vimba();                // Create a VimbaSystem object. This will be our entry point for everything else
        Camera camera;                          // Our camera
        FeatureCollection features;             // A list of camera features

        // The static details of a feature
        string strName;                         // The name of the feature
        string strDisplayName;                  // The display name of the feature
        string strTooltip;                      // A short description of the feature
        string strDescription;                  // A long description of the feature
        string strCategory;                     // A category to group features
        string strSFNCNamespace;                // The Standard Feature Naming Convention namespace
        string strUnit;                         // The measurement unit of the value

        // The changeable value of a feature
        object value;                           // A float, int, string or any other value

        try
        {
            sys.Startup();                                                                  // Initialize the Vimba API
            Console.WriteLine("Vimba Version V{0:D}.{1:D}.{2:D}", sys.Version.major, sys.Version.minor, sys.Version.patch);
            if (    null == strID                                                           // If no ID was provided use the first camera
                 && 0 < sys.Cameras.Count )
            {
                camera = sys.Cameras[0];                                                    // Get the camera
                camera.Open( VmbAccessModeType.VmbAccessModeFull );                         // Open the camera
            }
            else
            {
                camera = sys.OpenCameraByID( strID, VmbAccessModeType.VmbAccessModeFull );  // Get and open the camera
            }

            try
            {
                features = camera.Features;                                                 // Fetch all features of our cam

                // Query all static details as well as the value of all fetched features and print them out.
                foreach ( Feature feature in features )
                {
                    try
                    {
                        strName = feature.Name;
                    }
                    catch ( VimbaException ve )
                    {
                        strName = ve.Message;
                    }

                    try
                    {
                        strDisplayName = feature.DisplayName;
                    }
                    catch ( VimbaException ve )
                    {
                        strDisplayName = ve.Message;
                    }

                    try
                    {
                        strTooltip = feature.ToolTip;
                    }
                    catch ( VimbaException ve )
                    {
                        strTooltip = ve.Message;
                    }

                    try
                    {
                        strDescription = feature.Description;
                    }
                    catch ( VimbaException ve )
                    {
                        strDescription = ve.Message;
                    }

                    try
                    {
                        strCategory = feature.Category;
                    }
                    catch ( VimbaException ve )
                    {
                        strCategory = ve.Message;
                    }

                    try
                    {
                        strSFNCNamespace = feature.SFNCNamespace;
                    }
                    catch ( VimbaException ve )
                    {
                        strSFNCNamespace = ve.Message;
                    }

                    try
                    {
                        strUnit = feature.Unit;
                    }
                    catch ( VimbaException ve )
                    {
                        strUnit = ve.Message;
                    }

                    try
                    {                     
                        switch ( feature.DataType )
                        {
                            case VmbFeatureDataType.VmbFeatureDataBool:     value = feature.BoolValue;
                                break;
                            case VmbFeatureDataType.VmbFeatureDataCommand:  value = null;
                                break;
                            case VmbFeatureDataType.VmbFeatureDataEnum:     value = feature.EnumValue;
                                break;
                            case VmbFeatureDataType.VmbFeatureDataFloat:    value = feature.FloatValue;
                                break;
                            case VmbFeatureDataType.VmbFeatureDataInt:      value = feature.IntValue;
                                break;                            
                            case VmbFeatureDataType.VmbFeatureDataString:   value = feature.StringValue;
                                break;
                            default:                                        value = null;
                                break;
                        }
                    }
                    catch ( VimbaException ve )
                    {
                        value = ve.Message;
                    }

                    Console.WriteLine( "/// Feature Name: " + strName );
                    Console.WriteLine( "/// Display Name: " + strDisplayName );
                    Console.WriteLine( "/// Tooltip: " + strTooltip );
                    Console.WriteLine( "/// Description: " + strDescription );
                    Console.WriteLine( "/// SNFC Namespace: " + strSFNCNamespace );
                    if ( null != value )
                    {
                        Console.WriteLine(" /// Value: " + value.ToString() + " " + strUnit );
                    }
                    else
                    {
                        Console.WriteLine(" /// Value: [None]" );
                    }
                    Console.WriteLine();
                }
            }
            finally
            {
                camera.Close();
            }
        }
        finally
        {
            sys.Shutdown();
        }
    }
}

}}} // Namespace AVT::Vimba::Exanples