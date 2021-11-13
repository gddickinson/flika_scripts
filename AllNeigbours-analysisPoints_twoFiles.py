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

print('All-Neighbours analysis for {} and {}'.format(fileName1,fileName2))

#save path
saveName= fileName1.split('.')[0] + '_All-Neighbour-result.csv'

    
#load data into df1
column_names = ['frame','center_x','center_y']
df1 = pd.read_csv(fileName1,delimiter=' ',header=None,dtype={0:int,1:float,2:float})
df1.columns = column_names

#load data into df2
df2 = pd.read_csv(fileName2,delimiter=' ',header=None,dtype={0:int,1:float,2:float})
df2.columns = column_names

#create empty DF for results
column_names2 = ['testData_index', 'trainData_index', 'distance']
resultDF = pd.DataFrame(columns=column_names2)

#funciton for NN
def getAllNeighbors(train,test,k=1):
    tree = KDTree(train, leaf_size=5)   
    dist, ind = tree.query(test, k=k)
    #dist.reshape(np.size(dist),)     
    return dist, ind

#select columns
testData_df = df1[['center_x','center_y']]
trainData_df = df2[['center_x','center_y']]

#all neighbour
distances, trainData_indices = getAllNeighbors(trainData_df.to_numpy(),testData_df.to_numpy(), k=len(trainData_df.to_numpy()))

#add distances to df
for i in range(len(distances)):
    for j in range(len (distances[i])):
        resultDF = resultDF.append({'testData_index': i, 'trainData_index': trainData_indices[i][j] , 'distance': distances[i][j]}, ignore_index=True)


#save results table as csv
resultDF.to_csv(saveName)

print('Result file saved to {}'.format(saveName))

