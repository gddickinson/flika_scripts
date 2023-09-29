#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 17:33:14 2023

@author: george
"""

import warnings
warnings.simplefilter(action='ignore', category=Warning)

import numpy as np
import pandas as pd
from distutils.version import StrictVersion
from tqdm import tqdm
import os, glob, sys
import skimage.io as skio

import flika
from flika import global_vars as g
from flika.window import Window
from flika.process.file_ import save_file_gui, open_file_gui, open_file
from flika.roi import open_rois

flika_version = flika.__version__
if StrictVersion(flika_version) < StrictVersion('0.2.23'):
    from flika.process.BaseProcess import BaseProcess, WindowSelector, SliderLabel, CheckBox
else:
    from flika.utils.BaseProcess import BaseProcess, WindowSelector, SliderLabel, CheckBox

from flika import start_flika

def getIntensities(A, df):
    #intensities retrieved from image stack using point data (converted from floats to ints)

    n, w, h = A.shape

    #clear intensity list
    intensities = []

    for i in tqdm(range(len(df))):
        frame = round(df['frame'][i])
        x = round(df['x'][i])
        y = round(df['y'][i])

        #set x,y bounds for 3x3 pixel square
        xMin = x - 1
        xMax = x + 2

        yMin = y - 1
        yMax = y + 2

        #deal with edge cases
        if xMin < 0:
            xMin = 0
        if xMax > w:
            xMax = w

        if yMin <0:
            yMin = 0
        if yMax > h:
            yMax = h

        #get mean pixels values for 3x3 square
        intensities.append(np.mean(A[frame][yMin:yMax,xMin:xMax]))

    df['intensity'] = intensities

    return df

def addBgSubtractedIntensity(df, tiffFile, roi_1, cameraEstimate):
    newDF = getIntensities(tiffFile, df)

    #add background values for each frame
    for frame, value in enumerate(roi_1):
        newDF.loc[df['frame'] == frame, 'roi_1'] = value

    for frame, value in enumerate(cameraEstimate):
        newDF.loc[df['frame'] == frame, 'camera black estimate'] = value

    #add background subtracted intensity
    newDF['intensity - mean roi1'] = newDF['intensity'] - np.mean(newDF['roi_1'])
    newDF['intensity - mean roi1 and black'] = newDF['intensity'] - np.mean(newDF['roi_1']) - np.mean(newDF['camera black estimate'])
    return newDF

if __name__ == '__main__':

    path = '/Users/george/Desktop/testing_2'

    #add nn count
    fileList = glob.glob(path + '/**/*_NNcount.csv', recursive = True)

    for file in tqdm(fileList):

        tiffFile = os.path.splitext(file)[0].split('_locs')[0] + '.tif'
        roiFileName = 'ROI_' + os.path.basename(file).split('_locs')[0] + '.txt'
        roiFolder = os.path.dirname(file)
        roiFile = os.path.join(roiFolder,roiFileName)

        fa = start_flika()
        data_window = open_file(tiffFile)
        #get min values for each frame
        cameraEstimate = np.min(data_window.image, axis=(1,2))
        #load rois
        rois = open_rois(roiFile)
        #get trace for each roi
        roi_1 = rois[0].getTrace()

        fa.close()

        #load analysis df
        df = pd.read_csv(file)

        #load tiff
        A = skio.imread(tiffFile)

        #add bg subtracted analysis
        newDF = addBgSubtractedIntensity(df, A, roi_1, cameraEstimate)

        saveName = os.path.splitext(file)[0]+'_BGsubtract.csv'
        newDF.to_csv(saveName, index=None)
