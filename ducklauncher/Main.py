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
import sys
import math
import time
import getpass
import Xlib
import Xlib.display
from PySide import QtGui,QtCore
import Apps
import Config 
import Settings
import Window as window
import XlibStuff
import Files
#########
#########


class AppObject(QtGui.QFrame):
	def __init__(self, rect, parent=None):
		super(AppObject, self).__init__(parent)
		x,y,w,h=rect.getRect()
		self.clicked = QtCore.Signal() # can be other types (list, dict, object...)
		self.move(x,y)
		self.resize(w,h)
	def mousePressEvent(self, event):
		print "ah"
		self.clicked.emit()

class Launch(QtCore.QThread):
	def __init__(self,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.app=""
		self.parent=parent
	def run(self):
		os.system(self.app)
		QtGui.QApplication.processEvents()
class Launcher(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)#| QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setWindowTitle("ducklauncher")
		#screen size
		d = QtGui.QDesktopWidget()
		self.top_pos=0
		self.s_width = d.availableGeometry().width()
		self.s_height =d.availableGeometry().height()
		d.resized.connect(self.updateSize)
		#Config
		conf=Config.get()
		self.conf=conf
		self.HALF_OPEN_POS=int(conf['size'])
		self.ICO_TOP=self.HALF_OPEN_POS-5
		self.OPEN_STATE_TOP=self.ICO_TOP*4+5
		self.SIZE = 15
		self.R=int(conf['r'])
		self.G=int(conf['g'])
		self.B=int(conf['b'])
		self.ICON_SIZE=int(conf['icon-size'])
		#Geometry
		self.setGeometry(0,0,self.HALF_OPEN_POS+4,self.s_height)
		#reserve wndow space
		#self.activateWindow()
		xwin = XlibStuff.fix_window(self.winId(),self.HALF_OPEN_POS+5,0,0,0)
		#
		#Values
		self.apps_per_row = math.trunc(((self.s_width/3)-30)/self.ICON_SIZE)
		self.apps_per_col = math.trunc(((self.s_height)-30)/self.ICON_SIZE)
		self.apps_per_page=self.apps_per_col*self.apps_per_row
		self.app_page_state=0
		self.files_page_state=0
		self.Files = Files.getFiles()
		self.pos_x=self.HALF_OPEN_POS
		self.move=False
		self.current_state="half_open"
		self.activity="apps"
		self.dock_apps = Apps.find_info(self.conf['dock-apps'])
		self.current_text=''
		#Update open windows
		self.timer=QtCore.QTimer()
		self.timer.setInterval(2000)
		self.timer.start()
		self.timer.timeout.connect(self.updateOpenWindows)
		#
		self.open_windows=window.get_open_windows()
		self.open_win = window.open_windows()
		self.open_state=False
		#
		self.settings_win = Settings.Window(self)
		
	def paintEvent(self,e):
		qp=QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		####DRAW
		qp.setBrush(QtGui.QColor(40,40,40,200))
		qp.drawRect(0,0,self.pos_x+self.SIZE/2,self.s_height)
		
		#qp.setBrush(QtGui.QColor(200,20,20))
		pen = QtGui.QPen(QtGui.QColor(self.R,self.G,self.B), 8, QtCore.Qt.SolidLine)
		qp.setPen(pen)
		qp.drawLine(self.pos_x+self.SIZE/2-2,0,self.pos_x+self.SIZE/2-2,self.s_height)
		qp.setPen(QtGui.QPen(QtGui.QColor(self.R,self.G,self.B), 4, QtCore.Qt.SolidLine))
		r_s=3
		a=3
		r = QtCore.QRectF(self.pos_x-self.SIZE/2-a,self.s_height/2,r_s,r_s)
		qp.drawEllipse(r)
		r = QtCore.QRectF(self.pos_x-self.SIZE/2-a,self.s_height/2-r_s*3,r_s,r_s)
		qp.drawEllipse(r)
		r = QtCore.QRectF(self.pos_x-self.SIZE/2-a,self.s_height/2+r_s*3,r_s,r_s)
		qp.drawEllipse(r)
		##
		###
		if self.current_state == "half_open":
			qp.setBrush(QtGui.QColor(self.R,self.G,self.B))
			qp.drawRect(0,0,self.pos_x+self.SIZE/2,self.OPEN_STATE_TOP)
			rect = QtCore.QRectF(50,0,150,50)
			qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 3, QtCore.Qt.SolidLine))
			####DRAW BUTTONS
			qp.setBrush(QtGui.QColor(250,250,250,100))
			qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 2, QtCore.Qt.SolidLine))
			###Apps
			ICO_TOP=self.ICO_TOP
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/apps.svg")
			icon.paint(qp,7,ICO_TOP*0+5,ICO_TOP-5,ICO_TOP-5)
			#Files
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/file.svg")
			##temp_file
			icon.paint(qp,7,ICO_TOP*1+5,ICO_TOP-5,ICO_TOP-5)
			#Settings
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/settings.svg")
			icon.paint(qp,7,ICO_TOP*2+5,ICO_TOP-5,ICO_TOP-5)
			#Star
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/star.svg")
			icon.paint(qp,7,ICO_TOP*3+5,ICO_TOP-5,ICO_TOP-5)		
			#####
			#Dock Apps
			try:
				####OFF WE GOOO!
				for i,a in enumerate(self.dock_apps):
					ico = Apps.ico_from_name(str(a['icon']))
					if ico!=None:
						ico.paint(qp,6,self.OPEN_STATE_TOP+ICO_TOP*i+10,ICO_TOP-5,ICO_TOP-5)
			except KeyError:
				print 'No Dock apps'
			
			#Open Windows Button
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/open-apps.svg")
			icon.paint(qp,10,self.s_height-ICO_TOP*2-10,ICO_TOP-10,ICO_TOP-10)
			rect = QtCore.QRectF(10,self.s_height-ICO_TOP*2-10,ICO_TOP-10,ICO_TOP-10)
			qp.setFont(QtGui.QFont('Hermeneus One',14))
			qp.drawText(rect, QtCore.Qt.AlignCenter, str(len(self.open_windows)))
			#Quit Button
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/close.svg")
			icon.paint(qp,10,self.s_height-ICO_TOP,ICO_TOP-10,ICO_TOP-10)	
		##
		##
		if self.current_state=="open":
			
			if self.activity=="apps":
				###page_buttons
				#Current Text
				t_rect=QtCore.QRectF(10,10,self.s_width/8,30)
				if self.current_text=='':
					qp.drawText(t_rect, QtCore.Qt.AlignCenter, "Type to search..")
				else:
					qp.drawText(t_rect, QtCore.Qt.AlignCenter, "Searching: "+self.current_text)
				max_apps=  math.trunc(len(Apps.info(self.current_text))/self.apps_per_page)+1
				for i in range(0, max_apps):
						btn_size = 20
						x_pos = self.s_width/6-btn_size+(btn_size*i)
						rect = QtCore.QRectF(x_pos,2,btn_size,btn_size)
						qp.drawRect(rect)
						qp.drawText(rect,QtCore.Qt.AlignCenter,str(i+1))
				###app_buttons
				for i, app in enumerate(Apps.info(self.current_text)):
						app_page = math.trunc(i/self.apps_per_page)
						if app_page==self.app_page_state:
							qp.setBrush(QtGui.QColor(self.R,self.G,self.B))
							row_pos = math.trunc(i/self.apps_per_row)
							x_pos = self.ICON_SIZE*(i-(row_pos*self.apps_per_row))+30
							y_pos = row_pos*self.ICON_SIZE+30-(app_page*(self.ICON_SIZE*self.apps_per_col))
							try:		
								da_icon=Apps.ico_from_name(app["icon"])
								if da_icon!=None:
									da_icon.paint(qp,x_pos+10,y_pos+10,self.ICON_SIZE-30,self.ICON_SIZE-30)
									r1 =QtCore.QRect(x_pos+10,y_pos+10,self.ICON_SIZE-30,self.ICON_SIZE-30)
							except KeyError:
								i = QtGui.QImage('images/apps.png')
								rect= QtCore.QRectF(x_pos+10,y_pos+10,self.ICON_SIZE-30,self.ICON_SIZE-30)
								qp.drawImage(rect,i)
							qp.setPen(QtGui.QColor(250,250,250))
							text_rect = QtCore.QRectF(x_pos-5,y_pos+self.ICON_SIZE-20,self.ICON_SIZE,30)
							qp.setFont(QtGui.QFont('Hermeneus One',8))
							qp.drawText(text_rect,QtCore.Qt.AlignCenter,str(app["name"]))
				
			###	
			if self.activity=="files":
				#Buttons
				b1_rect=QtCore.QRectF(10,10,30,30)
				qp.drawRect(b1_rect)#temporarily
				ico = QtGui.QIcon("/usr/share/duck-launcher/icons/back.svg")
				max_files=  math.trunc(len(self.Files.all())/self.apps_per_page)+1
				for i in range(0, max_files):
						btn_size = 20
						x_pos = self.s_width/6-btn_size+(btn_size*i)
						rect = QtCore.QRectF(x_pos,2,btn_size,btn_size)
						qp.drawRect(rect)
						qp.drawText(rect,QtCore.Qt.AlignCenter,str(i+1))
				###app_buttons
				for i, f in enumerate(self.Files.all()):
						app_page = math.trunc(i/self.apps_per_page)
						if app_page==self.files_page_state:
							qp.setBrush(QtGui.QColor(self.R,self.G,self.B))
							row_pos = math.trunc(i/self.apps_per_row)
							x_pos = self.ICON_SIZE*(i-(row_pos*self.apps_per_row))+30
							y_pos = row_pos*self.ICON_SIZE+30-(app_page*(self.ICON_SIZE*self.apps_per_col))
							print Files.getFileIcon(f["whole_path"])
							try:	
								if f["type"]=="directory":
									da_icon=QtGui.QIcon("/usr/share/duck-launcher/icons/folder.svg")
									da_icon.paint(qp,x_pos+10,y_pos+10,self.ICON_SIZE-30,self.ICON_SIZE-30)	
								if f["type"]=="file":
									da_icon=QtGui.QIcon("/usr/share/duck-launcher/icons/file.svg")
									da_icon.paint(qp,x_pos+10,y_pos+10,self.ICON_SIZE-30,self.ICON_SIZE-30)	
							except KeyError:
								i = QtGui.QImage('images/apps.png')
								rect= QtCore.QRectF(x_pos+10,y_pos+10,self.ICON_SIZE-30,self.ICON_SIZE-30)
								qp.drawImage(rect,i)
							qp.setPen(QtGui.QColor(250,250,250))
							text_rect = QtCore.QRectF(x_pos-5,y_pos+self.ICON_SIZE-20,self.ICON_SIZE,30)
							qp.setFont(QtGui.QFont('Hermeneus One',8))
							qp.drawText(text_rect,QtCore.Qt.AlignCenter,f["name"])
			if self.activity=="star":
				qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 3, QtCore.Qt.SolidLine))
				all_rows=0
				for i,b in enumerate(self.conf['blocks']):
					all_stuff = Config.get_from_block(b)
					row_num = math.trunc(len(all_stuff)/self.apps_per_row)+1
					h=self.ICON_SIZE*all_rows+20
					all_rows+=row_num
					qp.setFont(QtGui.QFont('Hermeneus One',16))
					qp.drawText(QtCore.QRectF(20, h+10,self.s_width/3,200),b['name'])
					qp.setFont(QtGui.QFont('Hermeneus One',10))
					for j, thing in enumerate(all_stuff):
						#same thing as for the apps
						row_pos = math.trunc(j/self.apps_per_row)
						x_pos = self.ICON_SIZE*(j-(row_pos*self.apps_per_row))+40
						y_pos = (row_pos*self.ICON_SIZE+20)+h
						if thing['type']=='app':
							icon = Apps.ico_from_app(thing['value'])
							to_write=thing['value']
						elif thing['type']=='directory':
							icon = QtGui.QIcon('/usr/share/duck-launcher/icons/folder.svg')
							splitted = thing['value'].split('/')
							to_write =  splitted[-1]
						elif thing['type']=='file':
							icon = QtGui.QIcon('/usr/share/duck-launcher/icons/file.svg')
							splitted = thing['value'].split('/')
							to_write =  splitted[-1]
						icon.paint(qp, x_pos+15,y_pos+15, self.ICON_SIZE-50,self.ICON_SIZE-50)
						rect = QtCore.QRectF(x_pos+10, y_pos+self.ICON_SIZE-30, self.ICON_SIZE, 30)
						txt = qp.drawText(rect, to_write)
	def launch(self, n):
		print n
	def mouseMoveEvent(self,e):
		if self.current_state!='open':
			self.current_state="nothing"
		if self.current_state=='nothing':
			if e.x()>(self.pos_x-self.SIZE):
				self.move=True
			if self.move==True:
				self.update_pos(e.x())
	def mouseReleaseEvent(self,e):
		self.move=False
		###sets position to right one
		pos_list = [self.HALF_OPEN_POS, self.s_width/3]
		closest = min(pos_list, key=lambda x: abs(x-self.pos_x))
		if closest<self.pos_x:
			while closest<self.pos_x:
				self.pos_x-=5
				self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
				QtGui.QApplication.processEvents()
				self.update()
			self.pos_x=closest
			QtGui.QApplication.processEvents()
			self.update()
		elif closest>self.pos_x:
			while closest>self.pos_x:
				self.pos_x+=5
				self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
				QtGui.QApplication.processEvents()
				self.update()
			self.pos_x=closest
			QtGui.QApplication.processEvents()
			self.update()
		##set the current state
		if closest==self.HALF_OPEN_POS:
			self.current_state="half_open"
		elif closest==self.s_width/3:
			self.current_state="open"
		else: self.current_state="nothing"

	def mousePressEvent(self,e):
		x_m,y_m = e.x(),e.y()
		self.open_windows=window.get_open_windows()
		self.update()
		QtGui.QApplication.processEvents()
		if self.current_state=="open":
			if self.pos_x-self.SIZE<x_m<self.pos_x and self.move==False:
				self.close_it()
			###app events
			if self.activity == "apps":
				max_apps=  math.trunc(len(Apps.info(self.current_text))/self.apps_per_page)+1
				##Change Page
				for i in range(0,max_apps):
						btn_size = 20
						x_pos = self.s_width/6-btn_size+(btn_size*i)
						if x_pos<x_m<x_pos+btn_size and 2<y_m<2+btn_size:
							self.app_page_state=i
							self.update()
							QtGui.QApplication.processEvents()	
				## launch apps
				for i, app in enumerate(Apps.info(self.current_text)):
					app_page = math.trunc(i/self.apps_per_page)
					if app_page==self.app_page_state:
						row_pos = math.trunc(i/self.apps_per_row)
						x_pos = self.ICON_SIZE*(i-(row_pos*self.apps_per_row))+30
						y_pos = row_pos*self.ICON_SIZE+30-(app_page*(self.ICON_SIZE*self.apps_per_col))
						if x_pos<x_m<(x_pos+self.ICON_SIZE) and y_pos<y_m<(y_pos+self.ICON_SIZE):
							print "It should launch:  " + app["name"] + "  with  " + app["exec"]
							thread = Launch(parent=self)
							thread.app=app["exec"]
							thread.start()
							self.close_it()
			if self.activity == "files":
				if 10<x_m<40 and 10<y_m<40:
					l= self.Files.directory.split("/")[:-1][1:]
					new_dir=''
					for a in l:
						new_dir+='/'
						new_dir+=a
					if new_dir=='':new_dir='/'
					self.Files.directory=new_dir
					self.update()
				max_files=  math.trunc(len(self.Files.all())/self.apps_per_page)+1
				##Change Page
				for i in range(0,max_files):
						btn_size = 20
						x_pos = self.s_width/6-btn_size+(btn_size*i)
						if x_pos<x_m<x_pos+btn_size and 2<y_m<2+btn_size:
							self.files_page_state=i
							self.update()
							QtGui.QApplication.processEvents()	
				## launch apps
				for i, f in enumerate(self.Files.all()):
					app_page = math.trunc(i/self.apps_per_page)
					if app_page==self.files_page_state:
						row_pos = math.trunc(i/self.apps_per_row)
						x_pos = self.ICON_SIZE*(i-(row_pos*self.apps_per_row))+30
						y_pos = row_pos*self.ICON_SIZE+30-(app_page*(self.ICON_SIZE*self.apps_per_col))
						if x_pos<x_m<(x_pos+self.ICON_SIZE) and y_pos<y_m<(y_pos+self.ICON_SIZE):
							if f["type"]=="file":
								import webbrowser
								webbrowser.open(f["whole_path"])
							elif  f["type"]=="directory":
								self.Files.directory=f["whole_path"]
								self.update()
								QtGui.QApplication.processEvents()	
			if self.activity=="star":
				blocks=self.conf['blocks']
				all_rows=0
				for i,b in enumerate(blocks):
					all_stuff = Config.get_from_block(b)
					row_num = math.trunc(len(all_stuff)/self.apps_per_row)+1
					h=self.ICON_SIZE*all_rows+20
					all_rows+=row_num
					for j, thing in enumerate(all_stuff):
						row_pos = math.trunc(j/self.apps_per_row)
						x_pos = self.ICON_SIZE*(j-(row_pos*self.apps_per_row))+40
						y_pos = (row_pos*self.ICON_SIZE+20)+h
						if x_pos+15<x_m<x_pos+15+self.ICON_SIZE and y_pos+15<y_m<y_pos+15+self.ICON_SIZE:
							if thing['type']=='app':
								the_exec=""
								for a in Apps.info(''):
									if thing['value'] in a['name']:
										print "a"
										the_exec=a['exec']
								thread = Launch(parent=self)
								thread.app=the_exec
								thread.start()
								print "Launching " , thing['value'], "with :",the_exec
							else:
								import webbrowser
								webbrowser.open(thing['value'])
		if self.current_state=="half_open":
			##buttons
			if 0<x_m<self.HALF_OPEN_POS:
				if 0<y_m<self.ICO_TOP:
					self.activity="apps"
					self.current_text=''
					self.open_it()
				if self.ICO_TOP<y_m<self.ICO_TOP*2:
					self.activity="files"
					self.Files.directory=self.Files.default
					self.open_it()
				if self.ICO_TOP*2<y_m<self.ICO_TOP*3:
					self.activity="settings"
					self.settings_win.show()
				if self.ICO_TOP*3<y_m<self.ICO_TOP*4:
					self.activity="star"
					self.open_it()
				try:
				
					####OFF WE GOOO!
					for i,a in enumerate(self.dock_apps):
						if self.OPEN_STATE_TOP+self.ICO_TOP*i+10<y_m<self.OPEN_STATE_TOP+self.ICO_TOP*(i+1)+10:
							print "It should launch:  " + a["name"] + "  with  " + a["exec"]
							thread = Launch(parent=self)
							thread.app=a["exec"]
							thread.start()
							self.close_it()
				except KeyError:
					pass
				if  self.s_height-self.ICO_TOP*2-20<y_m<self.s_height-self.ICO_TOP-20:
					##open windows
					if self.open_state==False:
						if len(self.open_windows)>0:
							self.open_win.update_apps()
							self.open_win.show()
							self.open_state=True
						else:pass
					elif self.open_state==True:
						self.open_win.close()
						self.open_state=False
				if  self.s_height-self.ICO_TOP*2-20>y_m<self.s_height-self.ICO_TOP-20:
					self.open_win.close()
				if  self.s_height-self.ICO_TOP<y_m<self.s_height:
					sys.exit()
	def wheelEvent(self,e):
		if self.activity == 'apps':
			value= int(e.delta()/120)
			max_pages=math.trunc(len(Apps.info(self.current_text))/self.apps_per_page)
			if value<0 and self.app_page_state>0:
				self.app_page_state-=1
			if value>0 and self.app_page_state<max_pages:
				self.app_page_state+=1
			self.update()
			QtGui.QApplication.processEvents()
		if self.activity == 'files':
			value= int(e.delta()/120)
			max_pages=math.trunc(len(self.Files.all())/self.apps_per_page)
			if value<0 and self.app_page_state>0:
				self.app_page_state-=1
			if value>0 and self.app_page_state<max_pages:
				self.files_page_state+=1
			self.update()
			QtGui.QApplication.processEvents()
	def keyPressEvent(self, e):
		if e.key()==QtCore.Qt.Key_Backspace:
			self.current_text=self.current_text[:-1]
		elif e.key()==QtCore.Qt.Key_Return:
			pass
		elif e.text()!='':
			self.current_text+=e.text()
		else:
			if e.key()==16777250:
				self.activity="apps"
				self.open_it()
			if e.key()==16777249:
				print "a"
			print e.key()
		self.update()
	###ANIMATIONS	
	def update_pos(self,pos):
		if pos>4:
			self.pos_x=pos
			self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
	def open_it(self):
		while self.pos_x<self.s_width/3:
			self.current_state='nothing'
			self.pos_x+=1.5
			self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
		self.current_state="open"	
		self.update()
	def close_it(self):
		while self.pos_x>self.HALF_OPEN_POS:
			self.pos_x-=1
			self.current_state="nothing"
			self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
		self.current_state="half_open"	
		self.update()		
	def updateSize(self,x,y,w, h ):
		self.s_width=w
		self.s_height=h
		self.update()
	def updateOpenWindows(self):
		self.open_windows=window.get_open_windows()
		self.update()
	def update_all(self):
		import Config
		conf=Config.get()
		self.conf=conf
		self.HALF_OPEN_POS=int(conf['size'])
		self.ICO_TOP=self.HALF_OPEN_POS-5
		self.OPEN_STATE_TOP=self.ICO_TOP*4+5
		self.SIZE = 15
		self.R=int(conf['r'])
		self.G=int(conf['g'])
		self.B=int(conf['b'])
		self.ICON_SIZE=int(conf['icon-size'])
		self.apps_per_row = math.trunc(((self.s_width/3)-30)/self.ICON_SIZE)
		self.apps_per_col = math.trunc(((self.s_height)-30)/self.ICON_SIZE)
		self.apps_per_page=self.apps_per_col*self.apps_per_row
		self.dock_apps = Apps.find_info(conf['dock-apps'])
		self.pos_x=self.HALF_OPEN_POS
		self.current_state='half_open'
		self.setGeometry(0,self.top_pos,self.pos_x+self.SIZE/2,self.s_height)
		self.open_win.update_all()
		self.update()
		QtGui.QApplication.processEvents()
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	win = Launcher()
	win.show()
	win.raise_()
	sys.exit(app.exec_())