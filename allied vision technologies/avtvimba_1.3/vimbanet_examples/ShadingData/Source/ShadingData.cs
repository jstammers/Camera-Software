/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        ShadingData.cs

  Description: The ShadingData example will demonstrate how to use
               the shading data feature of the camera using VimbaNET.
               

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

class ShadingDataControl
{
    private static Camera m_camera;
    private static Byte[] m_data;

    public ShadingDataControl(Camera camera)
    {
        //Check parameters
        if (null == camera)
        {
            throw new ArgumentNullException("camera");
        }

        m_camera = camera;
    }

    //Save shading data to flash
    public static void SaveToFlash()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["ShadingDataSaveToFlash"];
        feature.RunCommand();
    }

    //Load shading data from flash
    public static void LoadFromFlash()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["ShadingDataLoadFromFlash"];
        feature.RunCommand();
    }

    //Clear shading data from flash
    public static void ClearFlash()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["ShadingDataClearFlash"];
        feature.RunCommand();
    }

    //Build shading data with image count
    public static void BuildImages(Int64 nImageCount)
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["ShadingBuildImages"];
        feature.IntValue = nImageCount;

        feature = features["ShadingDataBuild"];
        feature.RunCommand();
    }

    //Is shading data enabled
    public static bool IsEnabled
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["ShadingCorrectionEnable"];
            return feature.BoolValue;
        }
    }

    //Enable shading data
    public static bool Enable
    {
        set
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["ShadingCorrectionEnable"];
            feature.BoolValue = value;
        }
    }

    //Is shading data shown
    public static bool IsDataShown
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;
            feature = features["ShadingCorrectionShowData"];
            return feature.BoolValue;
        }
    }

    //Show shading data
    public static bool ShowData
    {
        set
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;
            feature = features["ShadingCorrectionShowData"];
            feature.BoolValue = value;
        }
    }

    //Get/Set raw data
    public static Byte[] RawData
    {
        get
        {
            return m_data;
        }
        set
        {
            m_data = value;
        }
    }

    //Upload shading data
    public static void Upload()
    {
        //Raw data empty
        if (0 == m_data.Length)
        {
            string output = "Shading data upload. Error code: " + ((int)VmbErrorType.VmbErrorOther);
            throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
        }

        FeatureCollection features = null;
        Feature fileOperationSelector = null;
        Feature fileOperationExecute = null;
        Feature fileOpenMode = null;
        Feature fileAccessBuffer = null;
        Feature fileAccessOffset = null;
        Feature fileAccessLength = null;
        Feature fileOperationStatus = null;
        Feature fileOperationResult = null;
        Feature fileStatus = null;
        Feature fileSize = null;
        Feature fileSelector = null;

        features = m_camera.Features;

        fileOperationSelector = features["FileOperationSelector"];
        fileOperationExecute = features["FileOperationExecute"];
        fileOpenMode = features["FileOpenMode"];
        fileAccessBuffer = features["FileAccessBuffer"];
        fileAccessOffset = features["FileAccessOffset"];
        fileAccessLength = features["FileAccessLength"];
        fileOperationStatus = features["FileOperationStatus"];
        fileOperationResult = features["FileOperationResult"];
        fileStatus = features["FileStatus"];
        fileSize = features["FileSize"];
        fileSelector = features["FileSelector"];

        fileSelector.EnumValue = "ShadingData";

        fileOpenMode.EnumValue = "Write";

        fileOperationSelector.EnumValue = "Open";

        fileOperationExecute.RunCommand();

        Int64 nFileSize = fileSize.IntValue;

        Int64 nMaxFileAccessLength = fileAccessLength.IntRangeMax;

        fileOperationSelector.EnumValue = "Write";

        Int64  nFileAccessOffset = 0;
        Int64  nFileAccessLength = Math.Min(nFileSize, nMaxFileAccessLength);
        byte[] data = new byte[nFileAccessLength];
        string LUTOperationStatus;

        do
        {
            fileAccessLength.IntValue = nFileAccessLength;

            m_data.CopyTo(data, nFileAccessOffset);
            
            fileAccessBuffer.RawValue = data;

            fileOperationExecute.RunCommand();

            LUTOperationStatus = fileOperationStatus.EnumValue;

            if (!LUTOperationStatus.Equals("Success"))
            {
                string output = "FileOperation " + fileOperationSelector.EnumValue + " failed";
                throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
            }

            nFileAccessOffset = fileAccessOffset.IntValue;

            nFileAccessLength = Math.Min(nFileSize - nFileAccessOffset, nMaxFileAccessLength);
        }
        while (nFileSize != nFileAccessOffset);

        fileOperationSelector.EnumValue = "Close";

        fileOperationExecute.RunCommand();

        LUTOperationStatus = fileOperationStatus.EnumValue;

        if (!LUTOperationStatus.Equals("Success"))
        {
            string output = "FileOperation " + fileOperationSelector.EnumValue + " failed";
            throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
        }
    }

    //Download shading data
    public static void Download()
    {
        FeatureCollection features = null;
        Feature fileOperationSelector = null;
        Feature fileOperationExecute = null;
        Feature fileOpenMode = null;
        Feature fileAccessBuffer = null;
        Feature fileAccessOffset = null;
        Feature fileAccessLength = null;
        Feature fileOperationStatus = null;
        Feature fileOperationResult = null;
        Feature fileStatus = null;
        Feature fileSize = null;
        Feature fileSelector = null;

        features = m_camera.Features;

        fileOperationSelector = features["FileOperationSelector"];
        fileOperationExecute = features["FileOperationExecute"];
        fileOpenMode = features["FileOpenMode"];
        fileAccessBuffer = features["FileAccessBuffer"];
        fileAccessOffset = features["FileAccessOffset"];
        fileAccessLength = features["FileAccessLength"];
        fileOperationStatus = features["FileOperationStatus"];
        fileOperationResult = features["FileOperationResult"];
        fileStatus = features["FileStatus"];
        fileSize = features["FileSize"];
        fileSelector = features["FileSelector"];

        fileSelector.EnumValue = "ShadingData";

        fileOpenMode.EnumValue = "Read";

        fileOperationSelector.EnumValue = "Open";

        fileOperationExecute.RunCommand();

        Int64 nFileSize = fileSize.IntValue;

        //Allocate buffer
        Array.Resize(ref m_data, (int)nFileSize);

        Int64 nMaxFileAccessLength = fileAccessLength.IntRangeMax;

        fileOperationSelector.EnumValue = "Read";

        Int64 nFileAccessOffset = 0;
        Int64 nFileAccessLength = Math.Min(nFileSize, nMaxFileAccessLength);
        Byte[] data = new Byte[nFileAccessLength];
        string LUTOperationStatus;

        do
        {
            fileAccessLength.IntValue = nFileAccessLength;

            fileOperationExecute.RunCommand();

            LUTOperationStatus = fileOperationStatus.EnumValue;

            if (!LUTOperationStatus.Equals("Success"))
            {
                string output = "FileOperation " + fileOperationSelector.EnumValue + " failed";
                throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
            }

            data = fileAccessBuffer.RawValue;
            Array.Copy(data, 0, m_data, nFileAccessOffset, nFileAccessLength);

            nFileAccessOffset = fileAccessOffset.IntValue;

            nFileAccessLength = Math.Min(nFileSize - nFileAccessOffset, nMaxFileAccessLength);
        }
        while (nFileSize != nFileAccessOffset);

        fileOperationSelector.EnumValue = "Close";

        fileOperationExecute.RunCommand();

        LUTOperationStatus = fileOperationStatus.EnumValue;

        if (!LUTOperationStatus.Equals("Success"))
        {
            throw new VimbaException((int)VmbErrorType.VmbErrorOther, "FileOperationStatus");
        }
    }

};

}}} // Namespace AVT.VmbAPINET.Examples