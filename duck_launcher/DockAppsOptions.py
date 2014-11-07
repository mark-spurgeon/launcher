#! /usr/bin/python
# -*- coding: utf-8 -*-
#########
#Copyright (C) 2014  Mark Spurgeon <markspurgeon96@hotmail.com>
	
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########

from PyQt4 import QtGui,QtCore
import dbus
import dbus.service
import Config
import Main
import Apps
def getConfigIface():
	# Enable glib main loop support
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	# Get the session bus
	bus = dbus.SessionBus()
	try:
		# Get the remote object
		remote_object = bus.get_object("org.duck.Launcher","/DBusWidget")
		# Get the remote interface for the remote object
		iface = dbus.Interface(remote_object, "org.duck.Launcher")
	except dbus.DBusException:
		iface=None

	return iface
def moveUpList(app_name, dock_apps):
	new_l=None
	dock_apps=[str(a) for a in dock_apps]
	if dock_apps.index(app_name) >0 and app_name in dock_apps:
		index=None
		for i, d in enumerate(dock_apps):
			if str(d)==str(app_name):
				index=i
				break
		if index!=None:
			new_l=dock_apps
			new_l.pop(index)
			new_l.insert(index-1,app_name)
	return new_l
def moveDownList(app_name, dock_apps):
	new_l=None
	dock_apps=[str(a) for a in dock_apps]
	if dock_apps.index(app_name) < len(dock_apps) and app_name in dock_apps:

		index=None
		for i, d in enumerate(dock_apps):
			if str(d)==str(app_name):
				index=i
				break
		if index!=None:
			new_l=dock_apps
			new_l.pop(index)
			new_l.insert(index+1,app_name)
	return new_l
