#! /usr/bin/python
# -*- coding: utf-8 -*-
#########
#Copyright (C) 2014  Mark Spurgeon <theduck.dev@gmail.com>
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
import wnck
import pickle
import platform 
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
#import codecs
from PyQt4 import QtGui,QtCore,QtWebKit
import Apps
import Config
import Window
import XlibStuff
import Files
import System
import DockAppsOptions
import Plugins
import Widgets
#########

########	
class Settings(QtCore.QThread):
	def __init__(self,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.parent=parent
	def run(self):	
		subprocess.call(["python","/usr/lib/duck_settings/main.py"])
##########
class Launcher(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self,None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground,True)
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,True)
		self.setWindowTitle("ducklauncher!!")#recognisable by wnck
		self.activateWindow()
		#screen size
		d = QtGui.QDesktopWidget()
		self.top_pos=0
		self.s_width = d.availableGeometry().width()
		self.s_height =d.availableGeometry().height()
		self.top_pos= d.availableGeometry().y()
		#Config values
		conf=Config.get()
		self.conf=conf
		self.HALF_OPEN_POS=int(conf['size'])
		self.ICO_TOP=self.HALF_OPEN_POS-5
		self.OPEN_STATE_TOP=self.ICO_TOP*4+5
		self.SIZE = 14
		#Geometry
		self.setGeometry(0,self.top_pos,self.HALF_OPEN_POS+9,self.s_height)
		#Values
		self.ICON_SIZE=int(conf['icon-size'])
		self.apps_per_row = math.trunc(((self.s_width/3)-50)/ int(self.conf["icon-size"]))
		self.apps_per_col = math.trunc(((self.s_height)-90)/ int(self.conf["icon-size"]))
		self.apps_per_page=self.apps_per_col*self.apps_per_row
		self.app_page_state=0
		self.appRect=None		
		self.drawAppRect=False
		self.pos_x=self.HALF_OPEN_POS-2
		self.move=False
		self.current_state="half_open"
		self.activity="apps"
		self.dock_apps = Apps.find_info(self.conf['dock-apps'])	
		self.current_text=''
		self.allApps=Apps.info(self.current_text)
		self.plugin=False
		self.pl_rect_pos=0
		self.pl_logo=None
		self.fg_color=(int(self.conf['r']),int(self.conf['g']),int(self.conf['b']))
		self.font_color=(int(self.conf['font-r']),int(self.conf['font-g']),int(self.conf['font-b']))
		##Windows
		#Enables the server which gets open windows
		self.op_thread=Window.openWindowsThread()
		self.op_thread.start()
		self.connect(self.op_thread,QtCore.SIGNAL("new-window"),self.addOpenWindow)
		self.connect(self.op_thread,QtCore.SIGNAL("remove-window"),self.updateOpenWindows)
		self.open_windows=Window.get_open_windows()
		self.ow_in_dock=[]
		#Dock Apps Options Window
		self.dock_options_win=DockAppsOptions.Window(parent=self)
		#Webview (for plugins, files, and settings view)
		self.webview=Widgets.pluginView(self)
		self.webview.setGeometry(2,60,self.s_width/3-20,self.s_height-60)
		#System window
		self.sys_win=System.Window()
		#Fake window, required to capture keyboard events
		self.fakewin = Fakewin(10,10, self)
		self.fakewin.show()
		XlibStuff.fix_window(self.winId(),self.HALF_OPEN_POS+3,0,0,0)
		#
	def paintEvent(self,e):
		qp=QtGui.QPainter(self)
		qp.fillRect(e.rect(), QtCore.Qt.transparent)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		####DRAW
		qp.setPen(QtCore.Qt.NoPen)
		qp.setBrush(QtGui.QColor(int(self.conf['r2']),int(self.conf['g2']),int(self.conf['b2']),int(self.conf["alpha"])))
		qp.drawRect(0,0,self.pos_x+7,self.s_height)

		##
		if self.current_state == "half_open":
			qp.setPen(QtCore.Qt.NoPen)
			qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2]))
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
					if a["name"] in [e["name"] for e in self.ow_in_dock]:
						qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2],100))	
						qp.drawRect(0,self.OPEN_STATE_TOP+ICO_TOP*i+8,self.HALF_OPEN_POS+3,ICO_TOP-1)
						qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2]))
						r_s=6
						c = QtCore.QRectF(-r_s/2,self.OPEN_STATE_TOP+ICO_TOP*i+8+ICO_TOP/2-r_s/2,r_s,r_s)
						qp.drawEllipse(c)
					QtGui.QIcon(Apps.ico_from_name(a['icon'])).paint(qp,4,self.OPEN_STATE_TOP+ICO_TOP*i+10,ICO_TOP,ICO_TOP-5)
				except KeyError:
					print("[Duck Launcher] Error: Some apps could not be found ")

			qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2]))
			if len(self.open_windows)>0:

				after_dapps = self.OPEN_STATE_TOP+len(self.dock_apps)*ICO_TOP+30
				all_wins=[e["info"]["id"] for e in self.ow_in_dock]
				ow_list=[o for o in self.open_windows if o["id"] not in all_wins] 
				if len(ow_list)>0:
					qp.drawRect(4, after_dapps-15, self.HALF_OPEN_POS-6,1)
				for i,w in enumerate(ow_list):
					y_pos=i*ICO_TOP+after_dapps
					r_s=6
					c = QtCore.QRectF(-r_s/2,y_pos+ICO_TOP/2-r_s,r_s,r_s)
					qp.drawEllipse(c)
					QtGui.QIcon(w["icon"]).paint(qp, 4, y_pos,ICO_TOP,ICO_TOP-5)
			qp.setPen(QtCore.Qt.NoPen)
			qp.setBrush(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]))
			print self.pos_x+7
			if self.pos_x+7>=70:
				s=12
			elif 55<self.pos_x+7<70:
				s=8
			elif 40<self.pos_x+7<=55:
				s=6
			elif self.pos_x+7<=40:
				s=4
			top_r=self.s_height-self.HALF_OPEN_POS/2-s/2
			qp.drawRect((self.pos_x+7)/2-2*s,top_r,s,s)
			qp.drawRect((self.pos_x+7)/2-s/2,top_r,s,s)
			qp.drawRect((self.pos_x+7)/2+s,top_r,s,s)
			#icon = QtGui.QIcon("/usr/share/duck-launcher/default-theme/sys.svg")
			#icon.paint(qp,10,self.s_height-self.HALF_OPEN_POS+8,self.HALF_OPEN_POS-15,self.HALF_OPEN_POS-15)
		##
		##
		if self.current_state=="open":
			#close=QtGui.QIcon("/usr/share/duck-launcher/default-theme/remove.svg")
			#close.paint(qp,self.pos_x-10,self.s_height-13,13,13)
			if self.activity=="apps":
				max_apps=  math.trunc((len(self.allApps)-1)/self.apps_per_page)+1
				if self.plugin==False:
					##pages
					btn_size = 15
					minus = math.trunc(len(self.allApps)/self.apps_per_page)*15/2
					for i in range(0, max_apps):
							x_pos = self.s_width/6-btn_size+(btn_size*i)-minus
							qp.setPen(QtCore.Qt.NoPen)
							qp.setBrush(QtGui.QColor(int(self.font_color[0]),int(self.font_color[1]),int(self.font_color[2])))
							rect = QtCore.QRectF(x_pos,2,btn_size,btn_size)
							if self.app_page_state==i:
								rect = QtCore.QRectF(x_pos+2,15,btn_size-1,btn_size-1)
							else:
								rect = QtCore.QRectF(x_pos+btn_size/4,15+btn_size/4,btn_size-btn_size/2,btn_size-btn_size/2)
							qp.drawEllipse(rect)
					###app_buttons
					for i, app in enumerate(self.allApps):
							app_page = math.trunc(i/self.apps_per_page)
							if app_page==self.app_page_state:
								qp.setBrush(QtGui.QColor(int(self.conf['r2']),int(self.conf['g2']),int(self.conf['b2'])))
								row_pos = math.trunc(i/self.apps_per_row)
								page_row_pos=row_pos-(self.apps_per_page/self.apps_per_row*app_page)
								col_pos=(i-(row_pos*self.apps_per_row))
								#pr,app["name"]
								x_pos = self.ICON_SIZE*col_pos+30+col_pos*10
								y_pos = page_row_pos*self.ICON_SIZE+30+page_row_pos*10
								try:
									if self.ICON_SIZE-60>20:
										rect=QtCore.QRect(x_pos+30,y_pos+30,self.ICON_SIZE-60,self.ICON_SIZE-60)
									elif self.ICON_SIZE-30>20:
										rect=QtCore.QRect(x_pos+15,y_pos+15,self.ICON_SIZE-30,self.ICON_SIZE-30)
									else:
										rect=QtCore.QRect(x_pos,y_pos,self.ICON_SIZE,self.ICON_SIZE)

									ico=Apps.ico_from_name(app["icon"])
									if ico!=None:
										QtGui.QIcon(Apps.ico_from_name(app["icon"])).paint(qp,rect)
									else:
										i = QtGui.QIcon('/usr/share/duck-launcher/default-theme/apps.svg')
										i.paint(qp,rect)
									
								except KeyError:
									i = QtGui.QIcon('/usr/share/duck-launcher/default-theme/apps.svg')
									i.paint(qp,x_pos+20,y_pos+20,self.ICON_SIZE-40,self.ICON_SIZE-40)
								qp.setPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]))
								text_rect = QtCore.QRectF(x_pos+5,y_pos+self.ICON_SIZE-10,self.ICON_SIZE-10,60)
								#font
								font = QtGui.QFont(self.conf["font"],9)
								font.setLetterSpacing(QtGui.QFont.PercentageSpacing,116)
								font.setWeight(QtGui.QFont.Normal)
								font.setHintingPreference(QtGui.QFont.PreferDefaultHinting)
								qp.setFont(font)
								qp.drawText(text_rect,QtCore.Qt.TextWordWrap |QtCore.Qt.AlignHCenter,self.tr(app["name"]).replace(u"Â", ""))
				elif self.plugin==True:
					qp.setPen(QtCore.Qt.NoPen)
					qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2]))
					pl_rect=QtCore.QRect(0,0,self.pl_rect_pos,self.s_height)
					qp.drawRect(pl_rect)
				#Current Text
				qp.setPen(QtCore.Qt.NoPen)
				font = QtGui.QFont(self.conf["font"],10)
				font.setWeight(QtGui.QFont.Bold)
				qp.setFont(font)
				t_rect=QtCore.QRectF(20,18,self.s_width-36,20)
				t_rect_pl=QtCore.QRectF(70,18,self.s_width-36,20)
				if self.current_text=='':
					font = QtGui.QFont(self.conf["font"],10)
					font.setWeight(QtGui.QFont.Light)
					font.setStyle(QtGui.QFont.StyleItalic)
					qp.setFont(font)
					self.plugin=False
					qp.setPen(QtGui.QPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2],160), 1, QtCore.Qt.SolidLine))
					qp.drawText(t_rect, QtCore.Qt.AlignLeft, "Type to search")
				else:
					font = QtGui.QFont(self.conf["font"],10)
					#font.setWeight(QtGui.QFont.Light)
					qp.setFont(font)
					if "#" in self.current_text.split(" ")[0]:
						plugins_list=[]						
						for p in Plugins.get_plugin_names():
							if str(self.current_text.split(" ")[0]).lower().replace("#","") in p:
								plugins_list.append(p)
						if plugins_list:
							what_in_text=str(self.current_text.split(" ")[0].replace("#","")).lower()
							query_name=plugins_list[0]
							font =QtGui.QFont(self.conf["font"],10)
							fm=QtGui.QFontMetrics(QtGui.QFont(self.conf["font"],10))
							whole_width=0						
							for i,s in enumerate("#{}".format(query_name)):
								w = int(fm.charWidth("#{}".format(query_name),i))
								whole_width+=w
							if query_name==what_in_text:
								if self.plugin==False:
									qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2],255))
									qp.drawRect(19,37,whole_width+4,3)
									qp.setPen(QtGui.QPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]),1, QtCore.Qt.SolidLine))
									qp.drawText(t_rect, QtCore.Qt.AlignLeft,self.current_text)
								else:
									qp.setBrush(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2],255))
									qp.drawRect(69,37,whole_width+4,3)						
									qp.setPen(QtGui.QPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]),1, QtCore.Qt.SolidLine))
									qp.drawText(t_rect_pl, QtCore.Qt.AlignLeft,self.current_text)
									if self.pl_logo!=None:
										ico = QtGui.QIcon(self.pl_logo)
										ico.paint(qp,15,10,40,40)
							else:
								qp.setPen(QtGui.QPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]),1, QtCore.Qt.SolidLine))
								qp.drawText(t_rect, QtCore.Qt.AlignLeft,self.current_text)
						else:
							qp.setPen(QtGui.QPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]), 2, QtCore.Qt.SolidLine))
							qp.drawText(t_rect, QtCore.Qt.AlignLeft,self.current_text)
					else:
						self.plugin=False
						qp.setPen(QtGui.QPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]), 2, QtCore.Qt.SolidLine))
						qp.drawText(t_rect, QtCore.Qt.AlignLeft, self.current_text)
			###
			if self.activity=="star" :
				qp.setPen(QtGui.QPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]), 3, QtCore.Qt.SolidLine))
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
							icon = QtGui.QIcon(Apps.ico_from_app(str(thing['value'])))
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
					qp.setPen(QtCore.Qt.NoPen)
					qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2]))
					qp.drawRect(18, h+40,self.s_width/6,2)
					qp.setPen(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2]))
					qp.setFont(QtGui.QFont(self.conf["font"],16))
					if isinstance(b["name"],list):
						b["name"]="".join(b["name"])
					qp.drawText(QtCore.QRectF(20, h+10,self.s_width/3,200),b['name'])

		qp.setPen(QtCore.Qt.NoPen)
		qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2]))
		'''
		if self.plugin==False:
			qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2]))
		else:
			qp.setBrush(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2],255))
		'''
		qp.drawRect(self.pos_x+5,0,2,self.s_height)
		qp.setBrush(QtGui.QColor(0,0,0,20))
		qp.drawRect(self.pos_x+7,0,3,self.s_height)
		qp.setBrush(QtGui.QColor(0,0,0,30))
		qp.drawRect(self.pos_x+7,0,2,self.s_height)
		qp.setBrush(QtGui.QColor(0,0,0,50))
		qp.drawRect(self.pos_x+7,0,1,self.s_height)
		if self.current_state!="half_open":
			qp.setPen(QtCore.Qt.NoPen)
			qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2],18))
			qp.drawRect(self.pos_x-14,0,20,self.s_height)
			if self.plugin==False:
				qp.setBrush(QtGui.QColor(self.fg_color[0],self.fg_color[1],self.fg_color[2],255))
			else:
				qp.setBrush(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2],255))
			r_s=5
			a=10
			r = QtCore.QRectF(self.pos_x-7,self.s_height/2-r_s/2,r_s,r_s)
			qp.drawEllipse(r)
			r = QtCore.QRectF(self.pos_x-7,self.s_height/2-a-r_s/2,r_s,r_s)
			qp.drawEllipse(r)
			r = QtCore.QRectF(self.pos_x-7,self.s_height/2+a-r_s/2,r_s,r_s)
			qp.drawEllipse(r)
		#Draw rect under clicked app
		if self.drawAppRect==True and self.appRect!=None:
			qp.setPen(QtCore.Qt.NoPen)
			qp.setBrush(QtGui.QColor(self.font_color[0],self.font_color[1],self.font_color[2],30))
			qp.drawRect(self.appRect)
	def mouseMoveEvent(self,e):
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,True)
		self.mousePressEvent(e)
		'''
		self.mousePressEvent(e)
		if e.x()>(self.pos_x-self.SIZE-5):
			if self.current_state=="open":
				self.move=True
		if self.move==True:
			self.webview.hide()
			self.current_state="nothing"
			self.update_pos(e.x())
		'''
	def mousePressEvent(self,e):
		x_m,y_m = e.x(),e.y()

		self.drawAppRect=False
		if self.current_state=="half_open":
			if 0<x_m<self.HALF_OPEN_POS:
				if y_m<self.ICO_TOP:
					self.appRect=QtCore.QRectF(0,2, self.HALF_OPEN_POS+4,self.ICO_TOP)
					self.drawAppRect=True
				if self.ICO_TOP<y_m<self.ICO_TOP*2:
					self.appRect=QtCore.QRectF(0,self.ICO_TOP+2, self.HALF_OPEN_POS+4,self.ICO_TOP)
					self.drawAppRect=True
				if self.ICO_TOP*2<y_m<self.ICO_TOP*3:
					self.appRect=QtCore.QRectF(0,self.ICO_TOP*2+2, self.HALF_OPEN_POS+4,self.ICO_TOP)
					self.drawAppRect=True
				if self.ICO_TOP*3<y_m<self.ICO_TOP*4:
					self.appRect=QtCore.QRectF(0,self.ICO_TOP*3+2, self.HALF_OPEN_POS+4,self.ICO_TOP)
					self.drawAppRect=True
			for i,a in enumerate(self.dock_apps):
				if self.OPEN_STATE_TOP+self.ICO_TOP*i+10<y_m<self.OPEN_STATE_TOP+self.ICO_TOP*(i+1)+10:
					self.appRect=QtCore.QRectF(0, self.OPEN_STATE_TOP+self.ICO_TOP*i+7, self.HALF_OPEN_POS+3,self.ICO_TOP)
					self.drawAppRect=True
			if len(self.open_windows)>0:
				after_dapps = self.OPEN_STATE_TOP+len(self.dock_apps)*self.ICO_TOP+30
				all_wins=[e["info"]["id"] for e in self.ow_in_dock]
				ow_list=[o for o in self.open_windows if o["id"] not in all_wins] 
				for i,w in enumerate(ow_list):
					y_pos=i*self.ICO_TOP+after_dapps-3
					if y_pos<y_m<y_pos+self.ICO_TOP:
						self.appRect=QtCore.QRectF(0, y_pos, self.HALF_OPEN_POS+3,self.ICO_TOP)
						self.drawAppRect=True

			#
			if self.s_height-self.HALF_OPEN_POS-5<y_m:
				self.appRect=QtCore.QRectF(0,self.s_height-self.HALF_OPEN_POS,self.HALF_OPEN_POS+3,self.HALF_OPEN_POS)
				self.drawAppRect=True
		if self.current_state=="open" and self.activity=="apps" and self.plugin==False:
			for i, app in enumerate(self.allApps):
				app_page = math.trunc(i/self.apps_per_page)
				if app_page==self.app_page_state:
					row_pos = math.trunc(i/self.apps_per_row)
					page_row_pos=row_pos-(self.apps_per_page/self.apps_per_row*app_page)
					col_pos=(i-(row_pos*self.apps_per_row))
					x_pos = self.ICON_SIZE*col_pos+30+col_pos*10
					y_pos = page_row_pos*self.ICON_SIZE+45+page_row_pos*10
					if x_pos<x_m<x_pos+int(self.conf["icon-size"]) and y_pos<y_m<y_pos+int(self.conf["icon-size"]):
						self.appRect=QtCore.QRectF(x_pos,y_pos,int(self.conf["icon-size"]),int(self.conf["icon-size"]))
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
		''''
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
					self.setGeometry(0,self.top_pos,self.pos_x+9,self.s_height)
					QtGui.QApplication.processEvents()
					self.update()
				self.pos_x=closest
				QtGui.QApplication.processEvents()
				self.update()
			elif closest>self.pos_x:
				while closest>self.pos_x:
					self.pos_x+=5
					self.setGeometry(0,self.top_pos,self.pos_x+9,self.s_height)
					QtGui.QApplication.processEvents()
					self.update()
				self.pos_x=closest
				QtGui.QApplication.processEvents()
				self.update()
			##set the current state
			if self.pos_x==self.HALF_OPEN_POS:
				self.pos_x-=3
				#self.dock_apps = Apps.find_info(self.conf['dock-apps'])	
				self.current_state="half_open"
			elif self.pos_x==self.s_width/3:
				self.pos_x-=3
				self.current_state="open"
			else: self.current_state="nothing"
			if self.plugin==True and self.current_state=='open' and self.activity=='apps':
				self.webview.show()
			if self.plugin==False and self.current_state=='open' and self.activity=='apps':
				self.current_text=""
				#self.initApps()
'''
		#Events
		#
		if self.current_state=="open":

			if self.pos_x-14<x_m<self.pos_x and self.move==False and e.button()==QtCore.Qt.LeftButton:
				self.close_it()
				if y_m>self.s_height-13:
					print("[Duck Launcher] Saving configuration.")
					c = Config.check_dict(self.conf)
					QtGui.QApplication.processEvents()
					print("[Duck Launcher] Quitting, Good Bye!")
					QtGui.qApp.quit()
			###app events
			if self.activity == "apps" and self.plugin==False:
				max_apps=  math.trunc((len(self.allApps)-1)/self.apps_per_page)+1
				minus = math.trunc(len(self.allApps)/self.apps_per_page)*15/2
				##Change Page
				for i in range(0,max_apps):
					btn_size = 15
					x_pos = self.s_width/6-btn_size+(btn_size*i)-minus
					if x_pos<x_m<x_pos+btn_size and 12<y_m<btn_size+12:
						self.app_page_state=i
						self.update()
						QtGui.QApplication.processEvents()
				for i, app in enumerate(self.allApps):
					app_page = math.trunc(i/self.apps_per_page)
					if app_page==self.app_page_state:
						row_pos = math.trunc(i/self.apps_per_row)
						page_row_pos=row_pos-(self.apps_per_page/self.apps_per_row*app_page)
						col_pos=(i-(row_pos*self.apps_per_row))
						x_pos = self.ICON_SIZE*col_pos+30+col_pos*10
						y_pos = page_row_pos*self.ICON_SIZE+45+page_row_pos*10
						if x_pos<x_m<x_pos+int(self.conf["icon-size"]) and y_pos<y_m<y_pos+int(self.conf["icon-size"]):
							if e.button()==QtCore.Qt.LeftButton:
								print("[Duck Launcher] Launching '{0}' with '{1}'".format(app["name"],app["exec"]) )
								thread = Widgets.Launch(parent=self)
								thread.app=app["exec"]
								thread.start()
								self.close_it()			
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
									thread = Widgets.Launch(parent=self)
									thread.app=the_exec
									thread.start()
									print("[Duck Launcher] Launching '{0}' with '{1}'".format(thing["value"], the_exec) )
								else:
									import webbrowser
									webbrowser.open(thing['value'])
		elif self.current_state=="half_open":
			##buttonsszd
			if 0<x_m<self.HALF_OPEN_POS:
				if e.button()==QtCore.Qt.LeftButton:
					if y_m<self.ICO_TOP:
						self.activity="apps"
						self.current_text=''
						self.open_it()
						#self.allApps=Apps.info(self.current_text)
					if self.ICO_TOP<y_m<self.ICO_TOP*2:
						HOME=os.path.expanduser("~")
						self.activity="apps"
						self.current_text="#Files "
						pl= Plugins.get(str(self.current_text))
						html=pl.html(color=(self.conf["r"],self.conf["g"],self.conf["b"]),font=self.conf["font"])
						if html!=None:
							self.open_it()
							self.plugin=True
							self.pl_logo="/usr/share/duck-launcher/default-theme/file.svg"
							self.fg_color=(40,40,40)
							self.font_color=(255,255,255)
							self.open_pl_rect()
							self.webview.setHtml(html)
							self.webview.show()
							#self.webview.page().mainFrame().setFocus()
							#self.webview.setFocus()
							self.update()
					if self.ICO_TOP*2<y_m<self.ICO_TOP*3:
						self.activity="settings"
						Settings(parent=self).start()
					if self.ICO_TOP*3<y_m<self.ICO_TOP*4:
						self.activity="star"
						self.open_it()
					if  self.s_height-self.HALF_OPEN_POS-5<y_m:
						if self.sys_win.isHidden():
							#self.open_win.close()
							self.sys_win.show()
						elif self.sys_win.isHidden()==False:
							self.sys_win.close()

				for i,a in enumerate(self.dock_apps):
					if self.OPEN_STATE_TOP+self.ICO_TOP*i+10<y_m<self.OPEN_STATE_TOP+self.ICO_TOP*(i+1)+10:
						if e.button()==QtCore.Qt.LeftButton:
							if a["name"] in [e["name"] for e in self.ow_in_dock]:
								l=[e for e in self.ow_in_dock if e["name"]==a["name"]]
								for k in l:
									c = Window.changeWindowState(parent=self,win_info=k["info"])
									c.start()								
							else:
								print("[Duck Launcher] Launching '{0}' with '{1}'".format(a["name"], a["exec"]) )
								thread = Widgets.Launch(parent=self)
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
				if len(self.open_windows)>0:
					after_dapps = self.OPEN_STATE_TOP+len(self.dock_apps)*self.ICO_TOP+30
					all_wins=[e["info"]["id"] for e in self.ow_in_dock]
					ow_list=[o for o in self.open_windows if o["id"] not in all_wins] 
					for i,w in enumerate(ow_list):
						y_pos=i*self.ICO_TOP+after_dapps-3
						if y_pos<y_m<y_pos+self.ICO_TOP:
							c = Window.changeWindowState(parent=self,win_info=w)
							c.start()
		self.update()	
	def wheelEvent(self,e):
		#Window.activateFakewin(self.fakewin.winId())
		if self.activity == 'apps':
			value= int(e.delta()/120)
			max_pages=math.trunc((len(self.allApps)-1)/self.apps_per_page)
			if value>0 and self.app_page_state>0:
				self.app_page_state-=1
			if value<0 and self.app_page_state<max_pages:
				self.app_page_state+=1
			self.update()
			self.repaint()
			QtGui.QApplication.processEvents()
	###ANIMATIONS
	def update_pos(self,pos):
		if pos>4 and pos<self.s_width/3+100:
			self.pos_x=pos
			self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2+5,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
	def open_it(self):
		Window.activateFakewin(self.fakewin.winId())
		self.plugin=False
		self.sys_win.close()
		self.dock_options_win.close()
		self.setGeometry(0,self.top_pos,self.s_width/3+8,self.s_height)
		while self.pos_x<self.s_width/3-4.5:
			self.current_state='nothing'
			if self.pos_x<self.s_width/7:
				self.pos_x=self.s_width/7
			else:
				self.pos_x+=float(self.conf["animation-speed"])
			self.repaint()
			QtGui.QApplication.processEvents()
		if self.pos_x!=self.s_width/3-4 :
			self.pos_x=self.s_width/3-4
		self.current_state="open"
		if self.activity=="apps":
			self.allApps=Apps.info(self.current_text)
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,False)
		self.update()
		QtGui.QApplication.processEvents()
	def close_it(self):
		if self.plugin==True:
			self.webview.hide()
			self.close_pl_rect()
			self.plugin=False
			self.font_color=(int(self.conf['font-r']),int(self.conf['font-g']),int(self.conf['font-b']))
			self.fg_color=(int(self.conf['r']),int(self.conf['g']),int(self.conf['b']))
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
			self.repaint()
			QtGui.QApplication.processEvents()
		if self.pos_x!=self.HALF_OPEN_POS-2:
			self.pos_x=self.HALF_OPEN_POS-2
		self.current_state="half_open"
		self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,True)
		self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2+3,self.s_height)
		self.update()
		QtGui.QApplication.processEvents()
	def open_pl_rect(self):
		self.pl_rect_pos=0
		while self.pl_rect_pos<(self.s_width/3):
			self.pl_rect_pos+=int(self.conf["animation-speed"])*2
			self.repaint()
			QtGui.QApplication.processEvents()
		self.pl_rect_pos=self.s_width/3+2
		self.update()
	def close_pl_rect(self):
		while self.pl_rect_pos>0:
			self.pl_rect_pos-=int(self.conf["animation-speed"])*2
			self.repaint()
			#QtGui.QApplication.processEvents()
		self.pl_rect_pos=0
		self.update()
	def update_all(self,conf):
		self.conf=conf
		if self.HALF_OPEN_POS!=int(conf["size"]):
			self.HALF_OPEN_POS=int(conf['size'])
			self.current_state="half_open"
			self.pos_x=int(conf["size"])
			self.setGeometry(0,self.top_pos,self.HALF_OPEN_POS+6,self.s_height)
			self.ICO_TOP=self.HALF_OPEN_POS-5
			self.OPEN_STATE_TOP=self.ICO_TOP*4+5
		elif self.ICON_SIZE!=int(conf['icon-size']):
			self.ICON_SIZE=int(conf['icon-size'])
			self.apps_per_row = math.trunc(((self.s_width/3)-30)/self.ICON_SIZE)
			self.apps_per_col = math.trunc(((self.s_height)-30)/self.ICON_SIZE)
			self.apps_per_page=self.apps_per_col*self.apps_per_row
		
		if self.conf["blocks"]==None:
			self.conf["blocks"]=[]
		if self.conf["dock-apps"]==None:
			self.conf["dock-apps"]=[]
		
		self.dock_apps = Apps.find_info(self.conf['dock-apps'])
		self.sys_win.update_all(conf)
		self.dock_options_win.update_all(conf)
		self.update()
		QtGui.QApplication.processEvents()
	####
	def changeQuery(self,q):
		if self.current_state!="open":
			self.open_it()
		#self.
	####
	def addOpenWindow(self, w):
		self.open_windows.append(w)
		self.ow_in_dock=[]
		for o in self.open_windows:
			dock_name=''
			in_dock=0
			d = [ s.lower() for s in o["title"].split(" ") ]
			for r in d:
				for d in self.dock_apps:
					dl = str(d["name"]).lower().split(" ")
					if r in dl:
						in_dock+=1
						dock_name=d["name"]
					
			if in_dock>0:
				new_dict={}
				new_dict["name"]=dock_name
				new_dict["info"]=o
				self.ow_in_dock.append(new_dict)
		self.update()
	def updateOpenWindows(self, w):
		self.open_windows=w
		self.ow_in_dock=[]
		for o in self.open_windows:
			dock_name=''
			in_dock=0
			d = [ s.lower() for s in o["title"].split(" ") ]
			for r in d:
				for d in self.dock_apps:
					dl = str(d["name"]).lower().split(" ")
					if r in dl:
						in_dock+=1
						dock_name=d["name"]
					
			if in_dock>0:
				new_dict={}
				new_dict["name"]=dock_name
				new_dict["info"]=o
				self.ow_in_dock.append(new_dict)
		self.update()
