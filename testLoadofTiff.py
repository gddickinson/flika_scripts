# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 18:12:43 2018

@author: George
"""

import time
import os.path
import sys
import numpy as np
import shutil, subprocess
import datetime
import json
import re
import pathlib

import tifffile

def get_permutation_tuple(src, dst):
    """get_permtation_tuple(src, dst)

    Parameters:
        src (list): The original ordering of the axes in the tiff.
        dst (list): The desired ordering of the axes in the tiff.

    Returns:
        result (tuple): The required permutation so the axes are ordered as desired.
    """
    result = []
    for i in dst:
        result.append(src.index(i))
    result = tuple(result)
    return result

filename = r"C:\Users\George\Dropbox\UCI\lightsheet sweep volume loading problem\three_sweep_1_MMStack_Pos0.ome.tif"

Tiff = tifffile.TiffFile(str(filename))
#metadata = get_metadata_tiff(Tiff)
A = Tiff.asarray()
Tiff.close()
axes = [tifffile.AXES_LABELS[ax] for ax in Tiff.series[0].axes]
target_axes = ['time', 'depth', 'width', 'height']
perm = get_permutation_tuple(axes, target_axes)
A = np.transpose(A, perm)

nScans, nFrames, x, y = A.shape

interleaved = np.zeros((nScans*nFrames,x,y))

z = 0
for i in np.arange(nFrames):
    for j in np.arange(nScans):
        interleaved[z] = A[j%nScans][i] 
        z = z +1




