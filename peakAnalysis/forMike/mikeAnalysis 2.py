# -*- coding: utf-8 -*-
"""
Created on Thu May 30 11:01:24 2019

@author: GEORGEDICKINSON
"""

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import h5py
import os
import shutil
import pandasql as ps
from itertools import groupby
from operator import itemgetter
from tqdm import tqdm

#picasso hdf5 format (without averaging): ['frame', 'x', 'y', 'photons', 'sx', 'sy', 'bg', 'lpx', 'lpy']
#Column Name       |	Description                                                                                                                      |	C Data Type
#frame	            |The frame in which the localization occurred, starting with zero for the first frame.	                                                |unsigned long
#x                |The subpixel x coordinate in camera pixels	                                                                                          |float
#y	              |The subpixel y coordinate in camera pixels	                                                                                          |float
#photons	       |The total number of detected photons from this event, not including background or camera offset	                                      |float
#sx	             |The Point Spread Function width in camera pixels                                                                                       |	float
#sy	             |The Point Spread Function height in camera pixels                                                                                      |	float
#bg	             |The number of background photons per pixel, not including the camera offset                                                            |	float
#lpx	         |The localization precision in x direction, in camera pixels, as estimated by the Cramer-Rao Lower Bound of the Maximum Likelihood fit.  |	float
#lpy	         |The localization precision in y direction, in camera pixels, as estimated by the Cramer-Rao Lower Bound of the Maximum Likelihood fit.  |	float


#set filepath
filePath = r"C:\Users\g_dic\Documents\bsu\forMike\20190913_All-Matrices_syn2_pure_Triangles_300msExp_Mid-9nt-3nM_MgCl2_18mM_PCA_12mM_PCD_TROLOX_1mM_10_38_52_substack_fixed_locs_render_DRIFT_3_filter_Matrix_05.hdf5"

#savePath = filePath.split('.')[0] + '_filtered.hdf5'

#open picasso hdf5 file as DF
locs = pd.read_hdf(filePath, '/locs')
#check header
headers = locs.dtypes.index
#print(headers)
#print(locs.head(n=1))

#scatter plot
#locs.plot.scatter(x='x',y='y',s=1)

#get centroid positions used for grid
centroids = np.array([
        
           [255.65026699, 256.2699313 ],
           [255.65522196, 255.9542909 ],
           [255.65336587, 256.16112367],
           [255.66110178, 255.74295807],
           [255.74678208, 256.05605212],
           [255.74547016, 256.16300094],
           [255.75104081, 256.2720415 ],
           [255.75228561, 255.84415798],
           [255.75351785, 255.95273798],
           [255.75479689, 255.73969906],
           [255.84866381, 256.05934078],
           [255.84685329, 256.16708376],
           [255.85103522, 256.27369471],
           [255.85160587, 255.74273925],
           [255.85740968, 255.85026562],
           [255.94392418, 256.27673285],
           [255.94391768, 256.05966314],
           [255.94611554, 256.17014591],
           [255.95094813, 255.95014021],
           [255.95158306, 255.85177168],
           [255.95400055, 255.74037337],
           [256.03677785, 256.2720229 ],
           [256.03969133, 256.06114094],
           [256.04283514, 256.16603679],
           [256.04661846, 255.85896198],
           [256.04490558, 255.96022842],
           [256.05086907, 255.7461775 ],
           [256.14012688, 256.1753788 ],
           [256.14023585, 256.0697952 ],
           [256.140229  , 256.2836567 ],
           [256.14513271, 255.75414015],
           [256.14299781, 255.96175843],
           [256.2314431 , 256.17345542],
           [256.23032086, 256.28052939],
           [256.23801515, 256.06644361],
           [256.23637598, 255.96237802],
           [256.2397271 , 255.75018973],
           [256.23966435, 255.85825364],
           [256.32819487, 256.17121161],
           [256.33097833, 255.75340018],
           [256.32980017, 256.06243964],
           [256.32933863, 255.96060716],
           [256.33441629, 255.85686116],
           [256.144     , 255.865     ],
           [255.851     , 255.954     ],
           [255.652     , 256.057     ],
           [255.659     , 255.846     ],
           [256.327     , 256.281     ]]

)



