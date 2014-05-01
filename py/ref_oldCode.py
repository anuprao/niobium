#!/usr/bin/python

# OpenGL 1.4 code

import math
import os

import numpy
from freetype import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame, pygame.image
from pygame.locals import *

width = 1600
height = 960

arrIcons = []

texIdB_P = None
texIdB_R = None
texIdNode = None
texIdPane = None

video_flags = None

bUpdate = False

bCTRLpressed = False

ftRegular = None
ftBold = None

#########################################################
'''
from pygame.locals  import *
from ctypes import windll

user32      = windll.user32
ShowWindow  = user32.ShowWindow
IsZoomed    = user32.IsZoomed

SW_MAXIMIZE =   3
SW_RESTORE  =   9

def getSDLWindow():
	return pygame.display.get_wm_info()['window']

def SDL_Maximize():
	return ShowWindow(getSDLWindow(), SW_MAXIMIZE)

def SDL_Restore():
	return ShowWindow(getSDLWindow(), SW_RESTORE)

def SDL_IsMaximized():
	return IsZoomed(getSDLWindow())
'''
#########################################################

def enableMouseMotion():
	pygame.event.set_allowed(MOUSEMOTION)

def disableMouseMotion():
	pygame.event.set_blocked(MOUSEMOTION)
	
#########################################################

def loadTexture(pathImg, lp=0, rp=0, tp=0, bp=0):
	
	bg_image = pygame.image.load(pathImg).convert_alpha()
	w = bg_image.get_width()
	h = bg_image.get_height()
	
	bg_data = pygame.image.tostring(bg_image,"RGBA", 0)
	
	glEnable(GL_TEXTURE_2D)
	
	texId = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, texId)
	
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_data)
	
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	
	return (texId, w, h, lp, rp, tp, bp)
	
#########################################################

class customfont:
	def __init__(self, pthFont, nSize):
		self.pthFont = pthFont
		self.nSize = nSize
		self.base = 0
		self.texfont = 0
		self.fontheight = None 
		self.fontwidth = None
		self.advanceX = None
		self.advanceY = None
		
	def enableTexture(self):
		glBindTexture( GL_TEXTURE_2D, self.texfont)
		glEnable(GL_TEXTURE_2D)
	
	def disableTexture(self):
		glBindTexture( GL_TEXTURE_2D, 0)
		glDisable(GL_TEXTURE_2D)
		
	def renderChar(self, chardata):
		glCallList(self.base + ord(chardata) )
		
	def renderStr(self, text):
		self.enableTexture()
		glListBase( self.base )
		glCallLists( [ord(c) for c in text] )	
		self.disableTexture()
		
	def makefont(self):
		vpadding = 6
		hpadding = 7
		
		# Load font
		face = Face(self.pthFont)
		face.set_char_size( self.nSize*64 )
		
		self.advanceX = [0]*128
		self.advanceY = [0]*128
		bitmap_left = [0]*128
		bitmap_top = [0]*128
		
		width, left, height, ascender, descender = 0, 0, 0, 0, 0
		for k in range(32,128):
			face.load_char( chr(k), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT )
			
			bitmap	= face.glyph.bitmap
			
			self.advanceX[k] = face.glyph.advance.x >> 6
			self.advanceY[k] = face.glyph.advance.y >> 6
			bitmap_left[k] = face.glyph.bitmap_left
			bitmap_top[k] = face.glyph.bitmap_top
			
			width = max( width, bitmap.width)
			left = min( left, face.glyph.bitmap_left )
			
			ascender  = max( ascender, face.glyph.bitmap_top )
			descender = max( descender, bitmap.rows-face.glyph.bitmap_top )
		
		self.fontheight = ascender + descender
		height = self.fontheight  + vpadding
		
		self.fontwidth = width
		width = self.fontwidth - left + hpadding
		
		Z = numpy.zeros((height*6, width*16), dtype=numpy.ubyte)
		for j in range(6):
			for i in range(16):
				k = 32+j*16+i
				c = chr(k)
				face.load_char(c, FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT )
				bitmap = face.glyph.bitmap
				
				x = i*width
				y = j*height
				
				x_l = x  - left + face.glyph.bitmap_left
				x_r = x_l + bitmap.width
				
				y_t = y + ascender - face.glyph.bitmap_top
				y_b = y_t + bitmap.rows
				
				Z[y_t:y_b,x_l:x_r].flat = bitmap.buffer			
		
		# Bound texture
		self.texfont = glGenTextures(1)
		glBindTexture( GL_TEXTURE_2D, self.texfont )
		glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
		glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
		glTexImage2D( GL_TEXTURE_2D, 0, GL_ALPHA, Z.shape[1], Z.shape[0], 0, GL_ALPHA, GL_UNSIGNED_BYTE, Z )
		
		# Generate display lists
		dx = width/float(Z.shape[1])
		dy = height/float(Z.shape[0])
		sy = vpadding/float(Z.shape[0])
		
		self.base = glGenLists(8*16)
		for i in range(8*16):
			c = chr(i)
			x = i%16
			y = i//16-2
			
			glNewList(self.base+i, GL_COMPILE)
			if (i >= 32):
				glBegin( GL_QUADS )
				
				glTexCoord2f( (x  )*dx, (y)*dy ), glVertex( 0,	 0 )
				glTexCoord2f( (x+1)*dx, (y)*dy ), glVertex( width, 0 )
				glTexCoord2f( (x+1)*dx, (y+1)*dy - sy), glVertex( width, height-vpadding)
				glTexCoord2f( (x  )*dx, (y+1)*dy - sy), glVertex( 0,	 height-vpadding )
				
				glEnd( )
				
				glTranslatef( self.advanceX[i], self.advanceY[i], 0 )		
			
			glEndList( )
			
		glBindTexture( GL_TEXTURE_2D, 0)

#########################################################

EVT_NONE = 0
EVT_TOUCH_DOWN = 1
EVT_TOUCH_UP = 2
EVT_TOUCH_MOTION = 3
EVT_TOUCH_CLICK = 4
EVT_TOUCH_DBLCLICK = 5
EVT_KEY_DOWN = 6
EVT_KEY_UP = 7

DEFAULT_WIDTH = 10
DEFAULT_HEIGHT = 10

DND_NONE = 0
DND_NODE = 1
DND_CONNECTION = 2

class AnimEvent:
	def __init__(self, animType, pHandler):
		self.animType = animType
		self.pHandler = pHandler
		self.bTriggered = False
			
class UiEvent:
	def __init__(self, eType, posX, posY, button):
		self.eType = eType
		self.posX = posX
		self.posY = posY
		self.button = button

