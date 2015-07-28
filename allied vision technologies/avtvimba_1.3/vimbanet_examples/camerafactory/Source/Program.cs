/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of CameraFactory example of VimbaNET.

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

class Program
{
    static void Main( string[] args )
    {
        Console.WriteLine();
        Console.WriteLine( "///////////////////////////////////////////" );
        Console.WriteLine( "/// AVT Vimba API CameraFactory Example ///" );
        Console.WriteLine( "///////////////////////////////////////////" );
        Console.WriteLine();

        try
        {
            if ( 0 < args.Length )
            {
                Console.WriteLine( "No parameters expected. Execution will not be affected by the provided parameter(s)." );
                Console.WriteLine();
            }

            FindCameras.Print();
        }
        catch ( VimbaException ve )
        {
            Console.WriteLine( ve.Message );
            Console.Write( "Return Code: " + ve.ReturnCode.ToString() + " (" + ve.MapReturnCodeToString() + ")" );
        }
        catch ( Exception e )
        {
            Console.WriteLine( e.Message );
        }

        Console.WriteLine();
    }
}

}}} // Namespace AVT::Vimba::Exanples
