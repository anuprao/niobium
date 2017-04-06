#!/usr/bin/python
import math
import os

import numpy
from freetype import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame, pygame.image
from pygame.locals import *

#########################################################

bUpdate = False

bCTRLpressed = False

#########################################################

class dragdropmanager:
	
	onlyInstance = None
	
	def __init__(self):
		self.isEmpty = True
		self.dropSrc = None
		self.dropObj = None
		
	@staticmethod
	def getInstance():
		if None == dragdropmanager.onlyInstance:
			dragdropmanager.onlyInstance = dragdropmanager()
		return dragdropmanager.onlyInstance
		
	def attachObject(self, dropSrc, dropObj):
		
		dropObj.show(False)
		
		self.dropSrc = dropSrc
		self.dropObj = dropObj
		self.isEmpty = False
		
		enableMouseMotion()
	
	def clearOnDrop(self):
		self.isEmpty = True
		self.dropSrc = None
		self.dropObj = None
		
		disableMouseMotion()
		
	def setPosForDrop(self, lx, ly):
		self.dropObj.setPosForDrop(lx-self.dropObj.dragpad_OffX, ly-self.dropObj.dragpad_OffY)
	
class draggable:
	def __init__(self, parent):
		self.bDragging = False
		
		self.m_dropx = 0
		self.m_dropy = 0
		
		self.draglocal_OffX = 0
		self.draglocal_OffY = 0
		
	def isUnderDrag(self):
		return self.bDragging
		
	def setDropLocation(self, mx, my):		
		self.m_dropx = mx - self.draglocal_OffX 
		self.m_dropy = my - self.draglocal_OffY 
		
	def startDrag(self, mx, my):		
		print "drag mode on"
		
		self.bDragging = True
		self.draglocal_OffX, self.draglocal_OffY = mx, my	
		self.setDropLocation(mx, my)
		
	def stopDrag(self):
		print "drag mode off"
		
		bReturn = False
		
		self.m_dropx = 0
		self.m_dropy = 0
		
		self.bDragging = False
		
		if 0 != self.m_dropx or 0 != self.m_dropy:
		
			bReturn = True	
		
		return bReturn

class selection:
	def __init__(self, parent):
		self.parent = parent
		
		self.clear()
		
	def clear(self):
		self.arrItems = []
		
	def isEmpty(self):
		bReturn = True
		if 0 < len(self.arrItems):
			bReturn = False
		return bReturn
		
	def addItem(self, item):
		self.arrItems.append(item)
		
	def containsPoint(self, lx, ly):
		bReturn = False
		
		for item in self.arrItems:
			#print "testing", item.name
			#print lx, ly
			#print item.m_x, item.m_y
			#print item.m_x + item.m_w , item.m_y + item.m_h
			if (lx >= item.m_x) and (lx <= item.m_x + item.m_w ) and (ly >= item.m_y) and (ly <= item.m_y + item.m_h) :
				bReturn = bReturn or True
		
		return bReturn
		
	def setDropLocation(self, mx, my):
		for item in self.arrItems:
			item.setDropLocation(mx, my)
		
	def startDrag(self, mx, my):
		for item in self.arrItems:		
			item.startDrag(mx, my)
		
		enableMouseMotion()
		
	def stopDrag(self):		
		bReturn = False
		
		for item in self.arrItems:		
			bReturn = bReturn or item.stopDrag()
			
		disableMouseMotion()
		
		return bReturn
		
	def isUnderDrag(self):
		bReturn = False
		
		for item in self.arrItems:
			bReturn = bReturn or item.isUnderDrag()
		
		return bReturn

class zoomable:
	def __init__(self, parent):
		self.bZooming = False
				
		self.zoomRESET = 1.0
		self.zoomMIN = 1.0 / 1024
		self.zoomMAX = 1.0 * 1024
		
		self.bZoomH = True
		self.bZoomV = True
		
	def isUnderZoom(self):
		return self.bZooming
		
	def recalculateVirtualSize(self, w, h):
		
		nw, nh = w, h
		
		if True == self.bZoomV:
			#nh = h*self.zoomlevel	
			nh = h/self.zoomlevel	
		
		if True == self.bZoomH:
			#nw = w*self.zoomlevel
			nw = w/self.zoomlevel
		
		return nw, nh
		
	def resetZoomlevel(self):
		self.zoomlevel = self.zoomRESET
		self.prev_zoomlevel = self.zoomlevel	
		
	def normalizeZoomlevel(self):
		if self.zoomlevel > self.zoomMAX:
			self.zoomlevel = self.zoomMAX
			
		if self.zoomlevel < self.zoomMIN:
			self.zoomlevel = self.zoomMIN
			
		#self.zoomlevel = round(self.zoomlevel,2)	
		
	def increaseZoomlevel(self):
		print "Z+"
		self.prev_zoomlevel = self.zoomlevel
		
		if self.zoomlevel >= self.zoomMIN and self.zoomlevel < self.zoomMAX:	
			self.zoomlevel = self.zoomlevel * 2.0
		
		self.normalizeZoomlevel()
		
	def decreaseZoomlevel(self):
		print "Z-"
		self.prev_zoomlevel = self.zoomlevel
		
		if self.zoomlevel > self.zoomMIN and self.zoomlevel <= self.zoomMAX:	
			self.zoomlevel = self.zoomlevel * 0.5
				
		self.normalizeZoomlevel()	
	
class panable:
	def __init__(self, parent):
		self.bPanning = False
		
		self.panDropLeft = 0
		self.panDropRight = 0
		self.panDropTop = 0
		self.panDropBottom = 0
		
		self.panlocal_OffX = 0
		self.panlocal_OffY = 0	
		
	def isUnderPan(self):
		return self.bPanning
		
	def startPan(self, cleft, cright, ctop, cbottom, mx, my):	
		print "pan mode on"	

		self.bPanning = True
		
		self.panDropLeft = cleft
		self.panDropRight = cright
		self.panDropTop = ctop
		self.panDropBottom = cbottom
			
		self.panlocal_OffX = mx
		self.panlocal_OffY = my	
		
		enableMouseMotion()
		
	def stopPan(self):
		print "pan mode off"
		
		bReturn = False
		
		self.cleft = self.panDropLeft
		self.cright = self.panDropRight
		self.ctop = self.panDropTop
		self.cbottom = self.panDropBottom
		
		self.bPanning = False
		
		if self.panDropLeft != self.panDropRight and self.panDropTop != self.panDropBottom :
			
			if self.cleft != self.panDropLeft or self.cright != self.panDropRight or self.ctop != self.panDropTop or self.cbottom != self.panDropBottom:
			
				bReturn = True	
		
		disableMouseMotion()
		
		return bReturn
		
	def setPanExtents(self, l, r, t, b):
		self.cleft = l
		self.cright = r
		self.ctop = t
		self.cbottom = b
		
	def updatePanExtents(self, mx, my, w, h):
		nx = mx - self.panlocal_OffX
		ny = my - self.panlocal_OffY
		
		tmpLeft = self.cleft - nx 
		tmpRight = tmpLeft + w
		tmpTop = self.ctop - ny
		tmpBottom = tmpTop + h
		
		if tmpLeft != tmpRight and tmpTop != tmpBottom:
			self.panDropLeft = tmpLeft
			self.panDropRight = tmpRight
			self.panDropTop = tmpTop
			self.panDropBottom = tmpBottom
		
	def getPanExtents(self):
		return self.cleft, self.cright, self.ctop, self.cbottom
		