class uiglobals:
	def __init__(self):
		pass
	
	@staticmethod	
	def renderTexture(widget, iTex, x, y, z, w, h):		
		global arrIcons
		
		texData = arrIcons[iTex]
	
		texId = texData[0]
		w = texData[1]
		h = texData[2]
				
		offX = x
		offY = y
		
		if None != widget:
			offX, offY = widget.localToGlobal(offX, offY)
		
		#glDisable(GL_COLOR_MATERIAL)
		glEnable(GL_TEXTURE_2D)
		
		glBindTexture(GL_TEXTURE_2D, texId)
		
		glPushMatrix()
		
		glTranslate(offX, offY, z)
		
		glBegin(GL_QUADS)
		
		glTexCoord2f( 0, 0)
		glVertex3f( 0, 0, 0)
		
		glTexCoord2f( 1, 0)
		glVertex3f( w, 0, 0)
		
		glTexCoord2f( 1, 1)
		glVertex3f( w, h, 0)
		
		glTexCoord2f( 0, 1)
		glVertex3f( 0, h, 0)
		
		glEnd()		
		
		glPopMatrix()
		
		glDisable( GL_TEXTURE_2D )
		#glEnable(GL_COLOR_MATERIAL)
		
	@staticmethod	
	def renderTextureSlice9(widget, iTex, x, y, z, w, h):	
		'''		Assumes 10 pixel slice on all 4 sides '''
		global arrIcons
		
		texData = arrIcons[iTex]
	
		texId = texData[0]
		tw = texData[1] 
		th = texData[2] 
		lp = texData[3] # 10
		rp = texData[4] # 10
		tp = texData[5] # 10
		bp = texData[6] # 10
		
		x0 = 0
		x1 = lp
		x2 = w-rp
		x3 = w
		
		v0 = float(0)/tw
		v1L = float(lp)/tw
		v1R = float(lp)/tw
		v2L = float(tw-rp)/tw
		v2R = float(tw-rp)/tw
		v3 = float(tw)/tw
		
		y0 = 0
		y1 = tp
		y2 = h-bp
		y3 = h
		
		h0 = float(0.0)/th
		h1T = float(tp)/th
		h1B = float(tp)/th
		h2T = float(th-bp)/th
		h2B = float(th-bp)/th
		h3 = float(th)/th
		
		
		offX = x
		offY = y
		
		if None != widget:
			offX, offY = widget.localToGlobal(offX, offY)
		
		#glDisable(GL_COLOR_MATERIAL)
		glEnable(GL_TEXTURE_2D)
		
		glBindTexture(GL_TEXTURE_2D, texId)
		
		glPushMatrix()
		
		glTranslate(offX, offY, z)
		
		glBegin(GL_QUADS)
		
		# TL
		
		glTexCoord2f( 0, 0)
		glVertex3f( x0, y0, 0)
		
		glTexCoord2f( v1L, 0)
		glVertex3f( x1, y0, 0)
		
		glTexCoord2f( v1L, h1T)
		glVertex3f( x1, y1, 0)
		
		glTexCoord2f( 0, h1T)
		glVertex3f( x0, y1, 0)
		
		glEnd()
			
		# TM
		
		glBegin(GL_QUADS)
		
		glTexCoord2f( v1R, 0)
		glVertex3f( x1, y0, 0)
		
		glTexCoord2f( v2L, 0)
		glVertex3f( x2, y0, 0)
		
		glTexCoord2f( v2L, h1T)
		glVertex3f( x2, y1, 0)
		
		glTexCoord2f( v1R, h1T)
		glVertex3f( x1, y1, 0)
		
		glEnd()	
		
		#TR
		
		glBegin(GL_QUADS)
		
		glTexCoord2f( v2R, 0)
		glVertex3f( x2, y0, 0)
		
		glTexCoord2f( v3, 0)
		glVertex3f( x3, y0, 0)
		
		glTexCoord2f( v3, h1T)
		glVertex3f( x3, y1, 0)
		
		glTexCoord2f( v2R, h1T)
		glVertex3f( x2, y1, 0)
		

		

		# ML
		
		glTexCoord2f( 0, h1B)
		glVertex3f( x0, y1, 0)
		
		glTexCoord2f( v1L, h1B)
		glVertex3f( x1, y1, 0)
		
		glTexCoord2f( v1L, h2T)
		glVertex3f( x1, y2, 0)
		
		glTexCoord2f( 0, h2T)
		glVertex3f( x0, y2, 0)
		
		# MM
		
		glTexCoord2f( v1R, h1B)
		glVertex3f( x1, y1, 0)
		
		glTexCoord2f( v2L, h1B)
		glVertex3f( x2, y1, 0)
		
		glTexCoord2f( v2L, h2T)
		glVertex3f( x2, y2, 0)
		
		glTexCoord2f( v1R, h2T)
		glVertex3f( x1, y2, 0)
		
		# MR
		
		glTexCoord2f( v2R, h1B)
		glVertex3f( x2, y1, 0)
		
		glTexCoord2f( v3, h1B)
		glVertex3f( x3, y1, 0)
		
		glTexCoord2f( v3, h2T)
		glVertex3f( x3, y2, 0)
		
		glTexCoord2f( v2R, h2T)
		glVertex3f( x2, y2, 0)
		
		
		# BL
		
		glTexCoord2f( 0, h2B)
		glVertex3f( x0, y2, 0)
		
		glTexCoord2f( v1L, h2B)
		glVertex3f( x1, y2, 0)
		
		glTexCoord2f( v1L, h3)
		glVertex3f( x1, y3, 0)
		
		glTexCoord2f( 0, h3)
		glVertex3f( x0, y3, 0)
		
		
		# BM
		
		glTexCoord2f( v1R, h2B)
		glVertex3f( x1, y2, 0)
		
		glTexCoord2f( v2L, h2B)
		glVertex3f( x2, y2, 0)
		
		glTexCoord2f( v2L, h3)
		glVertex3f( x2, y3, 0)
		
		glTexCoord2f( v1R, h3)
		glVertex3f( x1, y3, 0)
		
		# BR
		
		glTexCoord2f( v2R, h2B)
		glVertex3f( x2, y2, 0)
		
		glTexCoord2f( v3, h2B)
		glVertex3f( x3, y2, 0)
		
		glTexCoord2f( v3, h3)
		glVertex3f( x3, y3, 0)
		
		glTexCoord2f( v2R, h3)
		glVertex3f( x2, y3, 0)
		


		glEnd()			
		
		glPopMatrix()
		
		glDisable( GL_TEXTURE_2D )
		#glEnable(GL_COLOR_MATERIAL)
		
	@staticmethod
	def renderBkg(widget, x, y, z, w, h):	
		
		offX = x
		offY = y
		
		if None != widget:
			offX, offY = widget.localToGlobal(offX, offY)
					
		#print "offX, offY = ", offX, offY
		
		#glEnable(GL_COLOR_MATERIAL)
		glDisable( GL_TEXTURE_2D )
		
		glPushMatrix()
		
		glTranslate(offX, offY, z)
		
		glBegin(GL_QUADS)
		
		glColor4f(1.0, 1.0, 1.0, 1.0)
		
		glVertex3f( 0, 0, 0)
		glVertex3f( w, 0, 0)
		glVertex3f( w, h, 0)
		glVertex3f( 0, h, 0)
		
		glEnd()		
		
		glPopMatrix()
		
		glColor4f(1.0, 1.0, 1.0, 1.0)
		
		glEnable(GL_TEXTURE_2D)
		#glDisable(GL_COLOR_MATERIAL)		
		
