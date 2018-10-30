#!/usr/bin/python
'''
Program:
    This is a program for plot a histogram 
Usage: 
    histogram.py [image name]
Editor:
    Jacob975
20180930
#################################
update log

20181010 version alpha 1
    1. The code works
'''
from sys import argv
from astropy.io import fits as pyfits
import numpy as np
import time
import matplotlib.pyplot as plt
import math
from scipy import optimize

def hist_show(data, half_width = 80, shift = 0, VERBOSE = 0):
    # get rid of nan
    flatten_data = data[~np.isnan(data)]
    flatten_data = flatten_data[flatten_data < 100000.0]
    flatten_data = flatten_data[flatten_data > -10000.0]
    data_mean = np.mean(flatten_data)
    if math.isnan(data_mean):
        data_mean = 0.0
    # number is the number of star with this value
    # bin_edges is left edge position of each point on histagram.
    numbers, bin_edges = np.histogram(flatten_data, bins= 80, range = [data_mean - half_width + shift , data_mean + half_width + shift], normed = True)
    # find the maximum number, where will be the central of fitting figure.
    index_max = np.argmax(numbers)
    index_max = bin_edges[index_max]
    bin_middles = 0.5*(bin_edges[1:] + bin_edges[:-1])
    plt.title("Histogram")
    plt.plot(bin_middles, numbers)
    plt.savefig('{0}_hist.png'.format(image_name[:-5]))

def hist_gaussian(x, amp, mu, sig):
    return amp * np.power(2 * np.pi , -0.5)*np.exp(-np.power(x - mu , 2.) / (2 * np.power(sig, 2.)))/sig

def hist_gaussian_fitting(data, half_width = 160, shift = 0, VERBOSE = 0):
    # get rid of nan
    flatten_data = data[~np.isnan(data)]
    flatten_data = flatten_data[flatten_data < 100000.0]
    flatten_data = flatten_data[flatten_data > -10000.0]
    data_mean = np.mean(flatten_data)
    if math.isnan(data_mean):
        data_mean = 0.0
    # number is the number of star with this value
    # bin_edges is left edge position of each point on histagram.
    numbers, bin_edges = np.histogram(flatten_data, bins= 80, range = [data_mean - half_width + shift , data_mean + half_width + shift], normed = True)
    # find the maximum number, where will be the central of fitting figure.
    index_max = np.argmax(numbers)
    index_max = bin_edges[index_max]
    bin_middles = 0.5*(bin_edges[1:] + bin_edges[:-1])
    # initial paras
    if math.isnan(np.std(flatten_data)):
        std = 1.0
    else :
        std = np.std(flatten_data)
    moments = (0.01, data_mean, std)
    # fit 
    paras, cov = optimize.curve_fit(hist_gaussian, bin_middles, numbers, p0 = moments)
    return paras, cov
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 2:
        print "Error! The number of arguments is wrong."
        print "Usage: histogram.py [image name]" 
        exit()
    image_name = argv[1]
    #---------------------------------------
    # Load data
    image = pyfits.getdata(image_name)
    flatten_image = image.flatten()
    paras, covs = hist_gaussian_fitting(flatten_image)
    image_mean = np.mean(flatten_image)
    scale_shift = paras[1] - image_mean
    hist_show(flatten_image, shift = scale_shift)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
