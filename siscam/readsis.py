#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Load image files which have been saved by WinSIS."""

from __future__ import with_statement
import numpy
from numpy import fromfile, uint16, log, fromstring, ma
import os.path, sys, time

import struct

def image_size(filename):
    with open(filename, 'rb') as fid:
        return get_size(fid)

def get_size(fid):
    header = read_fid_full(fid, 200)
    height, width, xoff, yoff = struct.unpack('10x H H 182x H H', header)
    return width, height

def read(filename):
    with file(filename, 'rb') as fid:
        width, height = get_size(fid)
        data = read_fid_full(fid, size = width*height*2, timeout = 5)
        img = fromstring(data, dtype = uint16, count = width*height)
        img.shape = (height, width)
        return img

def read_fid_full(fid, size, timeout = 1):
    numbytesread = 0
    result = ''
    starttime = time.clock()
    while numbytesread < size:
        result += fid.read(size - numbytesread)
        numread = len(result)

        if time.clock() - starttime > timeout or numread>=size:
            break
        time.sleep(0.1)
    return result

def write_raw_image(filename, img):
    fid = file(filename, 'wb')
    fid.write(' '*10)
    height, width = img.shape
    ha = numpy.array([height], dtype = numpy.uint16)
    ha.tofile(fid)
    wa = numpy.array([width], dtype = numpy.uint16)
    wa.tofile(fid)
    fid.write(' '*182)
    fid.write(' '*4) #TODO: xoff, yoff
    if img.dtype == numpy.uint16:
        img.tofile(fid)
    else:
        img.astype(numpy.uint16).tofile(fid)
    fid.close()

def loadimg(filename):
    img = read(filename)
    img = img.astype(numpy.float32)
    h, w = img.shape
    imgK = img[:h/2]
    imgRb = img[h/2:]
    return ma.masked_where(imgK==0, imgK*1e-3-1.0), \
           ma.masked_where(imgRb==0, imgRb*1e-3-1.0)

def loadimg3(path):
    img1 = read(os.path.join(path, 'PIC1.SIS'))
    img2 = read(os.path.join(path, 'PIC2.SIS'))
    img3 = read(os.path.join(path, 'PIC3.SIS'))

    img = - (log(img1 - img3) - log(img2 - img3))
    return img[:1040], img[1040:], 

import Image, ImageFile
class SISImageFile(ImageFile.ImageFile):

    format = "SIS"
    format_description = "SIS image"

    def _open(self):
        header = self.fp.read(200)
        self.size = struct.unpack('10x H H 186x', header)
        self.mode = "I"
        self.tile = [
            ("raw", (0,0) + self.size, 200, ('I;16N', 0, 1)),
            ]

#Image.register_open('SIS', SISImageFile)
#Image.register_extension('SIS', '.sis')

def test_write_read():
    imgRb, imgK = loadimg('img/test.sis')

    imgRb = numpy.asarray(imgRb)
    rawimg = (1000*(imgRb + 1)).astype(numpy.uint16)
    
    write_raw_image('img/testsave.sis', rawimg)
    rawimgsaved = read('img/testsave.sis')
    print "load/save/load sucess:", numpy.all(rawimgsaved == rawimg)

def test_read(filename):
    print "loading..."
    sys.stdout.flush()
    loadimg(filename)
    print "done"
    sys.stdout.flush()

def test_save(filename, img):
    print "saving..."
    sys.stdout.flush()
    write_raw_image(filename, img)
    print "done"
    sys.stdout.flush()

def simultanous_write_read():
    import threading
    imgRb, imgK = loadimg('img/FITtoosmall.sis')
    rawimg = (1000*(numpy.asarray(imgRb) + 1)).astype(numpy.uint16)

    savethread = threading.Thread(target = test_save,
                                  args = ('img/testsave.sis', rawimg),
                                  )

    loadthread = threading.Thread(target = test_read,
                                  args = ('img/testsave.sis',),
                                  )

    savethread.run()
    loadthread.run()
    




def test_get_size():
    f = 'img/test.sis'
    print image_size(f)

if __name__ == '__main__':
    #test_write_read()
    simultanous_write_read()
    #test_get_size()
    
