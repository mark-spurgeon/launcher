#! /usr/bin/python
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
import os
import pickle
import platform 
import wnck
import dbus
import dbus.service
import dbus.mainloop.glib
import subprocess
import webbrowser
import gc
import imp
import sys
sys.dont_write_bytecode = True
import time
import math
import codecs
from jinja2 import Template
#import Xlib
#import Xlib.display
from PyQt4 import QtGui,QtCore,QtWebKit
import Apps
import Config
import Window
import XlibStuff
import Files
import System
import DockAppsOptions
import Plugins
#########

########	
def getCurrentPluginModule(name):
	home=os.path.expanduser("~")
	pl_dir=os.path.join(home,".duck-plugins")
	if os.path.isfile(os.path.join(pl_dir,name,"plugin.py")):
		plugin =imp.load_source(str(name),os.path.join(pl_dir,name,"plugin.py"))
		return plugin
class Settings(QtCore.QThread):
	def __init__(self,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.parent=parent
	def run(self):	
		subprocess.call(["python","/usr/lib/duck_settings/main.py"])
class Launch(QtCore.QThread):
	def __init__(self,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.app=""
		self.parent=parent
	def run(self):
		exec_list=self.app.split(" ")
		subprocess.call(exec_list)
		QtGui.QApplication.processEvents()
##########
##########
class Launcher(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self,None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
		self.setWindowTitle("ducklauncher!!")#recognisable by wnck
		self.activateWindow()
		#screen size
		d = QtGui.QDesktopWidget()
		self.top_pos=0
		self.s_width = d.availableGeometry().width()
		self.s_height =d.availableGeometry().height()
		self.top_pos= d.availableGeometry().y()
		#bg_width
		#Config
		conf=Config.get()
		self.conf=conf
		self.HALF_OPEN_POS=int(conf['size'])
		self.ICO_TOP=self.HALF_OPEN_POS-5
		self.OPEN_STATE_TOP=self.ICO_TOP*4+5
		self.SIZE = 14
		#self.R=int(conf['r'])
		#self.G=int(conf['g'])
		#self.B=int(conf['b'])
		#self.ICON_SIZE=int(conf['icon-size'])
		#Geometry
		self.setGeometry(0,self.top_pos,self.HALF_OPEN_POS+6,self.s_height)
		#Values
		self.appRect=None		
		self.drawAppRect=False
		self.pos_x=self.HALF_OPEN_POS-2
		self.move=False
		self.current_state="half_open"
		self.activity="apps"
		self.dock_apps = Apps.find_info(self.conf['dock-apps'])	
		self.current_text=''
		self.allApps=Apps.info(self.current_text)
		self.appHtmlSource="/usr/share/duck-launcher/default-theme/apps.html"
		self.appHtmlString=Template(open(self.appHtmlSource,"r").read()).render(color=(int(self.conf["r"]),int(self.conf["g"]),int(self.conf["b"])),font=str(self.conf["font"]), icon_size=int(self.conf["icon-size"])) 
		self.plugin=False
		#Open windows window
		self.open_windows=Window.get_open_windows()
		self.open_win = Window.open_windows()
		#Dock Apps Options Window
		self.dock_options_win=DockAppsOptions.Window(parent=self)
		#Webview for plugins
		self.webview=QtWebKit.QWebView(self)
		palette = self.webview.palette()
		palette.setBrush(QtGui.QPalette.Base, QtCore.Qt.transparent)
		self.webview.page().setPalette(palette)
		self.webview.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
		self.webview.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
		self.webview.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
		self.webview.connect(self.webview, QtCore.SIGNAL("linkClicked(const QUrl&)"), self.web_linkClicked)
		self.webview.page().mainFrame().javaScriptWindowObjectCleared.connect(self.web_populateJavaScriptWindowObject)
		self.webview.setHtml("<body style='background:rgb(230,100,80);'><input type='text' placehodler='aaa'></input></body>")
		self.webview.setGeometry(2,50,self.s_width/3-20,self.s_height-50)
		self.webview.activateWindow()
		self.webview.hide()
		#System window
		self.sys_win=System.Window()
		#Fake window
		self.fakewin = Fakewin(10,10, self)
		self.fakewin.show()
		XlibStuff.fix_window(self.winId(),self.HALF_OPEN_POS+5,0,0,0)
		#
	def paintEvent(self,e):
		qp=QtGui.QPainter(self)
		qp.fillRect(e.rect(), QtCore.Qt.transparent)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		####DRAW
		qp.setPen(QtCore.Qt.NoPen)
		qp.setBrush(QtGui.QColor(int(self.conf['r2']),int(self.conf['g2']),int(self.conf['b2']),int(self.conf["alpha"])))
		qp.drawRect(0,0,self.pos_x+7,self.s_height)
		qp.setPen(QtGui.QPen(QtGui.QColor(int(self.conf['r']),int(self.conf['g']),int(self.conf['b'])), 3, QtCore.Qt.SolidLine))
		qp.drawRect(self.pos_x+5,0,2,self.s_height)
		if self.current_state!="half_open":
			qp.setPen(QtGui.QPen(QtGui.QColor(int(self.conf['r']),int(self.conf['g']),int(self.conf['b']),30), 2, QtCore.Qt.SolidLine))
			qp.drawLine(self.pos_x-14,0,self.pos_x-14,self.s_height)
		qp.setPen(QtGui.QPen(QtGui.QColor(int(self.conf['r']),int(self.conf['g']),int(self.conf['b'])), 4, QtCore.Qt.SolidLine))
		qp.setBrush(QtGui.QBrush(QtGui.QColor(int(self.conf['r']),int(self.conf['g']),int(self.conf['b']))))
		r_s=2
		a=10
		r = QtCore.QRectF(self.pos_x-7,self.s_height/2-r_s/2,r_s,r_s)
		qp.drawEllipse(r)
		r = QtCore.QRectF(self.pos_x-7,self.s_height/2-a-r_s/2,r_s,r_s)
		qp.drawEllipse(r)
		r = QtCore.QRectF(self.pos_x-7,self.s_height/2+a-r_s/2,r_s,r_s)
		qp.drawEllipse(r)
		##
		###
		if self.current_state == "half_open":
			qp.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0),1,QtCore.Qt.SolidLine))
			qp.setBrush(QtGui.QColor(int(self.conf['r']),int(self.conf['g']),int(self.conf['b'])))
			qp.drawRect(0,0,self.pos_x+7,self.OPEN_STATE_TOP)
			rect = QtCore.QRectF(50,0,150,50)
			####DRAW BUTTONS
			###Apps
			ICO_TOP=self.HALF_OPEN_POS-5
			icon = QtGui.QIcon("/usr/share/duck-launcher/default-theme/apps.svg")
			icon.paint(qp,5,ICO_TOP*0+5,ICO_TOP,ICO_TOP-6)
			#Files
			icon = QtGui.QIcon("/usr/share/duck-launcher/default-theme/file.svg")
			##temp_file
			icon.paint(qp,5,ICO_TOP*1+5,ICO_TOP,ICO_TOP-6)
			#Settings
			icon = QtGui.QIcon("/usr/share/duck-launcher/default-theme/settings.svg")
			icon.paint(qp,5,ICO_TOP*2+5,ICO_TOP,ICO_TOP-6)
			#Star
			icon = QtGui.QIcon("/usr/share/duck-launcher/default-theme/star.svg")
			icon.paint(qp,5,ICO_TOP*3+5,ICO_TOP,ICO_TOP-6)
			#####
			#Dock Apps
			for i,a in enumerate(self.dock_apps):
				try:
					QtGui.QIcon(a['icon']).paint(qp,6,self.OPEN_STATE_TOP+ICO_TOP*i+10,ICO_TOP-5,ICO_TOP-5)
				except KeyError:
					print("[Duck Launcher] Error: Some apps could not be found ")
			
			#Open Windows Button
			qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 2, QtCore.Qt.SolidLine))
			icon = QtGui.QIcon("/usr/share/duck-launcher/default-theme/open-apps.svg")
			#icon = QtGui.QIcon("test-1.svg")
			icon.paint(qp,10,self.s_height-ICO_TOP*2-10,ICO_TOP-10,ICO_TOP-10)
			#rect = QtCore.QRectF(10,self.s_height-ICO_TOP*2-10,ICO_TOP-10,ICO_TOP-10)
			#qp.setFont(QtGui.QFont(self.conf["font"],self.HALF_OPEN_POS/3))
			#qp.drawText(rect, QtCore.Qt.AlignCenter, str(len(self.open_windows)))
			#System button
			icon = QtGui.QIcon("/usr/share/duck-launcher/default-theme/sys.svg")
			icon.paint(qp,10,self.s_height-self.HALF_OPEN_POS+8,self.HALF_OPEN_POS-15,self.HALF_OPEN_POS-15)
		##
		##
		if self.current_state=="open":
			close=QtGui.QIcon("/usr/share/duck-launcher/default-theme/remove.svg")
			close.paint(qp,self.pos_x-13,self.s_height-13,13,13)
			if self.activity=="apps":
				#Current Text
				qp.setPen(QtCore.Qt.NoPen)
				qp.setFont(QtGui.QFont(self.conf["font"],10))
				t_rect=QtCore.QRectF(20,20,self.s_width-36,20)
				if self.current_text=='':
					self.plugin=False
					qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 2, QtCore.Qt.SolidLine))
					qp.drawText(t_rect, QtCore.Qt.AlignLeft, "Type to search")
				else:
					if "#" in self.current_text.split(" ")[0]:
						plugins_list=[]						
						for p in Plugins.get_plugin_names():
							if str(self.current_text.split(" ")[0]).lower().replace("#","") in p:
								plugins_list.append(p)
						if plugins_list:
							what_in_text=str(self.current_text.split(" ")[0].replace("#","")).lower()
							query_name=plugins_list[0]
							fm=QtGui.QFontMetrics(QtGui.QFont(self.conf["font"],10))
							whole_width=0						
							for i,s in enumerate("#{}".format(query_name)):
								w = int(fm.charWidth("#{}".format(query_name),i))
								whole_width+=w
							if query_name==what_in_text:
								qp.setBrush(QtGui.QColor(int(self.conf["r"]),int(self.conf["g"]),int(self.conf["b"]),150))
								qp.drawRoundedRect(QtCore.QRectF(19,18,whole_width+4,20), 2,2)
							else:pass
							qp.setPen(QtGui.QPen(QtGui.QColor(255,255,255), 2, QtCore.Qt.SolidLine))
							qp.drawText(t_rect, QtCore.Qt.AlignLeft,self.current_text)
						else:
							qp.setPen(QtGui.QPen(QtGui.QColor(255,255,255), 2, QtCore.Qt.SolidLine))
							qp.drawText(t_rect, QtCore.Qt.AlignLeft,self.current_text)
					else:
						self.plugin=False
						qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 2, QtCore.Qt.SolidLine))
						qp.drawText(t_rect, QtCore.Qt.AlignLeft, self.current_text)
				#Page
				if self.plugin==False:
					pass
			###
			if self.activity=="files":
				pass
			if self.activity=="star" :
				qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 3, QtCore.Qt.SolidLine))
				all_rows=0
				blocks_l=pickle.loads(Config.get()["blocks"])
				for i,b in enumerate(blocks_l):
					all_stuff = Config.get_from_block(b)
					apps_per_row = math.trunc(((self.s_width/3)-30)/int(self.conf["icon-size"]))
					if len(all_stuff)!=apps_per_row:
						row_num = math.trunc(len(all_stuff)/apps_per_row)+1
					else:
						row_num = math.trunc(len(all_stuff)/apps_per_row)
					h=int(self.conf["icon-size"])*all_rows+i*50
					all_rows+=row_num
					qp.setFont(QtGui.QFont(self.conf["font"],8))
					for j, thing in enumerate(all_stuff):
						#same thing as for the apps
						row_pos = math.trunc(j/apps_per_row)
						x_pos = int(self.conf["icon-size"])*(j-(row_pos*apps_per_row))+40
						y_pos = (row_pos*int(self.conf["icon-size"])+20)+h+30
						if thing['type']=='app':
							icon = Apps.ico_from_app(str(thing['value']))
							to_write=str(thing['value'])
						elif thing['type']=='directory':
							print "a"
							icon = QtGui.QIcon(Apps.ico_from_name("folder"))
							splitted = thing['value'].split('/')
							to_write =  splitted[-1]
						elif thing['type']=='file':
							icon = QtGui.QIcon(Apps.ico_from_name("text-plain"))
							splitted = thing['value'].split('/')
							to_write =  splitted[-1]
						if icon!=None:
							icon.paint(qp, x_pos+15,y_pos+15, int(self.conf["icon-size"])-50,int(self.conf["icon-size"])-50)
							rect = QtCore.QRectF(x_pos-10, y_pos+int(self.conf["icon-size"])-30, int(self.conf["icon-size"]), 30)
							qp.drawText(rect,QtCore.Qt.TextWordWrap |QtCore.Qt.AlignHCenter,to_write)
					#Title
					qp.setPen(QtGui.QColor(0,0,0,0))
					qp.setBrush(QtGui.QColor(int(self.conf['r']),int(self.conf['g']),int(self.conf['b'])))
					qp.drawRect(18, h+40,self.s_width/6,2)
					qp.setPen(QtGui.QColor(250,250,250))
					qp.setFont(QtGui.QFont(self.conf["font"],16))
					if isinstance(b["name"],list):
						b["name"]="".join(b["name"])
					qp.drawText(QtCore.QRectF(20, h+10,self.s_width/3,200),b['name'])
		#Draw rect under clicked app
		if self.drawAppRect==True and self.appRect!=None:
			qp.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0),1,QtCore.Qt.SolidLine))
			qp.setBrush(QtGui.QColor(252,252,255,40))
			qp.drawRoundedRect(self.appRect,2,2)
	def mouseMoveEvent(self,e):
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,True)
		self.mousePressEvent(e)
		if e.x()>(self.pos_x-self.SIZE-5):
			if self.current_state=="half_open" and self.s_height/2-20<e.y()<self.s_height/2+20 :
				self.move=True
			if self.current_state=="open":
				self.move=True
		if self.move==True:
			self.webview.hide()
			self.current_state="nothing"
			self.update_pos(e.x())
		#repeat same as press event
	def mousePressEvent(self,e):
		x_m,y_m = e.x(),e.y()

		self.drawAppRect=False
		if self.current_state=="half_open":
			if 0<x_m<self.HALF_OPEN_POS:
				if y_m<self.ICO_TOP:
					self.appRect=QtCore.QRectF(0,2, self.HALF_OPEN_POS+4,self.ICO_TOP+3)
					self.drawAppRect=True
				if self.ICO_TOP<y_m<self.ICO_TOP*2:
					self.appRect=QtCore.QRectF(0,self.ICO_TOP+2, self.HALF_OPEN_POS+4,self.ICO_TOP+3)
					self.drawAppRect=True
				if self.ICO_TOP*2<y_m<self.ICO_TOP*3:
					self.appRect=QtCore.QRectF(0,self.ICO_TOP*2+2, self.HALF_OPEN_POS+4,self.ICO_TOP+3)
					self.drawAppRect=True
				if self.ICO_TOP*3<y_m<self.ICO_TOP*4:
					self.appRect=QtCore.QRectF(0,self.ICO_TOP*3+2, self.HALF_OPEN_POS+4,self.ICO_TOP+3)
					self.drawAppRect=True
			try:
				for i,a in enumerate(self.dock_apps):
					if self.OPEN_STATE_TOP+self.ICO_TOP*i+10<y_m<self.OPEN_STATE_TOP+self.ICO_TOP*(i+1)+10:
						self.appRect=QtCore.QRectF(0, self.OPEN_STATE_TOP+self.ICO_TOP*i+7, self.HALF_OPEN_POS+1,self.ICO_TOP)
						self.drawAppRect=True
			except KeyError:
				pass
			#
			if self.s_height-self.HALF_OPEN_POS-5<y_m:
				self.appRect=QtCore.QRectF(0,self.s_height-self.HALF_OPEN_POS,self.HALF_OPEN_POS+1,self.HALF_OPEN_POS)
				self.drawAppRect=True
			if  self.s_height-self.HALF_OPEN_POS*2<y_m<self.s_height-self.HALF_OPEN_POS-5:
				self.appRect=QtCore.QRectF(0,self.s_height-self.HALF_OPEN_POS*2-8,self.HALF_OPEN_POS+1,self.HALF_OPEN_POS+1)
				self.drawAppRect=True
		elif self.current_state=="open" and self.activity=="star":
			blocks=pickle.loads(str(self.conf["blocks"]))
			all_rows=0
			for i,b in enumerate(blocks):
				all_stuff = Config.get_from_block(b)
				apps_per_row = math.trunc(((self.s_width/3)-30)/int(self.conf["icon-size"]))
				if len(all_stuff)!=apps_per_row:
					row_num = math.trunc(len(all_stuff)/apps_per_row)+1
				else:
					row_num = math.trunc(len(all_stuff)/apps_per_row)
				h=int(self.conf["icon-size"])*all_rows+i*50
				all_rows+=row_num
				for j, thing in enumerate(all_stuff):
					row_pos = math.trunc(j/apps_per_row)
					x_pos = int(self.conf["icon-size"])*(j-(row_pos*apps_per_row))+40
					y_pos = (row_pos*int(self.conf["icon-size"])+20)+h+30
					if x_pos-10<x_m<x_pos-10+int(self.conf["icon-size"]) and y_pos<y_m<y_pos+int(self.conf["icon-size"]) and x_m<self.pos_x-self.SIZE-3:
						self.appRect=QtCore.QRectF(x_pos-10,y_pos,int(self.conf["icon-size"]),int(self.conf["icon-size"]))						
						self.drawAppRect=True
		self.update()
	def mouseReleaseEvent(self,e):
		x_m,y_m = e.x(),e.y()
		self.drawAppRect=False
		Window.activateFakewin(self.fakewin.winId())
		#While moving
		if self.current_state=="nothing":
			if self.plugin==False:
				self.webview.hide()	
			
			self.move=False
			###sets position to right one
			pos_list = [self.HALF_OPEN_POS, self.s_width/3]
			closest = min(pos_list, key=lambda x: abs(x-self.pos_x))
			if closest<self.pos_x:
				while closest<self.pos_x:
					self.pos_x-=5
					self.setGeometry(0,self.top_pos,self.pos_x+7,self.s_height)
					QtGui.QApplication.processEvents()
					self.update()
				self.pos_x=closest
				QtGui.QApplication.processEvents()
				self.update()
			elif closest>self.pos_x:
				while closest>self.pos_x:
					self.pos_x+=5
					self.setGeometry(0,self.top_pos,self.pos_x+7,self.s_height)
					QtGui.QApplication.processEvents()
					self.update()
				self.pos_x=closest
				QtGui.QApplication.processEvents()
				self.update()
			##set the current state
			if self.pos_x==self.HALF_OPEN_POS:
				self.pos_x-=3
				self.dock_apps = Apps.find_info(self.conf['dock-apps'])	
				self.current_state="half_open"
			elif self.pos_x==self.s_width/3:
				self.pos_x-=3
				self.current_state="open"
			else: self.current_state="nothing"
			if self.plugin==True and self.current_state=='open' and self.activity=='apps':
				self.webview.show()
			if self.plugin==False and self.current_state=='open' and self.activity=='apps':
				self.current_text=""
				self.initApps()
		#Events
		#
		elif self.current_state=="open":
			if self.pos_x-14<x_m<self.pos_x and self.move==False and e.button()==QtCore.Qt.LeftButton:
				self.close_it()
				if y_m>self.s_height-13:
					print("[Duck Launcher] Saving configuration.")
					Config.check_dict(self.conf)
					QtGui.QApplication.processEvents()
					print("[Duck Launcher] Quitting, Good Bye!")
					QtGui.qApp.quit()
			###app events
			elif self.activity==False and self.plugin==True:
				self.webview.show()
			elif self.activity == "files":
				pass
			elif self.activity=="star":
				blocks=pickle.loads(Config.get()["blocks"])
				all_rows=0
				apps_per_row = math.trunc(((self.s_width/3)-30)/int(self.conf["icon-size"]))
				for i,b in enumerate(blocks):
					all_stuff = Config.get_from_block(b)

					if len(all_stuff)!=apps_per_row:
						row_num = math.trunc(len(all_stuff)/apps_per_row)+1
					else:
						row_num = math.trunc(len(all_stuff)/apps_per_row)
					h=int(self.conf["icon-size"])*all_rows+i*50
					all_rows+=row_num

					for j, thing in enumerate(all_stuff):
						row_pos = math.trunc(j/apps_per_row)
						x_pos = int(self.conf["icon-size"])*(j-(row_pos*apps_per_row))+40
						y_pos = (row_pos*int(self.conf["icon-size"])+20)+h+30
						if x_pos-10<x_m<x_pos-10+int(self.conf["icon-size"]) and y_pos<y_m<y_pos+int(self.conf["icon-size"]) and x_m<self.pos_x-self.SIZE-3:
							if e.button()==QtCore.Qt.LeftButton:
								if thing['type']=='app':
									the_exec=""
									for a in Apps.info(''):
										if thing['value'] in a['name']:
											the_exec=a['exec']
									thread = Launch(parent=self)
									thread.app=the_exec
									thread.start()
									print("[Duck Launcher] Launching '{0}' with '{1}'".format(thing["value"], the_exec) )
								else:
									import webbrowser
									webbrowser.open(thing['value'])
		elif self.current_state=="half_open":
			##buttons
			if self.pos_x-self.SIZE<x_m<self.pos_x and self.move==False and self.s_height/2-20<y_m<self.s_height/2+20:
				self.activity="apps"
				self.current_text=""
				self.open_it()
				self.initApps()
			if 0<x_m<self.HALF_OPEN_POS:
				if e.button()==QtCore.Qt.LeftButton:
					if y_m<self.ICO_TOP:
						self.activity="apps"
						self.current_text=''
						self.open_it()
						#self.allApps=Apps.info(self.current_text)
						self.initApps()
					if self.ICO_TOP<y_m<self.ICO_TOP*2:
						HOME=os.path.expanduser("~")
						self.activity="apps"
						self.current_text="#Files "
						html= Plugins.get(str(self.current_text),color=(self.conf["r"],self.conf["g"],self.conf["b"]),font=self.conf["font"])
						if html!=None:
							self.open_it()
							self.webview.load(QtCore.QUrl(html))
							self.webview.show()
							self.plugin=True
							self.webview.page().mainFrame().setFocus()
							self.webview.setFocus()
							self.update()
					if self.ICO_TOP*2<y_m<self.ICO_TOP*3:
						self.activity="settings"
						Settings(parent=self).start()
					if self.ICO_TOP*3<y_m<self.ICO_TOP*4:
						self.activity="star"
						self.open_it()

					if  self.s_height-self.HALF_OPEN_POS*2<y_m<self.s_height-self.HALF_OPEN_POS-5:
						##open windows
						if self.open_win.isHidden():
							if len(self.open_windows)>0:
								#self.open_win.updateApps()
								self.open_win.show()
								self.sys_win.close()
							else:pass
						elif self.open_win.isHidden()==False:
							self.open_win.close()
					if  self.s_height-self.HALF_OPEN_POS-5<y_m:
						if self.sys_win.isHidden():
							self.open_win.close()
							self.sys_win.show()
						elif self.sys_win.isHidden()==False:
							self.sys_win.close()

				try:
					for i,a in enumerate(self.dock_apps):
						if self.OPEN_STATE_TOP+self.ICO_TOP*i+10<y_m<self.OPEN_STATE_TOP+self.ICO_TOP*(i+1)+10:
							if e.button()==QtCore.Qt.LeftButton:
								print("[Duck Launcher] Launching '{0}' with '{1}'".format(a["name"], a["exec"]) )
								thread = Launch(parent=self)
								thread.app=a["exec"]
								thread.start()
								self.dock_options_win.close()
							elif e.button()==QtCore.Qt.RightButton:
								#LaunchOption(y_pos, app_dict
								if self.dock_options_win.isHidden() or self.dock_options_win.app["name"]!=a["name"]:
									self.dock_options_win.update_all(self.conf)
									self.dock_options_win.setTopPosition(self.OPEN_STATE_TOP+self.ICO_TOP*i+10)
									self.dock_options_win.setApp(a)
									self.dock_options_win.updateWidth()
									self.dock_options_win.show()
								else:
									self.dock_options_win.close()
				except KeyError:
					pass
		self.update()	
	###ANIMATIONS
	def initApps(self):
		self.webview.setHtml(self.appHtmlString )
		self.webview.show()
		#self.webview.setHtml(self.appHtmlString )
		self.webview.page().mainFrame().setFocus()
		self.webview.page().mainFrame().evaluateJavaScript("changeIconSize({});".format(int(self.conf['icon-size'])))
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,False)
	def update_pos(self,pos):
		if pos>4 and pos<self.s_width/3+100:
			self.pos_x=pos
			self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
	def open_it(self):
		Window.activateFakewin(self.fakewin.winId())
		self.plugin=False
		self.sys_win.close()
		self.open_win.close()
		self.dock_options_win.close()
		while self.pos_x<self.s_width/3-5:
			self.current_state='nothing'
			if self.pos_x<self.s_width/7:
				self.pos_x=self.s_width/7
			else:
				self.pos_x+=float(self.conf["animation-speed"])
			self.setGeometry(0,self.top_pos,self.s_width/3+5,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
		if self.pos_x!=self.s_width/3-2 :
			self.pos_x=self.s_width/3-2
		self.current_state="open"
		if self.activity=="apps":
			self.allApps=Apps.info(self.current_text)
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,False)
		self.windowActivationChange(True)
		self.resetInputContext()
		self.webview.setEnabled(True)
		self.webview.setFocus(True)
		self.webview.resetInputContext()
		self.update()
		self.windowActivationChange(True)
		QtGui.QApplication.processEvents()
	def close_it(self):
		self.webview.hide()
		while self.pos_x>self.HALF_OPEN_POS:
			#old_pos=self.pos_x
			if self.pos_x<self.s_width/10:
				self.pos_x-=float(self.conf["animation-speed"])/4
			else:
				if self.pos_x>self.s_width/4:
					self.pos_x=self.s_width/4
				else:
					self.pos_x-=float(self.conf["animation-speed"])
			self.current_state="nothing"
			self.update()
			QtGui.QApplication.processEvents()
		if self.pos_x!=self.HALF_OPEN_POS-2:
			self.pos_x=self.HALF_OPEN_POS-2
		self.current_state="half_open"
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,True)
		self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
		self.update()
		QtGui.QApplication.processEvents()
	def updateOpenWindows(self):
		self.open_windows=Window.get_open_windows()
		try:
			if self.conf["size"]!=self.HALF_OPEN_POS:
				XlibStuff.fix_window(self.winId(),self.HALF_OPEN_POS+5,0,0,0)
		except:
			pass
		self.update()
		QtGui.QApplication.processEvents()
		Config.check_dict(self.conf)
	def update_all(self,conf):
		if self.HALF_OPEN_POS!=int(conf["size"]):
			self.HALF_OPEN_POS=int(conf['size'])
			self.webview.hide()
			self.current_state="half_open"
			self.pos_x=int(conf["size"])-2
			self.setGeometry(0,self.top_pos,self.HALF_OPEN_POS+6,self.s_height)
			self.ICO_TOP=self.HALF_OPEN_POS-5
			self.OPEN_STATE_TOP=self.ICO_TOP*4+5
		if self.activity=="apps" and self.plugin==False and int(self.conf["icon-size"])!=int(conf["icon-size"]):
			self.webview.page().mainFrame().evaluateJavaScript("changeIconSize({});".format(int(self.conf['icon-size'])))
		self.conf=conf
		if self.conf["blocks"]==None:
			self.conf["blocks"]=[]
		if self.conf["dock-apps"]==None:
			self.conf["dock-apps"]=[]
		
		self.dock_apps = Apps.find_info(self.conf['dock-apps'])
		self.open_win.update_all(conf)
		self.sys_win.update_all(conf)
		self.dock_options_win.update_all(conf)
		self.update()
		QtGui.QApplication.processEvents()

	#
	def web_linkClicked(self, url):
		str_url=str(url.toString())
		if "%TERMINAL%" in str_url:
			command=str_url.split("%TERMINAL%")
			command = [a for a in command if "file://" not in a]
			command= command[0].split(" ")
			command=[a for a in command if a ]
			t=LaunchCommand(parent=self,call=command)
			t.start()
		else:
			webbrowser.open(str(url.toString()))
	def web_populateJavaScriptWindowObject(self):
		self.webview.page().mainFrame().addToJavaScriptWindowObject('Duck', self)
	@QtCore.pyqtSlot()
	def submitForm(self):
		elements=[]
		for e in self.webview.page().mainFrame().findAllElements("*"):
			el={}
			el["type"] = str(e.localName())
			if e.hasAttribute("id"):
				el["id"]=str(e.attribute("id"))
			if e.hasAttribute("name"):
				el["name"]=str(e.attribute("name"))
			val= e.evaluateJavaScript('this.value').toPyObject()
			if val!=None:
				el["value"]=val
			elements.append(el)


		if "#" in self.current_text.split(" ")[0]:
			plugins_list=[]						
			for p in Plugins.get_plugin_names():
				if str(self.current_text.split(" ")[0]).lower().replace("#","") in p:
					plugins_list.append(p)
			if plugins_list:
				plugin_name=plugins_list[0]
				pl=getCurrentPluginModule(plugin_name)
				try:
					pl.onFormSubmit(elements)
				except:
					print("[Duck Launcher] No 'onFormSubmit()' method present in the plugin.")
	@QtCore.pyqtSlot(str,str)
	def sendData(self, thing, value):
		print "data : " , thing, value
		if "#" in self.current_text.split(" ")[0]:
			plugins_list=[]						
			for p in Plugins.get_plugin_names():
				if str(self.current_text.split(" ")[0]).lower().replace("#","") in p:
					plugins_list.append(p)
			if plugins_list:
				plugin_name=plugins_list[0]	
				pl=getCurrentPluginModule(plugin_name)
				try:
					pl.onDataSent(thing, value)
				except:
					print("[Duck Launcher] No 'onDataSent()' method present in the plugin.")
	@QtCore.pyqtSlot(str)
	def _filesGetFromPath(self,path):
		if str(self.current_text).lower().startswith("#files"):
			if os.path.isdir(path):
				stuff = Files.getFilesFromPath(path)
			elif path=="HOME":
				home=os.path.expanduser("~")
				stuff= Files.getFilesFromPath(home)
			else:
				stuff=[]
			self.webview.page().mainFrame().evaluateJavaScript("setNewFiles({})".format(stuff))
	@QtCore.pyqtSlot()
	def _appsGetAll(self):
		if self.activity=="apps" and self.plugin==False:
			self.allApps=Apps.info(self.current_text)
			self.webview.page().mainFrame().evaluateJavaScript("setNewApps({})".format(self.allApps))
	@QtCore.pyqtSlot(str)
	def _appsLaunch(self, the_exec):
		if self.activity=="apps" and self.plugin==False:
			thread = Launch(parent=self)
			thread.app=str(the_exec)
			thread.start()
			self.close_it()
