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
path = r"/Users/gdickinson/Desktop/rois"

#get all filenames containing '.txt in folder
fileList = [f for f in glob.glob(path + "**/*.txt", recursive=True)]


#loop through files
for fileName in fileList:
    print('Analysing {}'.format(fileName))

    #file to load
    #fileName = r"/Users/gdickinson/Desktop/testROIs3.txt"
    
    #save path
    saveName= fileName.split('.')[0] + '.csv'
    
    
    #parse file for data
    ID = []
    points = []
    centers =[]
    data = []
    
    text = open(fileName, 'r').read()
    rois = []
    kind = None
    pts = None
    
    j = 0
    for text_line in text.split('\n'):
        if kind is None:
            kind = text_line
            pts = []
        elif text_line == '':
            ID.append(kind)
            points.append(pts)
            centers.append([pts[0][0]+(pts[1][0]/2),pts[0][1]+(pts[1][1]/2)])  
            data.append([pts[0][0]+(pts[1][0]/2),pts[0][1]+(pts[1][1]/2)])
            
            kind = None
            pts = None
            j += 1
        else:
            pts.append(tuple(int(float(i)) for i in text_line.split()))
    
    
    
    #load data into df
    column_names = {'center_x','center_y'}
    df = pd.DataFrame(data = data,  columns=column_names)
    
    #calculate nearest neighbour distances
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

