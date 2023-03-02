#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 16:11:58 2022

@author: george
"""

###Creates macro to run thunderStorm for a batch of iles in ImageJ - works for >1 file

####TODO! run macro directly using python
#pip install pyimagej
#need to install maven and set PATH (export PATH=/Users/george/opt/apache-maven-3.8.6/bin:$PATH)

import glob
import os


def getFileList(path):
    #get folder paths
    #files = glob.glob(path + '/**/*_bin10.tif', recursive = True)   
    #files = glob.glob(path + '/**/*_crop100.tif', recursive = True)      # use for cropped files
    files = glob.glob(path + '/**/*.tif', recursive = True) 
    
    fileStr = str(files).replace('[', '')
    fileStr = fileStr.replace(']', '')    
    resStr = fileStr.replace('.tif', '_locs.csv')
    return fileStr, resStr

macroCommand = """for (i=0; i  < datapaths.length; i++) {
	//open(datapaths[i]);
	run("Bio-Formats Importer", "open=" + datapaths[i] +" color_mode=Default rois_import=[ROI manager] split_channels view=Hyperstack stack_order=XYCZT");
	run("Run analysis", "filter=[Wavelet filter (B-Spline)] scale=2.0 order=3 detector=[Local maximum] connectivity=4-neighbourhood threshold=std(Wave.F1) estimator=[PSF: Integrated Gaussian] sigma=1.6 fitradius=3 method=[Weighted Least squares] full_image_fitting=false mfaenabled=false renderer=[Averaged shifted histograms] magnification=5.0 colorizez=false threed=false shifts=2 repaint=50");
	run("Export results", "filepath=["+respaths[i]+"] fileformat=[CSV (comma separated)] sigma=true intensity=true chi2=true offset=true saveprotocol=true x=true y=true bkgstd=true id=true uncertainty=true frame=true");
	//close();
    while (nImages>0) { 
        selectImage(nImages); 
        close(); 
    } 
}"""

def writeMacro(datapaths,respaths,macroCommand,savepath):
    
    stringtowrite = "{}\n{}\n{}".format(datapaths,respaths,macroCommand)
    
    f = open(savepath, "w")
    f.write(stringtowrite)
    f.close()
    return
        
    

if __name__ == '__main__':
    #set top folder level for analysis
    path = '/Users/george/Data/BAPTA/gapSize_10frames'
    
    savepath = os.path.join(path,'thunderStorm_macro_auto.ijm')

    dataPathStr,resPathStr  = getFileList(path)
        
    datapaths = 'datapaths = newArray({});'.format(dataPathStr)
    respaths = 'respaths = newArray({});'.format(resPathStr)    
    
    writeMacro(datapaths, respaths, macroCommand, savepath)
    
    