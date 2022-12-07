#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 16:33:37 2022

@author: george
"""


import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree
from tqdm import tqdm
import os, glob
from matplotlib import pyplot as plt

def getNearestNeighbors(train,test,k=2):
    tree = KDTree(train, leaf_size=5)   
    dist, ind = tree.query(test, k=k)
    #dist.reshape(np.size(dist),)     
    return dist, ind

def getNN(expt):
    #load df
    df = pd.read_csv(expt)
    #sort by frmae
    df = df.sort_values(by=['frame'])
    #make empty list to store NN distances & indexes
    nnDistList = []
    nnIndexList = []
    #get list of frames in df to iterate over
    frames = df['frame'].unique().tolist()
    #get nn for each centroid position by frame
    for frame in frames:
        #filter by frame
        frameXY = df[df['frame'] == frame][['x','y']].to_numpy()
        #nearest neighbour
        distances, indexes = getNearestNeighbors(frameXY,frameXY, k=2)   
        #append distances and indexes of 1st neighbour to list
        nnDistList.extend(distances[:,1])
        nnIndexList.extend(indexes[:,1])

    #add results to dataframe
    df['nnDist'] =  nnDistList
    df['nnIndex'] = nnIndexList
    #save new df
    saveName = expt.split('.csv')[0] + '_NN.csv'
    df.to_csv(saveName)
    print('\n new tracks file exported to {}'.format(saveName)) 
    return

def processFiles(exptList):
    for expt in tqdm(exptList):
        getNN(expt)    
    return



if __name__ == '__main__':
    ##### RUN ANALYSIS        
    path = '/Users/george/Data/10msExposure10s'
    #path = '/Users/george/Data/10msExposure2s_fixed'
    
    #get expt paths
    exptList = glob.glob(path + '/**/*_SVMPredicted.csv', recursive = True)   
        
    #run analysis
    processFiles(exptList)