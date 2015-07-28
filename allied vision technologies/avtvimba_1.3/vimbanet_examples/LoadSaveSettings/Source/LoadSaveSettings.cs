/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        LoadSaveSettings.cs

  Description: The LoadSaveSettings example will demonstrate how to save the
               features from a camera to a fila and load them back from file
               using VimbaNET.
               

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
using System.Collections.Generic;
using System.Xml;
using System.Globalization;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

class LoadSaveSettings
{
    //A class to manage the target value
    //of a feature.
    private abstract class FeatureValue
    {
        private Feature m_Feature = null;

        public FeatureValue(Feature feature)
        {
            if(null == feature)
            {
                throw new ArgumentNullException("feature");
            }

            m_Feature = feature;
        }

        //Returns the according feature
        public Feature Feature
        {
            get
            {
                return m_Feature;
            }
        }

        //Returns true if feature is writeable at the moment
        public virtual bool IsWriteable
        {
            get
            {
                return m_Feature.IsWritable();
            }
        }

        //Returns true if feature currently contains desired target value
        public abstract bool IsTargetValue
        {
            get;
        }

        //Writes target value into the feature
        public abstract void ApplyTargetValue();
    };

    //A class to manage the target value
    //of an integer feature.
    private class IntegerValue : FeatureValue
    {
        private long m_TargetValue = 0;

        public IntegerValue(Feature feature, long targetValue)
            :   base(feature)
        {
            m_TargetValue = targetValue;
        }

        //Returns true if feature is writeable at the moment
        public override bool IsWriteable
        {
            get
            {
                //Check if it is writeable at all
                if(Feature.IsWritable() == false)
                {
                    return false;
                }
                
                //Then check if the target value is within the current range and
                //matches the increment.
                long minValue = Feature.IntRangeMin;
                long maxValue = Feature.IntRangeMax;
                if(     (m_TargetValue < minValue)
                    ||  (m_TargetValue > maxValue))
                {
                    return false;
                }
                
                long incValue = Feature.IntIncrement;
                if(incValue < 1)
                {
                    throw new Exception("Invalid increment found in a feature.");
                }
                if(((m_TargetValue - minValue) % incValue) != 0)
                {
                    return false;
                }

                return true;
            }
        }

        //Returns true if feature currently contains desired target value
        public override bool IsTargetValue
        {
            get
            {
                //Check if it is readable at all
                if(Feature.IsReadable() == false)
                {
                    return false;
                }
                
                //Now read the current value and compare it to our target value
                if(Feature.IntValue != m_TargetValue)
                {
                    return false;
                }
                
                return true;
            }
        }

        //Writes target value into the feature
        public override void ApplyTargetValue()
        {
            Feature.IntValue = m_TargetValue;
        }
    };

    //A class to manage the target value
    //of an float feature.
    private class FloatValue : FeatureValue
    {
        private double m_TargetValue = 0.0;

        public FloatValue(Feature feature, double targetValue)
            :   base(feature)
        {
            m_TargetValue = targetValue;
        }

        //Returns true if feature is writeable at the moment
        public override bool IsWriteable
        {
            get
            {
                //Check if it is writeable at all
                if(Feature.IsWritable() == false)
                {
                    return false;
                }
                
                //Then check if the target value is within the current range and
                //matches the increment.
                double minValue = Feature.FloatRangeMin;
                double maxValue = Feature.FloatRangeMax;
                if(     (m_TargetValue < minValue)
                    ||  (m_TargetValue > maxValue))
                {
                    return false;
                }

                return true;
            }
        }

        //Returns true if feature currently contains desired target value
        public override bool IsTargetValue
        {
            get
            {
                //Check if it is readable at all
                if(Feature.IsReadable() == false)
                {
                    return false;
                }

                double value = Feature.FloatValue;
                //Let's assume we don't want an exact match but
                //at least a very close match.
                if(Math.Abs(value - m_TargetValue) < 1e-8) //Match with absolute precision
                {
                    return true;
                }
                else if((Math.Abs(value - m_TargetValue) / Math.Max(Math.Abs(value), Math.Abs(m_TargetValue))) < 1e-8) //Match with relative precision
                {
                    return true;
                }
                
                return false; //No match
            }
        }

