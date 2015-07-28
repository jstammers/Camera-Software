/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        LookUpTable.cs

  Description: The LookUpTable example will demonstrate how to use
               the look up table feature of the camera using VimbaNET.
               

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
using System.Collections.Generic;

using AVT.VmbAPINET;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

public class LookUpTableCollection
{
    private static Camera m_camera;
    private static List<LookUpTableControl> m_tables;

    public LookUpTableCollection(Camera camera)
    {
        //Check parameters
        if (null == camera)
        {
            throw new ArgumentNullException("camera");
        }

        m_camera = camera;

        Int64 nCount = 0;
        nCount = Count;

        m_tables = new List<LookUpTableControl>();

        for (Int64 i = 0; i < nCount; i++)
        {
            LookUpTableControl control = new LookUpTableControl(m_camera, i);            
            m_tables.Add(control);
        }
    }

    //Get look up table count
    public static Int64 Count
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTSelector"];

            string[] controls = null;

            controls = feature.EnumValues;

            return (Int64)controls.LongLength;
        }
    }

    public LookUpTableControl this[Int64 nIndex]
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTSelector"];

            feature.IntValue = nIndex;

            return m_tables[(int)nIndex];
        }
    }

    //Get look up table active index
    public static Int64 ActiveIndex
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTSelector"];

            return feature.IntValue;
        }
    }

}

public class LookUpTableControl
{
    private Camera m_camera;
    private Int64   m_nIndex;
    private Byte[]  m_data;

    public LookUpTableControl(Camera camera, Int64 nIndex)
    {
        //Check parameters
        if (null == camera)
        {
            throw new ArgumentNullException("camera");
        }

        m_camera = camera;
        m_nIndex = nIndex;
    }

    //Enable look up table
    public void Enable(bool bEnable)
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["LUTEnable"];