class widget :
	def __init__(self):
		global DEFAULT_WIDTH
		global DEFAULT_HEIGHT
		
		self.name = "unnamed"
		self.m_x = 0
		self.m_y = 0
		self.m_z = 0
		self.m_w = DEFAULT_WIDTH
		self.m_h = DEFAULT_HEIGHT
		self.m_bShow = True
		self.m_bPressed = False
		self.m_bGrouped = False
		self.m_bAnimInProgress = False
		self.m_arrpChildren= []
		self.m_numWidgets = 0
		self.m_pParent = None
		self.m_arrpHandlers = {}
		self.m_arrEvent = []
		self.m_numEvents = 0
			
	def loadAssets(self):
		for child in self.m_arrpChildren:
			child.loadAssets()

	def redraw(self):
		if True == self.m_bShow :
			for child in self.m_arrpChildren:
				child.redraw()	

	def show(self, bShow):
		self.m_bShow = bShow		

	def setPressed(self, bPressed):
		self.m_bPressed = bPressed	

	def setPos(self, x, y):
		self.m_x = x
		self.m_y = y
		
	def moveByDelta(self, dx, dy):
		self.m_x = self.m_x + dx
		self.m_y = self.m_y + dy
		
	def setSize(self, w, h):
		self.m_w = w
		self.m_h = h

	def addChildWidget(self, child):
		self.m_arrpChildren.append(child)
		nId = len(self.m_arrpChildren) - 1
		child.setParent(self)
		
		return nId

	def localToGlobal(self, x, y):
		
		if None != self.m_pParent :
			x, y = self.m_pParent.localToGlobal(x, y)
		
		x = x + self.m_x
		y = y + self.m_y
		
		return x, y

	def globalToLocal(self, x, y):
		if None != self.m_pParent :
			x, y = self.m_pParent.globalToLocal(x, y)

		x = x - self.m_x
		y = y - self.m_y
		
		return x, y
		
	def toLocal(self, x, y):
		x = x - self.m_x
		y = y - self.m_y
		
		return x, y

	def toParent(self, parentName, x, y):
		
		if parentName != self.name:			
			x = x + self.m_x
			y = y + self.m_y
			
			if None != self.m_pParent :
					x, y = self.m_pParent.toParent(parentName, x, y)
		
		return x, y

	def containsPoint(self, lx, ly):
		bReturn = False
		
		return bReturn
		
	def getTopmostChildAt(self, lx, ly, belowChild=None):
		tmpChild = None
		ptX, ptY = lx, ly
		numChildren = len(self.m_arrpChildren)
		i = numChildren - 1
		while (None == tmpChild) and (i >= 0):
			child = self.m_arrpChildren[i]
			
			if (ptX >= child.m_x) and (ptX <= child.m_x + child.m_w ) and (ptY >= child.m_y) and (ptY <= child.m_y + child.m_h) :
				if None == belowChild :
					tmpChild = child
				else:
					if belowChild.m_z > child.m_z:
						tmpChild = child
			
			i = i - 1
			
		return tmpChild
		
	def setParent(self, pParent):
		self.m_pParent = pParent	

	def processEvent(self, pUiEvent):
		bProcessed = False
		bRedraw = False
		bNeedRedraw0 = False
		bNeedRedraw1 = False
		bNeedRedraw2 = False
		bNeedRedraw3 = False
		
		# obtain child widget at nearest Z
		if EVT_TOUCH_DOWN <= pUiEvent.eType or EVT_TOUCH_DBLCLICK >= pUiEvent.eType :
			lx, ly = self.toLocal(pUiEvent.posX, pUiEvent.posY)
			child = self.getTopmostChildAt(lx, ly)
			if None != child :
				pNewUiEvent = UiEvent(pUiEvent.eType, lx, ly, pUiEvent.button)
				bProcessed, bRedraw = child.processEvent(pNewUiEvent)
		
		if (False == bProcessed) and (True == self.m_bShow):

			pGroupParent = None
			
			if True == self.m_bGrouped :
				if None != self.m_pParent :
					pGroupParent = self.m_pParent
			
			if None != pGroupParent :
				bNeedRedraw0 = pGroupParent.executePreHandler(self, pUiEvent.eType)
			
			bNeedRedraw1 = self.executePreHandler(self, pUiEvent.eType)
			
			if True == self.m_arrpHandlers.has_key(pUiEvent.eType):
				pHandler = self.m_arrpHandlers[pUiEvent.eType]
				if None != pHandler :
					pHandler(self, pUiEvent)
					bProcessed = True
					#print "bProcessed", bProcessed
			
			bNeedRedraw2 = self.executePostHandler(self, pUiEvent.eType)
			
			if None != pGroupParent :
				bNeedRedraw3 = pGroupParent.executePostHandler(self, pUiEvent.eType)
				
		bRedraw = bRedraw or bNeedRedraw0 or bNeedRedraw1 or bNeedRedraw2 or bNeedRedraw3
		
		return bProcessed, bRedraw

	def setHandler(self, eType, pHandler):
		self.m_arrpHandlers[eType] = pHandler	

	def executePreHandler(self, widget, event):
		return False	

	def executePostHandler(self, widget, event):
		return False		

	def setGrouped(self, bGrouped):
		self.m_bGrouped = bGrouped	

	def postEvent(self, pEvent):
		bPresentInEventList = False
		
		for pTmp in self.m_arrEvent:
			if pTmp.eType == pEvent.eType:
				pTmp.bTriggered = True
				bPresentInEventList = True

		if False == bPresentInEventList:
			if None != self.m_pParent:
				self.m_pParent.postEvent(pEvent)

	def addEventHandler(self, animType, pHandler):
		animevent = AnimEvent(animType, pHandler)
		self.m_arrEvent.append(animevent)
		
	def updateAnimation(self):
		bUpdated = False
		
		for pAnimTmp in self.m_arrEvent:
			if True == pAnimTmp.bTriggered:
				bDone = pAnimTmp.pHandler(self)
				if True == bDone:
					pAnimTmp.bTriggered = False

				bUpdated = True
		
		for tmp in self.m_arrpChildren:
			if None != pTmp:
				bUpdated = bUpdated | (pTmp.updateAnimation())

		return bUpdated
		