        //Writes target value into the feature
        public override void ApplyTargetValue()
        {
            Feature.FloatValue = m_TargetValue;
        }
    };

    //A class to manage the target value
    //of an enumeration feature.
    private class EnumerationValue : FeatureValue
    {
        private string m_TargetValue = null;

        public EnumerationValue(Feature feature, string targetValue)
            :   base(feature)
        {
            if(string.IsNullOrEmpty(targetValue))
            {
                throw new ArgumentNullException("targetValue");
            }

            m_TargetValue = targetValue;
        }

        //Returns true if feature is writeable at the moment
        public override bool IsWriteable
        {
            get
            {
                //Check if it is writeable at all
                if(Feature.IsWritable() == false)
                {
                    return false;
                }
                
                //Check if the target value is one of our enum entries
                string[] enumValues = Feature.EnumValues;
                foreach(string enumValue in enumValues)
                {
                    if(string.Compare(enumValue, m_TargetValue, StringComparison.Ordinal) == 0)
                    {
                        if(Feature.IsEnumValueAvailable(enumValue))
                        {
                            return true;
                        }
                    }
                }

                return false;
            }
        }

        //Returns true if feature currently contains desired target value
        public override bool IsTargetValue
        {
            get
            {
                //Check if it is readable at all
                if(Feature.IsReadable() == false)
                {
                    return false;
                }

                if(string.Compare(Feature.EnumValue, m_TargetValue, StringComparison.Ordinal) != 0)
                {
                    return false;
                }

                return true;
            }
        }

        //Writes target value into the feature
        public override void ApplyTargetValue()
        {
            Feature.EnumValue = m_TargetValue;
        }
    };

    //A class to manage the target value
    //of an string feature.
    private class StringValue : FeatureValue
    {
        private string m_TargetValue = null;

        public StringValue(Feature feature, string targetValue)
            :   base(feature)
        {
            if(null == targetValue)
            {
                throw new ArgumentNullException("targetValue");
            }

            m_TargetValue = targetValue;
        }

        //Returns true if feature currently contains desired target value
        public override bool IsTargetValue
        {
            get
            {
                //Check if it is readable at all
                if(Feature.IsReadable() == false)
                {
                    return false;
                }

                if(string.Compare(Feature.StringValue, m_TargetValue, StringComparison.Ordinal) != 0)
                {
                    return false;
                }

                return true;
            }
        }

        //Writes target value into the feature
        public override void ApplyTargetValue()
        {
            Feature.StringValue = m_TargetValue;
        }
    };

    //A class to manage the target value
    //of an boolean feature.
    private class BooleanValue : FeatureValue
    {
        private bool m_TargetValue = false;

        public BooleanValue(Feature feature, bool targetValue)
            :   base(feature)
        {
            m_TargetValue = targetValue;
        }

        //Returns true if feature currently contains desired target value
        public override bool IsTargetValue
        {
            get
            {
                //Check if it is readable at all
                if(Feature.IsReadable() == false)
                {
                    return false;
                }

                if(Feature.BoolValue != m_TargetValue)
                {
                    return false;
                }

                return true;
            }
        }

        //Writes target value into the feature
        public override void ApplyTargetValue()
        {
            Feature.BoolValue = m_TargetValue;
        }
    };

