#!/usr/bin/env python
# png.py - PNG encoder in pure Python
# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""
Pure Python PNG Reader/Writer
"""

from __future__ import with_statement

import sys
import zlib
import struct
import math
from array import array
import numpy
import operator

class PngWriter:
    """
    PNG encoder in pure Python.
    """

    def __init__(self, filename,
                 image,
                 transparent=None,
                 background=None,
                 gamma=None,
                 has_alpha=False,
                 bitdepth = None,
                 significant_bits = None,
                 compression=1,
                 chunk_limit=2**20,
                 metadata = {}):

        greyscale = True

        """
        Write a PNG image to the output file.
        """

        
        """
        Create a PNG encoder object.

        Arguments:
        width, height - size of the image in pixels
        transparent - create a tRNS chunk
        background - create a bKGD chunk
        gamma - create a gAMA chunk
        greyscale - input data is greyscale, not RGB
        has_alpha - input data has alpha channel (RGBA)
        bitdepth - number of bits per sample
        compression - zlib compression level (1-9)
        chunk_limit - write multiple IDAT chunks to save memory

        If specified, the transparent and background parameters must
        be a tuple with three integer values for red, green, blue, or
        a simple integer (or singleton tuple) for a greyscale image.

        If specified, the gamma parameter must be a float value.

        """

        height, width = image.shape 

        if has_alpha and transparent is not None:
            raise ValueError(
                "transparent color not allowed with alpha channel")

        if bitdepth is None:
            bitdepth = 8*image.dtype.itemsize
            print 'PngWriter: New bitdepth:',bitdepth

        if bitdepth not in [8,16]:
            print 'bitdepth=',bitdepth
            raise ValueError("bitdepth not supported")

        if significant_bits is None:
            significant_bits = bitdepth

        if significant_bits>bitdepth:
            raise ValueError('significant bits must be smaller than bitdepth of image')

        if transparent is not None:
            if greyscale:
                if type(transparent) is not int:
                    raise ValueError(
                        "transparent color for greyscale must be integer")
                transparent = [transparent,]
            else:
                if not (len(transparent) == 3 and
                        type(transparent[0]) is int and
                        type(transparent[1]) is int and
                        type(transparent[2]) is int):
                    raise ValueError(
                        "transparent color must be a triple of integers")

        if background is not None:
            if greyscale:
                if type(background) is not int:
                    raise ValueError(
                        "background color for greyscale must be integer")
                background = [background,]
            else:
                if not (len(background) == 3 and
                        type(background[0]) is int and
                        type(background[1]) is int and
                        type(background[2]) is int):
                    raise ValueError(
                        "background color must be a triple of integers")

        self.width = width
        self.height = height
        self.transparent = transparent
        self.background = background
        self.gamma = gamma
        self.greyscale = greyscale
        self.has_alpha = has_alpha
        self.bitdepth = bitdepth
        self.bytes_per_sample = 1 if bitdepth<=8 else 2
        self.significant_bits = significant_bits
        self.compression = compression
        self.chunk_limit = chunk_limit

        if self.greyscale:
            self.color_depth = 1
            if self.has_alpha:
                self.color_type = 4
                self.psize = self.bytes_per_sample * 2
            else:
                self.color_type = 0
                self.psize = self.bytes_per_sample
        else:
            self.color_depth = 3
            if self.has_alpha:
                self.color_type = 6
                self.psize = self.bytes_per_sample * 4
            else:
                self.color_type = 2
                self.psize = self.bytes_per_sample * 3


        #start writing file
        with open(filename, 'wb') as outfile:

            #PNG-file-signature
            outfile.write(struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10))

            #IHDR
            self.write_chunk(outfile, 'IHDR',
                             struct.pack("!2I5B", self.width, self.height,
                                         self.bytes_per_sample * 8,
                                         self.color_type, 0, 0, 0))

            #tRNS
            if self.transparent is not None:
                if self.greyscale:
                    self.write_chunk(outfile, 'tRNS',
                                     struct.pack("!1H", *self.transparent))
                else:
                    self.write_chunk(outfile, 'tRNS',
                                     struct.pack("!3H", *self.transparent))

            #bKGD
            if self.background is not None:
                if self.greyscale:
                    self.write_chunk(outfile, 'bKGD',
                                     struct.pack("!1H", *self.background))
                else:
                    self.write_chunk(outfile, 'bKGD',
                                     struct.pack("!3H", *self.background))

            #gAMA
            if self.gamma is not None:
                self.write_chunk(outfile, 'gAMA',
                                 struct.pack("!L", int(self.gamma * 100000)))

            #TODO: fails for color images
            if self.significant_bits != self.bitdepth:
                self.write_chunk(outfile, 'sBIT',
                                 struct.pack("B", self.significant_bits))

            #write metadata
            for key, val in metadata.iteritems():
                keyenc = str(key).encode('latin1', 'ignore')
                textenc = str(val).encode('latin1', 'ignore')
                data = '\x00'.join((keyenc, textenc))
                self.write_chunk(outfile, 'tEXt',
                                 data)

            #IDAT
            if self.compression is not None:
                compressor = zlib.compressobj(self.compression)
            else:
                compressor = zlib.compressobj()



            #write image data    

            #check if sample scaling necessary
            if self.significant_bits != self.bitdepth:
                do_scale = True
                shift_bits = self.bitdepth - self.significant_bits
                clip_value = 2**self.significant_bits - 1
            else:
                do_scale = False

            #choose proper data type TODO: correct only for greyscale
            imgdtype = numpy.uint8 if self.bitdepth <= 8 else numpy.uint16

            #ensure input array is C contiguous and has right data type
            #TODO: contiguous not necessary if copy is done for scanline
            image_array = numpy.ascontiguousarray(image, dtype = imgdtype)
            #img_data = image_array.view(dtype = numpy.ubyte)

            #list to collect compressed data
            data_comp = []


            scanline = numpy.empty(shape = (image_array.shape[1],), dtype = imgdtype)
            #work = numpy.empty(shape = (img_data.shape[1] + imgdtype.itemsize,), dtype = numpy.ubyte) #idea: use this for everything, with some views for convenience
            #b = numpy.zeros_like(work)

            for line in image_array:
                if do_scale:
                    numpy.left_shift(line, shift_bits, scanline)
                else:
                    scanline[0:] = line[0:]
                    #numpy.multiply(line, 1, scanline)
                    

                scanline.byteswap(True)

                #no filter
                s1 = compressor.compress(chr(0))
                if s1: data_comp.append(s1)

                ##Sub filter, poor compression
                #work[0] = 1
                #work[1:] = line[:]
                #numpy.subtract(work[2:], work[1:-1], work[2:])

                ##Up filter
                #work[0] = 2
                #numpy.subtract(line, b, work[1:])
                #b = line

                s2 = compressor.compress(scanline.data)
                if s2:
                    data_comp.append(s2)

            data_comp.append(compressor.flush())

            #total data length
            l = reduce(operator.add, [len(s) for s in data_comp])
            print "compressed size: %4.1f"%(100.0*l/(image_array.size*image_array.itemsize))

            #write IDAT chunk
            cs = zlib.crc32('IDAT')
            outfile.write(struct.pack(">I", l))
            outfile.write('IDAT')
            for entry in data_comp:
                outfile.write(entry)
                cs = zlib.crc32(entry, cs)
            outfile.write(struct.pack(">i", cs))

            self.write_chunk(outfile, 'IEND', '')


    def write_chunk(self, outfile, tag, data):
        """
        Write a PNG chunk to the output file, including length and checksum.
        """
        outfile.write(struct.pack("!i", len(data)))
        outfile.write(tag)
        outfile.write(data)
        checksum = zlib.crc32(tag)
        checksum = zlib.crc32(data, checksum)
        outfile.write(struct.pack("!i", checksum))


