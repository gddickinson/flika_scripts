#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:13:24 2022

@author: george
"""

import numpy as np
import pandas as pd

from tqdm import tqdm
import os, glob

from sklearn.neighbors import KDTree
import math

from scipy import stats, spatial
from matplotlib import pyplot as plt


def getNearestNeighbors(train,test,k=2):
    tree = KDTree(train, leaf_size=5)   
    dist, ind = tree.query(test, k=k)
    #dist.reshape(np.size(dist),)     
    return dist, ind

def getNN(tracksDF, tracksDF_train, searchSVM):
    #sort by frame
    tracksDF = tracksDF.sort_values(by=['frame'])
    tracksDF_train = tracksDF_train.sort_values(by=['frame'])
    #make empty list to store NN distances & indexes
    nnDistList = []
    nnIndexList = []
    #get list of frames in tracksDF to iterate over
    frames = tracksDF['frame'].unique().tolist()
    #get nn for each centroid position by frame
    for i, frame in enumerate(frames):
        #filter by frame
        frameXY = tracksDF[tracksDF['frame'] == frame][['x','y']].to_numpy()
        frameXY_train = tracksDF_train[tracksDF_train['frame'] == frame][['x','y']].to_numpy()        
        #nearest neighbour
        distances, indexes = getNearestNeighbors(frameXY_train,frameXY, k=2)   
        #append distances and indexes of 1st neighbour to list
        nnDistList.extend(distances[:,1])
        #nnIndexList.extend(indexes[:,1])
        print('\r' + 'NN analysis complete for frame{} of {}'.format(i,len(frames)), end='\r')

    #add results to dataframe
    tracksDF['nnDist_inFrame_SVM{}'.format(searchSVM)] =  nnDistList
    #tracksDF['nnIndex_inFrame_all'] = nnIndexList

    tracksDF = tracksDF.sort_index()
    print('\r' + 'NN-analysis added', end='\r')

    return tracksDF

def calcNN_acrossClass(tracksList):
    
    for trackFile in tqdm(tracksList):
                
            ##### load data
            tracksDF = pd.read_csv(trackFile)
            
            SVM1 = tracksDF[tracksDF['SVM'] == 1] 
            SVM2 = tracksDF[tracksDF['SVM'] == 2]            
            SVM3 = tracksDF[tracksDF['SVM'] == 3]             
            
            #add nearest neigbours to df across differnt classes
            tracksDF = getNN(tracksDF,SVM1, 1)
            tracksDF = getNN(tracksDF,SVM2, 2)
            tracksDF = getNN(tracksDF,SVM3, 3)            
            
            #sort by original index
            tracksDF = tracksDF.sort_values('Unnamed: 0')           
            
            #save
            saveName = os.path.splitext(trackFile)[0] + '_NN-AcrossClass.csv'
            tracksDF.to_csv(saveName)
            print('\n new tracks file exported to {}'.format(saveName))   

   

if __name__ == '__main__':
    ##### RUN ANALYSIS        
    #path = '/Users/george/Data/10msExposure2s_test'
    path = '/Users/george/Data/tdt_20s/wt' 
    
    #get folder paths  
    tracksList = glob.glob(path + '/**/*_SVMPredicted_NN.csv', recursive = True)   
    
    #run analysis 
    calcNN_acrossClass(tracksList)
    

    
   