/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        SynchronousGrabDlg.cpp

  Description: MFC dialog class for the GUI of the SynchronousGrab example of
               VimbaCPP.

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

#include <stdafx.h>
#include <iostream>
#include <sstream>

#include "SynchronousGrab.h"
#include "SynchronousGrabDlg.h"

#ifndef UNICODE
    typedef std::ostringstream      string_stream_type;
#else
    typedef std::wostringstream     string_stream_type;
#endif

enum { NUM_COLORS   = 3, };
enum { BIT_DEPTH    = 8, };

// Ctor
CSynchronousGrabDlg::CSynchronousGrabDlg( CWnd* pParent )
    : CDialog(CSynchronousGrabDlg::IDD, pParent)
    , m_pApiController( new ApiController())
{
    m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

BEGIN_MESSAGE_MAP(CSynchronousGrabDlg, CDialog)
    ON_WM_SYSCOMMAND()
    ON_WM_PAINT()
    ON_WM_QUERYDRAGICON()
    ON_BN_CLICKED(IDC_BUTTON_STARTSTOP, &CSynchronousGrabDlg::OnBnClickedButtonStartstop)
    
    // Here we add the event handlers for Vimba events
    ON_MESSAGE( WM_CAMERA_LIST_CHANGED, OnCameraListChanged )	
END_MESSAGE_MAP()

BOOL CSynchronousGrabDlg::OnInitDialog()
{
    CDialog::OnInitDialog();
    
    SetIcon(m_hIcon, TRUE);
    SetIcon(m_hIcon, FALSE);

    // Start Vimba
    VmbErrorType    err = m_pApiController->StartUp();
    string_type     WindowText(_TEXT("SynchronousGrab (MFC version) Vimba Version V"));
    WindowText +=m_pApiController->GetVersion();
    SetWindowText( WindowText.c_str() );
    Log( _TEXT("Starting Vimba"), err );
    if ( VmbErrorSuccess == err )
    {
        // Initially get all connected cameras
        UpdateCameraListBox();
        std::stringstream strMsg;
        strMsg << "Cameras found..." << m_cameras.size();
        m_ListLog.InsertString( 0, CString( strMsg.str().c_str() ));  
    }

    return TRUE;
}

void CSynchronousGrabDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
    if ( SC_CLOSE == nID )
    {
        // Before we close the application we stop Vimba
        m_pApiController->ShutDown();
        if (m_pApiController)
        {
            delete m_pApiController;
            m_pApiController = NULL;
        } 
    }	
    
    CDialog::OnSysCommand(nID, lParam);
}

void CSynchronousGrabDlg::OnBnClickedButtonStartstop()
{
    VmbErrorType    err;
    int             nRow = m_ListBoxCameras.GetCurSel();

    if ( -1 < nRow )
    {
        // Get the frame
        FramePtr pFrame;
        err = m_pApiController->AcquireSingleImage( m_cameras[nRow], pFrame );
        if ( VmbErrorSuccess == err )
        {
            // See if it is not corrupt
            VmbFrameStatusType eReceiveStatus;
            err = pFrame->GetReceiveStatus( eReceiveStatus );
            if (    VmbErrorSuccess == err
                 && VmbFrameStatusComplete == eReceiveStatus )
            {
                // Set up image for MFC picture box
                if ( NULL != m_Image )
                {
                    m_Image.Destroy();
                }
                m_Image.Create(	m_pApiController->GetWidth(),
                                -m_pApiController->GetHeight(),
                                NUM_COLORS * BIT_DEPTH );

                VmbUchar_t *pBuffer;
                VmbUchar_t *pColorBuffer = NULL;
                err = pFrame->GetImage( pBuffer );
                if ( VmbErrorSuccess == err )
                {
                    VmbUint32_t nSize;
                    err = pFrame->GetImageSize( nSize );
                    if ( VmbErrorSuccess == err )
                    {
                        VmbPixelFormatType ePixelFormat = m_pApiController->GetPixelFormat();
                        if (	VmbPixelFormatMono8 == ePixelFormat
                            ||	VmbPixelFormatBgr8 == ePixelFormat )
                        {
                            // Convert mono to bgr if necessary
                            if ( VmbPixelFormatMono8 == ePixelFormat )
                            {
                                pColorBuffer = new VmbUchar_t[ nSize * NUM_COLORS ];
                                MonoToBGR( pBuffer, pColorBuffer, nSize );
                                pBuffer = pColorBuffer;
                            }

                            // Copy it
                            // We need that because MFC might repaint the view after we have released the frame already
                            CopyToImage( pBuffer, &m_Image );

                            if ( NULL != pColorBuffer )
                            {
                                delete[] pColorBuffer;
                                pColorBuffer = NULL;
                            }

                            // Display it
                            RECT rect;
                            m_PictureBoxStream.GetWindowRect( &rect );
                            ScreenToClient( &rect );
                            InvalidateRect( &rect, false );
                        }
                    }
                }             
            }
            else
            {
                // If we receive an incomplete image we do nothing
                err = VmbErrorOther;
            }
        }
        Log( _TEXT("Acquire single image"), err );
    }
    else
    {
        m_ListLog.InsertString( 0, CString( "Please select a camera." ));
    }
}

