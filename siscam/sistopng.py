import os, os.path, sys
import subprocess

import readsis, Image, png_writer

def sis_to_png(sisfilename, pngfilename = None, overwrite = False):
    """Convert sis image file to PNG, 16-bit grayscale"""

    root, ext = os.path.splitext(sisfilename)
    if ext.lower() != '.sis':
        print "Error: input file is not an SIS file"
        return
    
    if pngfilename is None:
        pngfilename = root + '.png'

    if not overwrite:
        try:
            f = open(pngfilename, 'r+')
            f.close()
        except IOError:
            pass
        else:
            print "Warning: output file already exists!"
            return

    #convert_IM(sisfilename, pngfilename)
    #convert_PIL(sisfilename, pngfilename)
    convert_png_writer(sisfilename, pngfilename)

def convert_IM(sisfilename, pngfilename):
    width, height = readsis.image_size(sisfilename)
    cmd = 'convert -size %dx%d+200 -depth 16 -endian lsb ' + \
    '-quality 10 -type grayscale ' + \
    '-evaluate Multiply 10 "gray:%s" "%s"'
    cmd = cmd%(width, height, sisfilename, pngfilename)
    p = subprocess.Popen(cmd, shell = True)
    outstd, outerr = p.communicate()
    p.wait()
    if p.returncode:
        print "Error in converting file", sisfilename
        print str(outstd), str(outerr)
    else:
        print sisfilename, 'converted'

def convert_PIL(sisfilename, pngfilename):
    img = readsis.read(sisfilename)
    img_pil = Image.fromstring('I', (img.shape[1], img.shape[0]), img.tostring(), 'raw', 'I;16N', 0, 1)
    img_pil.save(pngfilename, bits=16)
    print sisfilename, 'converted'

def convert_png_writer(sisfilename, pngfilename):
    import png_writer
    img = readsis.read(sisfilename)
    png_writer.PngWriter(pngfilename, img,
                         transparent = 0,
                         significant_bits = 13,
                         compression = 1,
                         metadata = {'Author': 'Gregor Thalhammer',
                                     'Title': 'absorption image',
                                     'Software': 'sistopng',
                                     'Source': 'SIS285',
                                     'image type': 'optical density',
                                     'scale optical density': 1000,
                                     'format version': 1},
                         )

def convert_all(root, overwrite = False):
    for dirpath, dirs, files in os.walk(root):
        for sisfile in [f for f in files if os.path.splitext(f)[1].lower() == '.sis']:
            try:
                sis_to_png(os.path.join(dirpath, sisfile), overwrite=overwrite)
            except Exception, e:
                print "Error:", e

if __name__ == '__main__':
    import time
    tic = time.time()
    #sis_to_png('img/20061115_0.sis', overwrite = True)

    sis_to_png('img/20090126-waveplate-0047.sis', overwrite = True)
    
    
    #convert_all('2009/2009-01-28', overwrite = True)
    print "elapsed time: %.0fms"%(1e3*(time.time()-tic))
    

