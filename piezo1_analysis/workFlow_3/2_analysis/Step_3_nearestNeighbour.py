#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:13:24 2022

@author: george
"""

import warnings
warnings.simplefilter(action='ignore', category=Warning)

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

def getNN(tracksDF):
    #sort by frame
    tracksDF = tracksDF.sort_values(by=['frame'])
    #make empty list to store NN distances & indexes
    nnDistList = []
    nnIndexList = []
    #get list of frames in tracksDF to iterate over
    frames = tracksDF['frame'].unique().tolist()
    #get nn for each centroid position by frame
    for i, frame in enumerate(frames):
        #filter by frame
        frameXY = tracksDF[tracksDF['frame'] == frame][['x [nm]','y [nm]']].to_numpy()
        #nearest neighbour
        distances, indexes = getNearestNeighbors(frameXY,frameXY, k=2)   
        #append distances and indexes of 1st neighbour to list
        nnDistList.extend(distances[:,1])
        #nnIndexList.extend(indexes[:,1])
        print('\r' + 'NN analysis complete for frame{} of {}'.format(i,len(frames)), end='\r')

    #add results to dataframe
    tracksDF['nnDist_inFrame'] =  nnDistList
    #tracksDF['nnIndex_inFrame_all'] = nnIndexList

    tracksDF = tracksDF.sort_index()
    print('\r' + 'NN-analysis added', end='\r')

    return tracksDF

def calcNNforFiles(tracksList, minNumberSegments=1):
    for trackFile in tqdm(tracksList):
                
            ##### load data
            tracksDF = pd.read_csv(trackFile)
            
            #add nearest neigbours to df
            tracksDF = getNN(tracksDF)
            
            #just keep nn info
            tracksDF = tracksDF[['id', 'frame', 'x [nm]', 'y [nm]', 'nnDist_inFrame']]
            
            #save
            saveName = os.path.splitext(trackFile)[0] + '_NN.csv'
            tracksDF.to_csv(saveName)
            print('\n new tracks file exported to {}'.format(saveName))   


def addNNtoSVMFiles(svmFileList):
    for svmFile in tqdm(svmFileList):  
        ##### load svm
        svmDF = pd.read_csv(svmFile) 
        ##### load locID_NN
        nnFile = svmFile.split('_SVM-ALL.csv')[0] + '_locsID_NN.csv'
        nnDF = pd.read_csv(nnFile) 
        nnDF = nnDF[['id','nnDist_inFrame']]
        nnDF['nnDist_inFrame'] = nnDF['nnDist_inFrame'] / 108
        #nnDF['x2'] = nnDF['x [nm]'] / 108        
        #nnDF['y2'] = nnDF['y [nm]'] / 108  
        
        #join df based on id
        svmDF = svmDF.join(nnDF.set_index('id'), on='id')
        
        #save
        saveName = os.path.splitext(svmFile)[0] + '_NN.csv'
        svmDF.to_csv(saveName)
        print('\n NN-file exported to {}'.format(saveName))  
    
    

if __name__ == '__main__':
    ##### RUN ANALYSIS           
    path = '/Users/george/Data/BAPTA/gapSize_10frames'

    
    #get folder paths  
    tracksList = glob.glob(path + '/**/*_locsID.csv', recursive = True)   
    
    #run analysis - filter for track lengths > 5
    calcNNforFiles(tracksList)
    
    #add nn to SVM files based on id
    svmFileList = glob.glob(path + '/**/*_SVM-ALL.csv', recursive = True)     
    addNNtoSVMFiles(svmFileList)
    
    
    