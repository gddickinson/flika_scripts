#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 12:14:01 2022

@author: george
"""
import numpy as np
import pandas as pd


def filterDFbyXYZ(locs, x, y, frame):
    row = (locs['x [nm]'] == x) & (locs['y [nm]'] == y) & (locs['frame'] == frame) 
    return locs['id'][row]

def getID(df, locs):
    df['id'] = df.apply(lambda row : filterDFbyXYZ(locs, row['x [nm]'], row['y [nm]'], row['frame']),axis=1)
    return df


locsFile = '/Users/george/Data/10msExposure2s_test/wt/GB_165_2022_03_01_HTEndothelial_NonBapta_plate1_1_MMStack_Default_bin10_crop20_locsID.csv'
tracksFile = '/Users/george/Data/10msExposure2s_test/wt/GB_165_2022_03_01_HTEndothelial_NonBapta_plate1_1_MMStack_Default_bin10_crop20_locsID_tracks.csv'

locs = pd.read_csv(locsFile)
df = pd.read_csv(tracksFile)

newDF = getID(df, locs)



