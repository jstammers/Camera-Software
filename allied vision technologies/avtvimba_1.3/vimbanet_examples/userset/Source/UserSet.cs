/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        UserSet.cs

  Description: The UserSet example will demonstrate how deal with the user sets
               stored inside the cameras using VimbaNET.
               

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

public class UserSetCollection
{
    private static Camera m_camera;
    private static List<UserSetControl> m_usersets;

    public UserSetCollection(Camera camera)
    {
        //Check parameters
        if (null == camera)
        {
            throw new ArgumentNullException("camera");
        }

        m_camera = camera;

        Int64 nCount = 0;
        nCount = Count;

        m_usersets = new List<UserSetControl>();

        for(int i = 0; i < nCount; i++)
        {
            UserSetControl control = new UserSetControl(m_camera, i);            
            m_usersets.Add(control);
        }
    }

    //Get user set count
    public static Int64 Count
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["UserSetSelector"];

            string[] controls = null;

            controls = feature.EnumValues;

            return controls.Length;
        }
    }
    
    //Get user set control
    public UserSetControl this[Int64 nIndex]
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            //Access to user set changes the selector
            feature = features["UserSetSelector"];

            feature.IntValue = nIndex;

            return m_usersets[(int)nIndex];
        }
    }

    //Get selected user set index
    public static Int64 SelectedIndex
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["UserSetSelector"];

            return feature.IntValue;
        }
    }

    //Get user set default index
    public static Int64 DefaultIndex
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["UserSetDefaultSelector"];

            return feature.IntValue;
        }
    }
}

public class UserSetControl
{
    private Camera m_camera;
    private Int64 m_nIndex;

    public UserSetControl(Camera camera, Int64 nIndex)
    {
        //Check parameters
        if (null == camera)
        {
            throw new ArgumentNullException("camera");
        }

        m_camera = camera;
        m_nIndex = nIndex;
    }

    //Is user set default
    public bool IsDefault
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["UserSetDefaultSelector"];

            Int64 nDefaultIndex = feature.IntValue;

            if (nDefaultIndex == m_nIndex)
            {
                return true;
            }

            return false;
        }
    }

    //Make user set default
    public void MakeDefault()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        try
        {
            feature = features["UserSetDefaultSelector"];
            feature.IntValue = m_nIndex;
        }
        catch
        {
            feature = features["UserSetMakeDefault"];
            feature.RunCommand();
        }
    }

    //Save user set to flash
    public void SaveToFlash()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["UserSetSave"];
        feature.RunCommand();
    }

    //Load user set from flash
    public void LoadFromFlash()
    {
        FeatureCollection features = null;
        Feature feature = null;

        features = m_camera.Features;

        feature = features["UserSetLoad"];
        feature.RunCommand();
    }

    //Get user set operation result
    public Int64 OperationResult
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["UserSetOperationResult"];

            return feature.IntValue;
        }
    }

    //Get user set operation status
    public Int64 OperationStatus
    {
        get
        {
            FeatureCollection features = null;
            Feature feature = null;

            features = m_camera.Features;

            feature = features["UserSetOperationResult"];

            return feature.IntValue;
        }
    }
};

}}} // Namespace AVT.VmbAPINET.Examples