class image(widget):
	def __init__(self):
		widget.__init__(self)
		self.texReleased = None
		
	def setReleasedImage(self, texReleased):
		self.texReleased = texReleased
						
	def redraw(self):
		if True == self.m_bShow:
			if False == self.m_bPressed:
				if None != self.texReleased:
					uiglobals.renderTextureSlice9(self, self.texReleased, 0, 0, -1, self.m_w, self.m_h)
		
		widget.redraw(self)
		
class clickableimage(image):
	def __init__(self):
		image.__init__(self)
		self.texReleased = None
		
	def setPressedImage(self, texPressed):
		self.texPressed = texPressed
						
	def redraw(self):	
		if True == self.m_bShow:
			if True == self.m_bPressed:
				if None != self.texPressed:
					uiglobals.renderTextureSlice9(self, self.texPressed, 0, 0, -1, self.m_w, self.m_h)
			
		image.redraw(self)
		
class buttonabstract(clickableimage):
	def __init__(self):
		clickableimage.__init__(self)
		self.idLabel = None
		
	def redraw(self):
		
		if True == self.m_bShow:
			if True == self.m_bPressed:
				uiglobals.renderTextureSlice9(self, texIdB_P, 0, 0, -1, self.m_w, self.m_h)
			else:
				uiglobals.renderTextureSlice9(self, texIdB_R, 0, 0, -1, self.m_w, self.m_h)
			
		clickableimage.redraw(self)
		
class button(buttonabstract):
	def __init__(self):
		buttonabstract.__init__(self)
		
	def executePreHandler(self, widget, event):
		bRedraw = False
		if EVT_TOUCH_DOWN == event :
			self.setPressed(True)
			bRedraw = True
		return bRedraw
		
	def executePostHandler(self, widget, event):		
		bRedraw = False
		if EVT_TOUCH_UP == event :
			self.setPressed(False)
			bRedraw = True
		return bRedraw	
		
class togglebutton(buttonabstract):
	def __init__(self):
		buttonabstract.__init__(self)
		
	def executePostHandler(self, widget, event):		
		bRedraw = False
		if EVT_TOUCH_UP == event :
			self.setPressed(not self.m_bPressed)
			bRedraw = True
		return bRedraw		
		
class radiobutton(togglebutton):
	def __init__(self):
		togglebutton.__init__(self)

class listabstract(widget):
	def __init__(self):
		widget.__init__(self)
		
	def addChildWidget(self, child):
		child.setGrouped(True)
		# child.moveByDelta(self.pad, self.pad)
		nId = widget.addChildWidget(self, child)
		
		#print 
		#print self.name, self.m_x, self.m_y, self.m_w, self.m_h
		
		rectnew = pygame.Rect(self.m_x, self.m_y, self.m_w, self.m_h)
		for tmpchild in self.m_arrpChildren:
			rectchild = pygame.Rect(self.m_x + tmpchild.m_x, self.m_y + tmpchild.m_y, tmpchild.m_w, tmpchild.m_h)
			#print tmpchild.name, self.m_x + tmpchild.m_x, self.m_y + tmpchild.m_y, tmpchild.m_w, tmpchild.m_h
			rectnew = pygame.Rect.union(rectnew, rectchild)
		
		self.m_x = rectnew.x 
		self.m_y = rectnew.y 
		self.m_w = rectnew.w
		self.m_h = rectnew.h
		
		return nId
	
class buttonbar(listabstract):
	def __init__(self):
		listabstract.__init__(self)

class togglebuttonbar(listabstract):
	def __init__(self):
		listabstract.__init__(self)
		self.btnCurr = None
		
	def executePreHandler(self, widget, event):
		bRedraw = False
		if EVT_TOUCH_UP == event :
			if None != self.btnCurr:
				print self.btnCurr.name
				self.btnCurr.setPressed(False)
				bRedraw = True
		return bRedraw
		
	def executePostHandler(self, widget, event):		
		bRedraw = False
		if EVT_TOUCH_UP == event :
			self.btnCurr = widget
			print self.btnCurr.name
			bRedraw = True
		return bRedraw	

class toolbox(listabstract):
	def __init__(self):
		global texIdPane
		
		listabstract.__init__(self)
		
		self.texReleased = None
		self.setReleasedImage(texIdPane)
		
	def setReleasedImage(self, texReleased):
		self.texReleased = texReleased
				
	def redraw(self):
		glPushMatrix()	
		
		uiglobals.renderTextureSlice9(self, self.texReleased, 0, 0, -1, self.m_w, self.m_h)
		
		listabstract.redraw(self)
		
		glPopMatrix()	
		
#########################################################

class connection(widget):
	def __init__(self):
		widget.__init__(self)
		
		self.dndType = DND_CONNECTION
		self.dragpad_OffX = 0
		self.dragpad_OffY = 0
		
		self.x1 = 0.0
		self.y1 = 0.0
		
		self.x2 = 10.0
		self.y2 = 10.0		
	
	def setPosForDrop(self, lx, ly):
		self.x2 = lx
		self.y2 = ly
		
	def redraw(self):
		if True == self.m_bShow :
			
			zoomlevel = 1.0
			
			dx = self.x2 - self.x1
			dy = self.y2 - self.y1
			
			if 0.0 != dx and 0.0 != dy :
				# 4 control points in space
				#ctrlpoints = [ [ 0.0, 0.0, 0.0], [ 100.0, -15.0, 0.0], [ 200.0, 115.0, 0.0], [ 300.0, 100.0, 0.0]    ]			
				
				xa = dx/3.0 + self.x1
				ya = self.y1 - 0.10*dy
				
				#print xa, ya
				
				xb = (2.0*dx)/3.0 + self.x1
				yb = self.y2 + 0.10*dy
				
				ctrlpoints = [ [ self.x1, self.y1, 0.0], [ xa, ya, 0.0], [ xb, yb, 0.0], [ self.x2, self.y2, 0.0]    ]			
				
				numSegs = int( 5 * zoomlevel ) + 40
				
				
				glPushMatrix()
				
				glColor4f(0.7, 0.7, 0.7, 1.0)
				
				glLineWidth(3.0 * zoomlevel)
				
				# we want to draw with t from 0.0 to 1.0
				# and we give the dimensions of the data
				glMap1f(GL_MAP1_VERTEX_3, 0.0, 1.0, ctrlpoints)
				glEnable(GL_MAP1_VERTEX_3)
				
				glHint( GL_LINE_SMOOTH_HINT, GL_NICEST )
				glEnable( GL_LINE_SMOOTH )
				
				glHint( GL_POLYGON_SMOOTH_HINT, GL_NICEST )
				glEnable(GL_POLYGON_SMOOTH)
				
				# draw a curve with 30 steps from t=0.0 to t=1.0
				glBegin(GL_LINE_STRIP)
				
				for i in range(0,numSegs+1):
					glEvalCoord1f(i/float(numSegs))
				
				glEnd()
				
				glDisable( GL_POLYGON_SMOOTH )
				glDisable( GL_LINE_SMOOTH )
				
				glDisable(GL_MAP1_VERTEX_3)
				
				glColor4f(1.0, 1.0, 1.0, 1.0)
				
				glPopMatrix()
	
