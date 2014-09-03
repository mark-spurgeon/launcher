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

from PySide import QtGui,QtCore
import dbus
import dbus.service
import Config
import Main
class Window(QtGui.QMainWindow):
	def __init__(self,parent=None):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)#|QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
		#Values
		self.parent=parent
		self.app={}
		self.conf=self.parent.conf
		self.drawButtonRect=False
		self.buttonRect=None
		self.width=200
		self.height=30*3
		self.y_pos=147
		self.size=int(Config.get()["size"])
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.move(self.size+10,self.y_pos)
		self.resize(self.width+10,self.height+10)
	def paintEvent(self,e):
		qp=QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		qp.setPen(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.setBrush(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.drawRoundedRect(QtCore.QRectF(10,0,self.width-10,self.height),2,2)
		qp.setPen(QtGui.QColor(250,250,250,255))
		qp.setBrush(QtGui.QColor(250,250,250,255))
		qp.drawRect(9,0,5,self.height)
		icon=QtGui.QIcon("/usr/share/duck-launcher/icons/win.svg")
		icon.paint(qp, -10,self.size/2-10, 20,20)
		#
		qp.setFont(QtGui.QFont(Config.get()["font"],12))
		t_rect=QtCore.QRectF(10,0,self.width-10,30)
		qp.drawText(t_rect,QtCore.Qt.AlignCenter,self.app["name"])
		qp.drawLine(26,30,self.width-20,30)
		#open
		if self.drawButtonRect==True and self.buttonRect!=None:
			qp.setPen(QtGui.QColor(0,0,0,0))
			qp.setBrush(QtGui.QColor(254,254,255,60))
			qp.drawRect(self.buttonRect)
			
		qp.setPen(QtGui.QColor(10,10,10,145))
		qp.setFont(QtGui.QFont(Config.get()["font"],10))
		o_rect=QtCore.QRectF(50,30,self.width-10,30)
		qp.drawText(o_rect,QtCore.Qt.AlignVCenter,"Open")
		removeIcon=QtGui.QIcon("/usr/share/duck-launcher/icons/open.svg")
		removeIcon.paint(qp, 25,34,20,20)
		#remove
		qp.setPen(QtGui.QColor(12,10,10,140))
		r_rect=QtCore.QRectF(50,60,self.width-10,30)
		qp.drawText(r_rect, QtCore.Qt.AlignVCenter,"Remove")
		removeIcon=QtGui.QIcon("/usr/share/duck-launcher/icons/remove.svg")
		removeIcon.paint(qp, 25,64,20,20)
	def mouseMoveEvent(self,e):
		self.mousePressEvent(e)
	def mousePressEvent(self,e):
		x_m,y_m=e.x(),e.y()
		self.drawButtonRect=False
		if 15<x_m<self.width-15 and 30<y_m<55:
			#open
			self.buttonRect=QtCore.QRectF(10,30,self.width-10,30)
			self.drawButtonRect=True
			self.update()
		elif 15<x_m<self.width-15 and 57<y_m<85:
			self.buttonRect=QtCore.QRectF(10,60,self.width-10,26)
			self.drawButtonRect=True
			self.update()
		else:
			self.drawButtonRect=False
			self.buttonRect=None
			self.update()
	def mouseReleaseEvent(self,e):
		x_m, y_m = e.x(),e.y()
		self.drawButtonRect=False
		if 15<x_m<self.width-15 and 30<y_m<55:
			print("[Duck Launcher] Launching '{0}' with '{1}'".format(self.app["name"],self.app["exec"]) )
			thread = Main.Launch(parent=self)
			thread.app=self.app["exec"]
			thread.start()
			self.close()
		if 15<x_m<self.width-15 and 65<y_m<85:
			print("Removing {}".format(self.app["name"]))
			new_list = [x for x in self.conf["dock-apps"] if str(x) != self.app["name"]]
			self.conf["dock-apps"]=new_list
			self.parent.update_all(self.conf)
			self.close()
	def updateWidth(self):
		self.drawButtonRect=False
		if self.app.has_key("name"):
			textFont =QtGui.QFont(Config.get()["font"],16)
			fm = QtGui.QFontMetrics(textFont)
			whole_width=0
			for i,s in enumerate(self.app["name"]):
				w = int(fm.charWidth(self.app["name"],i))
				whole_width+=w
			if whole_width<130:
				whole_width=130
			self.width=whole_width
			self.update_all(self.conf)
	def setTopPosition(self,pos):
		self.y_pos=pos
		self.update_all(self.conf)
	def setApp(self,_dict):
		self.app=_dict
		self.update_all(self.conf)
	def update_all(self, conf):
		self.conf=conf
		self.size=int(self.conf['size'])
		self.move(self.size+10,self.y_pos)
		self.resize(self.width+10,self.height+10)
		self.r=int(self.conf["r"])
		self.g=int(self.conf["g"])
		self.b=int(self.conf["b"])
		self.update()
