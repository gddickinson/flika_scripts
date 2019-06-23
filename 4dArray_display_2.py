import numpy as np
from os.path import expanduser, join
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from numpy import moveaxis
from skimage.transform import rescale
from pyqtgraph.dockarea import *
from pyqtgraph import mkPen

#filePath = join(expanduser("~/Desktop"),'array_4D_data_bead.npy')
filePath = join(expanduser("~/Desktop"),'array_4D_data.npy')

originalData = np.load(filePath)
dataShape = originalData.shape
height = dataShape[3]
width = dataShape[2]
nVols = dataShape[1]
nSteps = dataShape[0]
print(dataShape)

###################################################

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


def get_transformation_coordinates(I, theta):
    negative_new_max = False
    S = get_transformation_matrix(theta)
    S_inv = np.linalg.inv(S)
    mx, my = I.shape

    four_corners = np.matmul(S, np.array([[0, 0, mx, mx],
                                          [0, my, 0, my],
                                          [1, 1, 1, 1]]))[:-1,:]
    range_x = np.round(np.array([np.min(four_corners[0]), np.max(four_corners[0])])).astype(np.int)
    range_y = np.round(np.array([np.min(four_corners[1]), np.max(four_corners[1])])).astype(np.int)
    all_new_coords = np.meshgrid(np.arange(range_x[0], range_x[1]), np.arange(range_y[0], range_y[1]))
    new_coords = [all_new_coords[0].flatten(), all_new_coords[1].flatten()]
    new_homog_coords = np.stack([new_coords[0], new_coords[1], np.ones(len(new_coords[0]))])
    old_coords = np.matmul(S_inv, new_homog_coords)
    old_coords = old_coords[:-1, :]
    old_coords = old_coords
    old_coords[0, old_coords[0, :] >= mx-1] = -1
    old_coords[1, old_coords[1, :] >= my-1] = -1
    old_coords[0, old_coords[0, :] < 1] = -1
    old_coords[1, old_coords[1, :] < 1] = -1
    new_coords[0] -= np.min(new_coords[0])
    keep_coords = np.logical_not(np.logical_or(old_coords[0] == -1, old_coords[1] == -1))
    new_coords = [new_coords[0][keep_coords], new_coords[1][keep_coords]]
    old_coords = [old_coords[0][keep_coords], old_coords[1][keep_coords]]
    return old_coords, new_coords


def perform_shear_transform(A, shift_factor, interpolate, datatype, theta):
    A = moveaxis(A, [1, 3, 2, 0], [0, 1, 2, 3])
    m1, m2, m3, m4 = A.shape
    if interpolate:
        A_rescaled = np.zeros((m1*int(shift_factor), m2, m3, m4))
        for v in np.arange(m4):
            print('Upsampling Volume #{}/{}'.format(v+1, m4))
            A_rescaled[:, :, :, v] = rescale(A[:, :, :, v], (shift_factor, 1.), mode='constant', preserve_range=True)
    else:
        A_rescaled = np.repeat(A, shift_factor, axis=0)
    mx, my, mz, mt = A_rescaled.shape
    I = A_rescaled[:, :, 0, 0]
    old_coords, new_coords = get_transformation_coordinates(I, theta)
    old_coords = np.round(old_coords).astype(np.int)
    new_mx, new_my = np.max(new_coords[0]) + 1, np.max(new_coords[1]) + 1
    # I_transformed = np.zeros((new_mx, new_my))
    # I_transformed[new_coords[0], new_coords[1]] = I[old_coords[0], old_coords[1]]
    # Window(I_transformed)
    D = np.zeros((new_mx, new_my, mz, mt))
    D[new_coords[0], new_coords[1], :, :] = A_rescaled[old_coords[0], old_coords[1], :, :]
    E = moveaxis(D, [0, 1, 2, 3], [3, 1, 2, 0])
    E = np.flip(E, 1)
    #Window(E[0, :, :, :])
    E = E.astype(datatype)
    return E


shift_factor = 3
interpolate = False
theta = 45
    
#originalData= perform_shear_transform(originalData, shift_factor, interpolate, originalData.dtype, theta)

data = originalData[:,0,:,:]

#################### GUI #####################################

#define app
app = QtGui.QApplication([])

## Create window with 4 docks
win = QtGui.QMainWindow()
win.resize(1000,800)
win.setWindowTitle('Lightsheet 3D display')

#create Dock area
area = DockArea()
win.setCentralWidget(area)

#define docks
d1 = Dock("Top View", size=(500,400))
d2 = Dock("X slice", size=(500,400), closable=True)
d3 = Dock("Y Slice", size=(500,400), closable=True)
d4 = Dock("Free ROI", size=(500,400), closable=True)
d5 = Dock("Time Slider", size=(1000,50))