class Fakewin(QtGui.QMainWindow):
	def __init__(self,width,height,parent):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnBottomHint|QtCore.Qt.FramelessWindowHint)
		
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setWindowTitle("ducklauncher!!!")
		self.setGeometry(0,0,width,height)
		self.parent=parent
		##
		self.timer=QtCore.QTimer()
		self.timer.setInterval(6000)
		self.timer.start()
		self.timer.timeout.connect(self.parent.updateOpenWindows)
	def keyPressEvent(self, e):
		if e.key()==QtCore.Qt.Key_Backspace:
			if self.parent.plugin==False:
				self.parent.current_text=self.parent.current_text[:-1]
				self.parent.allApps=Apps.info(str(self.parent.current_text))
				self.parent.webview.page().mainFrame().evaluateJavaScript("setNewApps({})".format(self.parent.allApps))
				self.parent.update()
		elif e.key()==QtCore.Qt.Key_Return:
			if len(self.parent.allApps)==1:
				a=self.parent.allApps[0]
				print("[Duck Launcher] Launching '{0}' with '{1}'".format(a["name"], a["exec"]) )
				thread = Launch(parent=self.parent)
				thread.app=a["exec"]
				thread.start()
				self.parent.close_it()
				self.parent.current_text=''
				self.parent.allApps=Apps.find_info('')	
			html= Plugins.get(str(self.parent.current_text),color=(self.parent.conf["r"],self.parent.conf["g"],self.parent.conf["b"]),font=self.parent.conf["font"])
			if html!=None:
				self.parent.webview.load(QtCore.QUrl(html))
				self.parent.webview.show()
				self.parent.plugin=True
				self.parent.webview.page().mainFrame().setFocus()
				self.parent.webview.setFocus()
				self.update()
		elif e.key()==16777216:
			#ESC
			self.parent.current_text=""		
			self.parent.allApps=Apps.info(str(self.parent.current_text))
			self.parent.webview.page().mainFrame().evaluateJavaScript("setNewApps({})".format(self.parent.allApps))	
			self.parent.initApps()
		elif e.text()!='':
			self.parent.current_text+=e.text()
			self.parent.allApps=Apps.info(str(self.parent.current_text))
			self.parent.webview.page().mainFrame().evaluateJavaScript("setNewApps({})".format(self.parent.allApps))
			self.parent.update()
		else:
			if e.key()==16777250:
				if self.parent.current_state=="half_open":
					self.parent.activity="apps"
					self.parent.current_text=''
					self.parent.allApps=Apps.info('')
					self.parent.initApps()
					self.parent.open_it()
				elif self.parent.current_state=="open":
					self.parent.close_it()
		self.parent.update()
	def quitApp(self):
		print "quit"

