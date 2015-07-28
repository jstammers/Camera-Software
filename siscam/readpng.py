#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Load image files saved as PNG."""

from __future__ import with_statement
import os.path, sys, time
import numpy
import Image
from PngImagePlugin import PngInfo

def read(filename):
    img_pil = Image.open(filename)
    img_pil.load()
    print img_pil.info
    if img_pil.mode == 'I':
        s = img_pil.tostring('raw', ('I;16B',0,1))
        width, height = img_pil.size
        img = numpy.fromstring(s, dtype = numpy.uint16)
        img.shape = (height, width)
        img.byteswap(True)
    elif img_pil.mode == 'RGB':
        s = img_pil.convert('L').tostring()
        width, height = img_pil.size
        img = numpy.fromstring(s, dtype = numpy.uint8)
        img.shape = (height, width)
    return img, img_pil.info

def write_raw_image(filename, img):
    pnginfo = PngInfo()
    pnginfo.add_text('absorption_image_scale', '10000') #TODO: 
    
    if img.dtype != numpy.uint16:
        img = img.astype(numpy.uint16)
        
    img_pil = Image.fromstring('I', (img.shape[1], img.shape[0]), img.tostring(), 'raw', 'I;16N', 0, 1)
    img_pil.save(filename, bits=16, pnginfo = pnginfo)

def loadimg(filename):
    img, info = read(filename)
    scale = info.get('absorption_image_scale', '1000')
    scale = 1.0/float(scale)
    img = img.astype(numpy.float32)
    h, w = img.shape
    imgK = img[:h/2]
    imgRb = img[h/2:]
    return numpy.ma.masked_where(imgK==0, imgK*scale-1.0), \
           numpy.ma.masked_where(imgRb==0, imgRb*scale-1.0)

def test_write_read():
    imgRb, imgK = loadimg('img/20061115_0.png')

    imgRb = numpy.asarray(imgRb)
    rawimg = (1000*(imgRb + 1)).astype(numpy.uint16)
    
    write_raw_image('testpngsave.png', rawimg)
    rawimgsaved, info = read('testpngsave.png')
    print info
    
    if (rawimgsaved == rawimg).all():
        print "load/save/load sucess"
    else:
        raise Exception

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
    imgRb, imgK = loadimg('img/20061116_0.png')
    rawimg = (1000*(numpy.asarray(imgRb) + 1)).astype(numpy.uint16)

    savethread = threading.Thread(target = test_save,
                                  args = ('img/testpng.png', rawimg),
                                  )

    loadthread = threading.Thread(target = test_read,
                                  args = ('img/testpng.png',),
                                  )

    savethread.run()
    loadthread.run()
    
if __name__ == '__main__':
    test_read('testpng.png')
    test_write_read()
    #simultanous_write_read()

    
