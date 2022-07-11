#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 13:34:38 2021

@author: gdickinson
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree


#select file2
fileName1 = r"/Users/george/Desktop/points/testPoints.txt"
fileName2 = r"/Users/george/Desktop/points/testPoints2.txt"

print('NN analysis for {} and {}'.format(fileName1,fileName2))

#save path
saveName= fileName1.split('.')[0] + '_NN-result.csv'

    
#load data into df1
column_names = ['frame','center_x','center_y']
df1 = pd.read_csv(fileName1,delimiter=' ',header=None,dtype={0:int,1:float,2:float})
df1.columns = column_names

#load data into df2
column_names = ['frame','center_x','center_y']
df2 = pd.read_csv(fileName2,delimiter=' ',header=None,dtype={0:int,1:float,2:float})
df2.columns = column_names

#funciton for NN
def getNearestNeighbors(train,test,k=1):
    tree = KDTree(train, leaf_size=5)   
    dist, ind = tree.query(test, k=k)
    #dist.reshape(np.size(dist),)     
    return dist, ind

#select columns
testData_df = df1[['center_x','center_y']]
trainData_df = df2[['center_x','center_y']]

#nearest neighbour
distances, trainData_indices = getNearestNeighbors(trainData_df.to_numpy(),testData_df.to_numpy())

#add distances to df
df1['distance_to_NN'] = distances

#add neigbour index
df1['index_of_NN'] = trainData_indices

df1['comparison file'] = fileName2

#save results table as csv
df1.to_csv(saveName)

print('Result file saved to {}'.format(saveName))

