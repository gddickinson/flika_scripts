#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 18:27:20 2022

@author: george
"""

import numpy as np
import pandas as pd

from tqdm import tqdm
import os, glob


def filterDFandLocs(dfFile, locsIdentifer='_tracks2RG2_SVMPredicted2.csv', colName='SVM'):
    #load df with SVM
    df = pd.read_csv(dfFile)
    #load original locs file
    locsFileName = dfFile.split(locsIdentifer)[0] + '.csv'
    locs = pd.read_csv(locsFileName)
    #load SVM3 df
    df_SVM3_file = dfFile.split('_locsID2_tracks2RG2_SVMPredicted2.csv')[0] + '_locsID_tracksRG_SVMPredicted_SVM-3.csv'
    df_SVM3 = pd.read_csv(df_SVM3_file) 
    #filter by SVM class
    df_SVM2 = df[df[colName]==2]
    df_SVM3_extras = df[df[colName]==3]
    
    #combine SVM3 tracks
    maxTrackNumber = max(df_SVM3['track_number'])
    df_SVM3_extras['track_number'] = df_SVM3_extras['track_number'] + maxTrackNumber 
    df_SVM3 = df_SVM3.append(df_SVM3_extras)
    
    df_SVM2and3 = df_SVM2.append(df_SVM3)
        
    #get ids of SVM tracks
    filteredID_list = df_SVM2and3['id'].tolist()
    print(1 in filteredID_list)
    
            
    #filter locs file to get locs not allocated to filtered df    
    remainingLocs = locs[~locs.index.isin(filteredID_list)]
    remainingLocs['id'] = remainingLocs['id'].astype('int')
    remainingLocs = remainingLocs.set_index('id')
    
    #save df and locs files
    df_SVM2.to_csv(dfFile.split('.csv')[0] + '_SVM-2.csv', index=None)
    df_SVM3.to_csv(df_SVM3_file.split('_SVMPredicted_SVM-3.csv')[0] + '_SVMPredicted2_SVM-3.csv', index=None)   
    remainingLocs.to_csv(locsFileName.split('_locsID2.csv')[0] + '_locsID3.csv')
    return df_SVM2, df_SVM3,locs, remainingLocs


if __name__ == '__main__':
    ##### RUN ANALYSIS        
    #path = '/Users/george/Data/10msExposure2s'
    #path = '/Users/george/Data/10msExposure2s_fixed'
    path = '/Users/george/Data/10msExposure2s_test'    
    
    #get expt folder list
    exptList = glob.glob(path + '/**/*_tracks2RG2_SVMPredicted2.csv', recursive = True)   

    for file in tqdm(exptList):
        df_SVM2, df_SVM3,locs, remainingLocs = filterDFandLocs(file)
