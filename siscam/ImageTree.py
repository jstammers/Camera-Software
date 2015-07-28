#!/usr/bin/python
#-*- coding: latin-1 -*-

"""Provides classes for representing and displaying list of saved
image files as tree."""
import re

from os import listdir, stat, walk
from os.path import join, isdir, basename

import wx
from wx.lib.mixins import treemixin

class LabeledList(list):
    """derived list class with label. Used as Node for tree structure."""
    def __init__(self, entries = [], label = None):
        super(LabeledList, self).__init__(entries)
        self.label = label

    def __repr__(self):
        return str(self.label) + ': '+ super(LabeledList, self).__repr__()

class DirListEntry(object):
    """stores data for tree entries (nodes and leaves)"""
    def __init__(self, name = "", path = ""):
        self._name = name
        self._path = path
        if path:
            self._mtime = stat(path).st_mtime
        else:
            self._mtime = None

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    def get_mtime(self):
        return self._mtime

    def set_mtime(self, value):
        self._mtime = value

    mtime = property(get_mtime, set_mtime)

class TreeModel(object):
    """Represents files organized in a tree structure. Provides
    methods needed for VirtualTree mixin class."""

    def __init__(self, root):
        self.root = root
        self.createfiletree()

    def getitem(self, indices):
        "helper method to access tree structure"
        if len(indices)>2:
            #leafs need special treatment
            return self.tree[indices[0]][indices[1]][indices[2]]
        else:
            item = self.tree
            for index in indices:
                item = item[index]
            return item.label

    def GetItemText(self, indices):
        return self.getitem(indices).name
        
    def GetItemFile(self, indices):
        return self.getitem(indices).path

    def GetChildrenCount(self, indices):
        if len(indices)>2: #a leaf has no children
            return 0
        
        item = self.tree
        for index in indices:
            item = item[index]
        return len(item)

    imagefilematch = re.compile(r'\d{8}-(?P<name>.*)-(?P<nr>\d{4})\.(?P<ext>(sis|SIS|png|PNG))')
    dirmatch = re.compile(r'\d{4}-\d{2}-\d{2}')

    def createfiletree(self):
        rootdir = self.root

        #initialize empty list
        root = LabeledList([], label = ('images', rootdir))

        #populate with all dirs that match pattern and contain image subdir
        for dirpath, dirs, files in walk(rootdir):
            name = basename(dirpath)
            if self.dirmatch.match(name) and 'images' in dirs:
                label = DirListEntry(name = name, path = join(dirpath, 'images'))
                root.append(LabeledList([], label = label))

        root.sort(key = lambda x: x.label.name)

        #add subtree (measurements/images)
        for day in root:
            day.extend(self.createdaysubtree(day.label.path))

        self.tree = root

    def createdaysubtree(self, daydir):
        """create subtree measurements/images for directory daydir"""

        # get content of daydir (-> names)
        #dayimgdir = join(daydir, 'images')
        dayimgdir = daydir
        try:
            names = listdir(dayimgdir)
        except EnvironmentError:
            print 'cannot list content of directory "%s"'%dayimgdir
            names = []

        #loop over all image files in day dir, sort into corresponding list
        measdict = {}
        for filename in names:
            m = self.imagefilematch.match(filename)
            if m is None:
                continue #file is not an image file, continue with next iteration

            #found imagefile, get corresponding measurement name
            measname = m.group('name')

            #get (or create if not yet existing) list of images for
            #measurement
            if measdict.has_key(measname):
                imagelist = measdict[measname]
            else:
                #create new list
                label = DirListEntry(name = measname)
                imagelist = LabeledList([], label)
                measdict[measname] = imagelist

            
            imagelist.append(DirListEntry(name = m.group('nr') + " (%s)"%m.group('ext').lower(),
                                          path = join(dayimgdir, filename))
                                          )
            
        for imagelist in measdict.itervalues():
            imagelist.sort(key = lambda x: x.name)

        return measdict.values() #return list of imagelists

    def find_file(self, filename, index = []):
        """try to find file in leafs of tree, return full path to image"""

        num_children = self.GetChildrenCount(index)
        if num_children == 0:
            name = self.GetItemFile(index)
            if basename(name) == filename:
                return name
        else:
            for idx in range(num_children):
                r = self.find_file(filename, index + [idx,])
                if r:
                    break
            return r
        
