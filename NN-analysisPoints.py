#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 13:34:38 2021

@author: gdickinson
"""

import numpy as np
import os
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import glob

#select folder
path = r"/Users/gdickinson/Desktop/points"

#get all filenames containing '.txt in folder
fileList = [f for f in glob.glob(path + "**/*.txt", recursive=True)]


#loop through files
for fileName in fileList:
    print('Analysing {}'.format(fileName))

    #file to load
    #fileName = r"/Users/gdickinson/Desktop/testROIs3.txt"
    
    #save path
    saveName= fileName.split('.')[0] + '.csv'
    
        
    #load data into df
    column_names = ['frame','center_x','center_y']
    df = pd.read_csv(fileName,delimiter=' ',header=None,dtype={0:int,1:float,2:float})
    df.columns = column_names
    
    #calculate nearest neighbour distances
    centers = df.reset_index()[['center_x', 'center_y']].values.tolist()
    X = np.array(centers)
    nbrs = NearestNeighbors(n_neighbors=2).fit(X)
    distances, indices = nbrs.kneighbors(X)
    
    #add distances to df
    df['distance_to_NN'] = distances[:,1]
    
    #add neigbour index
    df['index_of_NN'] = indices[:,1]
    
    
    #export csv
    df.to_csv(saveName)

print('Finished')

