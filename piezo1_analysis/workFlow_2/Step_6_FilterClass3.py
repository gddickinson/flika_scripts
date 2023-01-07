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


def filterDFandLocs_SVM3(dfFile, locsIdentifer='_tracksRG_SVMPredicted.csv', colName='SVM'):
    #load df with SVM
    df = pd.read_csv(dfFile)
    #load original locs file
    locsFileName = dfFile.split(locsIdentifer)[0] + '.csv'
    locs = pd.read_csv(locsFileName)
    locs['id'] = locs['id'].astype('int')
    
    #filter by SVM class
    filteredDF = df[df[colName]==3]
    filteredID_list = filteredDF['id'].tolist()

    
    #filter locs file to get locs not allocated to filtered df    
    remainingLocs = locs[~locs['id'].isin(filteredID_list)]   
    #remainingLocs = remainingLocs.set_index('id')
    
    #save df and locs files
    filteredDF.to_csv(dfFile.split('.csv')[0] + '_SVM-3.csv', index=None)
    remainingLocs.to_csv(locsFileName.split('.csv')[0] + '2.csv', index=None)
    return filteredDF, locs, remainingLocs


if __name__ == '__main__':
    ##### RUN ANALYSIS        
    #path = '/Users/george/Data/10msExposure2s'
    #path = '/Users/george/Data/10msExposure2s_fixed'
    #path = '/Users/george/Data/10msExposure2s_test'    
    #path = '/Users/george/Data/10msExposure2s_new'
    path = '/Users/george/Data/tdt' 
    
 
    #get expt folder list
    exptList = glob.glob(path + '/**/*_SVMPredicted.csv', recursive = True)   

    for file in tqdm(exptList):
        filteredDF, locs, locs_remaining = filterDFandLocs_SVM3(file)
