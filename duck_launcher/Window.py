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
from PySide import QtCore,QtGui
import gtk
import wnck
import Xlib
#from gi.repository import Gtk
#from gi.repository import Wnck as wnck
import sys
import time
#
import Apps
import Config
#
def activateFakewin(id_):
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	for w in win:
		if id_ ==w.get_xid():
			w.activate(int(time.time()))
	
def close_window(title):
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	for w in win:
		if title==w.get_xid():
			w.close(int(time.time()))
	
########
class changeWindowState(QtCore.QThread):
	def __init__(self,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.win_info=None
		self.parent=parent
	def run(self):
		screen = wnck.screen_get_default()
		screen.force_update()
		active= screen.get_active_window()
		if active.get_name()=="ducklauncher!!!":
			active= screen.get_previously_active_window()
		win = screen.get_windows()
		for w in win:
			if self.win_info['id'] == w.get_xid():
				try:
					if w.is_minimized():
						w.activate(int(time.time()))
					elif w.get_xid()==active.get_xid():
						w.minimize()
					else:
						w.activate(int(time.time()))
				except AttributeError:
					w.activate(int(time.time()))
########
def get_open_windows():
	gtk.main_iteration()
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	windows=[]
	for w in win:
			if  'NORMAL' in str(w.get_window_type()):
				if "ducklauncher!!!"==w.get_name():
					pass			
				elif w.is_sticky()!=True and "ducklauncher!!"!=w.get_name():
					window={}	
					window['id']=w.get_xid()
					window['title'] =w.get_name()
					window['app']=w.get_application().get_name()
					windows.append(window)
	return windows
	
class open_windows(QtGui.QMainWindow):
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
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.move(self.size+10,self.height-self.size*2.4)
		self.resize(self.size*self.win_len*1.3+20,self.size*1.5)
	def paintEvent(self,e):
		qp=	QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		qp.setPen(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.setBrush(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.drawRect(10,0,self.size*self.win_len*1.3+10,self.size*1.8)
		qp.setPen(QtGui.QColor(250,250,250))
		qp.setBrush(QtGui.QColor(250,250,250))
		qp.drawRect(9,0,5,self.size*1.8)
		half_height=self.size*0.9
		icon=QtGui.QIcon("/usr/share/duck-launcher/icons/win.svg")
		icon.paint(qp, -10,half_height-10, 20,20)
		for i,w in enumerate(self.windows):
			ico = Apps.ico_from_app(w['app'])
			if ico==None:
				ico = Apps.ico_from_app(w["title"])
				if ico==None:
					ico=QtGui.QIcon("/usr/share/duck-launcher/icons/apps.svg")
			ico.paint(qp,20+self.size*i*1.3, 10, self.size*1.1, self.size*1.1)
		
	def mousePressEvent(self,e):
		x_m,y_m=e.x(),e.y()
		for i,w in enumerate(self.windows):
			if 20+self.size*i*1.3<x_m<20+self.size*(i+1)*1.1 and 10<y_m<10+self.size*1.1:
				c = changeWindowState()
				c.parent=self
				c.win_info=w
				c.start()
		self.updateApps()
	def updateApps(self):
		self.icon_size=Config.get()['size']
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.resize(self.size*self.win_len*1.3+20,self.size*1.1+20)
		self.update()
		QtGui.QApplication.processEvents()
	def update_all(self):
		import Config 
		self.size=int(Config.get()['size'])
		self.move(self.size+10,self.height-self.size*2.4)
		self.resize(self.size*self.win_len*1.3+20,self.size*2.4)
		self.r=Config.get()['r']
		self.g=Config.get()['g']
		self.b=Config.get()['b']
