/// DRAGGING

function draggable(item) {
	this.bDragging = false;
	
	this.m_dropx = 0;
	this.m_dropy = 0;
	
	this.draglocal_OffX = 0;
	this.draglocal_OffY = 0;
	
	this.item = item;
	this.localMatrix = null;
}
		
draggable.prototype.isUnderDrag = function () {	
	return this.bDragging;
}

draggable.prototype.setDropLocation = function (mx, my) {
	this.m_dropx = mx - this.draglocal_OffX;
	this.m_dropy = my - this.draglocal_OffY; 
	
	//var tMat = new Snap.Matrix();
	//tMat.translate(this.m_dropx, this.m_dropy);
	//this.item.transform(tMat);	
	
	var m = this.localMatrix.clone();
	m.translate(this.m_dropx, this.m_dropy);
	this.item.attr({
		transform: m
		});
}

draggable.prototype.startDrag = function (mx, my) {
	this.bDragging = true;
	this.draglocal_OffX = mx;
	this.draglocal_OffY = my;
	this.localMatrix = this.item.transform().localMatrix.clone();
	this.setDropLocation(mx, my);
}

draggable.prototype.stopDrag = function () {	
	
	bReturn = false;
	
	//
	/*
	var m = this.item.transform().localMatrix.clone();
	
	var snapX = m.x() % 100;
	var snapY = m.y() % 100;
	
	snapX = snapX == 0 ? 0 : -snapX;
	snapY = snapY == 0 ? 0 : -snapY;
	
	m.translate(snapX,snapY);
	this.item.attr({
		transform: m
		});
	*/
	//
	
	this.localMatrix = null;
	
	this.m_dropx = 0;
	this.m_dropy = 0;
		
	this.bDragging = false;
	
	if ((0 != this.m_dropx) || (0 != this.m_dropy)) {
		bReturn = true;	
	}
	
	return bReturn;
}
	
/// SELECTION

function selection() {
	
	this.clear = function() {
		this.arrItems = [];
	}
	
	this.clear();
}

selection.prototype.isEmpty = function () {
	var bReturn = true;
	
	if (0 < this.arrItems.length) {
		bReturn = false;
	}
		
	return bReturn;
}
	
selection.prototype.addItem = function (item) {
	this.arrItems.push(item);
}
	
selection.prototype.containsPoint = function (lx, ly) {
	var bReturn = false;
	
	for (var index in this.arrItems) {
		item = this.arrItems[index];
		if ((lx >= item.m_x) && (lx <= item.m_x + item.m_w ) && (ly >= item.m_y) && (ly <= item.m_y + item.m_h)) {
			bReturn = bReturn || true;
		}
	}
	
	return bReturn;
}
	
selection.prototype.setDropLocation = function (mx, my) {
	for (var index in this.arrItems) {
		item = this.arrItems[index];
		item.m_dragObj.setDropLocation(mx, my);
	}
}
	
selection.prototype.startDrag = function (mx, my) {
	for (var index in this.arrItems) {
		item = this.arrItems[index];
		item.m_dragObj.startDrag(mx, my);
	}
	
	//enableMouseMotion();
}
	
selection.prototype.stopDrag = function () {		
	var bReturn = false;
	
	for (var index in this.arrItems) {
		item = this.arrItems[index];
		bReturn = bReturn || item.m_dragObj.stopDrag();
	}
		
	//disableMouseMotion();
	
	return bReturn;
}
	
selection.prototype.isUnderDrag = function () {
	var bReturn = false;
	
	for (var index in this.arrItems) {
		item = this.arrItems[index];
		bReturn = bReturn || item.m_dragObj.isUnderDrag();
	}
	
	return bReturn;
}
		
/// PANNING

function panable() {
	this.bPanning = false;

	this.panDropLeft = 0;
	this.panDropRight = 0;
	this.panDropTop = 0;
	this.panDropBottom = 0;

	this.panlocal_OffX = 0;
	this.panlocal_OffY = 0;	
	
	this.cleft = 0;		
	this.cright = 0;
	this.ctop = 0;
	this.cbottom = 0;
}

panable.prototype.isUnderPan = function () {
	return this.bPanning;
}

panable.prototype.startPan = function (cleft, cright, ctop, cbottom, mx, my) {

	this.bPanning = true;
	
	this.panDropLeft = cleft;
	this.panDropRight = cright;
	this.panDropTop = ctop;
	this.panDropBottom = cbottom;
			
	this.panlocal_OffX = mx;
	this.panlocal_OffY = my;
	
	//enableMouseMotion();
}
	