class nodeport(widget):
	def __init__(self):
		widget.__init__(self)
		self.setHandler(EVT_TOUCH_DOWN, self.onClickPort)
	
	def redraw(self):
		if True == self.m_bShow :
			glPushMatrix()	
			
			uiglobals.renderBkg(self, 0, 0, -5, self.m_w, self.m_h)
			
			widget.redraw(self)
			
			glPopMatrix()

		
	def onClickPort(self, widget, pUiEvent):
		print "onClickPort"	
		
		connX = connection()
		connX.name = "connX"
		
		sx, sy = self.m_pParent.toParent("nodechart", pUiEvent.posX, pUiEvent.posY)
		
		connX.x1 = sx
		connX.y1 = sy
		
		dm = dragdropmanager.getInstance()
		dm.attachObject(widget, connX)

# TODO rework on node

#########################################################

class view:
	def __init__(self):
		pass
		
class canvasview(view):
	def __init__(self):
		view.__init__(self)
		
class wallview(view):
	def __init__(self):
		view.__init__(self)
		
class inputsview(view):
	def __init__(self):
		view.__init__(self)
		
#########################################################

class outputwindow:
	def __init__(self):
		pass
		
class videowindow(outputwindow):
	def __init__(self):
		outputwindow.__init__(self)
		
class appwindow(outputwindow):
	def __init__(self):
		outputwindow.__init__(self)
		
class previewwindow(outputwindow):
	def __init__(self):
		outputwindow.__init__(self)
		
#########################################################

class clip:
	def __init__(self):
		pass
		
class timeline:
	def __init__(self):
		pass
		
class timelineeditor:
	def __init__(self):
		pass

#########################################################

# TODO rework on nodechart : fix panning, simplify coordinates

# TODO rework on listabstract : addChildWidget

# TODO gstreamer

# TODO text render

# TODO resize support

# TODO icon

# TODO tooltip

# TODO localization

# TODO theme

# TODO animation support

# TODO grid overlay

# TODO snap to grid

# TODO align

#########################################################

class node(image):
	def __init__(self):
		global texIdNode
		
		image.__init__(self)
		
		self.setReleasedImage(texIdNode)
		
		self.dndType = DND_NODE
		self.dragpad_OffX = 10
		self.dragpad_OffY = 10
		
		self.m_dragObj = draggable(self)
		
	def setPos(self, x, y):
		image.setPos(self, x, y)
		self.m_dragObj.m_x = x
		self.m_dragObj.m_y = y
		
	def setPosForDrop(self, lx, ly):
		self.setPos(lx, ly)
		
	def setDropLocation(self, mx, my):
		self.m_dragObj.setDropLocation(mx, my)
		
	def startDrag(self, mx, my):	
		self.m_dragObj.startDrag(mx, my)
		
	def stopDrag(self):		
		dx, dy = self.m_dragObj.m_dropx, self.m_dragObj.m_dropy
		bReturn = self.m_dragObj.stopDrag()
		image.moveByDelta(self, dx, dy)
		return bReturn
		
	def isUnderDrag(self):
		return self.m_dragObj.isUnderDrag()
		
	def redraw(self):
		global ftRegular
		if True == self.m_bShow :
			glPushMatrix()	
			
			x, y, w, h = 0, 0, self.m_w, self.m_h
			
			if True == self.isUnderDrag() :
				x, y = self.m_dragObj.m_dropx, self.m_dragObj.m_dropy
			
			glTranslate(x,y,0)
			
			uiglobals.renderTextureSlice9(self, self.texReleased, 0, 0, -1, w, h)
			offX, offY = self.localToGlobal(0, 0)
			
			glPushMatrix()
			glTranslate( offX+5, offY+5, 0)
			glColor(1, 1, 1, 1)
			ftRegular.renderStr(self.name)
			glColor(1, 1, 1, 1)		
			glPopMatrix()
			
			widget.redraw(self)
			
			glPopMatrix()