class Window(QtGui.QMainWindow):
	def __init__(self,parent=None):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)#|QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
		#Values
		d = QtGui.QDesktopWidget()
		self.top_pos= d.availableGeometry().y()
		self.parent=parent
		self.app={}
		self.conf=self.parent.conf
		self.drawButtonRect=False
		self.buttonRect=None
		self.width=200
		self.height=30*4
		self.y_pos=147
		self.size=int(Config.get()["size"])
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.state="normal"
		self.move(self.size+10,self.y_pos+self.top_pos)
		self.resize(self.width+10,self.height+10)
	def eventFilter(self, source, event):
		if event.type() == QtCore.QEvent.MouseMove:
			if event.buttons() == QtCore.Qt.NoButton:
				pos = event.pos()
				print pos
			else:
				print event.pos()
		if event.type() == QtCore.QEvent.KeyPress:
			print "aa"
			
		return QtGui.QMainWindow.eventFilter(self, source, event)
	def paintEvent(self,e):
		qp=QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		qp.setPen(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.setBrush(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.drawRoundedRect(QtCore.QRectF(10,0,self.width-10,self.height),2,2)
		qp.setPen(QtGui.QColor(255,255,255,255))
		qp.setBrush(QtGui.QColor(255,255,255,255))
		qp.drawRect(9,0,5,self.height)
		icon=QtGui.QIcon("/usr/share/duck-launcher/icons/win.svg")
		icon.paint(qp, -10,self.size/2-10, 20,20)
		#
		qp.setFont(QtGui.QFont(Config.get()["font"],12))
		t_rect=QtCore.QRectF(10,0,self.width-10,30)
		t_rect2=QtCore.QRectF(11,1,self.width-10,30)
		qp.setPen(QtGui.QColor(40,40,40,80))
		qp.drawText(t_rect2,QtCore.Qt.AlignCenter,self.app["name"])
		qp.setPen(QtGui.QColor(255,255,255,255))
		qp.drawText(t_rect,QtCore.Qt.AlignCenter,self.app["name"])
		qp.drawLine(26,30,self.width-20,30)
		if self.drawButtonRect==True and self.buttonRect!=None:
			qp.setPen(QtGui.QColor(0,0,0,0))
			qp.setBrush(QtGui.QColor(255,255,255,40))
			qp.drawRect(self.buttonRect)
		if self.state=="normal":
			qp.setFont(QtGui.QFont(Config.get()["font"],10))
			o_rect=QtCore.QRectF(50,30,self.width-10,30)
			qp.setPen(QtGui.QColor(255,255,255,255))
			qp.drawText(o_rect,QtCore.Qt.AlignVCenter,"Open")
			removeIcon=QtGui.QIcon("/usr/share/duck-launcher/icons/open.svg")
			removeIcon.paint(qp, 25,34,20,20)
			#move
			r_rect=QtCore.QRectF(50,60,self.width-10,30)
			qp.drawText(r_rect, QtCore.Qt.AlignVCenter,"Move")
			removeIcon=QtGui.QIcon("/usr/share/duck-launcher/icons/move.svg")
			removeIcon.paint(qp, 25,64,20,20)

			#remove
			r_rect=QtCore.QRectF(50,90,self.width-10,30)
			qp.drawText(r_rect, QtCore.Qt.AlignVCenter,"Remove")
			removeIcon=QtGui.QIcon("/usr/share/duck-launcher/icons/remove.svg")
			removeIcon.paint(qp, 25,94,20,20)
		elif self.state=="moving":
			if self.width<150:
				self.width=150
				self.resize(150,self.height)
			icon=Apps.ico_from_name(self.app["icon"])
			if icon!=None:
				w = self.width/2-40
				icon.paint(qp,w,40,70,70)
			upicon=QtGui.QIcon("/usr/share/duck-launcher/icons/up.svg")
			upicon.paint(qp, self.width/2+35,35,40,40)
			downicon=QtGui.QIcon("/usr/share/duck-launcher/icons/down.svg")
			downicon.paint(qp, self.width/2+35,self.height-45,40,40)

	def mouseMoveEvent(self,e):
		self.mousePressEvent(e)
	def mousePressEvent(self,e):
		x_m,y_m=e.x(),e.y()
		self.drawButtonRect=False
		if self.state=="normal":
			if 15<x_m<self.width-15 and 30<y_m<55:
				#open
				self.buttonRect=QtCore.QRectF(10,30,self.width-10,30)
				self.drawButtonRect=True
			elif 15<x_m<self.width-15 and 57<y_m<85:
				#move
				self.buttonRect=QtCore.QRectF(10,60,self.width-10,30)
				self.drawButtonRect=True
			elif 15<x_m<self.width-15 and 87<y_m<115:
				#remove
				self.buttonRect=QtCore.QRectF(10,90,self.width-10,30)
				self.drawButtonRect=True
			else:
				self.drawButtonRect=False
				self.buttonRect=None
		elif self.state=="moving":
			if 35<y_m<80 and self.width/2+35<x_m<self.width/2+75:
				self.buttonRect=QtCore.QRectF(self.width/2+35,35,40,40)
				self.drawButtonRect=True
			if self.height-45<y_m<self.height-5 and self.width/2+35<x_m<self.width/2+75:
				self.buttonRect=QtCore.QRectF(self.width/2+35,self.height-45,40,40)
				self.drawButtonRect=True			
		self.update()
	def mouseReleaseEvent(self,e):
		x_m, y_m = e.x(),e.y()
		self.drawButtonRect=False
		if self.state=="normal":
			if 15<x_m<self.width-15 and 30<y_m<55:
				print("[Duck Launcher] Launching '{0}' with '{1}'".format(self.app["name"],self.app["exec"]) )
				thread = Main.Launch(parent=self)
				thread.app=self.app["exec"]
				thread.start()
				self.close()
			if 15<x_m<self.width-15 and 65<y_m<85:
				print "Moving the app"
				self.state="moving"
			if 15<x_m<self.width-15 and 87<y_m<115:
				print("Removing {}".format(self.app["name"]))
				new_list = [x for x in self.conf["dock-apps"] if str(x) != self.app["name"]]
				self.conf["dock-apps"]=new_list
				self.parent.update_all(self.conf)
				self.close()
		elif self.state=="moving":
			if 35<y_m<80 and self.width/2+35<x_m<self.width/2+75:
				print "Moving Ùp"
				new_dock_apps = moveUpList(self.app["name"], self.parent.conf["dock-apps"])
				if new_dock_apps!=None:
					index = new_dock_apps.index(self.app["name"])
					pos = self.parent.OPEN_STATE_TOP+self.parent.ICO_TOP*index+10
					self.setTopPosition(pos)
					self.parent.conf["dock-apps"]=new_dock_apps
					self.parent.update_all(self.parent.conf)
			if self.height-45<y_m<self.height-5 and self.width/2+35<x_m<self.width/2+75:
				print "Moving Down"
				new_dock_apps = moveDownList(self.app["name"], self.parent.conf["dock-apps"])
				if new_dock_apps!=None:
					d_index = new_dock_apps.index(self.app["name"])
					pos = self.parent.OPEN_STATE_TOP+self.parent.ICO_TOP*d_index+10
					self.setTopPosition(pos)
					self.parent.conf["dock-apps"]=new_dock_apps
					self.parent.update_all(self.parent.conf)
		self.update()
	def updateWidth(self):
		self.drawButtonRect=False
		if self.app.has_key("name"):
			textFont =QtGui.QFont(Config.get()["font"],16)
			fm = QtGui.QFontMetrics(textFont)
			whole_width=0
			for i,s in enumerate(self.app["name"]):
				w = int(fm.charWidth(self.app["name"],i))
				whole_width+=w
			if whole_width<110:
				whole_width=110
			self.width=whole_width
			self.update_all(self.conf)
	def setTopPosition(self,pos):
		self.y_pos=pos
		self.update_all(self.conf)
	def setApp(self,_dict):
		self.app=_dict
		self.update_all(self.conf)
		self.state="normal"
	def update_all(self, conf):
		self.conf=conf
		self.size=int(self.conf['size'])
		self.move(self.size+10,self.y_pos)
		self.resize(self.width+10,self.height+10)
		self.r=int(self.conf["r"])
		self.g=int(self.conf["g"])
		self.b=int(self.conf["b"])
		self.update()
