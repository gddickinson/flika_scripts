# -*- coding: utf-8 -*-
"""
Created on Wed Mar 04 14:03:56 2015

@author: George
"""

#### SYMETRICAL GAUSSIAN  
#Takes an nxm matrix and returns an nxm matrix which is the gaussian fit
#of the first.  p0 is a list of parameters [xorigin, yorigin, sigma,amplitude]


from analyze.puffs.gaussianFitting import *

open_file()
subtract(100) #subtract baseline


p0=[25,25,10,100]
bounds=[(0,50),(0,50),(5,20),(10,200)]
I=g.m.currentWindow.image
#I=g.m.puffAnalyzer.highpass_window.image[999] #for normalized frame
p, I_fit, dummy = fitGaussian(I,p0,bounds)
print(p) #array with [x,y,sigma,amplitude]
Window(I_fit)
