/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        MainForm.cs

  Description: Forms class for the GUI of the SynchronousGrab example of
               VimbaNET.

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
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using AVT.VmbAPINET;

namespace SynchronousGrab
{
    public partial class MainForm : Form
    {
        private VimbaHelper m_VimbaHelper = null;

        public MainForm()
        {
            InitializeComponent();
        }

        //Add log message to logging list box
        private void LogMessage(string message)
        {
            if(null == message)
            {
                throw new ArgumentNullException("message");
            }

            int index = m_LogList.Items.Add(string.Format("{0:yyyy-MM-dd HH:mm:ss.fff}: {1}", DateTime.Now, message));
            m_LogList.TopIndex = index;
        }

        //Add an error log message and show an error message box
        private void LogError(string message)
        {
            LogMessage(message);

            MessageBox.Show(message, "Message", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }

        private void UpdateCameraList()
        {
            //Remember the old selection (if there was any)y
            CameraInfo oldSelectedItem = m_CameraList.SelectedItem as CameraInfo;
            m_CameraList.Items.Clear();

            List<CameraInfo> cameras = m_VimbaHelper.CameraList;

            CameraInfo newSelectedItem = null;
            foreach(CameraInfo cameraInfo in cameras)
            {
                m_CameraList.Items.Add(cameraInfo);

                if(null == newSelectedItem)
                {
                    //At least select the first camera
                    newSelectedItem = cameraInfo;
                }
                else if(null != oldSelectedItem)
                {
                    //If the previous selected camera is still available
                    //then prefer this camera.
                    if(string.Compare(newSelectedItem.ID, cameraInfo.ID, StringComparison.Ordinal) == 0)
                    {
                        newSelectedItem = cameraInfo;
                    }
                }
            }

            //If available select a camera.
            if(null != newSelectedItem)
            {
                m_CameraList.SelectedItem = newSelectedItem;
            }
        }

        private void OnCameraListChanged(object sender, EventArgs args)
        {
            //Start an async invoke in case this method was not
            //called by the GUI thread.
            if(InvokeRequired == true)
            {
                BeginInvoke(new CameraListChangedHandler(this.OnCameraListChanged), sender, args);
                return;
            }

            if(null != m_VimbaHelper)
            {
                try
                {
                    UpdateCameraList();

                    LogMessage("Camera list updated.");
                }
                catch(Exception exception)
                {
                    LogError("Could not update camera list. Reason: " + exception.Message);
                }
            }
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            try
            {
                //Start up Vimba SDK
                VimbaHelper vimbaHelper = new VimbaHelper();
                vimbaHelper.Startup(this.OnCameraListChanged);
                Text += String.Format(" Vimba Version V{0}", vimbaHelper.GetVersion());
                m_VimbaHelper = vimbaHelper;

                try
                {
                    UpdateCameraList();
                }
                catch(Exception exception)
                {
                    LogError("Could not update camera list. Reason: " + exception.Message);
                }
            }
            catch(Exception exception)
            {
                LogError("Could not startup Vimba API. Reason: " + exception.Message);
            }
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if(null != m_VimbaHelper)
            {
                try
                {
                    //Shutdown Vimba SDK when application exits
                    m_VimbaHelper.Shutdown();

                    m_VimbaHelper = null;
                }
                catch(Exception exception)
                {
                    LogError("Could not shutdown Vimba API. Reason: " + exception.Message);
                }
            }
        }

        private void m_AcquireButton_Click(object sender, EventArgs e)
        {
            try
            {
                //Determine selected camera
                CameraInfo selectedItem = m_CameraList.SelectedItem as CameraInfo;
                if(null == selectedItem)
                {
                    throw new NullReferenceException("No camera selected.");
                }

                //Acquire an image synchronously (snap) from selected camera
                Image image = m_VimbaHelper.AcquireSingleImage(selectedItem.ID);

                //Display image
                m_PictureBox.Image = image;

                LogMessage("Image acquired synchronously.");
            }
            catch(Exception exception)
            {
                LogError("Could not acquire image. Reason: " + exception.Message);
            }
        }

        //Toggle mode between zoomed and 1:1 image display
        private void ToogleDisplayMode()
        {
            if(PictureBoxSizeMode.Zoom == m_PictureBox.SizeMode)
            {
                m_PictureBox.SizeMode = PictureBoxSizeMode.AutoSize;
                m_PictureBox.Dock = DockStyle.None;
            }
            else
            {
                m_PictureBox.SizeMode = PictureBoxSizeMode.Zoom;
                m_PictureBox.Dock = DockStyle.Fill;
            }
        }

        private void m_PictureBox_DoubleClick(object sender, EventArgs e)
        {
            ToogleDisplayMode();
        }

        private void m_DisplayPanel_DoubleClick(object sender, EventArgs e)
        {
            ToogleDisplayMode();
        }

        private void m_CameraList_SelectedIndexChanged(object sender, EventArgs e)
        {
            CameraInfo cameraInfo = m_CameraList.SelectedItem as CameraInfo;
            if(null == cameraInfo)
            {
                //Disable button if no camera is selected
                m_AcquireButton.Enabled = false;
            }
            else
            {
                //Enable button if a camera is selected
                m_AcquireButton.Enabled = true;
            }
        }
    }
}
