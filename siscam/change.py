import os
import threading
import time
import win32api, win32con, win32file, win32event, pywintypes, ntsecuritycon
import Queue

class DirChange(object):

    def __init__(self, dirname):
        self.dir_name = dirname
        self.dir_handle = win32file.\
                          CreateFile(self.dir_name, 
                                     ntsecuritycon.FILE_LIST_DIRECTORY,
                                     win32con.FILE_SHARE_READ,
                                     None, # security desc
                                     win32con.OPEN_EXISTING,
                                     win32con.FILE_FLAG_BACKUP_SEMANTICS |
                                     win32con.FILE_FLAG_OVERLAPPED,
                                     None)

        self.watcher_thread_changes = []
        self.watcher_thread = threading.Thread(target=self._watcherThread,
                                               args=(self.dir_name,
                                                     self.dir_handle,
                                                     self.watcher_thread_changes))
        self.watcher_thread.start()

        self.queue = Queue.Queue(0)

        self.reporter_thread = threading.Thread(target = self.reporterThread)
        self.reporter_thread.start()
        
        

    def reporterThread(self):
        while True:
            item = self.queue.get()
            print "reporter: ",item
            if item == "the end":
                print "stop reporting"
                return


    def _watcherThread(self, dirname, dirhandle, changes):

        flags = win32con.FILE_NOTIFY_CHANGE_FILE_NAME | \
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME | \
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
                #win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES | \
        
        buf = win32file.AllocateReadBuffer(8192)
        overlapped = pywintypes.OVERLAPPED()
        overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)

        while 1:
            win32file.ReadDirectoryChangesW(dirhandle,
                                            buf,
                                            True, #sub-tree
                                            flags,
                                            overlapped)

            # Wait for our event, or for 5 seconds.
            rc = win32event.WaitForSingleObject(overlapped.hEvent, 5000)
            print "end of wait", rc
            if rc == win32event.WAIT_OBJECT_0:
                # got some data!  Must use GetOverlappedResult to find out
                # how much is valid!  0 generally means the handle has
                # been closed.  Blocking is OK here, as the event has
                # already been set.
                try:
                    nbytes = win32file.GetOverlappedResult(dirhandle, overlapped, True)
                except Exception, e:
                    ##note: might also fail with error 995, operation aborted
                    print "caught exception"
                    print e
                    if e[0] == 995:
                        print "exiting"
                        self.queue.put('the end')
                        return


                if nbytes:
                    bits = win32file.FILE_NOTIFY_INFORMATION(buf, nbytes)

                    #changes.extend(bits)
                    #print "change detected:", bits
                    self.queue.put(bits)
                    
                else:
                    print "looks like dir handle was closed, exiting"
                    self.queue.put('the end')
                    return


    def stop(self):
        self.dir_handle.Close()
        self.watcher_thread.join(5)
        if self.watcher_thread.isAlive():
            print "FAILED to wait for thread termination"

    def stabilize(self):
        time.sleep(1)

    def testSimple(self):
        testfile = os.path.join(self.dir_name, "test_file")
        fh = open(testfile, "w")
        fh.write('x')
        fh.close()
        os.remove(testfile)
        self.stabilize()
        
        #changes = self.watcher_thread_changes
        #print changes



#if __name__ == '__main__':
watcher = DirChange(r"2008") #2008
watcher.testSimple()

    #time.sleep(10)
    
    #watcher.stop()
    #time.sleep(5)
