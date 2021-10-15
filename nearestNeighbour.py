# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 13:21:23 2021

@author: g_dic
"""

import pandas as pd
from sklearn.neighbors import KDTree
import numpy as np

#file to load
#fileName = r"C:\Users\g_dic\Dropbox\_forIan\SIM data.csv"
fileName = "/Users/gdickinson/Dropbox/_forIan/SIM data.csv"

#save path
saveName = fileName.split('.')[0] + '_NN-Result.csv'

#load data into df
df = pd.read_csv(fileName)

#funciton for NN
def getNearestNeighbors(train,test,k=1):
    tree = KDTree(train, leaf_size=5)   
    dist, ind = tree.query(test, k=k)
    #dist.reshape(np.size(dist),)     
    return dist, ind

#select columns
testData_df = df[['CenterPx2X[px]','CenterPx2Y[px]','CenterPx2Z[px]']]
trainData_df = df[['CenterPxX[px]','CenterPxY[px]','CenterPxZ[px]']]

#drop nan
trainData_df = trainData_df.dropna()

#nearest neighbour
distances, trainData_indexes = getNearestNeighbors(trainData_df.to_numpy(),testData_df.to_numpy())

#results table
#test data
test_df = df[['Entity','ObjectId3D','CenterPx2X[px]','CenterPx2Y[px]','CenterPx2Z[px]']]
#nearest neigbours
NN_df = df[['Entity.1', 'ObjectId3D.1', 'CenterPxX[px]','CenterPxY[px]', 'CenterPxZ[px]']]
NN_df = NN_df.iloc[trainData_indexes.flatten(), :]
#combine
results_df = pd.concat([test_df.reset_index(),NN_df.reset_index()],axis=1)
#add distances
results_df['distance'] = distances

#save results table as csv
results_df.to_csv(saveName)
