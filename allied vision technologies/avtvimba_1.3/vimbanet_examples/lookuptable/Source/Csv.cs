/*=============================================================================
  Copyright (C) 2012 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Csv.cs

  Description: Helper to access a CSV file using VimbaNET.
               

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
using System.IO;
using System.Text;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

public class Csv
{
    private char m_VD;
    private char m_RD;
    private bool bHasHeader;

    public Csv()
    {
        m_VD = ';';
        m_RD = '\n';
        bHasHeader = false;
    }
        
    public char VD
    {
        set
        {
            m_VD = value;
        }
        get
        {
            return m_VD;
        }
    }

    public char RD
    {
        get
        {
            return m_RD;
        }
    }


    public bool HasHeader
    {
        get
        {
            return bHasHeader;
        }
    }

    // Class to store a CSV row
    public class CsvRow : List<string>
    {
        public string LineText { get; set; }
    } // class CsvRow

    // Class to write data to a CSV file
    public class CsvSave : StreamWriter
    {
        private Csv m_instance;

        public CsvSave(string filename, Csv instance)
            : base(filename)
        {
            m_instance = instance;
        }

        // Writes a single row to a CSV file.
        public void Row(CsvRow row)
        {
            StringBuilder builder = new StringBuilder();
            foreach (string value in row)
            {
                builder.Append(value);
            }
            row.LineText = builder.ToString();
            WriteLine(row.LineText);
        }
    }; // class CsvSave

    // Class to load data from CSV
    public class CsvLoad : StreamReader
    {
        private Csv m_instance;

        public CsvLoad(string filename, Csv instance)
            : base(filename)
        {
            m_instance = instance;
        }

        // Reads a row of data from CSV
        public bool Row(CsvRow row)
        {
            row.LineText = ReadLine();
            if (String.IsNullOrEmpty(row.LineText))
                return false;

            int pos = 0;
            int rows = 0;

            while (pos < row.LineText.Length)
            {
                string value;

                int start = pos;
                while (pos < row.LineText.Length && row.LineText[pos] != m_instance.m_VD)
                {
                    pos++;
                }
                value = row.LineText.Substring(start, pos - start);

                // Add field to list
                if (rows < row.Count)
                {
                    row[rows] = value;
                }
                else
                {
                    row.Add(value);
                }
                rows++;

                if (pos < row.LineText.Length)
                {
                    pos++;
                }
            }

            // Delete unused items
            while (row.Count > rows)
            {
                row.RemoveAt(rows);
            }

            return (row.Count > 0);
        }
    }; // class CsvLoad
}; // class Csv

}}} // Namespace AVT.VmbAPINET.Examples