class nodechart(widget):
	def __init__(self, w, h):
		widget.__init__(self)
		widget.setSize(self, w, h)
		
		self.currVirtualWidth = self.m_w
		self.currVirtualHeight = self.m_h
		
		self.m_SelObj = selection(self)
		
		self.m_PanObj = panable(self)
		
		self.m_ZoomObj = zoomable(self)
		self.m_ZoomObj.resetZoomlevel()
		
		self.setHandler(EVT_TOUCH_DOWN, self.onTouchDown)
		self.setHandler(EVT_TOUCH_MOTION, self.onTouchMotion)
		self.setHandler(EVT_TOUCH_UP, self.onTouchUp)	
		
		cursorX = self.m_w/2
		cursorY = self.m_h/2		
		self.setCursorVirtualLoc(cursorX, cursorY, cursorX, cursorY)		
		G_cursorX, G_cursorY = self.localToGlobal(cursorX, cursorY)
		pygame.mouse.set_pos(G_cursorX, G_cursorY)

	def setSize(self, w, h):
		widget.setSize(self, w, h)
		w, h = self.m_ZoomObj.recalculateVirtualSize(self.m_w, self.m_h)
		
	def setCursorVirtualLoc(self, lx, ly, tx, ty):
		self.cleft = lx - (self.currVirtualWidth*tx)/self.m_w 
		self.cright = self.cleft + self.currVirtualWidth
		self.ctop = ly - (self.currVirtualHeight*ty)/self.m_h
		self.cbottom = self.ctop + self.currVirtualHeight
		
		self.m_PanObj.setPanExtents(self.cleft, self.cright, self.ctop, self.cbottom)
		
	def localToVirtual(self, lx, ly):
		mx = self.cleft + (self.currVirtualWidth * lx)/self.m_w 
		my = self.ctop + (self.currVirtualHeight * ly)/self.m_h
		return mx, my
		
	def acceptDropAt(self, src, obj):
		print "dropped"
		
		self.addChildWidget(obj)
		
		src.setPressed(False)
		
		return True
		
	def updatePanExtents(self, mx, my):
		self.m_PanObj.updatePanExtents(mx, my, self.currVirtualWidth, self.currVirtualHeight)		
		
	def onTouchMotion(self, event, pUiEvent):		
		global bUpdate
		
		ex = pUiEvent.posX
		ey = pUiEvent.posY
		
		lx, ly = self.localToVirtual(ex, ey)
		
		if 1 == pUiEvent.button:
			
			dm = dragdropmanager.getInstance()
			if None != dm:
				if False == dm.isEmpty :
					#print "carrying"
					if DND_NODE == dm.dropObj.dndType or DND_CONNECTION == dm.dropObj.dndType:
						dm.setPosForDrop(lx, ly)
						dm.dropObj.show(True)
						bUpdate = True
			
			if True == self.m_PanObj.isUnderPan() :
				self.updatePanExtents(lx, ly)
				bUpdate = True
			
			if True == self.m_SelObj.isUnderDrag() : 
				self.m_SelObj.setDropLocation(lx, ly)
				bUpdate = True

	def onTouchDown(self, event, pUiEvent):	
	
		ex = pUiEvent.posX
		ey = pUiEvent.posY
		
		lx, ly = self.localToVirtual(ex, ey)
		
		if 1 == pUiEvent.button:
			
			if True == self.m_SelObj.containsPoint(lx, ly):
				
				#print "clicked inside selection"
				
				self.m_SelObj.startDrag(lx, ly)										

			else:
				
				child = self.getTopmostChildAt(lx, ly, None)
				if None != child:
					if False == bCTRLpressed:
						self.m_SelObj.clear()
						#print "added", child.name,
					#else:
						#print "appended", child.name,
					
					#print " to selection"
					self.m_SelObj.addItem(child)
					
					self.m_SelObj.startDrag(lx, ly)											
					
				else:
					
					#print "emptied selection"
					self.m_SelObj.clear()
					
					self.m_PanObj.startPan(self.cleft, self.cright, self.ctop, self.cbottom, lx, ly)
					self.setCursorVirtualLoc(lx, ly, ex, ey)
		
	def onTouchUp(self, event, pUiEvent):	
		global bUpdate
		
		ex = pUiEvent.posX
		ey = pUiEvent.posY
		
		lx, ly = self.localToVirtual(ex, ey)
		
		if 4 == pUiEvent.button:
			
			self.m_ZoomObj.increaseZoomlevel()
			w, h = self.m_ZoomObj.recalculateVirtualSize(self.m_w, self.m_h)
			self.currVirtualWidth = w
			self.currVirtualHeight = h
			
			self.setCursorVirtualLoc(lx, ly, ex, ey)
			bUpdate = True
			
		elif 5 == pUiEvent.button:
			
			self.m_ZoomObj.decreaseZoomlevel()	
			w, h = self.m_ZoomObj.recalculateVirtualSize(self.m_w, self.m_h)
			self.currVirtualWidth = w
			self.currVirtualHeight = h
			
			self.setCursorVirtualLoc(lx, ly, ex, ey)
			bUpdate = True
		
		elif 1 == pUiEvent.button:
			
			dm = dragdropmanager.getInstance()
			if None != dm:
				if False == dm.isEmpty :
					if DND_NODE == dm.dropObj.dndType or DND_CONNECTION == dm.dropObj.dndType:
						dm.setPosForDrop(lx, ly)
						bTmpUpdate = self.acceptDropAt(dm.dropSrc, dm.dropObj)
						dm.clearOnDrop()
						bUpdate = bTmpUpdate
					
			if True == self.m_SelObj.isUnderDrag() : 
				bTmpUpdate = self.m_SelObj.stopDrag()
				bUpdate = bTmpUpdate
			
			elif True == self.m_PanObj.isUnderPan() :
					
					bTmpUpdate = self.m_PanObj.stopPan()
					l, r, t, b = self.m_PanObj.getPanExtents()
					self.cleft = l
					self.cright = r
					self.cbottom = b
					self.ctop = t
					
					bUpdate = bTmpUpdate
		
	def redraw(self):
		if True == self.m_bShow :
			glPushMatrix()	
			
			glMatrixMode(GL_PROJECTION)
			
			prevTransform = glGetFloatv(GL_PROJECTION_MATRIX)
			
			glLoadIdentity()	
			
			l, r, t, b = self.cleft, self.cright, self.ctop, self.cbottom, 
			
			if True == self.m_PanObj.isUnderPan() :
				l, r, t, b = self.m_PanObj.panDropLeft, self.m_PanObj.panDropRight, self.m_PanObj.panDropTop, self.m_PanObj.panDropBottom
			
			glOrtho(l, r, b, t, -10, 10)
			
			# draw grid
			'''
			l = round(l,2)
			r = round(r,2)
			t = round(t,2)
			b = round(b,2)
			
			tmpl = l
			
			while tmpl < r:
				glPushMatrix()
				
				glTranslate(tmpl, t, 0)
				
				glLineWidth(0.125)
				
				glBegin(GL_LINE_STRIP)
				
				glColor4f(0.7, 0.7, 0.7, 0.125)
				
				glVertex3f( 0, 0, 0)
				glVertex3f( 0, b-t, 0)
				
				glEnd()		
				
				glPopMatrix()
				
				tmpl = tmpl + 40.0
				
			tmpt = t
			
			while tmpt < b:
				glPushMatrix()
				
				glTranslate(l, tmpt, 0)
				
				glLineWidth(0.125)
				
				glBegin(GL_LINE_STRIP)
				
				glColor4f(0.7, 0.7, 0.7, 0.125)
				
				glVertex3f( 0, 0, 0)
				glVertex3f( r-l, 0, 0)
				
				glEnd()		
				
				glPopMatrix()
				
				tmpt = tmpt + 40.0			
			
			# draw children
			'''
			glColor4f(1.0, 1.0, 1.0, 1.0)
			
			widget.redraw(self)
			
			dm = dragdropmanager.getInstance()
			if None != dm:
				if False == dm.isEmpty :		
					dm.dropObj.redraw()
			
			
			'''
			# 4 control points in space
			#ctrlpoints = [ [ 0.0, 0.0, 0.0], [ 100.0, -15.0, 0.0], [ 200.0, 115.0, 0.0], [ 300.0, 100.0, 0.0]    ]			
			
			x1 = 0.0
			y1 = 0.0
			
			x2 = 800.0
			y2 = 600.0
			
			xa = (x2 - x1)/3.0 + x1
			ya = y1 - 0.10*(y2-y1)
			
			#print xa, ya
			
			xb = (2.0*(x2 - x1))/3.0 + x1
			yb = y2 + 0.10*(y2-y1)
			
			ctrlpoints = [ [ x1, y1, 0.0], [ xa, ya, 0.0], [ xb, yb, 0.0], [ x2, y2, 0.0]    ]			
			
			numSegs = int( 5 * self.m_ZoomObj.zoomlevel ) + 40
			
			glColor4f(0.7, 0.7, 0.7, 1.0)
			
			glTranslate(200.0, 200.0, 0)
			
			glLineWidth(3.0*self.m_ZoomObj.zoomlevel)
			
			# we want to draw with t from 0.0 to 1.0
			# and we give the dimensions of the data
			glMap1f(GL_MAP1_VERTEX_3, 0.0, 1.0, ctrlpoints)
			glEnable(GL_MAP1_VERTEX_3)
			
			glHint( GL_LINE_SMOOTH_HINT, GL_NICEST )
			glEnable( GL_LINE_SMOOTH )
			
			glHint( GL_POLYGON_SMOOTH_HINT, GL_NICEST )
			glEnable(GL_POLYGON_SMOOTH)
			
			
			# draw a curve with 30 steps from t=0.0 to t=1.0
			glBegin(GL_LINE_STRIP)
			
			for i in range(0,numSegs+1):
				glEvalCoord1f(i/float(numSegs))
			
			glEnd()
			
			glDisable( GL_POLYGON_SMOOTH )
			glDisable( GL_LINE_SMOOTH )

			glDisable(GL_MAP1_VERTEX_3)
			
			glColor4f(1.0, 1.0, 1.0, 1.0)
			'''
			
			
			glLoadMatrixf(prevTransform)
			
			glMatrixMode(GL_MODELVIEW)
			glPopMatrix()	
		