class Fakewin(QtGui.QMainWindow):
	def __init__(self,width,height,parent):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnBottomHint|QtCore.Qt.FramelessWindowHint)
		#self.mapToParent()
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setWindowTitle("ducklauncher!!!")
		self.setGeometry(0,0,width,height)
		self.parent=parent
		##
	def keyPressEvent(self, e):
		QtCore.QCoreApplication.sendEvent(self.parent, e)
		if e.key()==QtCore.Qt.Key_Backspace:
			self.parent.current_text=self.parent.current_text[:-1]
			if self.plugin==False:
				self.parent.allApps=Apps.info(str(self.parent.current_text))
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
			pl= Plugins.get(str(self.parent.current_text))
			#html = pl.html(color=(self.parent.conf["r"],self.parent.conf["g"],self.parent.conf["b"]),font=self.parent.conf["font"])
			if pl.isAlright():
				self.parent.fg_color=pl.getColor("background")
				self.parent.font_color=pl.getColor("foreground")
				self.parent.pl_logo=pl.getLogo()
				if self.parent.plugin==False:
					self.parent.plugin=True
					self.parent.open_pl_rect()
				html = pl.html(color=(self.parent.conf["r"],self.parent.conf["g"],self.parent.conf["b"]),font=self.parent.conf["font"])
				if html !=None:
					self.parent.webview.setHtml(html)
				else:print("ummm, error")
				self.parent.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock,False)
				self.update()
				self.parent.update()
				self.parent.webview.show()
				self.parent.webview.page().mainFrame().setFocus()
				self.parent.webview.setFocus()
				self.parent.webview.update()
		elif e.key()==16777216:
			#ESC
			if self.parent.plugin==False:
				self.parent.current_text=""		
				self.parent.allApps=Apps.info('')
				self.parent.app_page_state=0
			if self.parent.plugin==True:
				self.parent.close_it()
			self.parent.update()
			#QtGui.QApplication.processEvents()
		elif e.text()!='':
			self.parent.current_text+=e.text()
			self.parent.app_page_state=0
			self.parent.allApps=Apps.info(str(self.parent.current_text))
			#self.parent.webview.page().mainFrame().evaluateJavaScript("setNewApps({})".format(self.parent.allApps))
			self.parent.update()
		else:
			if e.key()==16777250:
				if self.parent.current_state=="half_open":
					self.parent.activity="apps"
					self.parent.current_text=''
					self.parent.allApps=Apps.info('')
					self.parent.open_it()
				elif self.parent.current_state=="open":
					self.parent.webview.hide()
					self.parent.close_pl_rect()
					self.parent.fg_color=(int(self.parent.conf['r']),int(self.parent.conf['g']),int(self.parent.conf['b']))
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
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getFontR(self):
		return int(self.conf["font-r"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getFontG(self):
		return int(self.conf["font-g"])
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='i')
	def getFontB(self):
		return int(self.conf["font-b"])
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
		if self.parent.plugin==False:
			self.parent.fg_color=(int(self.parent.conf["r"]),int(self.parent.conf["g"]),int(self.parent.conf["b"]))
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setG1(self,v):
		self.conf["g"]=v
		self.parent.conf=self.conf
		if self.parent.plugin==False:
			self.parent.fg_color=(int(self.parent.conf["r"]),int(self.parent.conf["g"]),int(self.parent.conf["b"]))
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setB1(self,v):
		self.conf["b"]=v
		self.parent.conf=self.conf
		if self.parent.plugin==False:
			self.parent.fg_color=(int(self.parent.conf["r"]),int(self.parent.conf["g"]),int(self.parent.conf["b"]))
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
		self.conf["icon-size"]=int(v)
		self.parent.conf=self.conf
		self.parent.update_all(self.conf)
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
		self.parent.update_all(self.conf)
	@dbus.service.method("org.duck.Launcher", in_signature='',out_signature="")
	def setFontR(self,v):
		self.conf["font-r"]=v
		self.parent.conf=self.conf
		if self.parent.plugin==False:
			self.parent.font_color=(int(self.parent.conf["font-r"]),int(self.parent.conf["font-g"]),int(self.parent.conf["font-b"]))
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setFontG(self,v):
		self.conf["font-g"]=v
		self.parent.conf=self.conf
		if self.parent.plugin==False:
			self.parent.font_color=(int(self.parent.conf["font-r"]),int(self.parent.conf["font-g"]),int(self.parent.conf["font-b"]))
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setFontB(self,v):
		self.conf["font-b"]=v
		self.parent.conf=self.conf
		if self.parent.plugin==False:
			self.parent.font_color=(int(self.parent.conf["font-r"]),int(self.parent.conf["font-g"]),int(self.parent.conf["font-b"]))
		self.parent.update()
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setDockApps(self,v):
		self.conf["dock-apps"]=v
		self.parent.conf=self.conf
		self.parent.dock_apps=Apps.find_info(self.conf['dock-apps'])
		self.parent.update_all(self.conf)
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setBlocks(self,v):
		self.conf["blocks"]=v
		self.parent.conf=self.conf
		self.parent.update_all(self.conf)
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def setInit(self,v):
		self.conf["init-manager"]=v
		self.parent.conf=self.conf
		self.parent.update_all(self.conf)
	@dbus.service.method("org.duck.Launcher", in_signature='', out_signature='')
	def update(self):
		self.parent.conf=self.conf
		self.parent.update_all(self.conf)
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
class MyApp(QtGui.QApplication):
	def __init__(self,args):
		QtGui.QApplication.__init__(self, args)
	def x11EventFilter(self,e):
		#print e
		#e.accept()
		QtCore.QEvent(int(e)).accept()
		return False
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
		app =MyApp(sys.argv)
		#app.setAutoSipEnabled(True)
		QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
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