class DBusWidget(dbus.service.Object):
	def __init__(self,parent, name, session):
		# export this object to dbus
		self.parent=parent
		self.conf=Config.get()
		dbus.service.Object.__init__(self, name, session)
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getR1(self):
		return int(self.conf["r"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getG1(self):
		return int(self.conf["g"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getB1(self):
		return int(self.conf["b"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getR2(self):
		return int(self.conf["r2"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getG2(self):
		return int(self.conf["g2"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getB2(self):
		return int(self.conf["b2"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getAlpha(self):
		return int(self.conf["alpha"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getIconSize(self):
		return int(self.conf["icon-size"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getLauncherWidth(self):
		return int(self.conf["size"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getAnimationSpeed(self):
		return float(self.conf["animation-speed"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='s')
	def getFont(self):
		return self.conf["font"]
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='v')
	def getDockApps(self):
		print "h"
		return list(self.conf["dock-apps"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='v')
	def getBlocks(self):
		return self.conf["blocks"]
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='s')
	def getInit(self):
		return self.conf["init-manager"]
	####SET
	@dbus.service.method("org.duck.Launcher", in_signature='',out_signature="")
	def setR1(self,v):
		self.conf["r"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setG1(self,v):
		self.conf["g"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setB1(self,v):
		self.conf["b"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setR2(self,v):
		self.conf["r2"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setG2(self,v):
		self.conf["g2"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setB2(self,v):
		self.conf["b2"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setAlpha(self,v):
		self.conf["alpha"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setIconSize(self,v):
		self.conf["icon-size"]=v
		self.parent.webview.page().mainFrame().evaluateJavaScript("changeIconSize({});".format(int(v)))
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setLauncherWidth(self,v):
		self.conf["size"]=v
		self.parent.conf=self.conf
		self.parent.HALF_OPEN_POS=int(v)
		self.parent.webview.hide()
		self.parent.current_state="half_open"
		self.parent.pos_x=int(v)-2
		self.parent.setGeometry(0,self.parent.top_pos,int(v)+6,self.parent.s_height)
		self.parent.ICO_TOP=int(v)-5
		self.parent.OPEN_STATE_TOP=self.parent.ICO_TOP*4+5
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setAnimationSpeed(self,v):
		self.conf["animation-speed"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setFont(self,v):
		self.conf["font"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setDockApps(self,v):
		self.conf["dock-apps"]=v
		self.parent.conf=self.conf
		self.parent.dock_apps=Apps.find_info(self.conf['dock-apps'])
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setBlocks(self,v):
		self.conf["blocks"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setInit(self,v):
		self.conf["init-manager"]=v
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def update(self):
		self.parent.conf=self.conf
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def exit(self):
		QtGui.qApp().quit()
		
	'''
	# A signal that will be exported to dbus
	@dbus.service.signal("com.example.SampleWidget", signature='')
	def clicked(self):
		print "clicked"

	# Another signal that will be exported to dbus
	@dbus.service.signal("com.example.SampleWidget", signature='')
	def lastWindowClosed(self):
		pass
	'''

if __name__ == "__main__":
	do=True

	version = platform.python_version()
	if "2.7" not in version:
		do=False
		print("Sorry, you need python 2.7 to run Duck Launcher")
	#check if there is already Duck Launcher...launched
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	for w in win:
		if "ducklauncher!!" in w.get_name():
			do=False 

	if do==True:

		gc.disable()
		app = QtGui.QApplication(sys.argv)
		QtGui.QApplication.setApplicationName("Duck Launcher")
		win = Launcher()
		win.show()
		#win.raise_()
	
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		session_bus = dbus.SessionBus(private=True)
		name = dbus.service.BusName("org.duck.Launcher", session_bus)
		widget = DBusWidget(win,session_bus, '/DBusWidget')

		app.setActiveWindow(win)
		sys.exit(app.exec_())
	elif do==False:
		print("Quiting Duck Launcher")
