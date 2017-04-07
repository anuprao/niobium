#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# niobium.py
#
# Copyright (c) 2017, Refer accompanying contributors.txt file for authors.
# Refer accompanying LICENSE file for the applicable licensing terms.
#

import os
from math import *

#########################################################

class dragdropmanager(object):
	
	onlyInstance = None
	
	def __init__(self):
		
		self.enableMouseMotionCb = None
		self.disableMouseMotionCb = None
		
		self.isEmpty = True
		self.dropSrc = None
		self.dropObj = None
		
	@staticmethod
	def getInstance():
		if None == dragdropmanager.onlyInstance:
			dragdropmanager.onlyInstance = dragdropmanager()
		return dragdropmanager.onlyInstance
		
	def attachObject(self, dropSrc, dropObj):
		print("attach for drop")
		# TODO: Set state of dropObj to indicate it in flight
		#dropObj.show(False)
		
		self.dropSrc = dropSrc
		self.dropObj = dropObj
		self.isEmpty = False
		
		if None != self.enableMouseMotionCb:
			self.enableMouseMotionCb()
	
	def clearOnDrop(self):
		print("cleared on drop")
		self.isEmpty = True
		self.dropSrc = None
		self.dropObj = None
		
		if None != self.disableMouseMotionCb:
			self.disableMouseMotionCb()
		
	def setPosForDrop(self, lx, ly):
		self.dropObj.setPosForDrop(lx, ly)
	
class draggable(object):
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
		
		#print("set drop location", self.m_dropx, self.m_dropy)
		
	def startDrag(self, mx, my):		
		print("start drag")
		
		self.bDragging = True
		
		self.draglocal_OffX = mx
		self.draglocal_OffY = my
			
		self.setDropLocation(mx, my)
		
	def stopDrag(self):
		print("stop drag")
		
		bReturn = False
		
		self.m_dropx = 0
		self.m_dropy = 0
		
		self.bDragging = False
		
		if 0 != self.m_dropx or 0 != self.m_dropy:
		
			bReturn = True	
		
		return bReturn

class selectable(object):
	def __init__(self, parent):
		self.bSelected = False
		
	def isSelected(self):
		return self.bSelected
		
class selection(object):
	def __init__(self, parent, enableMouseMotionCb=None, disableMouseMotionCb=None):
		
		self.enableMouseMotionCb = enableMouseMotionCb
		self.disableMouseMotionCb = disableMouseMotionCb
		
		self.parent = parent
		
		self.arrItems = []
		
	def clear(self):
		print("clearing selection")
		
		for item in self.arrItems:
			item.m_Selection.bSelected = False
			
		self.arrItems = []
		
	def isEmpty(self):
		bReturn = True
		if 0 < len(self.arrItems):
			bReturn = False
		return bReturn
		
	def addItem(self, item):
		print("adding item to selection @",len(self.arrItems))
		self.arrItems.append(item)
		item.m_Selection.bSelected = True
		
	def removeItem(self, item):
		print("removing item from selection")
		self.arrItems.remove(item)
		item.m_Selection.bSelected = False
		
	def containsItem(self, item):
		bReturn = False
		
		if item in self.arrItems:
			bReturn = True
		
		return bReturn
		
	def containsPoint(self, lx, ly):
		bReturn = False
		
		for item in self.arrItems:
			if (lx >= item.m_x) and (lx <= item.m_x + item.m_w ) and (ly >= item.m_y) and (ly <= item.m_y + item.m_h) :
				bReturn = bReturn or True
		
		return bReturn
		
	def setDropLocation(self, mx, my):
		for item in self.arrItems:
			#item.setDropLocation(mx, my)
			
			parent = item.parent
			if None == parent:
				item.setDropLocation(mx, my)
			else:
				if parent not in self.arrItems:
					item.setDropLocation(mx, my)			
		
	def startDrag(self, mx, my):
		for item in self.arrItems:	
			
			#item.startDrag(mx, my)
			
			parent = item.parent
			if None == parent:
				item.startDrag(mx, my)
			else:
				if parent not in self.arrItems:
					item.startDrag(mx, my)
		
		if None != self.enableMouseMotionCb:
			self.enableMouseMotionCb()
		
	def stopDrag(self):		
		bReturn = False
		
		for item in self.arrItems:		
			
			#bReturn = bReturn or item.stopDrag()
			
			parent = item.parent
			if None == parent:
				bReturn = bReturn or item.stopDrag()
			else:
				if parent not in self.arrItems:
					bReturn = bReturn or item.stopDrag()			
			
		if None != self.disableMouseMotionCb:
			self.disableMouseMotionCb()
		
		return bReturn
		
	def isUnderDrag(self):
		bReturn = False
		
		for item in self.arrItems:
			bReturn = bReturn or item.isUnderDrag()
		
		return bReturn
	
