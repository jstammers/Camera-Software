from __future__ import with_statement

import filewatch

from difflib import SequenceMatcher, Differ
import sequenceparser
reload(sequenceparser)

def dictcompare(d1, d2):
    diffkeys = []
    if d1 is None or d2 is None:
        return
    if set(d1.keys()) != set(d2.keys()):
        return
    for k in d1.keys():
        if d1[k] != d2[k]: diffkeys.append(k)
    return diffkeys

class Watcher:
    def __init__(self):
        with file('z:/running.txt') as infile:
            self.oldfile = infile.readlines()
            print "stored initial sequence"

    def sequence_changed(self):
        print "new sequence?"
        with file('z:/running.txt') as infile:
            self.newfile = infile.readlines()

        differ = SequenceMatcher(None, self.oldfile, self.newfile
                                 )
        for group in differ.get_grouped_opcodes(1):
            for tag, i1, i2, j1, j2 in group: 
                if tag == 'replace':

                    nold = i2-i1
                    nnew = j2-j1


                    if (nold == nnew):
                        for k in range(nold):
                            old = sequenceparser.linematch(self.oldfile[i1+k])
                            new = sequenceparser.linematch(self.newfile[j1+k])
                            changedkey = dictcompare(old, new)
                            if changedkey:
                                print new['name'], 
                                print "changed:", changedkey[0], new[changedkey[0]]

                    else:
                        print "too many lines changed at once", nold, nnew

        self.oldfile = self.newfile

        print "---"
        

watcher = filewatch.FileChangeNotifier(r'Z:\running.txt', Watcher().sequence_changed)
watcher.start()
