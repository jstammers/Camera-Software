#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Store and display fit results in table."""

from __future__ import with_statement

import wx
import wx.grid
import wx.aui

import numpy
import sys

from observer import Subject, changes_state
import gridtypes
import dynamic_expressions

import functools
import re
import types
from custom_events import ReloadImageEvent
from settings import varfile
class DynamicExpressionDialog(wx.Dialog):
    """
    Create dialog for entering dynamic expressions.
    """
    def __init__(self, parent, title, expression = ''):
        wx.Dialog.__init__(self, parent, -1, title, )
        
        if 0:
            reload(dynamic_expressions)  #use most recent entries in
                                #moduly dynamic_expressions NOTE: this
                                #fails if cwd has changed (e.g., due
                                #to saving results)

        sizer = wx.BoxSizer(wx.VERTICAL)

        #top label
        label = wx.StaticText(self, -1, 'Enter dynamic expression')
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        #entry with label
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, 'expression:')
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.text = wx.ComboBox(self, -1, value = expression,
                                choices = dynamic_expressions.dynamic_expressions)
        box.Add(self.text, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        #bottom line
        line = wx.StaticLine(self, -1, size = (20,-1), style = wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        #buttons
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)


def changes_data(f):
    """decorator for methods which changes data. Needed to see wheter
    file has been modified after last save. Changes attribute
    'modified'."""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        self.modified = True
        return f(self, *args, **kwargs)
    return wrapper


def query_yes_no(question, default = 'yes'):
    valid = {'yes':True,'no':False,'y':True,'n':False,'ye':True}
    if default is None:
        prompt = '[y/n]'
    elif default == 'yes':
        prompt = '[Y/n]'
    elif default == 'no':
        prompt = '[y/N]'
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question+prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' ")
class FitResultDataTable(wx.grid.PyGridTableBase, Subject):
    """
    Stores and handles all data for fit results.
    """
    
    def __init__(self):
        wx.grid.PyGridTableBase.__init__(self)

        self.begin_batch() #avoid updates

        #initialize fields

        #NOTE: if columns added, perhaps it's necessary to change fitpar
        #below
        var_bool = query_yes_no("Load extra variables from the Variables.txt file?")
       
        varlist = []
        if var_bool:
            var_array=numpy.loadtxt(varfile,skiprows = 1,dtype={'names':('variables','values'),'formats':('S15','f4')})
            for line in var_array:
                    varlist.append(line[0])
                    varlist.append('double_empty:5,3')
                    varlist.append(2)
                    if line ==var_array[0]:
                            varlist.append(1)
                    else:
                            varlist.append(0)
                    varlist.append('')
        
        rowlist=[
            #name       type          dynamic show
            'FileID',   'long',             0, 1, '',  #0
            'Filename', 'string',           0, 0, '',  #1
            #'N K',      'double_empty:4,1', 0, 1, 'K', #2
            #'Nerr K',   'double_empty:4,2', 0, 0, 'K',
            #'Nth K',    'double_empty:4,1', 0, 0, 'K', #3
            #'Nbec K',   'double_empty:4,1', 0, 0, 'K', #4
            #'OD K',     'double_empty:4,1', 0, 0, 'K', #5
            #'sx K',     'double_empty:4,1', 0, 1, 'K', #6
            #'sxerr K',  'double_empty:4,2', 0, 0, 'K', #7
            #'sy K',     'double_empty:4,1', 0, 1, 'K', #8
            #'syerr K',  'double_empty:4,2', 0, 0, 'K', #9
            #'rx K',     'double_empty:4,1', 0, 0, 'K', #10
            #'rxerr K',  'double_empty:4,2', 0, 0, 'K', #11
            #'ry K',     'double_empty:4,1', 0, 0, 'K', #12
            #'ryerr K',  'double_empty:4,2', 0, 0, 'K', #13
            #'mx K',     'double_empty:4,1', 0, 0, 'K', #14
            #'myerr K',  'double_empty:4,2', 0, 0, 'K', #15
            #'my K',     'double_empty:4,1', 0, 0, 'K', #16
            #'myerr K',  'double_empty:4,2', 0, 0, 'K', #17
            #'T K',      'double_empty:4,3', 0, 1, 'K', #18
            #'Terr K',   'double_empty:4,3', 0, 0, 'K', #19
            #'sigma K',  'double_empty:4,3', 0, 0, 'K',
            #'params K', 'string',           0, 0, 'K', #20
            'N Rb',     'double_empty:4,1', 0, 1, 'Rb',#21
            'Nerr Rb',  'double_empty:4,2', 0, 0, 'Rb',#21
            'Nth Rb',   'double_empty:4,1', 0, 0, 'Rb',#22
            'Nbec Rb',  'double_empty:4,1', 0, 0, 'Rb',#23
            'OD Rb',    'double_empty:4,1', 0, 0, 'Rb',#24
            'ODerr Rb', 'double_empty:4,1', 0, 0, 'Rb',#25
            'sx Rb',    'double_empty:4,1', 0, 1, 'Rb',#26
            'sxerr Rb', 'double_empty:4,2', 0, 0, 'Rb',#27
            'sy Rb',    'double_empty:4,1', 0, 1, 'Rb',#28
            'syerr Rb', 'double_empty:4,2', 0, 0, 'Rb',#29
            'rx Rb',    'double_empty:4,1', 0, 0, 'Rb',#30
            'rxerr Rb', 'double_empty:4,2', 0, 0, 'Rb',#31
            'ry Rb',    'double_empty:4,1', 0, 0, 'Rb',#32
            'ryerr Rb', 'double_empty:4,2', 0, 0, 'Rb',#33
            'mx Rb',    'double_empty:4,1', 0, 0, 'Rb',#34
            'mxerr Rb', 'double_empty:4,2', 0, 0, 'Rb',#35
            'my Rb',    'double_empty:4,1', 0, 0, 'Rb',#36
            'myerr Rb', 'double_empty:4,2', 0, 0, 'Rb',#37
            'T Rb',     'double_empty:4,3', 0, 1, 'Rb',#38
            'Terr Rb',  'double_empty:4,3', 0, 0, 'Rb',#39
            'sigma Rb', 'double_empty:4,3', 0, 0, 'Rb',
            'params Rb','string',           0, 0, 'Rb',#40
            'dynamic',  'double_empty:5,3', 1, 1, '',  #41
            'dynamic 2','double_empty:5,3', 1, 0, '',  #42
            'dynamic 3','double_empty:5,3', 1, 0, '',  #43
            'dynamic 4','double_empty:5,3', 1, 0, '',  #44
            'user',     'double_empty:5,3', 0, 1, '',  #45
            'user2',    'double_empty:5,3', 0, 0, '',  #45
            'user3',    'double_empty:5,3', 0, 0, '',  #46
            'Omit',     'bool_custom',      0, 1, '',  #47
            #'Remark',   'string',           0, 1, '',  #48
            ]
        _columns = numpy.array(rowlist+varlist+['Remark','string',0,1,''], dtype = numpy.object)
        #_columns.shape = (-1, 5)

               
        #_columns = numpy.append(_columns,['Remark','string', 0, 1, ''])
        _columns.shape = (-1, 5)

        self.colLabels = _columns[:,0] #:column labels
        self.dataTypes = _columns[:,1] #:data types

        #:indices of columns whith dynamic content
        self.dynamic_cols = list(numpy.where(_columns[:,2]==1)[0])
        self.variable_cols= list(numpy.where(_columns[:,2]>1)[0])
        print self.variable_cols
        #:expressions for dynamic columns"
        self.dynamic_expressions = ['']*len(self.dynamic_cols)
        
        #:date stored in table, as numpy array of objects
        self.data = numpy.array(
            ['']*len(self.colLabels),
            dtype = numpy.object,
            ndmin = 2
            )

        #dict (keys: species) for list of columns of fit params
        self.fitparcols = {'K': [], 'Rb': []}
        for col, species in enumerate(_columns[:,4]):
            if species:
                self.fitparcols[species].append(col)

        #:which rows are masked
        self.rowmask = numpy.array([False])

        #:dictionary for custom column labels
        self.column_labels_custom = {} 

        #:indices of columns that are displayed
        self.colsel = list(_columns[:,3].nonzero()[0])

        #:initialize column sizes
        self.colsize = [50]*len(self.colLabels) #array to store width of columns
        self.colsize[-2] = 30
        self.colsize[-1] = 200

        #dict of sets to store column numbers which shall be displayed as X or Y values
        self.marks = {'X': set(),
                      'Y1': set(),
                      'Y2': set(),
                      'G': set(),
                      }

        self.CanHaveAttributes() #TODO: nötig???

        #:measurement name
        self.name = ""

        #:associated filename
        self.filename = None

        #:is the active table
        self.active = True

        #:do record values
        self.record = True

        #:Table is not (yet) modified
        self.modified = False

        #observers
        self.observers = set()

        self.end_batch()
      
          

    #{ required methods for the wxPyGridTableBase interface
    def GetNumberRows(self):
        return len(self.data)
        
    def GetNumberCols(self):
        return len(self.colsel)

    def IsEmptyCell(self, row, col):
        try:
            val = self.data[row, self.colsel[col]]
            if val is None or val is '':
                return True
            else:
                return False
            
        except IndexError:
            return True

    def GetValue(self, row, col):
        try:
            return self.data[row, self.colsel[col]]
        except IndexError:
            return ''

    @changes_state
    @changes_data
    def SetValue(self, row, col, value):
        """Set value if user set value. If necessary, append
        rows. Updates dynamic columns. Signal this to observers.
        @param col: column numbered as visible
        """
        try:
            self.data[row, self.colsel[col]] = value
        except IndexError:
            while self.GetNumberRows()-1<=row:
                self.AppendRows()
            self.data[row, self.colsel[col]] = value
            
        self.update_dynamic_cols(row)

    def GetColLabelValue(self, col):
        """Get column labels as displayed on top of table. Add markers
        to name of column"""
        label = self.column_label(self.colsel[col])
        
        labels = []
        for mark in sorted(self.marks.keys()):
            if self.colsel[col] in self.marks[mark]:
                labels.append(mark)

        if labels:
            return label + "\n(" + ','.join(labels) + ')'
        else:
            return label
        
    def GetRowLabelValue(self, row):
        if self.active:
            if row == self.GetNumberRows() - 2:
                return "next"
            elif row == self.GetNumberRows() - 1:
                return "..."
        else:
            if row >= self.GetNumberRows() - 2:
                return ""

        return "%d"%(row + 0)

    def GetTypeName(self, row, col):
        return self.dataTypes[self.colsel[col]]

    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[self.colsel[col]].split(':')[0]
        #check for substring! e.g., 'double' matches custom type
        #'double_empty'
        return typeName in colType 

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

    #{ Additional methods
    def SetValueRaw(self, row, rawcol, value):
        """Set value of entry. For internal use.
        @param rawcol: column numbered like in Table (not on screen)
        """
        try:
            self.data[row, rawcol] = value
        except IndexError:
            while self.GetNumberRows()-1<=row:
                self.AppendRows()
            self.data[row, rawcol] = value

    def GetValueRaw(self, row, rawcol):
        return self.data[row, rawcol]

    def colname_to_raw(self, field):
        rawcol = numpy.flatnonzero(self.colLabels == field)
        return rawcol[0] if len(rawcol) == 1 else None

    def raw_to_colname(self, rawcol):
        try:
            return self.colLabels[rawcol]
        except IndexError:
            return None

    def SetValueNamed(self, row, field, value):
        rawcol = self.colname_to_raw(field)
        if rawcol is not None:
            self.SetValueRaw(row, rawcol, value)
        else:
            raise ValueError('no column named "%s"'%field)

    def GetValueNamed(self, row, field):
        rawcol = self.colname_to_raw(field)
        if rawcol is not None:
            return self.GetValueRaw(row, rawcol)
        else:
            raise ValueError('no column named "%s"'%field)

    def column_label(self, rawcol):
        """helper function to get column label
        @param rawcol: column numbered like in full table
        """
        label = self.colLabels[rawcol]

        try:
            idx = self.dynamic_cols.index(rawcol)
        except ValueError:
            pass
        else:
            if self.dynamic_expressions[idx]:
                label = self.dynamic_expressions[idx]

        #custom labels overrides automic column labels
        custom_label = self.column_labels_custom.get(rawcol)
        if custom_label:
            label = custom_label

        return label

    @changes_data
    def AppendRows(self, numRows = 1):
        """Append empty rows to table"""
        for i in range(numRows):
            self.data = numpy.vstack((self.data,
                                      numpy.array([''] * self.data.shape[1], dtype = numpy.object),
                                      ))
        self.rowmask = numpy.append(self.rowmask, numpy.zeros((numRows,), dtype = numpy.bool))

        msg = wx.grid.GridTableMessage(self,
                                       wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                                       numRows)
        #if not self._batchcount:
        #    self.GetView().ProcessTableMessage(msg)
        self.GetView().ProcessTableMessage(msg)
        return True

    @changes_state
    @changes_data
    def UpdateResults(self, data, row = None):
        """Update values of actual row (only if active) from fit results.
        @param data: dict, possibly with keys 'K', 'Rb', ...
        """
        if not self.active:
            return

        if row is None:
            row = self.active_row

        self.SetValueRaw(row, 0, row) #set FileID

        #take only values from fit with match column labels
        for species, fitpars in data.iteritems():

            #clear fit parameter entries for species TODO: always
            #cleared, even if fitpars not valid (Note: NoFit says
            #invalid
            for rawcol in self.fitparcols[species]:
                self.SetValueRaw(row, rawcol, None)

            if fitpars.valid:
                for key, val in fitpars.valuedict().iteritems():
                    try:
                        rawcol = self.colLabels.tolist().index(key+' '+species)
                        self.SetValueRaw(row, rawcol, val)
                    except ValueError:
                        pass

        self.update_dynamic_cols()
        self.update_variable_cols()

        self.GetView().MakeCellVisible(row, 0)
        self.GetView().Refresh()

    def UpdateFilename(self, filename):
        """Update filename entry"""
        if not self.active:
            return
        
        row = self.active_row
        col = self.colname_to_raw('Filename')
        self.SetValueRaw(row, col, filename)
        self.GetView().Refresh()

    def DeleteCols(self, pos=0, numcols=1):
        pass

    def AppendCols(self, numcols=1, updateLabels = True):
        pass

    #not used
    #def DeleteRows(self, pos = 0, numRows = 1):
    #   print "Delete Rows", numRows, pos

    def SetColSize(self, col, size):
        self.colsize[self.colsel[col]] = size

    def GetColSize(self, col):
        return self.colsize[self.colsel[col]]

    @changes_state
    @changes_data
    def SetColMark(self, col, mark, remove = False):
        """Set (or remove) column mark.
        @param col: column number, for which mark s be set
        @param mark: mark. One of 'X', 'Y1', 'Y2', 'G', ...
        @type mark: string
        @param remove: if True, remove mark for column
        """
        if not remove:
            if mark == "X" or mark == 'G':
                #only one column can be labeled as 'X', remove existing 'X' mark
                self.marks[mark].clear()
            self.marks[mark].add(self.colsel[col])
        else:
            self.marks[mark].remove(self.colsel[col])

    def GetAttr(self, row, col, kind):
        """Give attribute (colour, font, ...) for entry."""
        
        #print "Get Attr",row,col,kind

        provider = self.GetAttrProvider()
        if provider and provider.GetAttr(row, col, kind):
            attr = provider.GetAttr(row, col, kind).Clone()
        else:
            attr = wx.grid.GridCellAttr()

        #color marks
        if self.colsel[col] in self.marks['X']:
            attr.SetBackgroundColour(wx.Color(255, 230, 230))
        elif self.colsel[col] in self.marks['Y1']:
            attr.SetBackgroundColour(wx.Color(255, 255, 205))
        elif self.colsel[col] in self.marks['Y2']:
            attr.SetBackgroundColour(wx.Color(255, 255, 155))
        elif self.colsel[col] in self.marks['G']:
            attr.SetBackgroundColour(wx.Color(155, 255, 155))

        #color dynamic columns
        if self.colsel[col] in self.dynamic_cols:
            attr.SetBackgroundColour(wx.Color(200, 200, 200))

        #color last rows
        maxRows = self.GetNumberRows()
        if self.active:
            if maxRows - row == 1: #last row
                attr.SetBackgroundColour(wx.Color(255, 230, 230))
            elif maxRows - row == 2: #second to last row
                attr.SetBackgroundColour(wx.Color(255, 255, 205))
            elif maxRows - row == 3:
                if self.record:
                    attr.SetBackgroundColour(wx.Color(200, 255, 200))
                else:
                    attr.SetBackgroundColour(wx.Color(255, 100, 100))
        else:
            if maxRows - row <= 2:
                attr.SetBackgroundColour(wx.Color(127, 127, 127))

        if self.rowmask[row]:
            attr.SetTextColour(wx.Color(0,0,255))
            
        return attr

    @changes_state
    @changes_data
    def maskrows(self, rows, setmask = True):
        self.rowmask[rows] = setmask

    @changes_state
    @changes_data
    def omitrows(self, rows):
        col = self.colname_to_raw('Omit')
        for row in rows:
            self.data[row][col] = True

    def colhasmark(self, col, mark):
        "return True if column col is marked mit mark"
        return self.colsel[col] in self.marks.get(mark, [])

    #{ service methods for plot
    @property
    def plotdata(self):

        #collect x values
        if len(self.marks['X']) == 1:
            xcol = tuple(self.marks['X'])
            xdata = numpy.ma.zeros((self.GetNumberRows()-2,))
            xdata.mask = numpy.ma.getmaskarray(xdata)

            for k, row in enumerate(self.data[:-2]):
                try:
                    xdata[k] = row[xcol]
                except ValueError:
                    xdata.mask[k] = True

            xcollabel = self.column_label(xcol[0]) #xcol is tuple with single entry
        else:
            xcol = None
            xdata = numpy.ma.array([])
            xcollabel = ''

        #collect group values
        if len(self.marks['G']) == 1:
            gcol = tuple(self.marks['G'])
            gdata = numpy.ma.zeros((self.GetNumberRows()-2,))
            gdata.mask = numpy.ma.getmaskarray(gdata)

            for k, row in enumerate(self.data[:-2]):
                try:
                    gdata[k] = row[gcol]
                except ValueError:
                    gdata.mask[k] = True

            gcollabel = self.column_label(gcol[0]) #xcol is tuple with single entry
        else:
            gcol = None
            gdata = numpy.ma.array([])
            gcollabel = ''

        #collect ydata (list of arrays)
        ycols = []
        ydatas = []
        ycollabels = []

        for ymark in ['Y1', 'Y2']:
            ycol = sorted(self.marks[ymark])
            if len(ycol):
                ydata = numpy.ma.zeros((self.GetNumberRows()-2, len(ycol)))
                ydata.mask = numpy.ma.getmaskarray(ydata)

                #collect ycols data
                for k, row in enumerate(self.data[:-2]):
                    for yi, yc in enumerate(ycol):
                        try:
                            ydata[k, yi] = row[yc]
                        except ValueError:
                            ydata.mask[k, yi] = True

                ycols.append(ycol)
                ydatas.append(ydata)
                ycollabels.append(map(self.column_label, ycol))
                

        #masked entries
        masked = self.rowmask[:-2]

        #collect yid and omitted
        #init arrays
        yid = numpy.zeros(shape = (self.GetNumberRows()-2,), dtype = numpy.integer)
        omitted = numpy.zeros(shape = (self.GetNumberRows()-2,), dtype = numpy.bool_)

        omitcol = self.colname_to_raw('Omit')
        for k, row in enumerate(self.data[:-2]):
            yid[k] = k
            if row[omitcol]: 
                omitted[k] = True

        def sel(data, take):
            if len(data):
                return data[take]
            else:
                return data

        #remove omitted values
        take = ~omitted
        #ydatas = [data[take] for data in ydatas]
        for k, data in enumerate(ydatas):
            #print k, repr(take), repr(data)
            ydatas[k] = data[take]
            
        xdata, yid, masked, gdata = \
               (sel(data, take) for data in
                (xdata, yid, masked, gdata))

        ##TODO: won't work
        #for data in [xdata,yid,omitted,gdata, masked]+ydatas:
        #    if len(data):
        #        data = data[take]

        #calculate group indices (i.e. integer to which group each data point belongs
        #use group index -1 for empty group value
        gvals = []
        if gcol:
            gidx = -1*numpy.ones(xdata.shape, dtype = numpy.int_)
            for idx, val in enumerate(numpy.unique(gdata).compressed()):
                gidx[gdata==val] = idx
                gvals.append(val)
        else:
            gidx = numpy.zeros(xdata.shape, dtype = numpy.int_)

        gvals = numpy.asarray(gvals)

        #sort data
        if xcol:
            sortind = xdata.argsort()

            ydatas = [data[sortind] for data in ydatas]
            xdata, yid, gidx, masked, gdata =\
                   (sel(data, sortind) for data in
                    (xdata, yid, gidx, masked, gdata))

        d = dict()
        d['yid'] = yid

        d['xcol'] = xcol
        d['xcollabel'] = xcollabel
        
        d['ycols'] = ycols
        d['ycollabels'] = ycollabels

        d['gcol'] = gcol
        d['gdata'] = gdata
        d['gcollabel'] = gcollabel
        d['gidx'] = gidx
        d['gvals'] = gvals

        d['masked'] = masked
        
        d['name'] = self.name

        ydatas = [data for data in ydatas if data.size] #TODO this doesn't remove empty arrays!
        
        #print len(ydatas), [data.shape for data in ydatas]

        return (xdata, ydatas, d)

    @property
    def active_row(self):
        row = max(0, self.GetNumberRows() - 3)
        return row

    #@changes_state
    def activate(self, status = True):
        self.active = status

    def set_record(self, status = True):
        self.record_data = status

    def get_record(self):
        return self.record_data

    record = property(get_record, set_record)

    def update_dynamic_cols(self, row = None, column = None):
        """
        recalculate values of 'dynamic columns'.
        @param row: row. If no argument given, recalculate value of active (last) row
        @param column: column. If not given, recalculate all dynamic columns
        """
        if row is None:
            row = self.active_row

        valuedict = {}
        for label, value in zip(self.colLabels, self.data[row].tolist()):
            valuedict[label.replace(' ', '_')] = value
        
        for col, expression in zip(self.dynamic_cols, self.dynamic_expressions):
            if column is None or col == column: 
                try:
                    result = eval(expression, valuedict)
                except StandardError:
                    #print "Error evaluation expression", expression
                    self.SetValueRaw(row, col, None)
                else:
                    self.SetValueRaw(row, col, result)
    def update_variable_cols(self,row=None,column=None):
        if row is None:
            row=self.active_row
        var_array=numpy.loadtxt(varfile,skiprows = 1,dtype={'names':('variables','values'),'formats':('S10','f4')})

        i=0
        print self.variable_cols
        for col in self.variable_cols:
            self.SetValueRaw(row,col,var_array[i][1])
            i+=1

    #@changes_data #(reset = True) #TODO: decorator with parameter?
    def save_data_csv(self, filename):
        """save data in comma seperated format."""
        #add masked entry as last column
        fields = numpy.r_[self.colLabels, ['masked']]

        #add dynamic expression to column headers
        for k, col in enumerate(self.dynamic_cols):
            fields[col] += " [%s]"%self.dynamic_expressions[k] if self.dynamic_expressions[k] else ''

        #add custom labels to field names 
        for col, fieldname in enumerate(fields):
            custom_label = self.column_labels_custom.get(col)
            fields[col] += " (%s)"%custom_label if custom_label else ''

            fields[col] += " {*}" if (col in self.colsel and (fieldname.find('user')==0 or col in self.dynamic_cols)) else ''
            
        #add options
        
        
        #don't save last two lines
        data   = numpy.c_[self.data[:-2], self.rowmask[:-2]]

        with open(filename, 'wb') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(fields)
            #writer.writerows(data)
            for row in data:
                r = [entry.encode('latin_1') if type(entry) is types.UnicodeType else entry for entry in row]
                writer.writerow(r)
            self.modified = False

    def load_data_csv(self, filename):
        """load date from csv file into table"""
        import csv

        self.begin_batch() #avoid unecessary updates

        #delete old data
        #TODO: check of deleting data is really what user wants
        #TODO: create method for clearing data
        msg = wx.grid.GridTableMessage(self,
                                       wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                                       0,
                                       self.GetNumberRows())
        self.rowmask = numpy.array([], dtype = numpy.bool)
        self.data = numpy.empty(shape = (0, len(self.colLabels)), dtype = numpy.object)
        self.GetView().ProcessTableMessage(msg)
        
        #process file
        with open(filename, 'rb') as f:

            #read first row to extract fieldnames
            header = csv.reader(f).next()

            #parse field header "name [dynamic] (custom label)"
            pattern = re.compile(r"(?P<name>\w+(\s\w+)?)\s*(\[(?P<dynamic>.*)\])?\s*(\((?P<label>.*)\))?\s*(\{(?P<options>.*)\})?",
                                 re.VERBOSE)
            fields = []
            dyn_expr = {}
            cust_label = {}
            vis_cols = {}
            for entry in header:
                r = pattern.match(entry)
                d = r.groupdict()
                name = d['name']
                if name:
                    fields.append(name)
                    if d['dynamic']: dyn_expr[name] = d['dynamic']
                    if d['label']: cust_label[name] = d['label']
                    if d['options']:
                        if '*' in d['options']: vis_cols[name] = True

            #set dynamic expressions
            for k, col in enumerate(self.dynamic_cols):
                dexpr = dyn_expr.get(self.colLabels[col])
                if dexpr:
                    self.dynamic_expressions[k] = dexpr

            #set custom column labels
            for k, label in enumerate(self.colLabels):
                clabel = cust_label.get(label)
                if clabel:
                    self.column_labels_custom[k] = clabel

            #also show columns which are marked as visible in csv file
            colsel = set(self.colsel)
            for k, label in enumerate(self.colLabels):
                if vis_cols.get(label):
                    colsel.add(k)
            colsel = list(colsel)
            colsel.sort()
            self.View.SetColumnSelection(colsel)

            #read data
            reader = csv.DictReader(f, fieldnames = fields)

            row = -1
            for rowdict in reader:
                row += 1
                self.AppendRows()

                if rowdict.get('masked') == 'True':
                    self.maskrows(row)

                #loop over columns in _actual_ table, 
                for col, typelabel in enumerate(zip(self.dataTypes, self.colLabels)):
                    datatype, label = typelabel

                    #ask csv reader whether corresponding entry exists    
                    value = rowdict.get(label)
                    if value is None or value == '':
                        continue

                    try:
                        #convert string value to proper type
                        #TODO: optimize it by creating a table of conversion functions
                        #or a table method that takes a string
                        if wx.grid.GRID_VALUE_FLOAT in datatype:
                            val = float(value)
                        elif wx.grid.GRID_VALUE_NUMBER in datatype:
                            val = int(value)
                        elif wx.grid.GRID_VALUE_BOOL in datatype:
                            if value == '1' or value == 'True':
                                val = True
                            else:
                                val = False
                        elif wx.grid.GRID_VALUE_STRING in datatype:
                            val = value
                        else:
                            print "loading of type %s is not supported"%datatype
                            continue

                        self.SetValueRaw(row, col, val)
                    except ValueError:
                        print "warning reading csv: cannot convert value '%s' to type %s"%(value, datatype)

        self.AppendRows(2)        
        self.end_batch()
        self.modified = False

    def give_metadata(self):
        """return metadata, not stored in table data, e.g. which
        columns are displayed, dynamic expressions, marks, ..."""

        m = dict()
        m['dynamic_expressions'] = self.dynamic_expressions

        cust_labels = {}
        for key, value in self.column_labels_custom.iteritems():
            cust_labels[self.raw_to_colname(key)] = value
        m['column_labels_custom'] = cust_labels

        m['colsel'] = [self.raw_to_colname(col) for col in self.colsel]

        colsizedict = {}
        for col, size in enumerate(self.colsize):
            colsizedict[self.raw_to_colname(col)] = size
        m['colsize'] = colsizedict

        marksdict = {}
        for mark, colset in self.marks.iteritems():
            marksdict[mark] = [self.raw_to_colname(col) for col in colset]
        m['marks']  = marksdict

        m['name'] = self.name
        return m

    def set_metadata(self, m):
        """opposite of give_metadata..."""

        m_dyn_ex = m['dynamic_expressions']
        self.dynamic_expressions[0:len(m_dyn_ex)] = m_dyn_ex

        m_cust_lab = m['column_labels_custom']
        cust_labels = {}
        for name, value in m_cust_lab.iteritems():
            cust_labels[self.colname_to_raw(name)] = value
        self.column_labels_custom = cust_labels

        self.colsel = [self.colname_to_raw(name) for name in m['colsel']]

        colsize = {}
        for name, size in m['colsize'].iteritems():
            colsize[self.colname_to_raw(name)] = size

        dcolsize = m['colsize']
        for col in range(len(colsize)):
            size = dcolsize.get(self.raw_to_colname)
            if size is not None:
                self.colsize[col] = size

        for mark, colnames in m['marks'].iteritems():
            self.marks[mark] = set([self.colname_to_raw(name) for name in colnames])

                
class FitResultDataTableGrid(wx.grid.Grid):

    ID_popup_MaskRow         = wx.NewId()
    ID_popup_MaskSelection   = wx.NewId()
    ID_popup_UnmaskSelection = wx.NewId()
    ID_popup_OmitSelection   = wx.NewId()
    ID_popup_ReloadRow       = wx.NewId()

    ID_popup_Column_SetX     = wx.NewId()
    ID_popup_Column_SetY1    = wx.NewId()
    ID_popup_Column_SetY2    = wx.NewId()
    ID_popup_Column_SetG     = wx.NewId()
    ID_popup_Select_Columns  = wx.NewId()
    ID_popup_Set_Column_Label= wx.NewId()
    ID_popup_Column_SetExpression = wx.NewId()
    ID_popup_Column_Recalculate   = wx.NewId()
    
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)

        self.RegisterDataType('double_empty',
                              gridtypes.FloatRenderer(),
                              wx.grid.GridCellFloatEditor())

        self.RegisterDataType('bool_custom',
                              gridtypes.BoolRenderer(),
                              gridtypes.BoolEditor()
                              )

        table = FitResultDataTable()
        self.SetTable(table, True)
        
        #self.SetRowLabelSize(0)
        self.SetMargins(0,0)

        #self.AutoSizeColumns(False)

        #self.SetDefaultColSize(50, True) #not necessary, overwritten by next line?
        self.RestoreColSizes()

        #self.SetColumnSelection(None) #Initialize Column Selection
        self.SetSelectionMode(1)
        
        #wx.grid.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick) #open editor with double click
        wx.grid.EVT_GRID_LABEL_RIGHT_CLICK(self, self.OnLabelRightClick)
        #wx.grid.EVT_GRID_LABEL_RIGHT_DCLICK(self, self.OnLabelRightDoubleClick)

        #self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        self.Bind(wx.EVT_MENU, self.OnPopupMaskRow, id = self.ID_popup_MaskRow)
        self.Bind(wx.EVT_MENU, self.OnPopupMaskSelection, id = self.ID_popup_MaskSelection)
        self.Bind(wx.EVT_MENU, self.OnPopupUnmaskSelection, id = self.ID_popup_UnmaskSelection)
        self.Bind(wx.EVT_MENU, self.OnPopupOmitSelection, id = self.ID_popup_OmitSelection)
        self.Bind(wx.EVT_MENU, self.OnPopupReloadRow, id = self.ID_popup_ReloadRow)

        self.Bind(wx.EVT_MENU_RANGE, self.OnPopupColumn,
                  id = self.ID_popup_Column_SetX,
                  id2 = self.ID_popup_Column_SetG)
        self.Bind(wx.EVT_MENU, self.OnSelectColumns, id = self.ID_popup_Select_Columns)
        self.Bind(wx.EVT_MENU, self.OnSetColumnLabel, id = self.ID_popup_Set_Column_Label)
        self.Bind(wx.EVT_MENU, self.OnSetDynamicExpression, id = self.ID_popup_Column_SetExpression)
        self.Bind(wx.EVT_MENU, self.OnRecalculateDynamicExpression,
                  id = self.ID_popup_Column_Recalculate)

        self.Bind(wx.grid.EVT_GRID_COL_SIZE, self.OnColSize)

        #self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnCellChange)

        #self.EnableDragColMove()

        self.Bind(wx.EVT_CHAR, self.OnKey)
        
        
    def OnKey(self, event):
        key = event.KeyCode
        if key == wx.WXK_DELETE:
            row = self.GridCursorRow
            col = self.GridCursorCol
            self.Table.SetValue(row, col, '')
            self.Refresh()
        else:
            event.Skip()

    def OnLeftDClick(self, evt):
        
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    
    def OnLabelRightClick(self, evt):
        """right click on row or column header. create popup
        menu. saves current status for menu callbacks in self.act*"""
        
        self.actRow = evt.Row
        self.actCol = evt.Col
            
        if evt.Row<0 and evt.Col>=0: #right click on column label

            menu = wx.Menu()
            
            miX = menu.Append(self.ID_popup_Column_SetX,
                              "Set this Column as X",
                              kind = wx.ITEM_CHECK)
            if self.Table.colhasmark(evt.Col, 'X'):
                miX.Check()

            miY1 = menu.Append(self.ID_popup_Column_SetY1,
                              "Set this Column as Y1",
                              kind = wx.ITEM_CHECK)
            if self.Table.colhasmark(evt.Col, 'Y1'):
                miY1.Check()

            miY2 = menu.Append(self.ID_popup_Column_SetY2,
                               "Set this Column as Y2",
                               kind = wx.ITEM_CHECK)
            if self.Table.colhasmark(evt.Col, 'Y2'):
                miY2.Check()

            miG = menu.Append(self.ID_popup_Column_SetG,
                               "Set this Column as Group By",
                               kind = wx.ITEM_CHECK)
            if self.Table.colhasmark(evt.Col, 'G'):
                miG.Check()

            if self.Table.colsel[evt.Col] in self.Table.dynamic_cols:
                menu.Append(self.ID_popup_Column_SetExpression,
                            "Set expression ...")
                menu.Append(self.ID_popup_Column_Recalculate,
                            "Recalculate all values")
                
            menu.Append(self.ID_popup_Select_Columns,
                        "Display Columns ...")
            menu.Append(self.ID_popup_Set_Column_Label,
                        "Set Column Label ...")

            self.PopupMenu(menu)
            menu.Destroy()
            

        elif evt.Col<0 and evt.Row>=0: #right click on row label
            menu = wx.Menu()
            
            miM = menu.Append(self.ID_popup_MaskRow,
                              "Mask Row",
                              kind = wx.ITEM_CHECK)
            if self.Table.rowmask[evt.Row]:
                miM.Check()

            if self.Table.GetValueNamed(evt.Row, 'Filename'):
                menu.Append(self.ID_popup_ReloadRow, 'Reload image')
                
            if self.IsSelection():
                menu.Append(self.ID_popup_MaskSelection, "Mask Selection")
                menu.Append(self.ID_popup_UnmaskSelection, "Unmask Selection")
                menu.Append(self.ID_popup_OmitSelection, "Omit Selection")

            self.actRowSelection = self.GetSelectedRows()
            
            self.PopupMenu(menu)
            menu.Destroy()
            
        evt.Skip()

    def OnPopupMaskRow(self, evt):
        self.Table.maskrows(self.actRow, ~self.Table.rowmask[self.actRow])
        self.Refresh()

    def OnPopupMaskSelection(self, evt):
        self.Table.maskrows(self.actRowSelection)
        self.ClearSelection()
        self.Refresh()
        
    def OnPopupUnmaskSelection(self, evt):
        self.Table.maskrows(self.actRowSelection, False)
        self.ClearSelection()
        self.Refresh()

    def OnPopupOmitSelection(self, evt):
        self.Table.omitrows(self.actRowSelection)
        self.ClearSelection()
        self.Refresh()

    def OnPopupReloadRow(self, evt):
        """Post ReloadImageEvent (received by main application) to
        reload image stored in column 'Filename', results should be
        written to selected row"""
        evt = ReloadImageEvent(filename = self.Table.GetValueNamed(self.actRow, 'Filename'),
                               target = {'name': self.Table.name,
                                         'row': self.actRow}
                               )
        wx.PostEvent(self, evt)

    def OnPopupColumn(self, event):
        id = event.GetId()
        
        if id == self.ID_popup_Column_SetX:
            mark = 'X'
        elif id == self.ID_popup_Column_SetY1:
            mark = 'Y1'
        elif id == self.ID_popup_Column_SetY2:
            mark = 'Y2'
        elif id == self.ID_popup_Column_SetG:
            mark = 'G'

        self.Table.SetColMark(self.actCol, mark, remove = not event.IsChecked())
            
        self.Refresh()

    def OnSetDynamicExpression(self, event):
        col = self.Table.colsel[self.actCol]
        idx = self.Table.dynamic_cols.index(col)
        old_expression = self.Table.dynamic_expressions[idx]

        dialog = DynamicExpressionDialog(self,
                                         title = "dynamic expression",
                                         expression = old_expression)
        
        if (dialog.ShowModal() == wx.ID_OK):
            #self.Table.dynamic_expressions[idx] = dialog.Value
            self.Table.dynamic_expressions[idx] = dialog.text.Value
            for row in range(self.Table.GetNumberRows()):
                self.Table.update_dynamic_cols(row = row, column = col)
            self.Refresh()
            self.Table.update_observers()

    def OnRecalculateDynamicExpression(self, event):
        for row in range(self.Table.GetNumberRows()):
            self.Table.update_dynamic_cols(row = row, column = self.Table.colsel[self.actCol])
        self.Refresh()
        self.Table.update_observers()

    def OnSetColumnLabel(self, event):
        """Set column label. This label is used for axis labels, legends, ..."""
        rawcol = self.Table.colsel[self.actCol]

        dialog = wx.TextEntryDialog(self,
                                    message = "Enter column label",
                                    caption = "Column label",
                                    defaultValue = self.Table.column_labels_custom.get(rawcol, ''),
                                    )
        if (dialog.ShowModal() == wx.ID_OK):
            self.Table.column_labels_custom[rawcol] = dialog.Value
            self.Refresh()
            self.Table.update_observers()
            

    def OnSelectColumns(self, event):
        #columns = self.Table.colLabels.tolist()
        columns = []
        for i, rawlabel in enumerate(self.Table.colLabels):
            customlabel = self.Table.column_label(i)
            if rawlabel == customlabel:
                columns.append(rawlabel)
            else:
                columns.append("%s (%s)"%(customlabel, rawlabel))
        
        selection = self.Table.colsel
        
        dialog = wx.MultiChoiceDialog(self,
                                      "Select Columns",
                                      "Select Columns...",
                                      columns
                                      )
        dialog.SetSelections(selection)
        
        if (dialog.ShowModal() == wx.ID_OK):
            self.SetColumnSelection(dialog.GetSelections())

    def SetColumnSelection(self, selections):
        """
        SetColumnSelection.

        Selects which columns are displayed. For this, tell the Grid
        first to remove all columns, and add again all columns. By
        this everything is updated accordingly. Then fix width of
        columns.

        @param selection: list of indices of the columns which are
        displayed
        """
        self.BeginBatch() #avoid unnecessary screen refreshes

        if selections is None:
            selections = self.Table.colsel

        #tell GridTable all columns have been removed
        self.DeleteCols(0, self.GetNumberCols())
        msg = wx.grid.GridTableMessage(self.GetTable(),
                                       wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED,
                                       0,
                                       self.GetNumberCols())
        self.ProcessTableMessage(msg)

        #add columns, update
        self.Table.colsel = selections
        msg = wx.grid.GridTableMessage(self.GetTable(),
                                       wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED,
                                       len(selections)
                                       )
        self.ProcessTableMessage(msg)
        msg = wx.grid.GridTableMessage(self.GetTable(),
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.ProcessTableMessage(msg)

        #restore saved sizes
        self.RestoreColSizes()

        self.EndBatch()
        self.Refresh()
            
    def OnColSize(self, evt):
        col = evt.GetRowOrCol()
        size = self.GetColSize(col)
        self.Table.SetColSize(col, size)

    def RestoreColSizes(self):
        for col in range(self.GetNumberCols()):
            self.SetColSize(col, self.Table.GetColSize(col))


    def GetDefaultRendererForType(self, typ):
        pass
        #print "GetRenderer for type", typ
        
    
        #if type == 'custom':
        #    return MyCustomRenderer()
        #else:
        #    return wx.grid.Grid.GetDefaultRendererForType(type)

        #return wx.grid.Grid.GetDefaultRendererForType(type)
        


    def GetDefaultEditorForType(self, typ):
        #print "GetEditor for type", typ
        return
    
        if typ == 'custom':
            return wx.grid.GridCellFloatEditor()
        else:
            return wx.grid.Grid.GetDefaultEditorForType(typ)

        #return wx.grid.Grid.GetDefaultRendererForType(type)
   
        
    #def OnCellChange(self, evt):
    #    self.Table.inform_observers()

    def GetMetadata(self):
        return self.Table.give_metadata()

    def ApplyTemplate(self, metadata):
        self.Table.set_metadata(metadata)
        self.SetColumnSelection(None)
        self.Refresh()
        self.Table.update_observers()
        

class GridPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(
            self, parent, -1
            )
        self.grid = FitResultDataTableGrid(self)
        
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.grid,1, wx.GROW)
        self.SetSizer(bs)


class TabbedGridPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.notebook = wx.aui.AuiNotebook(self,
                                           style = wx.aui.AUI_NB_TOP |
                                           wx.aui.AUI_NB_TAB_SPLIT |
                                           wx.aui.AUI_NB_TAB_MOVE |
                                           wx.aui.AUI_NB_WINDOWLIST_BUTTON |
                                           wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB |
                                           wx.aui.AUI_NB_TAB_EXTERNAL_MOVE)
        self.pages = []
        

        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.OnPageClosed, self.notebook)

    def addpage(self, name = ''):
        page = FitResultDataTableGrid(self.notebook)

        page.Table.AppendRows(1)

        self.pages.append(page)
        self.notebook.AddPage(page, name)
        return page
    
    def OnPageClosed(self, event):
        id = event.Selection
        del self.pages[id]
        print "page closed", id
        event.Skip()

    @property
    def grid(self):
        pageid = self.notebook.GetSelection()
        return self.pages[pageid]
    
class TestFrame(wx.Frame):
    def __init__(self, parent):

        wx.Frame.__init__(
            self, parent, -1, "Custom Table, data driven Grid  Demo", size=(640,480)
            )

        self.panel = wx.Panel(self, -1, style=0)

        self.gridpanel = GridPanel(self.panel)

        self.button = wx.Button(self.panel, -1, "Select Columns")
        self.button.SetDefault()
        self.button.Bind(wx.EVT_BUTTON, self.OnButton)

        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.button)
        bs.Add(self.gridpanel, 1, wx.GROW|wx.ALL, 5)
        self.panel.SetSizer(bs)

    def OnButton(self, evt):

        self.gridpanel.grid.SelectColumns()

class TestFrameNotebook(wx.Frame):
    def __init__(self, parent):

        wx.Frame.__init__(
            self, parent, -1, "Custom Table, data driven Grid  Demo", size=(640,480)
            )

        self.panel = wx.Panel(self, -1, style=0)

        self.gridpanel = TabbedGridPanel(self.panel)

        self.gridpanel.addpage('results 1')
        self.gridpanel.addpage('results 2')
        

        self.button = wx.Button(self.panel, -1, "Select Columns")
        self.button.SetDefault()
        self.button.Bind(wx.EVT_BUTTON, self.OnButton)

        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.button)
        bs.Add(self.gridpanel, 1, wx.GROW|wx.ALL, 5)
        self.panel.SetSizer(bs)

    def OnButton(self, evt):

        self.gridpanel.grid.SelectColumns()
        

        


#---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    #frame = TestFrame(None)
    frame = TestFrameNotebook(None)
    frame.Show(True)
    app.MainLoop()


#---------------------------------------------------------------------------