class panable(object):
	def __init__(self, parent, enableMouseMotionCb=None, disableMouseMotionCb=None):
		
		self.enableMouseMotionCb = enableMouseMotionCb
		self.disableMouseMotionCb = disableMouseMotionCb
				
		self.bPanning = False
		
		self.panlocal_OffX = 0
		self.panlocal_OffY = 0	
		
		self.m_panx = 0	
		self.m_pany = 0
		
	def isUnderPan(self):
		return self.bPanning
		
	def resetPan(self, mx, my):	
		self.panlocal_OffX = mx
		self.panlocal_OffY = my	
		
	def startPan(self, mx, my):	
		print("pan mode on")	

		self.bPanning = True
			
		self.resetPan(mx, my)
		
		self.m_panx = 0
		self.m_pany = 0
		
		if None != self.enableMouseMotionCb:
			self.enableMouseMotionCb()
			
	def stopPan(self):
		print("pan mode off")
		
		self.panlocal_OffX = 0
		self.panlocal_OffY = 0	
		
		self.m_panx = 0
		self.m_pany = 0
		
		self.bPanning = False
		
		if None != self.disableMouseMotionCb:
			self.disableMouseMotionCb()
			
	def updatePan(self, mx, my):
		self.m_panx = (mx - self.panlocal_OffX)
		self.m_pany = (my - self.panlocal_OffY)	
		
		return 	self.m_panx, self.m_pany
		
class trackable(object):
	def __init__(self, parent, enableMouseMotionCb=None, disableMouseMotionCb=None):
		
		self.enableMouseMotionCb = enableMouseMotionCb
		self.disableMouseMotionCb = disableMouseMotionCb
				
		self.bTracking = False
		
		self.anchorX = 0
		self.anchorY = 0	
		
		self.trackX = 0	
		self.trackY = 0
		
	def isUnderTrack(self):
		return self.bTracking
		
	def resetTrack(self, mx, my):	
		self.anchorX = mx
		self.anchorY = my	
		
	def startTrack(self, mx, my):	
		print("track mode on")	

		self.bTracking = True
			
		self.resetTrack(mx, my)
		
		self.trackX = mx
		self.trackY = my
		
		if None != self.enableMouseMotionCb:
			self.enableMouseMotionCb()
			
	def stopTrack(self):
		print("track mode off")
		
		self.anchorX = 0
		self.anchorY = 0	
		
		self.trackX = 0
		self.trackY = 0
		
		self.bTracking = False
		
		if None != self.disableMouseMotionCb:
			self.disableMouseMotionCb()
			
	def updateTrack(self, mx, my):
		self.trackX = mx
		self.trackY = my
		
class zoomable(object):
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
			nh = h/self.zoomlevel		
		
		if True == self.bZoomH:
			nw = w/self.zoomlevel
		
		return (nw, nh)
		
	def resetZoomlevel(self):
		print("[1]")
		self.zoomlevel = self.zoomRESET
		self.prev_zoomlevel = self.zoomlevel	
		
	def normalizeZoomlevel(self):
		if self.zoomlevel > self.zoomMAX:
			self.zoomlevel = self.zoomMAX
			
		if self.zoomlevel < self.zoomMIN:
			self.zoomlevel = self.zoomMIN
		
	def increaseZoomlevel(self):
		print("[+]")
		self.prev_zoomlevel = self.zoomlevel
		
		if self.zoomlevel >= self.zoomMIN and self.zoomlevel < self.zoomMAX:	
			self.zoomlevel = self.zoomlevel * 1.2
		
		self.normalizeZoomlevel()
		
	def decreaseZoomlevel(self):
		print("[-]")
		self.prev_zoomlevel = self.zoomlevel
		
		if self.zoomlevel > self.zoomMIN and self.zoomlevel <= self.zoomMAX:	
			self.zoomlevel = self.zoomlevel / 1.2
				
		self.normalizeZoomlevel()	
		