class root(widget):
	def __init__(self):
		global width
		global height
		global arrIcons
		
		global texIdB_P
		global texIdB_R
		global texIdNode
		global texIdPane
		
		widget.__init__(self)
		
		self.name = "root"
		
		texBtn_P = loadTexture("../assets/pressedbkg.png", 10, 10, 10, 10)
		texIdB_P = len(arrIcons)
		arrIcons.append(texBtn_P)

		texBtn_R = loadTexture("../assets/releasedbkg.png", 10, 10, 10, 10)
		texIdB_R = len(arrIcons)
		arrIcons.append(texBtn_R)
		
		texNode = loadTexture("../assets/window.png", 64, 64, 64, 24)
		texIdNode = len(arrIcons)
		arrIcons.append(texNode)		

		texPane = loadTexture("../assets/panebkg.png", 10, 10, 10, 10) #slice9test.png") #
		texIdPane = len(arrIcons)
		arrIcons.append(texPane)
		
		texBtn1_P = loadTexture("../assets/use4762.png")
		texIdB1_P = len(arrIcons)
		arrIcons.append(texBtn1_P)

		texBtn1_R = loadTexture("../assets/use4738.png")
		texIdB1_R = len(arrIcons)
		arrIcons.append(texBtn1_R)

		texBtn2_P = loadTexture("../assets/use4892.png")
		texIdB2_P = len(arrIcons)
		arrIcons.append(texBtn2_P)

		texBtn2_R = loadTexture("../assets/use4890.png")
		texIdB2_R = len(arrIcons)
		arrIcons.append(texBtn2_R)
		
		texBtn3_P = loadTexture("../assets/timeline_pressed.png")
		texIdB3_P = len(arrIcons)
		arrIcons.append(texBtn3_P)

		texBtn3_R = loadTexture("../assets/timeline_released.png")
		texIdB3_R = len(arrIcons)
		arrIcons.append(texBtn3_R)
		
		texBtn4_P = loadTexture("../assets/use4706.png")
		texIdB4_P = len(arrIcons)
		arrIcons.append(texBtn4_P)

		texBtn4_R = loadTexture("../assets/use4730.png")
		texIdB4_R = len(arrIcons)
		arrIcons.append(texBtn4_R)
		
		texBtn5_P = loadTexture("../assets/use4812.png")
		texIdB5_P = len(arrIcons)
		arrIcons.append(texBtn5_P)

		texBtn5_R = loadTexture("../assets/use4734.png")
		texIdB5_R = len(arrIcons)
		arrIcons.append(texBtn5_R)
		
		texBtn6_P = loadTexture("../assets/use4904.png")
		texIdB6_P = len(arrIcons)
		arrIcons.append(texBtn6_P)

		texBtn6_R = loadTexture("../assets/use4928.png")
		texIdB6_R = len(arrIcons)
		arrIcons.append(texBtn6_R)
		
		texBtn7_P = loadTexture("../assets/addnode_pressed.png")
		texIdB7_P = len(arrIcons)
		arrIcons.append(texBtn7_P)

		texBtn7_R = loadTexture("../assets/addnode_released.png")
		texIdB7_R = len(arrIcons)
		arrIcons.append(texBtn7_R)		
		
		'''
		imgtest = image()
		imgtest.setPos(0, 0)
		imgtest.setSize(60, 60)
		imgtest.setPressedImage(texData)
		imgtest.setReleasedImage(texData)
		'''
		
		self.chart = nodechart(width, height)
		self.chart.name = "nodechart"
		self.chart.setPos(0, 0)
		self.addChildWidget(self.chart)
		
		node1 = node()
		node1.name = "testNd1"
		node1.setSize(320, 180)
		node1.setPos(self.chart.m_w/2 - node1.m_w/2, self.chart.m_h/2 - node1.m_h/2)
		self.chart.addChildWidget(node1)
		
		p1 = nodeport()
		p1.name = "port1"
		p1.setPos(310, 100)
		
		node1.addChildWidget(p1)
		
		
		
		node2 = node()
		node2.name = "testNd2"
		node2.setSize(320, 180)
		node2.setPos(self.chart.m_w/2 - node2.m_w/2 + 400, self.chart.m_h/2 - node2.m_h/2)
		self.chart.addChildWidget(node2)
		
		p2 = nodeport()
		p2.name = "port2"
		p2.setPos(0, 100)
		
		node2.addChildWidget(p2)
		
		
		node3 = node()
		node3.name = "testNd3"
		node3.setSize(320, 180)
		node3.setPos(self.chart.m_w/2 - node3.m_w/2 - 400, self.chart.m_h/2 - node3.m_h/2)		
		self.chart.addChildWidget(node3)		
		
		btnTest1 = button()
		btnTest1.name = "btnTest1"
		btnTest1.setPos(0, 0)
		btnTest1.setSize(40, 40)
		btnTest1.setPressedImage(texIdB1_P)
		btnTest1.setReleasedImage(texIdB1_R)	
		btnTest1.setHandler(EVT_TOUCH_UP, self.onClick1)
		
		btnTest2 = togglebutton()
		btnTest2.name = "btnTest2"
		btnTest2.setPos(60, 0)
		btnTest2.setSize(40, 40)
		btnTest2.setPressedImage(texIdB2_P)
		btnTest2.setReleasedImage(texIdB2_R)	
		btnTest2.setHandler(EVT_TOUCH_UP, self.onClick2)
		
		btnTest3 = radiobutton()
		btnTest3.name = "btnTest3"
		btnTest3.setPos(120, 0)
		btnTest3.setSize(40, 40)
		btnTest3.setPressedImage(texIdB3_P)
		btnTest3.setReleasedImage(texIdB3_R)	
		btnTest3.setHandler(EVT_TOUCH_UP, self.onClick3)
		
		btnBar1 = togglebuttonbar()
		btnBar1.name = "btnBar1"
		btnBar1.setPos(180, 0)
		
		btnTest4 = togglebutton()
		btnTest4.name = "btnTest4"
		btnTest4.setPos(0, 0)
		btnTest4.setSize(40, 40)
		btnTest4.setPressedImage(texIdB4_P)
		btnTest4.setReleasedImage(texIdB4_R)	
		btnTest4.setHandler(EVT_TOUCH_UP, self.onClick4)
		
		btnTest5 = togglebutton()
		btnTest5.name = "btnTest5"
		btnTest5.setPos(45, 0)
		btnTest5.setSize(40, 40)
		btnTest5.setPressedImage(texIdB5_P)
		btnTest5.setReleasedImage(texIdB5_R)	
		btnTest5.setHandler(EVT_TOUCH_UP, self.onClick5)
		
		btnTest6 = togglebutton()
		btnTest6.name = "btnTest6"
		btnTest6.setPos(90, 0)
		btnTest6.setSize(40, 40)
		btnTest6.setPressedImage(texIdB6_P)
		btnTest6.setReleasedImage(texIdB6_R)	
		btnTest6.setHandler(EVT_TOUCH_UP, self.onClick6)
		
		btnBar1.addChildWidget(btnTest4)
		btnBar1.addChildWidget(btnTest5)
		btnBar1.addChildWidget(btnTest6)
		
		btnAddNode = button()
		btnAddNode.name = "Add Node"
		btnAddNode.setPos(330, 0)
		btnAddNode.setSize(40, 40)
		btnAddNode.setPressedImage(texIdB7_P)
		btnAddNode.setReleasedImage(texIdB7_R)	
		btnAddNode.setHandler(EVT_TOUCH_DOWN, self.onAddNode)											
		
		self.tbox1 = toolbox()
		self.tbox1.name = "toolbox"
		self.tbox1.setPos(0, 20)
		self.tbox1.addChildWidget(btnTest1)
		self.tbox1.addChildWidget(btnTest2)
		self.tbox1.addChildWidget(btnTest3)
		self.tbox1.addChildWidget(btnBar1)
		self.tbox1.addChildWidget(btnAddNode)
		
		self.addChildWidget(self.tbox1)
		
	def onClick1(self, widget, pUiEvent):
		print "clicked 1"
		
	def onClick2(self, widget, pUiEvent):
		print "clicked 2"
		
	def onClick3(self, widget, pUiEvent):
		print "clicked 3"
		
	def onClick4(self, widget, pUiEvent):
		print "clicked 4"
		
	def onClick5(self, widget, pUiEvent):
		print "clicked 5"
		
	def onClick6(self, widget, pUiEvent):
		print "clicked 6"
		
	def onAddNode(self, widget, pUiEvent):
		print "onAddNode"	
		
		nodeX = node()
		nodeX.name = "testNdX"
		nodeX.setSize(320, 180)
		
		dm = dragdropmanager.getInstance()
		dm.attachObject(widget, nodeX)
		