#add docks to area
area.addDock(d1, 'left')        ## place d1 at left edge of dock area 
area.addDock(d2, 'right')       ## place d2 at right edge of dock area
area.addDock(d3, 'bottom', d1)  ## place d3 at bottom edge of d1
area.addDock(d4, 'bottom', d2)  ## place d4 at bottom edge of d2
area.addDock(d5, 'bottom')  ## place d4 at bottom edge of d2

#initialise image widgets
imv1 = pg.ImageView()
imv2 = pg.ImageView()
imv3 = pg.ImageView()
imv4 = pg.ImageView()

imageWidgits = [imv1,imv2,imv3,imv4]

#add image widgets to docks
d1.addWidget(imv1)
d2.addWidget(imv3)
d3.addWidget(imv2)
d4.addWidget(imv4)

#hide dock title-bars
d5.hideTitleBar()

def hide_titles():
    d1.hideTitleBar()
    d2.hideTitleBar()
    d3.hideTitleBar()
    d4.hideTitleBar()

def show_titles():
    d1.showTitleBar()
    d2.showTitleBar()
    d3.showTitleBar()
    d4.showTitleBar()

hide_titles()

#add menu functions
state = area.saveState()

def reset_layout():
    global state
    area.restoreState(state)

menubar = win.menuBar()

fileMenu1 = menubar.addMenu('&Options')
resetLayout = QtGui.QAction(QtGui.QIcon('open.png'), 'Reset Layout')
resetLayout.setShortcut('Ctrl+R')
resetLayout.setStatusTip('Reset Layout')
resetLayout.triggered.connect(reset_layout)
fileMenu1.addAction(resetLayout)

showTitles = QtGui.QAction(QtGui.QIcon('open.png'), 'Show Titles')
showTitles.setShortcut('Ctrl+G')
showTitles.setStatusTip('Show Titles')
showTitles.triggered.connect(show_titles)
fileMenu1.addAction(showTitles)

hideTitles = QtGui.QAction(QtGui.QIcon('open.png'), 'Hide Titles')
hideTitles.setShortcut('Ctrl+H')
hideTitles.setStatusTip('Hide Titles')
hideTitles.triggered.connect(hide_titles)
fileMenu1.addAction(hideTitles)

#add time slider
slider1 = QtGui.QSlider(QtCore.Qt.Horizontal)
slider1.setFocusPolicy(QtCore.Qt.StrongFocus)
slider1.setTickPosition(QtGui.QSlider.TicksBothSides)
slider1.setMinimum(0)
slider1.setMaximum(nVols)
slider1.setTickInterval(1)
slider1.setSingleStep(1)

d5.addWidget(slider1)


#display window
win.show()

#define single line roi
roi1 = pg.LineSegmentROI([[10, 64], [120,64]], pen='r')
imv1.addItem(roi1)

#define crosshair rois
roi2 = pg.LineSegmentROI([[0, 0], [width, 0]], pen='y', maxBounds=QtCore.QRect(0,0,0,height))
imv1.addItem(roi2)

roi3 = pg.LineSegmentROI([[0, 0], [0, height]], pen='y', maxBounds=QtCore.QRect(0,0,width,0))
imv1.addItem(roi3)

#define update calls for each roi
def update():
    global data, imv1, imv4
    d1 = roi1.getArrayRegion(data, imv1.imageItem, axes=(1,2))
    imv4.setImage(d1,autoLevels=False)

def update_2():
    global data, imv1, imv2
    d2 = np.rot90(roi2.getArrayRegion(data, imv1.imageItem, axes=(1,2)), axes=(1,0))
    imv2.setImage(d2,autoLevels=False)
    
def update_3():
    global data, imv1, imv3
    d3 = roi3.getArrayRegion(data, imv1.imageItem, axes=(1,2))
    imv3.setImage(d3,autoLevels=False)

#hide default imageview buttons
def hideButtons(imv):    
    imv.ui.roiBtn.hide()
    imv.ui.menuBtn.hide()

for imv in imageWidgits:
    hideButtons(imv)

#disconnect roi handles
def disconnectHandles(roi):
    handles = roi.getHandles()
    handles[0].disconnectROI(roi)
    handles[1].disconnectROI(roi)
    handles[0].currentPen = mkPen(None)
    handles[1].currentPen = mkPen(None) 
    handles[0].pen = mkPen(None)
    handles[1].pen = mkPen(None)     
    
disconnectHandles(roi2)
disconnectHandles(roi3)
 
#add data to main window
imv1.setImage(np.mean(data, axis=0)) #display topview (mean of slices)

#connect roi updates
roi1.sigRegionChanged.connect(update)
roi2.sigRegionChanged.connect(update_2)
roi3.sigRegionChanged.connect(update_3)

#initial update to populate roi windows
update()
update_2()
update_3()

#autolevel roi windows at start
imv2.autoLevels()
imv3.autoLevels()
imv4.autoLevels()

#connect time slider
def timeUpdate(value):
    global data
    data = originalData[:,value,:,:]
    imv1.setImage(np.mean(data, axis=0))
    update()
    update_2()
    update_3()
    return
 
slider1.valueChanged.connect(timeUpdate)