    private static void AddNode(Feature feature, string type, string value, XmlNode xmlNode, XmlDocument xmlDocument)
    {
        if(null == feature)
        {
            throw new ArgumentNullException("feature");
        }
        if(string.IsNullOrEmpty(type))
        {
            throw new ArgumentNullException("type");
        }
        if(null == value)
        {
            throw new ArgumentNullException("value");
        }
        if(null == xmlNode)
        {
            throw new ArgumentNullException("xmlNode");
        }
        if(null == xmlDocument)
        {
            throw new ArgumentNullException("xmlDocument");
        }

        string name = feature.Name;

        XmlElement xmlElement = xmlDocument.CreateElement(type);
        xmlElement.SetAttribute("Name", name);
        xmlElement.InnerText = value;

        xmlNode.InsertBefore(xmlElement, null);
    }

    //Save current camera settings to xml file
    public static void SaveToFile(Camera camera, string fileName, bool ignoreStreamable)
    {
        //Check parameters
        if(null == camera)
        {
            throw new ArgumentNullException("camera");
        }
        if(string.IsNullOrEmpty(fileName))
        {
            throw new ArgumentNullException("fileName");
        }

        //Our xml document
        XmlDocument xmlDocument = new XmlDocument();

        //Add a simple xml declaration such as <?xml version="1.0"?>
        XmlDeclaration xmlDeclaration = xmlDocument.CreateXmlDeclaration("1.0", null, null);
        xmlDocument.InsertAfter(xmlDeclaration, null);

        //All settings are embedded into a settings node
        XmlElement settingsNode = xmlDocument.CreateElement("Settings");
        xmlDocument.InsertBefore(settingsNode, null);

        //Get camera id
        string id = camera.Id;

        //Set camera ID as attribut in settings node
        settingsNode.SetAttribute("ID", id);

        //Get camera name
        string name = camera.Name;

        //Set camera name as attribut in settings node
        settingsNode.SetAttribute("Name", name);

        //Get camera model
        string model = camera.Model;

        //Set camera model as attribut in settings node
        settingsNode.SetAttribute("Model", model);

        //Get list of features
        FeatureCollection features = camera.Features;

        //Iterate over all features and add them to the xml
        foreach(Feature feature in features)
        {
            //Check if the current feature is readable now
            if(feature.IsReadable() == false)
            {
                continue;
            }

            if(false == ignoreStreamable)
            {
                //Check if the current feature is streamable
                if(feature.IsStreamable() == false)
                {
                    continue;
                }
            }
            
            //Now get the current features data type
            VmbFeatureDataType type = feature.DataType;

            //Only write features with the following data types:
            //Integer, Float, Enumeration, String and Boolean
            switch(type)
            {
            //Report unsupported feature data types
            default:
            case VmbFeatureDataType.VmbFeatureDataUnknown:
            case VmbFeatureDataType.VmbFeatureDataNone:
                throw new Exception("Unsupported data type found in a feature.");

            //Ignore some feature data types
            case VmbFeatureDataType.VmbFeatureDataCommand:
            case VmbFeatureDataType.VmbFeatureDataRaw:
                break;

            //Add xml nodes for supported feature data types
            case VmbFeatureDataType.VmbFeatureDataInt:
                {
                    long value = feature.IntValue;
                    AddNode(feature, "Integer", value.ToString(), settingsNode, xmlDocument);
                }
                break;

            case VmbFeatureDataType.VmbFeatureDataFloat:
                {
                    double value = feature.FloatValue;
                    string strValue = value.ToString("F15", CultureInfo.InvariantCulture);
                    AddNode(feature, "Float", strValue, settingsNode, xmlDocument);
                }
                break;

            case VmbFeatureDataType.VmbFeatureDataEnum:
                {
                    string strValue = feature.EnumValue;
                    AddNode(feature, "Enumeration", strValue, settingsNode, xmlDocument);
                }
                break;

            case VmbFeatureDataType.VmbFeatureDataString:
                {
                    string strValue = feature.StringValue;
                    AddNode(feature, "String", strValue, settingsNode, xmlDocument);
                }
                break;

            case VmbFeatureDataType.VmbFeatureDataBool:
                {
                    bool value = feature.BoolValue;
                    
                    string strValue = null;
                    if(true == value)
                    {
                        strValue = "True";
                    }
                    else
                    {
                        strValue = "False";
                    }

                    AddNode(feature, "Boolean", strValue, settingsNode, xmlDocument);
                }
                break;
            }
        }

        //Write the xml document to file
        xmlDocument.Save(fileName);
    }