// This event handler is triggered through a MFC message posted by the camera observer
LRESULT CSynchronousGrabDlg::OnCameraListChanged( WPARAM reason, LPARAM lParam )
{
    bool bUpdateList = false;

    // We only react on new cameras being found and known cameras being unplugged
    if ( UpdateTriggerPluggedIn == reason )
    {
        m_ListLog.InsertString( 0, CString( "Camera list changed. A new camera was discovered by Vimba." ));
        bUpdateList = true;
    }
    else if ( UpdateTriggerPluggedOut == reason )
    {
        m_ListLog.InsertString( 0, CString( "Camera list changed. A camera was disconnected from Vimba." ));
        bUpdateList = true;
    }
    
    if ( true == bUpdateList )
    {
        UpdateCameraListBox();
    }

    return 0;
}

// Converts mono 8 bit to mono bgr
void CSynchronousGrabDlg::MonoToBGR( VmbUchar_t *pInBuffer, VmbUchar_t *pOutBuffer, VmbUint32_t nInSize )
{
    while( 0 < nInSize-- )
    {
        for ( int i=0; i<NUM_COLORS; ++i )
        {
            *pOutBuffer = *pInBuffer;
            ++pOutBuffer;
        }

        ++pInBuffer;
    }
}

// Copies the content of a byte buffer to a MFC image with respect to the image's alignment
void CSynchronousGrabDlg::CopyToImage( VmbUchar_t *pInBuffer, CImage *pOutImage )
{
    if ( NULL != *pOutImage )
    {
        VmbUchar_t *    pCursor     = (VmbUchar_t*)pOutImage->GetBits();
        int             nHeight     = m_pApiController->GetHeight();
        int             nWidth      = m_pApiController->GetWidth() * NUM_COLORS;
        int             nStride     = pOutImage->GetPitch() - nWidth;

        if ( 0 < nStride)
        {
            for ( int y=0; y<nHeight; ++y )
            {
                for ( int x=0; x<nWidth; ++x )
                {
                    *pCursor = *pInBuffer;
                    ++pCursor;
                    ++pInBuffer;
                }
                // Consider stride
                pCursor += nStride;
            }
        }
        else
        {
            memcpy( pOutImage->GetBits(), pInBuffer, nWidth * nHeight );
        }
    }
}

// Queries and lists all known camera
void CSynchronousGrabDlg::UpdateCameraListBox()
{
    // Get all cameras currently connected to Vimba
    CameraPtrVector cameras = m_pApiController->GetCameraList();

    // Simply forget about all cameras known so far
    m_ListBoxCameras.ResetContent();
    m_cameras.clear();

    // And query the camera details again
    for (	CameraPtrVector::const_iterator iter = cameras.begin();
            cameras.end() != iter;
            ++iter )
    {
        std::string strInfo;
        std::stringstream strInfos;
        if ( VmbErrorSuccess == (*iter)->GetName( strInfo ))
        {
            strInfos << strInfo << " ";
        }
        else
        {
            strInfos << "[NoName] ";
        }
        // If for any reason we cannot get the ID of a camera we skip it
        if ( VmbErrorSuccess == (*iter)->GetID( strInfo ))
        {
            strInfos << strInfo;
            m_ListBoxCameras.AddString( CString(strInfos.str().c_str() ));
            m_cameras.push_back( strInfo );
        }
    }

    // Select first cam if none is selected
    if (    -1 == m_ListBoxCameras.GetCurSel()
         && 0 < m_cameras.size() )
    {
        m_ListBoxCameras.SetCurSel( 0 );
    }
}

// Prints out some logging
void CSynchronousGrabDlg::Log( string_type strMsg, VmbErrorType eErr )
{
    string_stream_type strErr;
    strErr << strMsg << _TEXT("...") << m_pApiController->ErrorCodeToMessage( eErr );
    m_ListLog.InsertString( 0, strErr.str().c_str() );
}


//
// The remaining functions are MFC intrinsic only
//

HCURSOR CSynchronousGrabDlg::OnQueryDragIcon()
{
    return static_cast<HCURSOR>(m_hIcon);
}

void CSynchronousGrabDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialog::DoDataExchange(pDX);
    DDX_Control( pDX, IDC_LIST_CAMERAS, m_ListBoxCameras );
    DDX_Control( pDX, IDC_LIST_LOG, m_ListLog );
    DDX_Control( pDX, IDC_BUTTON_STARTSTOP, m_ButtonStartStop );
    DDX_Control( pDX, IDC_PICTURE_STREAM, m_PictureBoxStream );
}

void CSynchronousGrabDlg::OnPaint()
{
    if (IsIconic())
    {
        CPaintDC dc(this);

        SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

        int     cxIcon  = GetSystemMetrics(SM_CXICON);
        int     cyIcon  = GetSystemMetrics(SM_CYICON);
        CRect   rect;
        GetClientRect(&rect);
        int     x       = (rect.Width() - cxIcon + 1) / 2;
        int     y       = (rect.Height() - cyIcon + 1) / 2;
        dc.DrawIcon(x, y, m_hIcon);
    }
    else
    {
        CDialog::OnPaint();

        if ( NULL != m_Image )
        {
            CPaintDC    dc( &m_PictureBoxStream );
            CRect       rect;
            m_PictureBoxStream.GetClientRect( &rect );
            // HALFTONE enhances image quality but decreases performance
            dc.SetStretchBltMode( HALFTONE );
            m_Image.StretchBlt( dc.m_hDC, rect );
        }
    }
}
