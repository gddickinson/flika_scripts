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


def filterDFandLocs(dfFile, locsIdentifer='_tracks3RG3_SVMPredicted3.csv', colName='SVM'):
    #load df with SVM
    df = pd.read_csv(dfFile)
    
    #load original locs file
    locsFileName = dfFile.split(locsIdentifer)[0] + '.csv'
    locs = pd.read_csv(locsFileName)
    
    #load SVM3 df
    df_SVM3_file = dfFile.split('_locsID3_tracks3RG3_SVMPredicted3.csv')[0] + '_locsID2_tracks2RG2_SVMPredicted2_SVM-3.csv'
    df_SVM3 = pd.read_csv(df_SVM3_file) 

    #load SVM2 df
    df_SVM2_file = dfFile.split('_locsID3_tracks3RG3_SVMPredicted3.csv')[0] + '_locsID2_tracks2RG2_SVMPredicted2_SVM-2.csv'
    df_SVM2 = pd.read_csv(df_SVM2_file) 
    print(len(df_SVM2))

    
    #filter by SVM class
    df_SVM1 = df[df[colName]==1]
    df_SVM2_extras = df[df[colName]==2]
    df_SVM3_extras = df[df[colName]==3]
    
    #combine SVM3 tracks - add max track numbers of df being combined to avoid track number overlap
    df_SVM3_extras['track_number'] = df_SVM3_extras['track_number'] + max(df_SVM3['track_number'])
    df_SVM3 = df_SVM3.append(df_SVM3_extras)
    
    #combine SVM2 tracks
    df_SVM2_extras['track_number'] = df_SVM2_extras['track_number'] + max(df_SVM2['track_number'])
    df_SVM2 = df_SVM2.append(df_SVM2_extras)    

    #combine all 
    df_SVM3['track_number'] = df_SVM3['track_number'] + max(df_SVM2['track_number'])     
    df_SVM2and3 = df_SVM2.append(df_SVM3)
     
    df_SVM1['track_number'] = df_SVM1['track_number'] + max(df_SVM2and3['track_number'])      
    df_All = df_SVM2and3.append(df_SVM1)
        
    #get ids of SVM tracks
    filteredID_list = df_All['id'].tolist()    
            
    #filter locs file to get leftover locs   
    remainingLocs = locs[~locs['id'].isin(filteredID_list)]  
    remainingLocs['id'] = remainingLocs['id'].astype('int')
    
    #save df and locs files
    df_SVM1.to_csv(dfFile.split('.csv')[0] + '_SVM-1.csv', index=None)
    df_SVM2.to_csv(df_SVM2_file.split('_tracks2RG2_SVMPredicted2_SVM-2.csv')[0] + '_tracks3RG3_SVMPredicted3_SVM-2.csv', index=None)      
    df_SVM3.to_csv(df_SVM3_file.split('_tracks2RG2_SVMPredicted2_SVM-3.csv')[0] + '_tracks3RG3_SVMPredicted3_SVM-3.csv', index=None)   
    df_All.to_csv(locsFileName.split('_locsID3.csv')[0] + '_SVM-ALL.csv', index=None)
    remainingLocs.to_csv(locsFileName.split('_locsID3.csv')[0] + '_locsID_UNLINKED.csv', index=None)
    
    return 


if __name__ == '__main__':
    ##### RUN ANALYSIS        
    #path = '/Users/george/Data/10msExposure2s'
    #path = '/Users/george/Data/10msExposure2s_fixed'
    path = '/Users/george/Data/10msExposure2s_test'    
    #path = '/Users/george/Data/10msExposure2s_new'
    
    #get expt folder list
    exptList = glob.glob(path + '/**/*_tracks3RG3_SVMPredicted3.csv', recursive = True)   

    for file in tqdm(exptList):
        remainingLocs = filterDFandLocs(file)
