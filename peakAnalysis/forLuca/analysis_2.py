# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 11:08:11 2021

@author: g_dic
"""

import os
from os.path import expanduser
import numpy as np
from qtpy import QtGui, QtWidgets, QtCore
from time import time
from distutils.version import StrictVersion
import pyqtgraph as pg
import flika
from flika import global_vars as g
from flika.window import Window
from flika.utils.io import tifffile
from flika.images import image_path
from flika.process.file_ import open_file
from flika import roi

flika_version = flika.__version__
if StrictVersion(flika_version) < StrictVersion('0.2.23'):
    from flika.process.BaseProcess import BaseProcess, SliderLabel, CheckBox, ComboBox
else:
    from flika.utils.BaseProcess import BaseProcess, SliderLabel, CheckBox, ComboBox
    
from flika import *
import pandas as pd
from matplotlib import pyplot as plt

import threading
#from multiprocessing import Pool
from multiprocessing import freeze_support
from pathos.threading import ThreadPool
from pathos.pools import ProcessPool
from pathos.serial import SerialPool

import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter
    
# start flika
start_flika()

# import drift-corrected data
data_path = r"C:\Users\georgedickinson\Desktop\forLuca\LPS3_3nM_20ms\20210129_Cal1site_LPS3_7_3nM_20ms__driftCorrected.tif"
dataWin  = open_file(data_path)

# load hand-picked rois
roi_path = r"C:\Users\georgedickinson\Desktop\forLuca\LPS3_3nM_20ms\rois.txt"
rois = roi.open_rois(roi_path)

# get traces for each roi
traceList = []

for roi in rois:
    traceList.append(roi.getTrace())

# identify peaks, determine amplitudes, ON and OFF times for each roi trace
amplitudes_ALL = []
maxAmplitudes_ALL = []
ONtimes_ALL = []
OFFtimes_ALL = []
nPeaks_ALL = []

ONtimeList_forMike = []
OFFtimeList_forMike = []

#All ROIs
roisToExamine = range(len(traceList))
#testing
#roisToExamine = [0]

for traceIndex in roisToExamine:
    x = traceList[traceIndex]
        
    # find trace baseline
    from peakutils import baseline
    base = baseline(x)
    fig1 = plt.figure(1)
    plt.plot(x, c='r');plt.plot(base, c='b')
    fig1.show()
    
    # subtract baseline
    x = x - base
    
    # find points above noise threshold    
    #thresholdNoise = 150 #eyeballed from data
    
    #set threshold using stdev 
    thresholdNoise = x.std()*3
    
    
    indexes = np.argwhere(x > thresholdNoise )
    fig2 =  plt.figure(2)
    plt.plot(indexes, x[indexes], "xr"); plt.plot(x)
    fig2.show()
    
    # group consecutive points into seperate peaks  
    peakList =[]
    peakOnlyData = []
    amplitudeList = []
    maxAmplitudeList = []
    ONtimeList = []
    OFFtimeList = []

    peakNumber = 0    


    for k,g in groupby(enumerate(indexes),lambda x:x[0]-x[1]):
        group = (map(itemgetter(1),g))
        group = list(map(int,group))
        # store points above threshold only
        peakOnlyData.append((group[0],group[-1]))
        #expand indexes by 1 frames in each direction for duration
        start = group[0]-0 # TURNED OFF
        end = group[-1]+0 # TURNED OFF
        # store expanded peak
        peakList.append((start,end))
        # get ON times
        ONtimeList.append(end-start+1)
        # get mean amplitude of detected points
        amplitudeList.append(np.mean(x[group]))
        # get max amplitude
        maxAmplitudeList.append(np.max(x[group]))    
        
        # append ON times and index for Mike
        ONtimeList_forMike.append([traceIndex, peakNumber, end-start+1])
        
        peakNumber += 1
    
    
    # get OFF times
    OFFtimeList.append(peakList[0][0])
    for i in range(1,len(peakList)):
        OFFtimeList.append(peakList[i][0]-peakList[i-1][-1])
        #indexed
        OFFtimeList_forMike.append([traceIndex,i, peakList[i][0]-peakList[i-1][-1]])

    
    # plot peaks
    #fig3 = plt.figure(3)
    #plt.plot(x)
    
    #for peak in peakList: #use peakList to see expanded peaks
    #    x_vals = range(peak[0],peak[-1]+1)
    #    y_vals = x[x_vals]
    #    plt.plot(x_vals, y_vals)
    #    fig3.show()
    
    # plot histograms of amplitudes, ON times and OFF times
    #amp
    #fig4 = plt.figure(4)
    #plt.hist(amplitudeList)
    #plt.title('Amplitudes')
    #plt.xlabel('amplitude')
    #plt.ylabel('number observed')
    
    #ON
    #fig5 = plt.figure(5)
    #plt.hist(ONtimeList)
    #plt.title('ON times')
    #plt.xlabel('ON time (frames)')
    #plt.ylabel('number observed')
    
    #ON
    #fig6 = plt.figure(6)
    #plt.hist(OFFtimeList)
    #plt.title('OFF times')
    #plt.xlabel('OFF time (frames)')
    #plt.ylabel('number observed')
    
    # roi stats
    amplitude_mean = np.mean(amplitudeList)
    amplitude_std = np.std(amplitudeList)
    maxAmplitude_mean = np.mean(maxAmplitudeList)
    maxAmplitude_std = np.std(maxAmplitudeList)    
    ONtime_mean = np.mean(ONtimeList)
    ONtime_std = np.std(ONtimeList)
    OFFtime_mean = np.mean(OFFtimeList)
    OFFtime_std = np.std(OFFtimeList)
    nPeaks = len(amplitudeList)
    
    
    # print out results
    print('----------')
    print('ROI: {} of {}'.format(traceIndex+1,len(traceList)))
    print('mean amplitude: {0:.2f} +/- {1:.2f} std'.format(amplitude_mean,amplitude_std))
    print('mean MAX amplitude: {0:.2f} +/- {1:.2f} std'.format(maxAmplitude_mean,maxAmplitude_std))    
    print('mean ON time: {0:.2f} +/- {1:.2f} std'.format(ONtime_mean,ONtime_std))
    print('mean OFF time: {0:.2f} +/- {1:.2f} std'.format(OFFtime_mean,OFFtime_std))
    print('number of peaks: {}'.format(nPeaks))    
    
    #add results to all roi lists
    amplitudes_ALL.extend(amplitudeList)
    maxAmplitudes_ALL.extend(maxAmplitudeList)
    ONtimes_ALL.extend(ONtimeList)
    OFFtimes_ALL.extend(OFFtimeList)
    nPeaks_ALL.extend([nPeaks])

print('----------') 
print('ROI analysis finished')


# experiment stats- all sites combined
amplitudes_ALL_mean = np.mean(np.array(amplitudes_ALL))
amplitudes_ALL_std = np.std(np.array(amplitudes_ALL))
maxAmplitudes_ALL_mean = np.mean(np.array(maxAmplitudes_ALL))
maxAmplitudes_ALL_std = np.std(np.array(maxAmplitudes_ALL))
ONtimes_ALL_mean = np.mean(np.array(ONtimes_ALL))
ONtimes_ALL_std = np.std(np.array(ONtimes_ALL))
OFFtimes_ALL_mean = np.mean(np.array(OFFtimes_ALL))
OFFtimes_ALL_std = np.std(np.array(OFFtimes_ALL))
nPeaks_ALL_mean = np.mean(np.array(nPeaks_ALL))
nPeaks_ALL_std = np.std(np.array(nPeaks_ALL))

ONtimes_ALL_median = np.median(np.array(ONtimes_ALL))
OFFtimes_ALL_median = np.median(np.array(OFFtimes_ALL))

# print out results
print('----------')
print('All results combined')
print('mean amplitude: {0:.2f} +/- {1:.2f} std'.format(amplitudes_ALL_mean,amplitudes_ALL_std))
print('mean MAX amplitude: {0:.2f} +/- {1:.2f} std'.format(maxAmplitudes_ALL_mean,maxAmplitudes_ALL_std))
print('mean ON time: {0:.2f} +/- {1:.2f} std'.format(ONtimes_ALL_mean,ONtimes_ALL_std))
print('median ON times: {0:.2f} +/- {1:.2f} std'.format(ONtimes_ALL_median,ONtimes_ALL_std))
print('mean OFF time: {0:.2f} +/- {1:.2f} std'.format(OFFtimes_ALL_mean,OFFtimes_ALL_std))
print('median OFF times: {0:.2f} +/- {1:.2f} std'.format(OFFtimes_ALL_median,OFFtimes_ALL_std))
print('mean number of peaks: {0:.2f} +/- {0:.2f} std'.format(nPeaks_ALL_mean,nPeaks_ALL_std)) 
print('total number of peaks: {}'.format(len(amplitudes_ALL)))  
print('number of ROIs: {}'.format(len(traceList)))  

# plot histograms
#mean amp
ampHist = plt.figure(7)
plt.hist(amplitudes_ALL,50)
plt.title('Mean Amplitudes')
plt.xlabel('amplitude')
plt.ylabel('number observed')

#max amp
ampHist = plt.figure(8)
plt.hist(maxAmplitudes_ALL,50)
plt.title('Max Amplitudes')
plt.xlabel('amplitude')
plt.ylabel('number observed')

#ON
ONHist = plt.figure(9)
plt.hist(ONtimes_ALL,50)
plt.title('ON times')
plt.xlabel('ON time (frames)')
plt.ylabel('number observed')

#OFF
OFFHist = plt.figure(10)
plt.hist(OFFtimes_ALL,50)
plt.title('OFF times')
plt.xlabel('OFF time (frames)')
plt.ylabel('number observed')

#ON log
ONHist = plt.figure(9)
plt.hist(ONtimes_ALL,50)
plt.title('ON times')
plt.xlabel('ON time (frames)')
plt.ylabel('number observed')
plt.xscale('log')

#OFF log
OFFHist = plt.figure(10)
plt.hist(OFFtimes_ALL,100)
plt.title('OFF times')
plt.xlabel('OFF time (frames)')
plt.ylabel('number observed')
plt.xscale('log')


#export 
import pandas as pd
peakTable = pd.DataFrame(nPeaks_ALL)
ONtimeTable = pd.DataFrame(ONtimeList_forMike)
OFFtimeTable = pd.DataFrame(OFFtimeList_forMike)

savePath = data_path.split('.')[0]
peakTable.to_csv(savePath + '_peakTable.csv')
ONtimeTable.to_csv(savePath + '_ONtimeTable.csv')
OFFtimeTable.to_csv(savePath + '_OFFtimeTable.csv')








