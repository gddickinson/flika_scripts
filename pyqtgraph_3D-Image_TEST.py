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
        
        
app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 200
w.show()
w.setWindowTitle('3D slice - texture plot')

filePath = join(expanduser("~/Desktop"),'array_4D_data.npy')

data = np.load(filePath)
data = data[:,10,:,:]
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