remap={  33:2,
         29:3,
         21:4,
         15:5,
         12:6,
         6:7,
         0:8,
         38:9,
         32:10,
         27:11,
         23:12,
         17:13,
         11:14,
         5:15,
         2:16,
         40:17,
         34:18,
         28:19,
         22:20,
         16:21,
         10:22,
         4:23,
         41:25,
         35:26,
         31:27,
         25:28,
         18:29,
         44:30,
         8:31,
         1:32,
         42:33,
         37:34,
         43:35,
         24:36,
         19:37,
         14:38,
         7:39,
         39:41,
         36:42,
         30:43,
         26:44,
         20:45,
         13:46,
         9:47,
         3:48,
         47:1,
         45:24,
         46:40                                                                         
         }



#plot centroids
#plt.scatter(centroids[:,0],centroids[:,1],c='red')

#add site position to each localization
#filter locs by centroid positions using SQL
searchArea = 0.04 * 0.04
filteredLocs= pd.DataFrame()
centroidList = centroids.tolist()

print('filtering site localizations')
for i in tqdm(range(len(centroidList))):
    query = "SELECT * FROM locs WHERE (((locs.x - {})*(locs.x - {})) + ((locs.y - {})*(locs.y - {}))) <= ({})".format(centroidList[i][0], centroidList[i][0], centroidList[i][1], centroidList[i][1], searchArea)
    filtered = ps.sqldf(query,locals())
    filtered['bindingSite'] = i
    filteredLocs = filteredLocs.append(filtered)

#plot
#filteredLocs.plot.scatter(x='x',y='y',s=1)

#plot all binding sites against time
#all origami
#filteredLocs.plot.scatter(x='frame',y='photons',c='bindingSite',colormap='tab20b',s=0.5)

amplitudes = []
maxAmplitudes = []
ONtimes = []
OFFtimes = []
nPeaks = []

print('getting peak attributes')
# loop through all origami
for origamiIndex in tqdm(range(max(filteredLocs['group']))):
    #filter by origami group
    origamiDF = filteredLocs.loc[filteredLocs['group'] == origamiIndex]
    #plot
    #origamiDF.plot.scatter(x='frame',y='photons')
    
    # loop thorugh all binding sites
    for siteIndex in np.unique(origamiDF['bindingSite']):
        #filter by site position
        siteDF = origamiDF.loc[origamiDF['bindingSite'] == siteIndex]
        #siteDF.plot.scatter(x='frame',y='photons')
        
        #generate list of consecutive frames (peaks)
        indexes = siteDF['frame']
        consecutiveFrames = []
        for k,g in groupby(enumerate(indexes),lambda x:x[0]-x[1]):
            group = (map(itemgetter(1),g))
            group = list(map(int,group))
            consecutiveFrames.append(group)
        
        #append number of peaks seen at each site for each origami    
        nPeaks.append([origamiIndex, siteIndex, len(consecutiveFrames )])
        
        # calculate peak attributes and append to lists         
        # loop through peaks
        for i in range(len(consecutiveFrames)):
            peakDF = siteDF.loc[siteDF['frame'].isin(consecutiveFrames[i])]
            #append every peaks amplitude and ON time to lists, include origami and site index
            amplitudes.append([origamiIndex, siteIndex, np.mean(peakDF['photons'])])
            maxAmplitudes.append([origamiIndex, siteIndex, np.max(peakDF['photons'])])
            ONtimes.append([origamiIndex, siteIndex, len(peakDF['frame'])])
        
        # seperate loop to get OFF times
        OFFtimes.append([origamiIndex, siteIndex, consecutiveFrames[0][0]])
        for i in range(1,len(consecutiveFrames)):
            OFFtimes.append([origamiIndex, siteIndex, consecutiveFrames[i][0]-consecutiveFrames[i-1][-1]])

    
print('ROI analysis finished')


