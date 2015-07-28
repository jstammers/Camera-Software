import numpy as np
import readsis
import readpng
from png_writer import PngWriter
import os.path

def imagesplit(img):
    h, w = img.shape
    return img[:h/2],img[h/2:]

def find_background(img, r = 10.0):

    bins = np.linspace(0, 500, 501)
    db   = np.mean(np.diff(bins)) #width of bins

    #calculate histogram
    h, b = np.histogram(img, bins-0.5*db, new = True)
    
    mx = h.argmax() #find peak of histogram, take this as first estimate
    sel = slice(max(0, mx-int(r/db)), min(len(h),mx+int(r/db))) #select range around maximum

    nrm = sum(h[sel]) #norm of selected part
    m = sum(h[sel]*b[sel])/nrm #calculate mean value
    s = np.sqrt(sum((h[sel]*((b[sel]-m)**2)))/nrm) #and standard deviation

    return m, s
    
def calc_img(img1, img2, img3):

    img_trans = np.true_divide(img1-img3, img2-img3)
    imga,  imgb  = imagesplit(img_trans)

    img2a, img2b = imagesplit(img2)
    ma, sa = find_background(img2a)
    mb, sb = find_background(img2b)

    mask = np.empty(shape = img_trans.shape, dtype = np.bool_)
    maska, maskb = imagesplit(mask)

    maska[:], maskb[:] = img2a<ma+4*sa, img2b<mb+4*sb

    img_trans = np.ma.array(data = img_trans, mask = mask, fill_value = np.NaN)

    data = {'image1': img1,
            'image2': img2,
            'image3': img3,
            'transmission': img_trans,
            'optical_density': -np.log(img_trans)}

    return data
    
def save_transmission_img_png(filename, img_trans):
    """save transmission image.
    @param filename: filename
    """

    scale = 2**15-1
    
    img_trans_I = np.array( (img_trans*scale).filled(fill_value = 0),
                            dtype = np.uint16)

    PngWriter(filename,
              img_trans_I,
              transparent = 0,
              metadata = {'format version': 1,
                          'image type': 'transmission',
                          'scale transmission': scale,
                          }
              )

def save_optical_density_img_png(filename, img_od, scale = 8000, significant_bits = 16):
    img_od_I = np.array( (img_od*scale+scale).filled(fill_value = 0),
                            dtype = np.uint16)

    PngWriter(filename,
              img_od_I,
              transparent = 0,
              bits = 16,
              significant_bits = significant_bits,
              metadata = {'format version': 1,
                          'image type': 'optical density',
                          'scale optical density': scale,
                          }
              )

def save_raw_img(filename, img):

    img = np.asarray(img,dtype = np.uint16)
    PngWriter(filename,
              img,
              significant_bits = 14,
              metadata = {'format version': 1,
                          'image type': 'raw'}
              )

def load_image_png(filename):
    img, metadata = readpng.read(filename)
    imagetype = metadata.get('image type')

    if imagetype == 'optical density':
        scale = float(metadata['scale optical density'])
        img = img.astype(np.float32)
        img = np.ma.masked_where(img==0, (1.0/scale) * img)
        img-= 1.0
        return imgsplit(img)

    elif imagetype == 'transmission':
        scale = float(metadata['scale transmission'])
        img = img.astype(np.float32)
        img = np.ma.masked_where(img==0, -np.log((1.0/scale)*img))
        return imgsplit(img)

    elif imagetype == 'raw':
        img = np.ma.array(img, dtype = np.float32)
        return imgsplit(img)

    else:
        img = np.ma.array(img, dtype = np.float32)
        img *= (1.0/255)
        return img, img
        

    
def load_image(filename):
    root, ext = os.path.splitext(filename)
    if ext.lower() == '.sis':
        print "read sis"
        return readsis.loadimg(filename)
    elif ext.lower() == '.png':
        print "read png"
        return load_image_png(filename)

def load_image_giacomo(filename):
    root, ext = os.path.splitext(filename)
    if ext.lower() == '.sis':
        print "read sis"
        return readsis.loadimg(filename)
    elif ext.lower() == '.png':
        print "read brasilian png"
        img, img = load_image_png(filename)
        img = -np.log(img)
        return img, img

    


def test_save_image():
    img1 = readsis.read('img/PIC1.sis').astype(np.int_)
    img2 = readsis.read('img/PIC2.sis').astype(np.int_)
    img3 = readsis.read('img/PIC3.sis').astype(np.int_)
    d = calc_img(img1, img2, img3)

    img_trans = d['transmission']

    save_trans_img('img/test_transmission.png', d)
    save_trans_img('img/test_transmission.png', d)
    save_raw_img('img/test_PIC1.png', img1)

def test_read_image():
    r = load_image('img/test.png')
    return r

if __name__ == '__main__':
    #test_save_image()
    r = test_read_image()
    
