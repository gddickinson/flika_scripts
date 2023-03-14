#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 19:05:03 2023

@author: george
"""

import warnings
warnings.simplefilter(action='ignore', category=Warning)

import pandas as pd

from tqdm import tqdm
import os, glob


def filterDF(df, colName, filterValue, filterOp):
    if filterOp == 'Over':
        filteredDF = df[df['{}'.format(colName)] > filterValue]
    if filterOp == 'Under':
        filteredDF = df[df['{}'.format(colName)] < filterValue]
    if filterOp == 'Equals':
        filteredDF = df[df['{}'.format(colName)] == filterValue]    
    if filterOp == 'NotEqual':
        filteredDF = df[df['{}'.format(colName)] != filterValue]  
    
    return filteredDF
        

if __name__ == '__main__':

    path = '/Users/george/Data/testing'
    
    colName = 'n_segments'
    filterValue = 10
    filterOp = 'Over'
    
    #get filenames for all files to filter under path folder
    fileList = glob.glob(path + '/**/*_NNcount.csv', recursive = True)     
    
    for file in tqdm(fileList): 
        
        df = pd.read_csv(file)
        
        filteredDF = filterDF(df, colName, filterValue, filterOp)
        
        saveName = os.path.splitext(file)[0]+'_{}{}{}.csv'.format(colName, filterOp, filterValue)
        #if you want to overwrite the file uncomment line below
        #saveName = file
        
        filteredDF.to_csv(saveName, index=None)