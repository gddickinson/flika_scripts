#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 09:50:12 2024

@author: george
"""

import warnings
warnings.simplefilter(action='ignore', category=Warning)

import numpy as np
import pandas as pd

from tqdm import tqdm
import os, glob

import skimage.io as skio
from sklearn.neighbors import KDTree
from matplotlib import pyplot as plt

def getNearestNeighbors(train,test,k=2):
    tree = KDTree(train, leaf_size=5)
    if k > len(train):
        #no neighbours to count return nan
        a = np.empty((k,k))
        a[:] = np.nan
        return np.nan, np.nan
    else:
        dist, ind = tree.query(test, k=k)
    #dist.reshape(np.size(dist),)
    return dist, ind

def getActinXY(tiff, threshold = 60):
    #generate binary from tiff
    binArray = np.zeros_like(tiff)
    binArray[tiff > threshold] = 1
    # Extract the x, y  coordinates from the binary array
    x, y = binArray.nonzero()
    return binArray, x,y

def addDistanceToActin(df, actin_x,actin_y):
    punctaXY = df[['x','y']].to_numpy()
    actinXY = np.column_stack([actin_y,actin_x])

    nnDistList = []

    #get nearest actin pixel distance
    distances, _ = getNearestNeighbors(actinXY,punctaXY)
    #append distances and indexes of 1st neighbour to list
    if (np.isnan(distances).any()):
        nnDistList.append(np.nan)
    else:
        nnDistList.extend(distances[:,1])

    df['distanceToActin'] = nnDistList
    #add track mean distance to actin
    df['mean_distanceToActin'] = df.groupby('track_number')[['distanceToActin']].transform('mean')
    return df


if __name__ == '__main__':
    ##### RUN ANALYSIS
    path = '/Users/george/Data/actin_test/analysis'

    #get files
    fileList = glob.glob(path + '/**/*_locErr.csv', recursive = True)

    #set threshold for actin
    actin_thresh = 60


    for file in tqdm(fileList):
        #load df
        df = pd.read_csv(file)
        #get tiff name
        tiffFile = file.split('_locs')[0] + '_actin_Probabilities.tif'
        #load tiff
        tiff = skio.imread(tiffFile, plugin='tifffile')
        #get x,y positions of actin pixels above threshold
        binArray, actin_x, actin_y = getActinXY(tiff,threshold=actin_thresh)
        #Add distance to nearrest actin pixel center
        newDF = addDistanceToActin(df, actin_x,actin_y)

# =============================================================================
#         ## UNCOMMENT TO DISPLAY ACTIN AND PUNCTA XY POS OVERLAID ON BINARY
#         # Plot the binary
#         plt.imshow(binArray)
#         # Plot the actin xy points
#         plt.scatter(actin_y, actin_x, c='red')
#         #plot puncta
#         #plt.scatter(df['x'], df['y'], c='blue')
#         plt.scatter(newDF['x'], newDF['y'], c=newDF['distanceToActin'], cmap='plasma')
#         # Display the plot
#         plt.show()
# =============================================================================

        #save new df
        saveName = os.path.splitext(file)[0]+'_ActinDist.csv'
        newDF.to_csv(saveName, index=None)

        #save binary image
        binSaveName = file.split('_locs')[0] + '_actin_Binary.tif'
        skio.imsave(binSaveName, binArray, plugin='tifffile')


