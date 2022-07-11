# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 17:51:19 2019

@author: George
"""

# -*- coding: utf-8 -*-
"""
Use GLImageItem to display image data on rectangular planes.

In this example, the image data is sampled from a volume and the image planes 
placed as if they slice through the volume.
"""
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
from OpenGL.GL import *
import pyqtgraph as pg
import numpy as np
from os.path import expanduser, join
from numpy import moveaxis
import copy
from skimage.transform import rescale

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
    #A = moveaxis(A, [1, 3, 2, 0], [0, 1, 2, 3])
    #A = moveaxis(A, [2, 3, 0, 1], [0, 1, 2, 3])
    A = moveaxis(A, [0, 3, 1, 2], [0, 1, 2, 3]) 
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

    D = np.zeros((new_mx, new_my, mz, mt))
    D[new_coords[0], new_coords[1], :, :] = A_rescaled[old_coords[0], old_coords[1], :, :]
    #E = moveaxis(D, [0, 1, 2, 3], [3, 1, 2, 0])
    #E = moveaxis(D, [0, 1, 2, 3], [2, 3, 0, 1])
    E = moveaxis(D, [0, 1, 2, 3], [0, 3, 1, 2])  
    E = np.flip(E, 1)

    return E


class GLBorderItem(gl.GLAxisItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem>`
    Overwrite of GLAxisItem 
    Displays borders of plot data 
    
    """
    
    def setSize(self, x=None, y=None, z=None, size=None):
        """
        Set the size of the axes (in its local coordinate system; this does not affect the transform)
        Arguments can be x,y,z or size=QVector3D().
        """
        if size is not None:
            x = size.x()
            y = size.y()
            z = size.z()
        self.__size = [x,y,z]
        self.update()

        
    def size(self):
        return self.__size[:]

    
# =============================================================================
#     def paint(self):
# 
#         #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#         #glEnable( GL_BLEND )
#         #glEnable( GL_ALPHA_TEST )
#         self.setupGLState()
#         
#         if self.antialias:
#             glEnable(GL_LINE_SMOOTH)
#             glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
#             
#         glBegin( GL_LINES )
#         
#         x,y,z = self.size()
#         glColor4f(0, 1, 0, .6)  # z is green
#         glVertex3f(0, 0, 0)
#         glVertex3f(0, 0, z)
# 
#         glColor4f(1, 1, 0, .6)  # y is yellow
#         glVertex3f(0, 0, 0)
#         glVertex3f(0, y, 0)
# 
#         glColor4f(0, 0, 1, .6)  # x is blue
#         glVertex3f(0, 0, 0)
#         glVertex3f(x, 0, 0)
#         glEnd()
# =============================================================================
        
    def paint(self):

        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glEnable( GL_BLEND )
        #glEnable( GL_ALPHA_TEST )
        self.setupGLState()
        
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            
        glBegin( GL_LINES )
        
        x,y,z = self.size()       

        def zFrame(x,y,z,r=1,g=1,b=1,thickness=0.6):
            glColor4f(r, g, b, thickness)  # z 
            glVertex3f(-(int(x)), -(int(y/2)), -(int(z/2)))
            glVertex3f(-(int(x)), -(int(y/2)), z-(int(z/2)))
            
            glColor4f(r, g, b, thickness)  # z 
            glVertex3f(-(int(x)), y -(int(y/2)), -(int(z/2)))
            glVertex3f(-(int(x)), y -(int(y/2)), z-(int(z/2)))        
    
            glColor4f(r, g, b, thickness)  # y 
            glVertex3f(-(int(x)), -(int(y/2)), -(int(z/2)))
            glVertex3f(-(int(x)), y -(int(y/2)), -(int(z/2)))
            
            glColor4f(r, g, b, thickness)  # y 
            glVertex3f(-(int(x)), -(int(y/2)), z-(int(z/2)))
            glVertex3f(-(int(x)), y -(int(y/2)), z-(int(z/2))) 

        
        def xFrame(x,y,z,r=1,g=1,b=1,thickness=0.6):
            glColor4f(r, g, b, thickness)  # x is blue
            glVertex3f(x-(int(x/2)), -(int(y)), -(int(z/2)))
            glVertex3f((int(x/2))-x, -(int(y)), -(int(z/2)))
    
            glColor4f(r, g, b, thickness)  # x is blue
            glVertex3f(x-(int(x/2)), -(int(y)), z-(int(z/2)))
            glVertex3f((int(x/2))-x, -(int(y)), z-(int(z/2)))        
            
            glColor4f(r, g, b, thickness)  # z 
            glVertex3f(x-(int(x/2)), -(int(y)), -(int(z/2)))
            glVertex3f(x-(int(x/2)), -(int(y)), z-(int(z/2)))
            
            glColor4f(r, g, b, thickness)  # z 
            glVertex3f((int(x/2))-x, -(int(y)), -(int(z/2)))
            glVertex3f((int(x/2))-x, -(int(y)), z-(int(z/2))) 
            

        def box(x,y,z,r=1,g=1,b=1,thickness=0.6):        
            zFrame(x/2,y,z,r=r,g=g,b=b,thickness=thickness)
            zFrame(x/2-x,y,z,r=r,g=g,b=b,thickness=thickness)        
            xFrame(x,y/2,z,r=r,g=g,b=b,thickness=thickness)
            xFrame(x,-y/2,z,r=r,g=g,b=b,thickness=thickness)        
       

        box(x,y,z)
        
        glEnd()
        
##############################################################################        
shift_factor = 1
interpolate = False
theta = 45       
        
app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 200
w.show()
w.setWindowTitle('3D slice - texture plot')

filePath = join(expanduser("~/Desktop"),'array_4D_data_roundCell.npy')

data = np.load(filePath)

#tData = copy.deepcopy(data)
transform = perform_shear_transform(data, shift_factor, interpolate, data.dtype, theta)
#transform = data
data = transform[:,0,:,:]
#tShape = tData.shape

#data = data[:,0,:,:]
shape = data.shape


## slice out three planes, convert to RGBA for OpenGL texture
levels = (0, 1000)

slice1 = int(shape[0]/2)
slice2 = int(shape[1]/2)
slice3 = int(shape[2]/2)

tex1 = pg.makeRGBA(data[slice1], levels=levels)[0]       # yz plane
tex2 = pg.makeRGBA(data[:,slice2], levels=levels)[0]     # xz plane
tex3 = pg.makeRGBA(data[:,:,slice3], levels=levels)[0]   # xy plane


## Create three image items from textures, add to view
v1 = gl.GLImageItem(tex1)
v1.translate(-slice2, -slice3, 0)
v1.rotate(90, 0,0,1)
v1.rotate(-90, 0,1,0)
w.addItem(v1)

v2 = gl.GLImageItem(tex2)
v2.translate(-slice1, -slice3, 0)
v2.rotate(-90, 1,0,0)
w.addItem(v2)

v3 = gl.GLImageItem(tex3)
v3.translate(-slice1, -slice2, 0)
w.addItem(v3)

#ax = gl.GLAxisItem()
ax = GLBorderItem()
ax.setSize(x=shape[0],y=shape[1],z=shape[2])
w.addItem(ax)

