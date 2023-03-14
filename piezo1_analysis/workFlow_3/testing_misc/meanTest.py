#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 14:22:45 2023

@author: george
"""
#%matplotlib qt 
import numpy as np
import pandas as pd
import skimage.io as skio
from tqdm import tqdm
import os, glob
from matplotlib import pyplot as plt
import pyqtgraph as pg


tiffFile = '/Users/george/Data/trackpyTest/GB_199_2022_09_01_HTEndothelial_NonBAPTA_plate1_2_MMStack_Default_bin10.tif'
locsFile = '/Users/george/Data/trackpyTest/GB_199_2022_09_01_HTEndothelial_NonBAPTA_plate1_2_MMStack_Default_bin10_locsID_tracksRG_SVMPredicted_NN_diffusion_velocity_AllLocs_NNcount.csv'

pixelSize = 0.108

#load tiff
A = skio.imread(tiffFile, plugin='tifffile')


trackList= [20,50,100]
traceList = []
        
d = 4 # Desired size of cropped image
A_pad = np.pad(A,((0,0),(d,d),(d,d)),'constant', constant_values=0)

frames = int(A_pad.shape[0])
A_crop = np.zeros((frames,d,d)) 
A_crop_stack = np.zeros((len(trackList),frames,d,d)) 
x_limit = int(d/2) 
y_limit = int(d/2)

#load locs
locs = pd.read_csv(locsFile)
locs = locs.dropna()
locs['track_number'] = locs['track_number'].astype(int)


for i, track_number in enumerate(trackList):
    #get track data
    trackDF = locs[locs['track_number'] == int(track_number)]
     
    # Extract x,y,frame data for each point
    points = np.column_stack((trackDF['frame'].to_list(), trackDF['x'].to_list(), trackDF['y'].to_list()))    
    

    #interpolate points for missing frames
    allFrames = range(int(min(points[:,0])), int(max(points[:,0]))+1)
    xinterp = np.interp(allFrames, points[:,0], points[:,1])
    yinterp = np.interp(allFrames, points[:,0], points[:,2])            
 
    #pad edges with last known position
    xinterp = np.pad(xinterp, (int(min(points[:,0])), frames-1 - int(max(points[:,0]))), mode='edge')
    yinterp = np.pad(yinterp, (int(min(points[:,0])), frames-1 - int(max(points[:,0]))), mode='edge')
    
    allFrames = range(0, frames)

    points = np.column_stack((allFrames, xinterp, yinterp)) 
       
    # Loop through each point and extract a cropped image
    for point in points:
        minX = int(point[1]) - x_limit + d # Determine the limits of the crop
        maxX = int(point[1]) + x_limit + d
        minY = int(point[2]) - y_limit + d
        maxY = int(point[2]) + y_limit + d
        crop = A_pad[int(point[0]),minX:maxX,minY:maxY] # Extract the crop
        A_crop[int(point[0])] = crop # Store the crop in the array of cropped images
    
    A_crop_stack[i] = A_crop # Store the crop in the array of cropped images
        
    trace = np.mean(A_crop, axis=(1,2))
    traceList.append(trace)

A_crop_stack[A_crop_stack== 0] = np.nan

meanImg = np.mean(A_crop_stack, axis=(0,1))
maxImg = np.max(A_crop_stack, axis=(0,1))

plt.imshow(meanImg)

# tracePlot = pg.plot(title="Test")

# #add signal traces for all tracks to plot
# for trace in traceList:
#     curve = pg.PlotCurveItem(trace)
#     tracePlot.addItem(curve)



# if __name__ == '__main__':

#     pg.exec()