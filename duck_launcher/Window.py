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
from PyQt4 import QtCore,QtGui
import gtk
import wnck
#from gi.repository import Gtk
#from gi.repository import Wnck as wnck
import os
import Image
import binascii
#
import Apps
import Config
#
def activateFakewin(id_):
	w = wnck.window_get(id_)
	w.activate(gtk.get_current_event_time())
	
def close_window(title):
	w=wnck.window_get(title)
	w.close(gtk.get_current_event_time())
	
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
		w=wnck.window_get(self.win_info ['id'])
		try:
			if w.is_minimized():
				w.activate(gtk.get_current_event_time())
			elif w.get_xid()==active.get_xid():
				w.minimize()
			else:
				w.activate(gtk.get_current_event_time())
		except AttributeError:
			w.activate(gtk.get_current_event_time())
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
					window['icon']=w.get_application().get_icon_name()
					pix=w.get_icon()
					pix= pix.scale_simple(128,128,gtk.gdk.INTERP_HYPER)
					ico_data=  pix.get_pixels_array()
					img = Image.fromarray(ico_data, 'RGBA')
					home = os.path.expanduser("~")+"/.duck"
					try:
    						os.stat(home)
					except:
    						os.mkdir(home)
					#print window					
					img.save("{0}/{1}.png".format(home,binascii.hexlify(window["icon"])))
					windows.append(window)
	return windows
	
class open_windows(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)#|QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
		#Values
		d = QtGui.QDesktopWidget()
		self.size=int(Config.get()['size'])
		self.height =d.availableGeometry().height()
		self.top_pos= d.availableGeometry().y()
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.drawButtonRect=False
		self.buttonRect=None
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.move(self.size+10,self.height-self.size*2.4+self.top_pos)
		self.resize(self.size*self.win_len*1.3+30,self.size*1.6+10)
		##
		self.timer=QtCore.QTimer()
		self.timer.setInterval(1000)
		self.timer.start()
		self.timer.timeout.connect(self.updateApps)
	def paintEvent(self,e):
		qp=	QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		qp.setPen(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.setBrush(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.drawRoundedRect(QtCore.QRectF(10,0,self.size*self.win_len*1.3+10,self.size*1.6),2,2)
		qp.setPen(QtGui.QColor(250,250,250))
		qp.setBrush(QtGui.QColor(250,250,250))
		qp.drawRect(9,0,5,self.size*1.6)
		half_height=self.size*0.9
		icon=QtGui.QIcon("/usr/share/duck-launcher/default-theme/win.svg")
		icon.paint(qp, -10,half_height-10, 20,20)
		
		if self.drawButtonRect==True and self.buttonRect!=None:
			qp.setPen(QtGui.QColor(0,0,0,0))
			qp.setBrush(QtGui.QColor(254,254,255,50))
			qp.drawRect(self.buttonRect)
		for i,w in enumerate(self.windows):
			ico = Apps.ico_from_app(w['icon'])
			if ico==None:
				home = os.path.expanduser("~")+"/.duck"
				try:
    					os.stat(home)
				except:
   						os.mkdir(home)
				if os.path.isfile("{0}/{1}.png".format(home,binascii.hexlify(w["icon"]))):
					ico = QtGui.QIcon("{0}/{1}.png".format(home,binascii.hexlify(w["icon"])))
				else:
					ico = QtGui.QIcon("/usr/share/duck-launcher/default-theme/apps.svg")
			ico.paint(qp,20+self.size*i*1.3, 10, self.size*1.1, self.size*1.1)
	def mousePressEvent(self,e):
		x_m,y_m=e.x(),e.y()
		self.drawButtonRect=False
		for i,w in enumerate(self.windows):
			if 20+self.size*i*1.3<x_m<20+self.size*i*1.3+self.size*1.1 and 10<y_m<10+self.size*1.1:
				self.buttonRect=QtCore.QRectF(self.size*i*1.3+15, 0, self.size*1.1+10, self.size*1.6)
				self.drawButtonRect=True
				self.update()
				QtGui.QApplication.processEvents()
	def mouseReleaseEvent(self,e):
		x_m,y_m=e.x(),e.y()
		self.drawButtonRect=False
		for i,w in enumerate(self.windows):
			if 20+self.size*i*1.3<x_m<20+self.size*i*1.3+self.size*1.1 and 10<y_m<10+self.size*1.1:
				c = changeWindowState()
				c.parent=self
				c.win_info=w
				c.start()
		self.update()
		QtGui.QApplication.processEvents()
	def mouseMoveEvent(self,e):
		self.mousePressEvent(e)
	def updateApps(self):
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.resize(self.size*self.win_len*1.3+30,self.size*1.6+10)
		self.update()
		QtGui.QApplication.processEvents()
	def update_all(self,conf):
		self.size=int(conf['size'])
		self.move(self.size+10,self.height-self.size*2.4+self.top_pos)
		self.resize(self.size*self.win_len*1.3+20+10,self.size*1.6+10)
		self.r=int(conf["r"])
		self.g=int(conf["g"])
		self.b=int(conf["b"])
		self.update()