panable.prototype.stopPan = function () {
	
	var bReturn = false;
	
	this.cleft = this.panDropLeft;
	this.cright = this.panDropRight;
	this.ctop = this.panDropTop;
	this.cbottom = this.panDropBottom;
	
	this.bPanning = false;
	
	if ((this.panDropLeft != this.panDropRight) && (this.panDropTop != this.panDropBottom)) {
		if ((this.cleft != this.panDropLeft) || (this.cright != this.panDropRight) || (this.ctop != this.panDropTop) || (this.cbottom != this.panDropBottom)) {
			bReturn = true;
		}
	}
	
	//disableMouseMotion();
	
	return bReturn;
}
	
panable.prototype.setPanExtents = function (l, r, t, b) {
	this.cleft = l;
	this.cright = r;
	this.ctop = t;
	this.cbottom = b;
}

panable.prototype.updatePanExtents = function (mx, my, w, h) {
	var nx = mx - this.panlocal_OffX;
	var ny = my - this.panlocal_OffY;
	
	var tmpLeft = this.cleft - nx;
	var tmpRight = tmpLeft + w;
	var tmpTop = this.ctop - ny;
	var tmpBottom = tmpTop + h;
	
	if ((tmpLeft != tmpRight) && (tmpTop != tmpBottom)) {
		this.panDropLeft = tmpLeft;
		this.panDropRight = tmpRight;
		this.panDropTop = tmpTop;
		this.panDropBottom = tmpBottom;
	}
}
	
panable.prototype.getPanExtents = function () {
	return [this.cleft, this.cright, this.ctop, this.cbottom];
}

/// Zooming

function zoomable() {
	this.bZooming = false;
			
	this.zoomRESET = 1.0;
	this.zoomMIN = 1.0 / 1024;
	this.zoomMAX = 1.0 * 1024;

	this.bZoomH = true;
	this.bZoomV = true;	
}

zoomable.prototype.isUnderZoom = function () {
	return this.bZooming;
}

zoomable.prototype.recalculateVirtualSize = function (w, h) {	
	var nw = w;
	var nh = h;
	
	if (true == this.bZoomV) {
		nh = h*this.zoomlevel;
	}	
	
	if (true == this.bZoomH) {
		nw = w*this.zoomlevel;
	}
	
	return [nw, nh];
}
	
zoomable.prototype.resetZoomlevel = function () {
	this.zoomlevel = this.zoomRESET;
	this.prev_zoomlevel = this.zoomlevel;
}
	
zoomable.prototype.normalizeZoomlevel = function () {
	if (this.zoomlevel > this.zoomMAX) {
		this.zoomlevel = this.zoomMAX;
	}
		
	if (this.zoomlevel < this.zoomMIN) {
		this.zoomlevel = this.zoomMIN;
	}	
}
	
zoomable.prototype.increaseZoomlevel = function () {
	this.prev_zoomlevel = this.zoomlevel;
	
	if ((this.zoomlevel >= this.zoomMIN) && (this.zoomlevel < this.zoomMAX)) {
		this.zoomlevel = this.zoomlevel * 1.2;
	}
	
	this.normalizeZoomlevel();
}
	
zoomable.prototype.decreaseZoomlevel = function () {
	this.prev_zoomlevel = this.zoomlevel;
	
	if ((this.zoomlevel > this.zoomMIN) && (this.zoomlevel <= this.zoomMAX)) {
		this.zoomlevel = this.zoomlevel / 1.2;
	}
	
	this.normalizeZoomlevel();
}
	
///

function makeDraggable(item) {
	item.m_dragObj = new draggable(item);
	//item["m_dragObj"] = new draggable();
}

///
	
