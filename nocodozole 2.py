# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 16:31:51 2015

@author: George
"""

open_file()

flashStart=857
flashEnd=951
subtract(650) #subtract baseline
data_window=ratio(0,800,'average'); #ratio(first_frame, nFrames, ratio_type), now we are in F/F0
data_window=set_value(1,flashStart,flashEnd) #remove flash
data_window.setWindowTitle('Data Window')
high_pass=butterworth_filter(1,.0003,1,keepSourceWindow=True) # High pass filter

#to reduce global signal noise  increase
low_pass=image_calculator(data_window,high_pass,'Subtract',keepSourceWindow=True) # we will use the low pass image as an approximation for the variance of the photon noise.  
low_pass.image[low_pass.image<1]=1 # We can't take the sqrt of a negative number
low_pass=power(.5) #convert from variance to standard deviation 
high_pass.setAsCurrentWindow()

norm_window=ratio(0,800,'standard deviation', keepSourceWindow=True) 

image_calculator(norm_window,low_pass,'Divide') #now the noise should be constant throughout the imaging field and over the duration of the movie
norm_window=set_value(0, 9500,9999) #our butterworth_filter gives us an artifact towards the end of the movie
norm_window.setWindowTitle('Norm Window')

butterworth_filter(1,0,.9,keepSourceWindow=True) 

gaussian_blur(2) #reduces number of pixels for analysis - good for large signals
threshold(0.4)
binary_window=set_value(0,0,250)
binary_window.setWindowTitle('Binary Window') 


#to reload saved workspace run these two lines
#binary_window=g.m.currentWindow
#norm_window=g.m.currentWindow

threshold_cluster(binary_window,data_window,norm_window,rotatedfit=False, maxSigmaForGaussianFit=20, density_threshold=4, time_factor=0.2, roi_width=7)
