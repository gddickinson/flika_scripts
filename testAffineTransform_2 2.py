import numpy as np
from os.path import expanduser, join
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from numpy import moveaxis
from skimage.transform import rescale
from pyqtgraph.dockarea import *
from pyqtgraph import mkPen
import flika
from flika import global_vars as g
from flika.window import Window
from flika.utils.io import tifffile
from flika.process.file_ import get_permutation_tuple
from flika.utils.misc import open_file_gui
import pyqtgraph as pg
import time
import os
from os import listdir
from os.path import expanduser, isfile, join
from distutils.version import StrictVersion
from copy import deepcopy
from flika import *
from flika.process.file_ import *
from flika.process.filters import *
from flika.window import *
flika_version = flika.__version__
if StrictVersion(flika_version) < StrictVersion('0.2.23'):
    from flika.process.BaseProcess import BaseProcess, SliderLabel, CheckBox, ComboBox
else:
    from flika.utils.BaseProcess import BaseProcess, SliderLabel, CheckBox, ComboBox

import copy

start_flika()


def get_transformation_matrix(theta=45):
    """
    theta is the angle of the light sheet
    Look at the pdf in this folder.
    """

    theta = theta/360 * 2 * np.pi # in radians
    hx = np.cos(theta)
    sy = np.sin(theta)
 
    S = np.array([[1, hx, 0],
                  [0, sy, 0],
                  [0, 0, 1]])

    return S


def transform(A):
    B = np.dot(A ,get_transformation_matrix())
    return B
    

theta = 45


filePath = join(expanduser("~/Desktop"),'array_4D_data_roundCell.npy')

data = np.load(filePath)

tData = copy.deepcopy(data)

data = data[:,0,:,:]
shape = data.shape

slice2 = int(shape[1]/2)

testImage = data[:,slice2]

Window(testImage, 'original')

tImage = transform(testImage)

Window(tImage, 'transform')








