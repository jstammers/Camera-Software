/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        RingBitmap.cs

  Description: Implementation file for the RingBitmap class.
               Contains a configurable ring bitmap array.
               Each bitmap will only be created one time and reused afterwards.

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
using System.Text;
using System.Drawing;
using System.Drawing.Imaging;

namespace AsynchronousGrab
{
    //helper class to provide necessary bitmap functions
    class RingBitmap
    {
        private int m_Size = 0;
        private Bitmap[] m_Bitmaps = null;              //Bitmaps to display images
        private int m_BitmapSelector = 0;               //selects Bitmap
        
        public RingBitmap(int size)
        {
            m_Size = size;
            m_Bitmaps = new Bitmap[m_Size];
        }

        //Bitmap rotation selector
        private void SwitchBitamp()
        {
            m_BitmapSelector++;

            if (m_Size == m_BitmapSelector)
                m_BitmapSelector = 0;
        }

        //return current bitmap as image
        public Image Image
        {
            get
            {
                return m_Bitmaps[m_BitmapSelector];
            }
        }

        //copy buffer in 8bppIndexed bitmap
        public void CopyToNextBitmap_8bppIndexed(int width, int height, byte[] buffer)
        {
            //switch to Bitmap object which is currently not in use by GUI
            SwitchBitamp();

            //check if this Bitmap object was already created -> else reuse it
            if (null == m_Bitmaps[m_BitmapSelector])
                m_Bitmaps[m_BitmapSelector] = new Bitmap(width, height, PixelFormat.Format8bppIndexed);

            //Set greyscale palette
            ColorPalette palette = m_Bitmaps[m_BitmapSelector].Palette;
            for (int i = 0; i < palette.Entries.Length; i++)
            {
                palette.Entries[i] = Color.FromArgb(i, i, i);
            }
            m_Bitmaps[m_BitmapSelector].Palette = palette;

            //Copy image data
            BitmapData bitmapData = m_Bitmaps[m_BitmapSelector].LockBits(new Rectangle( 0,
                                                                                        0,
                                                                                        width,
                                                                                        height),
                                                                         ImageLockMode.WriteOnly,
                                                                         PixelFormat.Format8bppIndexed);
            try
            {
                //Copy image data line by line
                for (int y = 0; y < height; y++)
                {
                    System.Runtime.InteropServices.Marshal.Copy(buffer,
                                                                y * width,
                                                                new IntPtr(bitmapData.Scan0.ToInt64() + y * bitmapData.Stride),
                                                                width);
                }
            }
            finally
            {
                m_Bitmaps[m_BitmapSelector].UnlockBits(bitmapData);
            }
        }

        //copy buffer in 24bppRgb bitmap
        public void CopyToNextBitmap_24bppRgb(int width, int height, byte[] buffer)
        {
            //switch to Bitmap object which is currently not in use by GUI
            SwitchBitamp();

            //check if this Bitmap object was already created -> else reuse it
            if (null == m_Bitmaps[m_BitmapSelector])
                m_Bitmaps[m_BitmapSelector] = new Bitmap(width, height, PixelFormat.Format24bppRgb);

            //Copy image data
            BitmapData bitmapData = m_Bitmaps[m_BitmapSelector].LockBits(new Rectangle( 0,
                                                                                        0,
                                                                                        width,
                                                                                        height),
                                                                        ImageLockMode.WriteOnly,
                                                                        PixelFormat.Format24bppRgb);
            try
            {
                //Copy image data line by line
                for (int y = 0; y < height; y++)
                {
                    System.Runtime.InteropServices.Marshal.Copy(buffer,
                                                                y * width * 3,
                                                                new IntPtr(bitmapData.Scan0.ToInt64() + y * bitmapData.Stride),
                                                                width * 3);
                }
            }
            finally
            {
                m_Bitmaps[m_BitmapSelector].UnlockBits(bitmapData);
            }
        }
    }
}
