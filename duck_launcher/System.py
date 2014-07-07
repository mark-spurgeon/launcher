# -*- coding: utf-8 -*-
#########
#Copyright (C) 2014  Mark Spurgeon <markspurgeon96@hotmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
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
import Xlib
import sys
import Config
def sysAction(what):
	platform="systemd"
	import dbus 
	bus = dbus.SystemBus()
	if platform=="systemd":
		try:
			#For systemd service management
			bus_object = bus.get_object("org.freedesktop.login1", "/org/freedesktop/login1") 
			if what=="sleep":
				bus_object.Suspend(0, dbus_interface="org.freedesktop.login1.Manager") 
			elif what=="restart":
				bus_object.Reboot(0, dbus_interface="org.freedesktop.login1.Manager") 
			elif what=="shutdown":
				bus_object.PowerOff(0, dbus_interface="org.freedesktop.login1.Manager") 
			else:print("Not supported yet.")
		except:print("Tried to {}, but didn't work, please report.".format(what))
	elif platform=="upstart":
		#For upstart service management
		try:
			if what=="sleep":
				bus_object = bus.get_object("org.freedesktop.UPower", " /org/freedesktop/UPower") 
				bus_object.Suspend(0, dbus_interface="org.freedesktop.UPower") 
			elif what=="restart":
				bus_object = bus.get_object("org.freedesktop.ConsoleKit", "/org/freedesktop/ConsoleKit/Manager") 
				bus_object.Restart(0, dbus_interface="org.freedesktop.ConsoleKit.Manager") 
			elif what=="shutdown":
				bus_object = bus.get_object("org.freedesktop.ConsoleKit", "/org/freedesktop/ConsoleKit/Manager") 
				bus_object.Stop(0, dbus_interface="org.freedesktop.ConsoleKit.Manager") 
			else:print("Not supported yet.")
		except: print("Tried to {}, but didn't work, please report.".format(what))