    public static void SaveToFile(Camera camera, string fileName)
    {
        SaveToFile(camera, fileName, false);
    }

    //Load settings from xml file and then set them in the camera
    //Parameters:
    //loadedFeatures:  Will contain the features that have been applied to the camera successfully
    //missingFeatures: Contains the features that couldn't be set
    //maxIterations:   Maximum number of interations (retries) to set all features
    public static void LoadFromFile(Camera camera, string fileName, out StringCollection loadedFeatures, out StringCollection missingFeatures, bool ignoreStreamable, uint maxIterations)
    {
        //Check parameters
        if(null == camera)
        {
            throw new ArgumentNullException("camera");
        }
        if(string.IsNullOrEmpty(fileName))
        {
            throw new ArgumentNullException("fileName");
        }

        //Load the xml document from file
        XmlDocument xmlDocument = new XmlDocument();
        xmlDocument.Load(fileName);

        //Get the settings node
        XmlNodeList xmlNodeList = xmlDocument.GetElementsByTagName("Settings");
        if(xmlNodeList.Count != 1)
        {
            throw new Exception("Invalid camera settings xml file.");
        }

        XmlNode settingsNode = xmlNodeList[0];
        if(null == settingsNode)
        {
            throw new Exception("Invalid camera settings xml file.");
        }

        //Get camera model
        string model = camera.Model;

        //Check if the camera model matches the one from the xml file
        XmlAttribute modelAttribute = settingsNode.Attributes["Model"];
        if(null == modelAttribute)
        {
            throw new Exception("Invalid camera settings xml file.");
        }

        if(string.Compare(model, modelAttribute.Value, StringComparison.Ordinal) != 0)
        {
            throw new Exception("Xml file doesn't match the camera model.");
        }

        StringCollection currentLoadedFeatures = new StringCollection();
        StringCollection currentMissingFeatures = new StringCollection();

        //First load all features from xml
        LinkedList<FeatureValue> featureValues = new LinkedList<FeatureValue>();
        foreach(XmlNode xmlNode in settingsNode.ChildNodes)
        {
            string type = xmlNode.Name;

            //Get the feature name from the attribute
            XmlAttribute nameAttribute = xmlNode.Attributes["Name"];
            if(null == nameAttribute)
            {
                throw new Exception("Invalid camera settings xml file.");
            }

            string name = nameAttribute.Value;

            //Get the feature target value as a string
            string value = xmlNode.InnerText;

            //Try to find the feature with the given name
            Feature feature = null;
            try
            {
                feature = camera.Features[name];
            }
            catch
            {
                feature = null;
            }

            if(null != feature)
            {
                bool loadFeature = true;
                if(false == ignoreStreamable)
                {
                    loadFeature = feature.IsStreamable();
                }
           
                if(true == loadFeature)
                {
                    //Create a feature value for the current feature
                    //by parsing the value depending on the features
                    //data type.
                    FeatureValue featureValue = null;
                    if(string.Compare(type, "Integer", StringComparison.Ordinal) == 0)
                    {
                        featureValue = new IntegerValue(feature, long.Parse(value.Trim()));
                    }
                    else if(string.Compare(type, "Float", StringComparison.Ordinal) == 0)
                    {
                        featureValue = new FloatValue(feature, double.Parse(value.Trim(), CultureInfo.InvariantCulture));
                    }
                    else if(string.Compare(type, "Enumeration", StringComparison.Ordinal) == 0)
                    {
                        featureValue = new EnumerationValue(feature, value.Trim());
                    }
                    else if(string.Compare(type, "String", StringComparison.Ordinal) == 0)
                    {
                        featureValue = new StringValue(feature, value);
                    }
                    else if(string.Compare(type, "Boolean", StringComparison.Ordinal) == 0)
                    {
                        string trimmedValue = value.Trim();
                        bool b = false;
                        if(     (string.Compare(trimmedValue, "true", StringComparison.OrdinalIgnoreCase) == 0)
                            ||  (string.Compare(trimmedValue, "1", StringComparison.Ordinal) == 0))
                        {
                            b = true;
                        }
                        else if(    (string.Compare(trimmedValue, "false", StringComparison.OrdinalIgnoreCase) == 0)
                                ||  (string.Compare(trimmedValue, "0", StringComparison.Ordinal) == 0))
                        {
                            b = false;
                        }
                        else
                        {
                            throw new Exception("Invalid camera settings xml file.");
                        }
                
                        featureValue = new BooleanValue(feature, b);
                    }

                    //Check if we were able to allocate the feature value
                    if(null == featureValue)
                    {
                        throw new Exception("Invalid camera settings xml file.");
                    }

                    //Add the new feature value to the list of feature values
                    featureValues.AddLast(featureValue);
                }
                else
                {
                    //We directly add the feature to the missing features list
                    //if feature is not streamable.
                    currentMissingFeatures.Add(name);
                }
            }
            else
            {
                //We directly add the feature to the missing features list
                //if no feature exists with the given name.
                currentMissingFeatures.Add(name);
            }
        }

        //Now we try to write all features into the camera
        uint iteration = 0;             //Counter for retries
        bool featuresComplete = false;  //Is true if all features have been set
        bool featuresWritten = true;    //Is true if any feature has been written during the last iteration

        while(      (false == featuresComplete)     //Only iterate if we are not done yet
                &&  (true == featuresWritten)       //Only iterate if we are not stuck (no features left that can be changed)
                &&  (iteration < maxIterations))    //Only iterate until we reach the maximum number of interations/retries
        {
            featuresComplete = true;
            featuresWritten = false;

            //Iterate over all feature values and try to set them
            foreach(FeatureValue featureValue in featureValues)
            {
                //We only set a feature if it doesn't already contain the target value
                if(false == featureValue.IsTargetValue)
                {
                    //Remember that there is at least one feature to be done
                    featuresComplete = false;

                    string name = featureValue.Feature.Name;

                    //We only set a feature if the target value can be written at the moment
                    if(featureValue.IsWriteable)
                    {
                        //Write the target value to the feature
                        featureValue.ApplyTargetValue();
                        
                        //Remember that we changed at least one feature
                        featuresWritten = true;
                    }
                }
            }

            iteration++;
        }

        //Finally check the contents of all features once more to make sure that all features
        //now contain the according target value.
        foreach(FeatureValue featureValue in featureValues)
        {
            //Add the feature to one of our lists depending on if it contains the target value.
            if(featureValue.IsTargetValue)
            {
                currentLoadedFeatures.Add(featureValue.Feature.Name);
            }
            else
            {
                currentMissingFeatures.Add(featureValue.Feature.Name);
            }
        }

        //Return the feature lists to the user if there
        //was no error.
        loadedFeatures = currentLoadedFeatures;
        missingFeatures = currentMissingFeatures;
    }

    public static void LoadFromFile(Camera camera, string fileName, out StringCollection loadedFeatures, out StringCollection missingFeatures, bool ignoreStreamable)
    {
        LoadFromFile(camera, fileName, out loadedFeatures, out missingFeatures, ignoreStreamable, 5);
    }

    public static void LoadFromFile(Camera camera, string fileName, out StringCollection loadedFeatures, out StringCollection missingFeatures)
    {
        LoadFromFile(camera, fileName, out loadedFeatures, out missingFeatures, false);
    }
};

}}} // Namespace AVT.VmbAPINET.Examples