Snap.plugin(function (Snap, Element, Paper, global) {
	
	var myproto = Element.prototype;
	
	//
	
	var m_w = 1024;
	var m_h = 640;
	
	var currVirtualWidth = m_w;
	var currVirtualHeight = m_h;
	
	var cursorX = 0;
	var cursorY = 0;
	
	var cleft = 1.0;
	var cright = 1.0;
	var ctop = 1.0;
	var cbottom = 1.0;
	
	//
	
	var bCTRLpressed = false;
	
	var m_SelObj;
	var m_PanObj;
	var m_ZoomObj;
		
	//

	function printInfo (node) {
		document.getElementById("zoom").innerHTML= "<a>zoom =" + m_ZoomObj.zoomlevel.toFixed(4) + "</a>";
		document.getElementById("cursorX").innerHTML= "<a>cursorX =" + cursorX.toFixed(4) + "</a>";
		document.getElementById("cursorY").innerHTML= "<a>cursorY =" + cursorY.toFixed(4) + "</a>";
		/*
		document.getElementById("old_width").innerHTML= "<a>old_width =" + old_width.toFixed(4) + "</a>";
		document.getElementById("old_height").innerHTML= "<a>old_height =" + old_height.toFixed(4) + "</a>";
		document.getElementById("new_width").innerHTML= "<a>new_width =" + new_width.toFixed(4) + "</a>";
		document.getElementById("new_height").innerHTML= "<a>new_height =" + new_height.toFixed(4) + "</a>";
		document.getElementById("cleft").innerHTML= "<a>cleft =" + cleft.toFixed(4) + "</a>";
		document.getElementById("cright").innerHTML= "<a>cright =" + cright.toFixed(4) + "</a>";
		document.getElementById("ctop").innerHTML= "<a>ctop =" + ctop.toFixed(4) + "</a>";
		document.getElementById("cbottom").innerHTML= "<a>cbottom =" + cbottom.toFixed(4) + "</a>";
		document.getElementById("tx").innerHTML= "<a>tx =" + tx.toFixed(4) + "</a>";
		document.getElementById("ty").innerHTML= "<a>ty =" + ty.toFixed(4) + "</a>";
		*/
	}
	
	function applyExtents (node) {	
		var strVB;
		
		if(false == m_PanObj.isUnderPan())
		{
			strVB = cleft + " " + ctop + " " + m_w*m_ZoomObj.zoomlevel + " " + m_h*m_ZoomObj.zoomlevel;
		} else {
			strVB = m_PanObj.panDropLeft + " " + m_PanObj.panDropTop + " " + (m_PanObj.panDropRight-m_PanObj.panDropLeft) + " " + (m_PanObj.panDropBottom-m_PanObj.panDropTop);
		}
			
		node.setAttribute("viewBox", strVB);
		
		printInfo(node);
	}
			
	function setCursorVirtualLoc(lx, ly, ex, ey) {
		cleft = lx - (currVirtualWidth*ex)/m_w;
		cright = cleft + currVirtualWidth;
		ctop = ly - (currVirtualHeight*ey)/m_h;
		cbottom = ctop + currVirtualHeight;
		
		m_PanObj.setPanExtents(cleft, cright, ctop, cbottom);
	}
		
	function localToVirtual(ex, ey) {
		var mx = cleft + (currVirtualWidth * ex)/m_w;
		var my = ctop + (currVirtualHeight * ey)/m_h;
		return [mx, my];
	}
	
	///  
		
	function updatePanExtents(mx, my) {
		m_PanObj.updatePanExtents(mx, my, currVirtualWidth, currVirtualHeight);
	}
			
	function handleMouseMove (e) {
		if (e.preventDefault) {
			e.preventDefault();
		}
		
		//
		//evtElement = Snap.getElementByPoint(e.clientX, e.clientY);
		//if(null != evtElement) {
			//if( evtElement.node == this ) {
				
				var containerElement = document.getElementById("mycontainer"); 
				
				var ex = e.pageX - containerElement.offsetLeft;
				var ey = e.pageY - containerElement.offsetTop;
				
				var localPts = localToVirtual(ex, ey);
				var lx = localPts[0];
				var ly = localPts[1];
				cursorX = lx;
				cursorY = ly;				
				
				if (true == m_PanObj.isUnderPan()) {
					updatePanExtents(lx, ly);
					
					applyExtents(e.target);
				}
				
				if (true == m_SelObj.isUnderDrag()) { 
					m_SelObj.setDropLocation(lx, ly);					
				}	
				
				printInfo(e.target);	
			//}
		//}
	}
	
	function handleMouseDown (e) {
		if (e.preventDefault) {
			e.preventDefault();
		}
		
		//evtElement = Snap.getElementByPoint(e.clientX, e.clientY);
		//if(null != evtElement) {
			//if( evtElement.node == this ) {	
					
				var containerElement = document.getElementById("mycontainer"); 
				
				var ex = e.pageX - containerElement.offsetLeft;
				var ey = e.pageY - containerElement.offsetTop;
				
				var localPts = localToVirtual(ex, ey);
				var lx = localPts[0];
				var ly = localPts[1];
				
				if (true == m_SelObj.containsPoint(lx, ly)) {
					m_SelObj.startDrag(lx, ly);									
				} else {
					
					child = null;
					evtElement = Snap.getElementByPoint(e.clientX, e.clientY);
					if(evtElement.node != this)
					{
						// Only select svg elements, do not select svg surface
						child = evtElement;
						
						// get highest draggable object
						// WARNING : Needs to be corrected for nested groups
						if(child.m_dragObj === undefined)
						{
							child = child.parent();
						}
						
					}
					
					if( null != child ) {
						if (false == bCTRLpressed) {
							m_SelObj.clear();
						}
						
						m_SelObj.addItem(child);
						
						m_SelObj.startDrag(lx, ly);											
					
					} else {
						m_SelObj.clear();
						
						m_PanObj.startPan(cleft, cright, ctop, cbottom, lx, ly);
						setCursorVirtualLoc(lx, ly, ex, ey);
						
						applyExtents(e.target);
					}
				}	
			//}
		//}				
	}

	function handleMouseUp (e) {
		if (e.preventDefault) {
			e.preventDefault();
		}
		
		//
		//var evtElement = Snap.getElementByPoint(e.clientX, e.clientY);
		//if(null != evtElement) {
			//if( evtElement.node == this ) {	
					
				var containerElement = document.getElementById("mycontainer"); 
				
				var ex = e.pageX - containerElement.offsetLeft;
				var ey = e.pageY - containerElement.offsetTop;
				
				var localPts = localToVirtual(ex, ey);
				var lx = localPts[0];
				var ly = localPts[1];
				
				if (true == m_SelObj.isUnderDrag()) {
					bTmpUpdate = m_SelObj.stopDrag();
				} else if (true == m_PanObj.isUnderPan()) {		
					var bTmpUpdate = m_PanObj.stopPan();
					
					var panPts = m_PanObj.getPanExtents();
					var l = panPts[0];
					var r = panPts[1];
					var t = panPts[2];
					var b = panPts[3];
					
					cleft = l;
					cright = r;
					cbottom = b;
					ctop = t;
					
					applyExtents(e.target);
				}
			//}
		//}			
	}
	
	function handleMouseWheel (e) {
		if (e.preventDefault) {
			e.preventDefault();
		}	
		
		var evt = window.event || e ;
		var delta=evt.detail? evt.detail*(-120) : evt.wheelDelta;
		
		//var evtElement = Snap.getElementByPoint(e.clientX, e.clientY);
		//if(null != evtElement) {
			//if( evtElement.node == this ) {	
			
				var containerElement = document.getElementById("mycontainer"); 
				
				var ex = e.pageX - containerElement.offsetLeft;
				var ey = e.pageY - containerElement.offsetTop;
				
				var localPts = localToVirtual(ex, ey);
				var lx = localPts[0];
				var ly = localPts[1];
				cursorX = lx;
				cursorY = ly;				
				
				if (delta > 0) {
					m_ZoomObj.increaseZoomlevel();
					var size = m_ZoomObj.recalculateVirtualSize(m_w, m_h);
					currVirtualWidth = size[0];
					currVirtualHeight = size[1];
					
					setCursorVirtualLoc(lx, ly, ex, ey);
					
					applyExtents(e.target);
					
				} else if (delta < 0) {
					m_ZoomObj.decreaseZoomlevel();
					var size = m_ZoomObj.recalculateVirtualSize(m_w, m_h);
					currVirtualWidth = size[0];
					currVirtualHeight = size[1];
					
					setCursorVirtualLoc(lx, ly, ex, ey);
					
					applyExtents(e.target);
				}
			//}
		//}
	}	
	
	function handleKeyDown (e) {
		//
		switch(e.keyCode)
		{
			case 17: 
			{
				bCTRLpressed = true;
			}
			break;
		}
	}

	function handleKeyUp (e) {
		//
		switch(e.keyCode)
		{
			case 17: 
			{
				bCTRLpressed = false;
			}
			break;
		}		
	}
	
	function handleKeyPress (e) {
		//
	}
	
	//
	
	function registerHandlers(node) {
		window.addEventListener("keydown", handleKeyDown, false);
		window.addEventListener("keypress", handleKeyPress, false);
		window.addEventListener("keyup", handleKeyUp, false);
				
		node.addEventListener('mousedown', handleMouseDown, false);		
		node.addEventListener('mousemove', handleMouseMove, false);
		node.addEventListener('mouseup', handleMouseUp, false);
			
		// register Mouse Wheel Handler
		if (navigator.userAgent.toLowerCase().indexOf('webkit') >= 0) {
			node.addEventListener('mousewheel', handleMouseWheel, false);
		} else {
			node.addEventListener('DOMMouseScroll', handleMouseWheel, false);
		}
		
		// WARNING: IE?
	}
	
	//
	
	myproto.initMyZoom = function (arg_width, arg_height) {
		m_w = arg_width;
		m_h = arg_height;
		
		currVirtualWidth = m_w;
		currVirtualHeight = m_h;
		
		m_SelObj = new selection();
		
		m_PanObj = new panable();
		
		m_ZoomObj = new zoomable();
		m_ZoomObj.resetZoomlevel();	
		
		cursorX = m_w/2;
		cursorY = m_h/2	;	
		setCursorVirtualLoc(cursorX, cursorY, cursorX, cursorY);
		
		var viewport = this.node;
		registerHandlers(viewport);
		applyExtents(viewport);
	}	
});