#########################################################
		
def feedKeyDownEvent(event):
	global bCTRLpressed
	
	if K_LCTRL == event.key:
		bCTRLpressed = True
	
def feedKeyUpEvent(event):
	global bCTRLpressed
	
	if K_LCTRL == event.key:
		bCTRLpressed = False
		
def setup():
	global width
	global height
	global video_flags
	global ftRegular
	global ftBold	
	
	#video_flags  = OPENGL | DOUBLEBUF | RESIZABLE
	video_flags  = OPENGL | DOUBLEBUF 
	
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)
	
	pygame.init()
	pygame.display.set_mode((width,height), video_flags)
	pygame.display.set_caption('simple timeline and nodechart - anup jayapal rao')
	
	aspect = float(width)/float(height)
	glViewport(0, 0, width, height)
	
	left = 0
	right = width
	top = 0
	bottom = height

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()	

	glOrtho(left, right, bottom, top, -10, 10)	
	
	glShadeModel(GL_SMOOTH)
	#glDisable(GL_COLOR_MATERIAL)
	glDisable(GL_LIGHTING)	
	glDisable(GL_DEPTH_TEST)
	glDisable(GL_LIGHTING)
	glDepthFunc(GL_LEQUAL)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
	
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)	
	
	pthfontRegular = 'Play-Regular.ttf'

	ftRegular = customfont(pthfontRegular, 14)
	ftRegular.makefont()

	pthfontBold = 'Play-Bold.ttf'

	ftBold = customfont(pthfontBold, 32)
	ftBold.makefont()	
	

###########################################################################################

setup()

pRoot = root()
pRoot.loadAssets()

disableMouseMotion()

bContinue = True
bUpdate = True
bProcessed = False
while bContinue:

	if True == bUpdate:
		#renderInterface()
		
		glClearDepth(1.0)
		glClearColor(0.2, 0.2, 0.2, 1.0)	
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
				
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		
		pRoot.redraw()
		
		pygame.display.flip()
		bUpdate = False
		
	evt = pygame.event.wait()
		
	if QUIT == evt.type:
		bContinue = False
	
	if pygame.VIDEORESIZE == evt.type:
		size = evt.size
		screen = pygame.display.set_mode(size, video_flags)	
		width = size[0]
		height = size[1]
		glViewport(0, 0, width, height)
	
	pUiEvent = None
	
	if MOUSEMOTION == evt.type:
		evts = pygame.event.get(MOUSEMOTION)
		if len(evts) > 0 :
			evt = evts[0]	
				
		pUiEvent = UiEvent(EVT_TOUCH_MOTION, evt.pos[0], evt.pos[1], evt.buttons[0])
	
	if MOUSEBUTTONDOWN == evt.type:
		pUiEvent = UiEvent(EVT_TOUCH_DOWN, evt.pos[0], evt.pos[1], evt.button)
		
	if MOUSEBUTTONUP == evt.type:
		pUiEvent = UiEvent(EVT_TOUCH_UP, evt.pos[0], evt.pos[1], evt.button)
		
	if KEYDOWN == evt.type:
		#pUiEvent = UiEvent(EVT_KEY_DOWN, -1, -1, evt.button)
		if K_LCTRL == evt.key:
			bCTRLpressed = True
		
	if KEYUP == evt.type:
		if K_ESCAPE == evt.key:
			bContinue = False
		elif K_LCTRL == evt.key:
			bCTRLpressed = False			
		else:
			pUiEvent = UiEvent(EVT_KEY_UP, -1, -1, evt.button)
	
	if None != pUiEvent:
		bProcessed, bRedraw = pRoot.processEvent(pUiEvent)
		pUiEvent = None
		
		# should be set to true only if update is needed
		bUpdate = bUpdate | bRedraw
		
