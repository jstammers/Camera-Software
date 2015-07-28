#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Calculate averages and errors."""
import numpy

def avgdata(x, y):
    """avgdata: calculates mean and std for y data.
    @param x: single column of x values
    @type x: numpy array
    @param y: array with len(x) rows
    @type y: numpy array
    @return: (x_unique, mean, std)
    """

    #print "avgdata:"
    #print "x: ", type(x), x
    #print "y: ", type(y), y

    #TODO: this fixes problem when only one line is present in Table,
    #then x and y are ndarrays, not ma!
    x = numpy.ma.array(x)
    y = numpy.ma.array(y)


    if len(y.shape) < 2:
        nycol = 1
    else:
        nycol = y.shape[1]

    #get data and boolean array of valid entries
    
    try:
        x_data = x.data
        if x.mask.any():
            x_valid = ~x.mask
        else:
            x_valid = numpy.ones(x.shape, dtype = numpy.bool)
    except AttributeError:
        x_data = x
        x_valid = numpy.ones(x.shape, dtype = numpy.bool)

    y_data = y.data
    try: 
        if y.mask.any():
            y_valid = ~y.mask
        else:
            y_valid = numpy.ones(y.shape, dtype = numpy.bool)
    except AttributeError:
        y_valid = numpy.ones(y.shape, dtype = numpy.bool)

    #unique, sorted valid x values
    x_unique = numpy.array(list(set(x_data[x_valid])))
    x_unique.sort()
    
    #prepare storage for results
    s = (len(x_unique),) + y_data.shape[1:]
    result_mean = numpy.zeros(shape = s, dtype = numpy.float_)
    result_std  = numpy.zeros(shape = s, dtype = numpy.float_)

    #loop over unique xdata
    for k, xval in enumerate(x_unique):

        #which valid entries belong to this entry?
        xsel = (x_data == xval);
        
        #loop over columns of y
            
        for l in range(nycol):
            ycol_data  = y_data[xsel , l]
            ycol_valid = y_valid[xsel, l]

            m = ycol_data[ycol_valid].mean()
            s = ycol_data[ycol_valid].std()
            
            result_mean[k, l] = m
            result_std[k, l]  = s

        #todo: remove outliers, recalculate mean and std. 

    x_unique = numpy.ma.array(x_unique, mask = ~numpy.isfinite(x_unique))
    result_mean = numpy.ma.array(result_mean, mask = ~numpy.isfinite(result_mean))
    result_std  = numpy.ma.array(result_std,  mask = ~numpy.isfinite(result_std))

    return x_unique, result_mean, result_std





if __name__ == '__main__':

    x = numpy.ma.array([3, 3, 3, 2, 2, 1])

    ymask = numpy.array([0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0])
    ymask.shape = (6,2)
    
    y = numpy.ma.array([[1, 1],
                        [2, 2],
                        [5, 5],
                        [1, 1],
                        [2, 2],
                        [0, 0]],
                       mask = ymask,
                       fill_value = numpy.NaN)

    

    print 'x: '
    print x

    print 'y: '
    print y
    
    x_unique, rm, rs = avgdata(x, y)

    print 'x_unique: ', x_unique


    print 'mean: '
    print rm

    print 'std:  '
    print rs
