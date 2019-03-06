# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 11:42:30 2015

@author: George
"""

open_file()
frame_binning(6)
pixel_binning(2)
slicekeeper(60,1666,1)
flashStart=80
flashEnd=99

subtract(670) #subtract baseline

data_window=ratio(0,flashStart,'average'); #ratio(first_frame, nFrames, ratio_type), now we are in F/F0
data_window=set_value(1,flashStart,flashEnd)
data_window.setWindowTitle('Data Window')

high_pass=butterworth_filter(1,0.005,0.6,keepSourceWindow=True) # High pass filter

###to reduce global signal noise  increase
low_pass=image_calculator(data_window,high_pass,'Subtract',keepSourceWindow=True) # we will use the low pass image as an approximation for the variance of the photon noise.  
low_pass.image[low_pass.image<1]=1 # We can't take the sqrt of a negative number
low_pass=power(.5) #convert from variance to standard deviation 
high_pass.setAsCurrentWindow()

norm_window=ratio(0,flashStart,'standard deviation', keepSourceWindow=True) 

image_calculator(norm_window,low_pass,'Divide') #now the noise should be constant throughout the imaging field and over the duration of the movie
norm_window=set_value(0,  1400, 1606) #our butterworth_filter gives us an artifact towards the end of the movie
norm_window.setWindowTitle('Norm Window')

#butterworth_filter(1,0,.9,keepSourceWindow=True) 

#gaussian_blur(2) #reduces number of pixels for analysis - good for large signals
threshold(2.7, kepSourceWindow=True)
binary_window=set_value(0,0,flashEnd)
binary_window.setWindowTitle('Binary Window') #check noise is same throughout record


#to reload saved workspace run these two lines
#binary_window=g.m.currentWindow
#norm_window=g.m.currentWindow

threshold_cluster(binary_window,data_window,norm_window,rotatedfit=False, maxSigmaForGaussianFit=20, density_threshold=4, time_factor=0.3, roi_width=3)
