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



def addNNtoDF(df, nnDF, pixelSize = 108):
        nnDF = nnDF[['id','nnDist_inFrame']]
        nnDF['nnDist_inFrame'] = nnDF['nnDist_inFrame'] / pixelSize        
        #join df based on id
        df = df.join(nnDF.set_index('id'), on='id')
        
        return df
        

if __name__ == '__main__':

    #path = '/Users/george/Data/tdt'  
    path = '/Users/george/Data/htag_cutout_wt/wt' 

    
    #add nn to SVM files based on id
    dfFileList = glob.glob(path + '/**/*_locsID_tracksRG_SVMPredicted.csv', recursive = True)     
    
    for dfFile in tqdm(dfFileList): 
        
        df = pd.read_csv(dfFile)
        nnDF = pd.read_csv(dfFile.split('_locsID_tracksRG_SVMPredicted.csv')[0] + '_locsID_NN.csv')
        
        newDF = addNNtoDF(df, nnDF)
        saveName = os.path.splitext(dfFile)[0]+'_NN.csv'
        newDF.to_csv(saveName, index=None)
    
    
    