# experiment stats- all sites combined
amplitudes_ALL_mean = np.mean(np.array(amplitudes)[:,2])
amplitudes_ALL_std = np.std(np.array(amplitudes)[:,2])
maxAmplitudes_ALL_mean = np.mean(np.array(maxAmplitudes)[:,2])
maxAmplitudes_ALL_std = np.std(np.array(maxAmplitudes)[:,2])
ONtimes_ALL_mean = np.mean(np.array(ONtimes)[:,2])
ONtimes_ALL_std = np.std(np.array(ONtimes)[:,2])
OFFtimes_ALL_mean = np.mean(np.array(OFFtimes)[:,2])
OFFtimes_ALL_std = np.std(np.array(OFFtimes)[:,2])
nPeaks_ALL_mean = np.mean(np.array(nPeaks)[:,2])
nPeaks_ALL_std = np.std(np.array(nPeaks)[:,2])
ONtimes_ALL_median = np.median(np.array(ONtimes)[:,2])
OFFtimes_ALL_median = np.median(np.array(OFFtimes)[:,2])

# print out results
print('----------')
print('All results combined')
print('mean amplitude: {0:.2f} photons +/- {1:.2f} std'.format(amplitudes_ALL_mean,amplitudes_ALL_std))
print('mean MAX amplitude: {0:.2f} photons +/- {1:.2f} std'.format(maxAmplitudes_ALL_mean,maxAmplitudes_ALL_std))
print('mean ON time: {0:.2f} frames +/- {1:.2f} std'.format(ONtimes_ALL_mean,ONtimes_ALL_std))
print('median ON times: {0:.2f} frames +/- {1:.2f} std'.format(ONtimes_ALL_median,ONtimes_ALL_std))
print('mean OFF time: {0:.2f} frames +/- {1:.2f} std'.format(OFFtimes_ALL_mean,OFFtimes_ALL_std))
print('median OFF times: {0:.2f} frames +/- {1:.2f} std'.format(OFFtimes_ALL_median,OFFtimes_ALL_std))
print('mean number of peaks: {0:.2f} +/- {0:.2f} std'.format(nPeaks_ALL_mean,nPeaks_ALL_std)) 
print('total number of peaks: {}'.format(len(np.array(amplitudes)[:,2])))  
print('number of ROIs: {}'.format(max(filteredLocs['group'])))  

# plot histograms
#mean amp
ampHist = plt.figure(7)
plt.hist(np.array(amplitudes)[:,2],50)
plt.title('Mean Amplitudes')
plt.xlabel('amplitude')
plt.ylabel('number observed')

#max amp
ampHist = plt.figure(8)
plt.hist(np.array(maxAmplitudes)[:,2],50)
plt.title('Max Amplitudes')
plt.xlabel('amplitude')
plt.ylabel('number observed')

#ON
ONHist = plt.figure(9)
plt.hist(np.array(ONtimes)[:,2],50)
plt.title('ON times')
plt.xlabel('ON time (frames)')
plt.ylabel('number observed')

#OFF
OFFHist = plt.figure(10)
plt.hist(np.array(OFFtimes)[:,2],50)
plt.title('OFF times')
plt.xlabel('OFF time (frames)')
plt.ylabel('number observed')

#ON log
ONHist = plt.figure(9)
plt.hist(np.array(ONtimes)[:,2],50)
plt.title('ON times')
plt.xlabel('ON time (frames)')
plt.ylabel('number observed')
plt.xscale('log')

#OFF log
OFFHist = plt.figure(10)
plt.hist(np.array(OFFtimes)[:,2],100)
plt.title('OFF times')
plt.xlabel('OFF time (frames)')
plt.ylabel('number observed')
plt.xscale('log')


#export 
import pandas as pd
peakTable = pd.DataFrame(nPeaks)      # number of peaks at each site
ONtimeTable = pd.DataFrame(ONtimes)   # ON times for each peak, indexed by origami and site
OFFtimeTable = pd.DataFrame(OFFtimes) # OFF times for each peak, indexed by origami and site

savePath = filePath.split('.')[0]
peakTable.to_csv(savePath + '_peakTable.csv')
ONtimeTable.to_csv(savePath + '_ONtimeTable.csv')
OFFtimeTable.to_csv(savePath + '_OFFtimeTable.csv')
