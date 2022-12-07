#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 17:25:00 2022

@author: george
"""
import numpy as np
import pandas as pd

from tqdm import tqdm
import os, glob


def makeLagDF(exptFolder):
    lagFiles = glob.glob(exptFolder + '/**/*_lagsHisto.txt', recursive = True)  
    lagDF = pd.DataFrame()
    
    #add lags to df
    for lagFile in tqdm(lagFiles):
        tempDF = pd.read_csv(lagFile,names=['lag'])
        colName = os.path.basename(lagFile).split('_MMStack')[0]
        lagDF[colName] = tempDF['lag']


    #df squared
    lagSquaredDF = np.square(lagDF)
    
    #export lagDF
    savename = os.path.join(exptFolder, '{}_lags.csv'.format(exptFolder.split('/')[-1]))
    savename2 = os.path.join(exptFolder, '{}_lagsquared.csv'.format(exptFolder.split('/')[-1]))
    lagDF.to_csv(savename, float_format='%.5f')
    print ('{} exported'.format(savename))
    lagSquaredDF.to_csv(savename2, float_format='%.5f')
    print ('{} exported'.format(savename2))    
    


if __name__ == '__main__':
    ##### RUN ANALYSIS        
    path = '/Users/george/Data/10msExposure2s'    
    #path = '/Users/george/Data/10msExposure2s_fixed'
    
    #get expt folder list
    exptList = glob.glob(path + '/*', recursive = True)   

    for exptFolder in tqdm(exptList):
        makeLagDF(exptFolder)







        