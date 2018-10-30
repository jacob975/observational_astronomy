#!/usr/bin/python
'''
Program:
    This is a program for calibrate M95 in Lulin data. 
Usage: 
    calibrate_images.py [raw_list] [dark_list] [bias_list] [flat_list]
Editor:
    Jacob975
20180930
#################################
update log

20180930 version alpha 1
    1. The code works.
20181010 version alpha 2
    1. Update the the approach to proper flats.
    2. Improve the effeciency
'''
from sys import argv
from astropy.io import fits as pyfits
import numpy as np
import time

# load a list of data, and load the exposure time.
# If True, read the filter information from header.
def load_data_list(name_list, read_filter = False):
    data_list = []
    exptime = 0.0
    data_filter = ""
    # More than 1 image
    try:
        for name in name_list:
            # exposure time
            if exptime == 0.0:
                header = pyfits.getheader(name)
                exptime = float(header['EXPTIME'])
            # Load filter
            if read_filter == True and data_filter == "":
                header = pyfits.getheader(name)
                data_filter = header['FILTER']
            # load data
            data = pyfits.getdata(name)
            data_list.append(data)
        data_array = np.array(data_list)
    # Only 1 image.
    except:
        name = str(name_list)
        header = pyfits.getheader(name)
        exptime = float(header['EXPTIME'])
        if read_filter:
            data_filter = header['FILTER']
        data_list = pyfits.getdata(name)
        data_array = np.array([data_list])
    if read_filter:
        return data_array, exptime, data_filter
    else:
        return data_array, exptime

# Load the first header in the list
def load_first_header(name_list):
    header = None
    # More than 1 image
    try:
        for name in name_list:
            # load data
            header = pyfits.getheader(name)
            break
    # Only 1 image.
    except:
        name = str(name_list)
        header = pyfits.getheader(name)
    return header

# Subtract the data with proper dark
def subdark(raw, raw_exptime, dark, dark_exptime, bias):
    data_subbias = raw - bias
    dark_subbias = dark - bias
    proper_dark = dark_subbias * raw_exptime / dark_exptime
    data_subdark = data_subbias - proper_dark
    return data_subdark

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 5:
        print "Error! The number of arguments is wrong."
        print "Usage: calibrate_images.py [raw_list] [dark_list] [bias_list] [flat_list]"
        print "Hint: files mentioned in the same list should have the same exposure time."
        exit()
    raw_list_name = argv[1]
    dark_list_name = argv[2]
    bias_list_name = argv[3]
    flat_list_name = argv[4]
    #---------------------------------------
    # Load data
    raw_name_list = np.loadtxt(raw_list_name, dtype = str)
    raw_array, raw_exptime, _filter = load_data_list(raw_name_list, read_filter = True)
    print "raw exptime = {0}".format(raw_exptime)
    dark_name_list = np.loadtxt(dark_list_name, dtype = str)
    dark_array, dark_exptime = load_data_list(dark_name_list)
    print "dark exptime = {0}".format(dark_exptime)
    bias_name_list = np.loadtxt(bias_list_name, dtype = str)
    bias_array, bias_exptime = load_data_list(bias_name_list)
    print "bias exptime = {0}".format(bias_exptime)
    flat_name_list = np.loadtxt(flat_list_name, dtype = str)
    flat_array, flat_exptime = load_data_list(flat_name_list)
    print "flat exptime = {0}".format(flat_exptime)
    #---------------------------------------
    # Start calibration
    # The formula for calibration
    #
    #           raw - bias - proper_dark
    # data = ---------------------------------------------------
    #           median (normalized (flat - bias - proper_dark))
    #
    # Create the denominator part
    print 'Reduction function:'
    print '           raw - bias - proper_dark'
    print ' data = ---------------------------------------------------'
    print '           median (normalized (flat - bias - proper_dark))'
    # Create the denominator part
    print '--- Denominator part ---'
    dark = np.median(dark_array, axis = 0)
    bias = np.median(bias_array, axis = 0)
    flat_list_subbias_subdark_n = []
    for flat in flat_array:
        flat_subbias_subdark = subdark(flat, flat_exptime, dark, dark_exptime, bias)
        flat_subbias_subdark_n = np.divide(flat_subbias_subdark, np.mean(flat_subbias_subdark))
        flat_list_subbias_subdark_n.append(flat_subbias_subdark_n)
    # Normalize
    flat_array_subbias_subdark_n = np.array(flat_list_subbias_subdark_n)
    # Take median amount all flats.
    flat_subbias_subdark_n_median = np.median(flat_array_subbias_subdark_n, axis = 0)
    pyfits.writeto('{0}_flat_n.fits'.format(_filter), flat_subbias_subdark_n_median, overwrite = True)
    print 'Done!'
    # Create the numerator part
    print '--- numerator part ---'
    for index, raw in enumerate(raw_array):
        raw_subbias_subdark = subdark(raw, raw_exptime, dark, dark_exptime, bias)
        try:
            raw_header = pyfits.getheader(raw_name_list[index])
            reduced_data = np.divide(raw_subbias_subdark, flat_subbias_subdark_n_median)
            pyfits.writeto('{0}_reduced.fits'.format(raw_name_list[index][:-4]), reduced_data, raw_header, overwrite = True)
        except IndexError :
            raw_header = pyfits.getheader(str(raw_name_list))
            reduced_data = np.divide(raw_subbias_subdark, flat_subbias_subdark_n_median)
            pyfits.writeto('{0}_reduced.fits'.format(str(raw_name_list)[:-4]), reduced_data, raw_header, overwrite = True)
    print 'Done'
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