class TreeModelSync(TreeModel):
    """Macht automatische Updates falls Änderung im Filesystem bemerkt wird.
    Note: daydir sollte tag/images sein!"""
    def __init__(self, root):
        #super(TreeModel, self).__init__(root)
        TreeModel.__init__(self, root)

    def check_day(self, index):
        
        """test if modify time of image directory has changed. Reload
        if necessary"""

        day = self.tree[index]
        daydir = day.label.path
        dirmtime = day.label.mtime
        actdirmtime = stat(daydir).st_mtime

        if actdirmtime > dirmtime:
            print "directory %s has changed, reloading"%daydir

            #recreate data structure day
            del day[:]
            day.extend(self.createdaysubtree(day.label.path))
            day.label.mtime = actdirmtime
            return True
        else:
            return False

    def GetChildrenCount(self, indices):

        #print "GetChildrenCount for index", indices

        if len(indices)>2: #a leaf has no children
            return 0
        
        if len(indices) == 1:
            self.check_day(indices[0])

        item = self.tree
        for index in indices:
            item = item[index]
        
        return len(item)

          
class ImageTree(treemixin.VirtualTree, wx.TreeCtrl):
    """Tree control."""

    def __init__(self, *args, **kwargs):
        self.tree = kwargs.pop('tree')
        super(ImageTree, self).__init__(*args, **kwargs)
        
    def OnGetItemText(self, indices):
        return self.tree.GetItemText(indices)
        
    def OnGetChildrenCount(self, indices):
        return self.tree.GetChildrenCount(indices)
        

class ImageTreePanel(wx.Panel):
    """Simple panel that contains ImageTree control"""
    def __init__(self, parent, tree):
        """@param tree: instance of TreeModel
        @type tree: TreeModel
        """

        self.treemodel = tree
        
        wx.Panel.__init__(self, parent, -1)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.treectrl = ImageTree(parent = self, tree = tree,
                                  style =
                                  #wx.TR_MULTIPLE | #gives strange errors
                                  wx.TR_HIDE_ROOT |
                                  wx.TR_HAS_BUTTONS |
                                  wx.TR_LINES_AT_ROOT 
                                  )
        self.treectrl.RefreshItems()
        self.vbox.Add(self.treectrl, 1, wx.GROW)
        self.SetSizer(self.vbox)
        self.Fit()

        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.treectrl)
        
    def OnActivate(self, event):
        index = self.treectrl.GetIndexOfItem(event.Item)
        file = self.treemodel.GetItemFile(index)
        print file

class ImageTreeApp(wx.App):
    """demo application to test ImageTreePanel"""
    def OnInit(self):
        frame = wx.Frame(None,
                         title = 'Image Tree',
                         size = (400, 300),
                         )
        datadir = settings.imagesavepath
        self.treemodel = TreeModelSync(datadir)
        self.panel = ImageTreePanel(frame, self.treemodel)
        self.panel.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.panel.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnRightClick)
        frame.Show(True)
        return True

    def OnActivate(self, event):
        #print "in ImageTreeApp/OnActivate. Item: ", event.Item
        index = self.panel.treectrl.GetIndexOfItem(event.Item)
        print "in ImageTreeApp/OnActivate ", index
        #if len(index)==3:
        file = self.treemodel.GetItemFile(index)
        print file
        next = self.panel.treectrl.GetNextSibling(event.Item)
        if next.IsOk():
            self.panel.treectrl.SelectItem(next)

    def OnRightClick(self, event):
        index = self.panel.treectrl.GetIndexOfItem(event.Item)
        print "in ImageTreeApp/OnRightClick", index

        menu = wx.Menu()
        if len(index)>=1:
            menu.Append(-1,"Day Menu")
        if len(index)>=2:
            menu.Append(-1,"Measurement Menu")
        if len(index)>=3:
            menu.Append(-1, "Image Menu")
            
        self.panel.PopupMenu(menu)
        menu.Destroy()
        

def run_imagetreeapp():
    gui = ImageTreeApp(redirect = False)
    gui.MainLoop()
    return gui

def test_search():
    datadir = settings.imagesavepath
    treemodel = TreeModelSync(datadir)
    print treemodel.find_file('20090208-results-0000.sis')

if __name__ == '__main__':
    import settings
    #gui = run_imagetreeapp()
    test_search()

    