class AreYouSure(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		d = QtGui.QDesktopWidget()
		self.w=350
		self.h=250
		self.height =d.availableGeometry().height()
		self.width =d.availableGeometry().width()
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.state=""
		self.setGeometry(self.width/2-self.w/2,self.height/2-self.h/2,self.w,self.h)
	def paintEvent(self, e):
		qp=QtGui.QPainter()
		qp.begin(self)
		qp.setFont(QtGui.QFont(Config.get()["font"],12))
		qp.setRenderHint(QtGui.QPainter.Antialiasing)
		qp.setBrush(QtGui.QColor(self.r,self.g,self.b))
		qp.setPen(QtGui.QColor(0,0,0,0))
		qp.drawRoundedRect(QtCore.QRectF(0,0,self.w,self.h),4,4)
		'''
		qp.setBrush(QtGui.QColor(20,20,20,10))
		qp.drawRect(0,self.h-50,self.w/2-6,50)
		qp.setBrush(QtGui.QColor(20,20,20,20))
		qp.drawRect(self.w/2+2,self.h-50,self.w/2,50)
		'''
		#title
		textRect=QtCore.QRectF(0,0,self.w,40)
		qp.setPen(QtGui.QColor(250,250,250))
		if self.state=="logout":
			qp.drawText(textRect,QtCore.Qt.AlignCenter,"Sorry, logout is not supported yet..")
			i = QtGui.QIcon("/usr/share/duck-launcher/icons/logout.svg")
			i.paint(qp, self.w/2-40,self.h/2-60,80,80)
		if self.state=="restart":
			qp.drawText(textRect,QtCore.Qt.AlignCenter,"Are sou sure you want to restart?")
			i = QtGui.QIcon("/usr/share/duck-launcher/icons/restart.svg")
			i.paint(qp, self.w/2-40,self.h/2-60,80,80)
		if self.state=="shutdown":
			qp.drawText(textRect,QtCore.Qt.AlignCenter,"Are you sure you want to shut down?")
			i = QtGui.QIcon("/usr/share/duck-launcher/icons/shutdown.svg")
			i.paint(qp, self.w/2-40,self.h/2-60,80,80)
		##Yes No
		qp.drawLine(20,self.h-50, self.w-20,self.h-50)	
		qp.drawLine(self.w/2, self.h-40, self.w/2,self.h-10)
		qp.drawText(QtCore.QRectF(0,self.h-50,self.w/2-6,50),QtCore.Qt.AlignCenter, "No")
		qp.drawText(QtCore.QRectF(self.w/2+2,self.h-50,self.w/2,50),QtCore.Qt.AlignCenter, "Yes")
	def mousePressEvent(self, e):
		if self.h-50<e.y()<self.h:
			if e.x()<self.w/2-6:
				self.close()
			elif e.x()>self.w/2+2:
				sysAction(self.state)
				self.close()
	def update_all(self):
		import Config
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.update()
class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint|QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		#self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
		#Values
		self.size=int(Config.get()['size'])
		d = QtGui.QDesktopWidget()
		self.height =Xlib.display.Display().screen().root.get_geometry().height
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.win_len=4
		self.move(self.size+10,self.height-self.size*1.5-2)
		self.resize(self.size*self.win_len*1.5,self.size*1.5)
		self.sure=AreYouSure()
	def paintEvent(self,e):
		qp=QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		qp.setPen(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.setBrush(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.drawRoundedRect(QtCore.QRectF(10,0,self.size*self.win_len*1.3+10,self.size*1.5),2,2)
		qp.setPen(QtGui.QColor(250,250,250))
		qp.setBrush(QtGui.QColor(250,250,250))
		qp.drawRect(9,0,5,self.size*1.8)
		half_height=self.size*1.1
		icon=QtGui.QIcon("/usr/share/duck-launcher/icons/win.svg")
		icon.paint(qp, -10,half_height-10, 20,20)
		#Sleep
		sl=QtGui.QIcon("/usr/share/duck-launcher/icons/sleep.svg")
		sl.paint(qp, 20,10,self.size,self.size)
		#Log out
		lo=QtGui.QIcon("/usr/share/duck-launcher/icons/logout.svg")
		lo.paint(qp, self.size*1.3+20,10,self.size,self.size)
		#Restart
		re=QtGui.QIcon("/usr/share/duck-launcher/icons/restart.svg")
		re.paint(qp, self.size*2*1.3+20,10,self.size,self.size)
		#Shutdown
		sd=QtGui.QIcon("/usr/share/duck-launcher/icons/shutdown.svg")
		sd.paint(qp, self.size*3*1.3+20,10,self.size,self.size)
		'''
		#Close window
		cl=QtGui.QIcon("/usr/share/duck-launcher/icons/close.svg")
		cl.paint(qp, self.size*4*1.3+20,10,self.size,self.size)
		'''
	def mousePressEvent(self,e):
		x_m,y_m=e.x(),e.y()
		if 10<y_m<self.size+10:
			self.close()
			if 20<x_m<self.size+20:
				sysAction("sleep")
			if self.size*1.3+20<x_m<self.size*1.3+20+self.size:
				self.sure.state="logout"
				self.sure.show()
			if self.size*2*1.3+20<x_m<self.size*2*1.3+20+self.size:
				self.sure.state="restart"
				self.sure.show()
			if self.size*3*1.3+20<x_m<self.size*3*1.3+20+self.size:
				self.sure.state="shutdown"
				self.sure.show()
			'''
			if self.size*4*1.3+20<x_m<self.size*4*1.3+20+self.size:
				sys.exit()
			'''
	def update_all(self):
		import Config
		self.size=int(Config.get()['size'])
		self.height =Xlib.display.Display().screen().root.get_geometry().height
		self.move(self.size+10,self.height-self.size*1.5)
		self.resize(self.size*self.win_len*1.5,self.size*1.5)
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.sure.update_all()
		self.update()