        feature.BoolValue = bEnable;
    }

    //Is look up table enabled
    public bool IsEnabled
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTEnable"];

            return feature.BoolValue;
        }
    }

    //Get look up table index
    public Int64 Index
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTIndex"];

            return feature.IntValue;
        }
    }

    public Int64 Value
    {
        //Get look up table value
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTValue"];

            return feature.IntValue;
        }

        //Set look up table index
        set
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTValue"];

            feature.IntValue = value;
        }
    }

    //Get value count
    public Int64 ValueCount
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTSizeBytes"];

            Int64 nLUTSizeBytes = feature.IntValue;

            Int64 nLUTBitDepthOut = 0;
            nLUTBitDepthOut = BitDepthOut;

            Int64 nLUTBytesPerValue = nLUTBitDepthOut > 8 ? 2 : 1;
            return (nLUTSizeBytes / nLUTBytesPerValue);
        }
    }

    //Get/set raw data
    public Byte[] RawData
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


    //Get bit depth in
    public Int64 BitDepthIn
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTBitDepthIn"];

            return feature.IntValue;
        }
    }

    //Get bit depth out
    public Int64 BitDepthOut
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["LUTBitDepthOut"];

            return feature.IntValue;
        }
    }

    //Download look up table
    public void Download()
    {
        FeatureCollection features = null;

        features = m_camera.Features;

        //Get size of LUT
        Feature LUTSize = null;
        LUTSize = features["LUTSizeBytes"];
        Int64 nLUTSize = LUTSize.IntValue;

        //Allocate buffer
        Array.Resize(ref m_data, (int)nLUTSize);
        
        //Read from camera
        try
        {
            //File access control
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
            Feature LUTSelector = null;

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

            LUTSelector = features["LUTSelector"];

            fileSelector.EnumValue = "LUT" + LUTSelector.EnumValue;

            fileOpenMode.EnumValue = "Read";

            fileOperationSelector.EnumValue = "Open";

            fileOperationExecute.RunCommand();

            string LUTOperationStatus;

            LUTOperationStatus = fileOperationStatus.EnumValue;

            if (!LUTOperationStatus.Equals("Success"))
            {
                string output = "FileOperation " + fileOperationSelector.EnumValue + " failed";
                throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
            }

            Int64 nFileSize = fileSize.IntValue;

            Int64 nMaxFileAccessLength = fileAccessLength.IntRangeMax;

            fileOperationSelector.EnumValue = "Read";

            Int64 nFileAccessOffset = 0;
            Int64 nFileAccessLength = Math.Min(nFileSize, nMaxFileAccessLength);
            Byte[] data = new Byte[nFileAccessLength];

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
                string output = "FileOperation " + fileOperationSelector.EnumValue + " failed";
                throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
            }
        }
        catch
        {
            //Used LUT index and value as indicator for GigE
            Feature LUTIndex = null;
            Feature LUTValue = null;
            LUTIndex = features["LUTIndex"];
            LUTValue = features["LUTValue"];

            //GigE
            try
            {
                //Get LUT address for GigE (indicator for direct memory access)
                Feature LUTAddress = null;
                LUTAddress = features["LUTAddress"];
                Int64 nLUTAddress = LUTAddress.IntValue;

                //Camera supports direct memory access for LUT
                uint nCompletedReads = 0;
                m_camera.ReadMemory((ulong)nLUTAddress, ref m_data, (uint)nLUTSize, ref nCompletedReads);
            }
            catch
            {
                //Camera doesn't support direct memory access for LUT
                Feature LUTBitDepthOut = null;
                LUTBitDepthOut = features["LUTBitDepthOut"];
                Int64 nLUTBitDepthOut = LUTBitDepthOut.IntValue;

                //Evaluate number of LUT entries
                Int64 nLUTBytePerValue = (nLUTBitDepthOut > 8) ? 2 : 1;
                Int64 nLUTEntries = nLUTSize / nLUTBytePerValue;

                //Set LUT values by iteration over indexes
                int iter = 0;
                Int64 nValue;
                for (Int64 i = 0; i < nLUTEntries; i++)
                {
                    LUTIndex.IntValue = i;

                    nValue = m_data[iter++];
                    if (2 == nLUTBytePerValue)
                    {
                        nValue = nValue << 8;
                        nValue += m_data[iter++];
                    }

                    LUTValue.IntValue = nValue;
                }
            }
        }
    }

    //Upload look up table
    public void Upload()
    {
        //Raw data empty
        if (0 == m_data.Length)
        {
            string output = "Look up table upload. Error code: " + ((int)VmbErrorType.VmbErrorOther);
            throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
        }

        FeatureCollection features = null;
        features = m_camera.Features;

        //Write to camera
        try
        {
            //Used file access control for 1394 cameras
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
            Feature LUTSelector = null;

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

            LUTSelector = features["LUTSelector"];

            fileSelector.EnumValue = "LUT" + LUTSelector.EnumValue;

            fileOpenMode.EnumValue = "Write";

            fileOperationSelector.EnumValue = "Open";

            fileOperationExecute.RunCommand();

            string LUTOperationStatus;

            LUTOperationStatus = fileOperationStatus.EnumValue;

            if (!LUTOperationStatus.Equals("Success"))
            {
                string output = "FileOperation " + fileOperationSelector.EnumValue + " failed";
                throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
            }

            Int64 nFileSize = fileSize.IntValue;

            Int64 nMaxFileAccessLength = fileAccessLength.IntRangeMax;

            fileOperationSelector.EnumValue = "Write";

            Int64 nFileAccessOffset = 0;
            Int64 nFileAccessLength = Math.Min(nFileSize, nMaxFileAccessLength);
            Byte[] data = new Byte[nFileAccessLength];

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
        catch
        {
            //Used LUT index and value as indicator for GigE
            Feature LUTIndex = null;
            Feature LUTValue = null;
            LUTIndex = features["LUTIndex"];
            LUTValue = features["LUTValue"];

            //GigE
            try
            {
                //Get LUT address for GigE (indicator for direct memory access)
                Feature LUTAddress = null;
                LUTAddress = features["LUTAddress"];
                Int64 nLUTAddress = LUTAddress.IntValue;

                //Camera supports direct memory access for LUT
                uint nCompletedWrites = 0;
                m_camera.WriteMemory((ulong)nLUTAddress, m_data, ref nCompletedWrites);
            }
            catch
            {
                //Camera doesn't support direct memory access for LUT
                
                //Get output bit depth
                Feature LUTBitDepthOut = null;
                LUTBitDepthOut = features["LUTBitDepthOut"];
                Int64 nLUTBitDepthOut = LUTBitDepthOut.IntValue;

                //Get size of LUT
                Feature LUTSize = null;
                LUTSize = features["LUTSizeBytes"];
                Int64 nLUTSize = LUTSize.IntValue;


                //Evaluate number of LUT entries
                Int64 nLUTBytePerValue = (nLUTBitDepthOut > 8) ? 2 : 1;
                Int64 nLUTEntries = nLUTSize / nLUTBytePerValue;

                //Set LUT values by iteration over indexes
                int iter = 0;
                Int64 nValue;
                for (Int64 i = 0; i < nLUTEntries; i++)
                {
                    LUTIndex.IntValue = i;                        

                    nValue = m_data[iter++];
                    if (2 == nLUTBytePerValue)
                    {
                        nValue = nValue << 8;
                        nValue += m_data[iter++];
                    }

                    LUTValue.IntValue = nValue;
                }
            }
        }
    }

    //Load look up table from flash
    public void LoadFromFlash()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        try
        {
            feature = features["LUTLoad"];
        }
        catch
        {
            feature = features["LUTLoadAll"];
        }

        feature.RunCommand();
    }

    //Save look up table to flash
    public void SaveToFlash()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        try
        {
            feature = features["LUTSave"];
        }
        catch
        {
            feature = features["LUTSaveAll"];
        }

        feature.RunCommand();
    }

    //Load look up table from Csv
    public void LoadFromCsv(string fileName, int nIndex)
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["LUTSizeBytes"];

        Int64 nLUTSize = feature.IntValue;

        //Evaluate number of LUT entries
        Int64 nLUTBytePerValue = (BitDepthOut > 8) ? 2 : 1;
        Int64 nLUTEntries = nLUTSize / nLUTBytePerValue;

        //Allocate buffer
        Array.Resize(ref m_data, (int)nLUTSize);

        // Load LUT from CSV
        Csv lut = new Csv();
        using (Csv.CsvLoad load = new Csv.CsvLoad(fileName, lut))
        {
            Csv.CsvRow row = new Csv.CsvRow();
            int i = 0;
            while (load.Row(row))
            {
                Byte[] data = new Byte[nLUTBytePerValue];
                if (2 == nLUTBytePerValue)
                {
                    Int16 nData = Int16.Parse(row[nIndex]);
                    data[0] = (Byte)(nData >> 8);
                    data[1] = (Byte)nData;
                }
                else
                {
                    Byte nData = Byte.Parse(row[nIndex]);
                    data[0] = nData;
                }

                Array.Copy(data, 0, m_data, i * nLUTBytePerValue, nLUTBytePerValue);
                i++;
            }
        }
    }

    //Save look up table to Csv
    public void SaveToCsv(string fileName)
    {
        //Raw data empty
        if (null == m_data)
        {
            string output = "Look up table upload. Error code: " + ((int)VmbErrorType.VmbErrorOther);
            throw new VimbaException((int)VmbErrorType.VmbErrorOther, output);
        }

        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["LUTSizeBytes"];

        Int64 nLUTSize = feature.IntValue;

        //Evaluate number of LUT entries
        Int64 nLUTBytePerValue = (BitDepthOut > 8) ? 2 : 1;
        Int64 nLUTEntries = nLUTSize / nLUTBytePerValue;

        // Save LUT data to CSV
        Csv lut = new Csv();
        using (Csv.CsvSave save = new Csv.CsvSave(fileName, lut))
        {
            for (int i = 0; i < nLUTEntries; i++)
            {
                Csv.CsvRow row = new Csv.CsvRow();
                Int64 data = m_data[i * nLUTBytePerValue];
                if (2 == nLUTBytePerValue)
                {
                    data = data << 8;
                    data += m_data[i * nLUTBytePerValue + 1]; 
                }
                row.Add(String.Format("{0}", data));
                save.Row(row);
            }
        }
    }
};

}}} // Namespace AVT.VmbAPINET.Examples