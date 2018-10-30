#!/usr/bin/python
'''
Program:
    This is a program for stacking images. 
Usage: 
    stack_img.py [image name list]
Editor:
    Jacob975
20181021
#################################
update log

20181021 version alpha 1
    1. The code works
'''
from sys import argv
from astropy.io import fits as pyfits
import numpy as np
import time

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 2:
        print "Error! The number of arguments is wrong."
        print "Usage: histogram.py [image name list]" 
        exit()
    image_name_list_name = argv[1]
    #---------------------------------------
    # Load data
    image_name_list = np.loadtxt(image_name_list_name, dtype = str)
    image_list = []
    header_list = []
    for i, name in enumerate(image_name_list):
        image_list.append(pyfits.getdata(name))
        header_list.append(pyfits.getheader(name))
    # Stack img 1 and img 2
    img12 = np.array(image_list[:2])
    print (img12.shape)
    stack_img12 = np.mean(img12, axis = 0)
    pyfits.writeto('stack_img12.fits', stack_img12, header_list[0])
    # Stack img 1, img 2, and img 3
    img123 = np.array(image_list)
    print (img123.shape)
    stack_img123 = np.mean(img123, axis = 0)
    pyfits.writeto('stack_img123.fits', stack_img123, header_list[0])
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
