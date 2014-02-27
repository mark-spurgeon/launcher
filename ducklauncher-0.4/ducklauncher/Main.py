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
import window
#########
conf=Config.get()
HALF_OPEN_POS=int(conf['size'])
ICO_TOP=HALF_OPEN_POS-5
OPEN_STATE_TOP=ICO_TOP*4+5
SIZE = 15
COLOR_R=int(conf['r'])
COLOR_G=int(conf['g'])
COLOR_B=int(conf['b'])
ICON_SIZE=int(conf['icon-size'])
#########

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
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint|QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		r_display = Xlib.display.Display().screen().root
		self.top_pos=0
		self.s_width = r_display.get_geometry().width
		self.s_height = r_display.get_geometry().height-self.top_pos
		#
		self.setGeometry(0,self.top_pos,HALF_OPEN_POS+4,self.s_height)
		#
		self.apps_per_row = math.trunc(((self.s_width/3)-30)/ICON_SIZE)
		self.apps_per_col = math.trunc(((self.s_height)-30)/ICON_SIZE)
		self.apps_per_page=self.apps_per_col*self.apps_per_row
		self.app_page_state=0
		self.pos_x=HALF_OPEN_POS
		self.move=False
		self.current_state="half_open"
		self.activity="apps"
		self.open_windows =window.get_open_windows()
		#
		self.open_win = window.open_windows(HALF_OPEN_POS,self.s_height,COLOR_R,COLOR_G,COLOR_B)
		self.open_state=False
	def paintEvent(self,e):
		qp=QtGui.QPainter()
		qp.begin(self)
		####DRAW
		qp.setBrush(QtGui.QColor(40,40,40,200))
		qp.drawRect(0,0,self.pos_x+SIZE/2,self.s_height)
		
		#qp.setBrush(QtGui.QColor(200,20,20))
		pen = QtGui.QPen(QtGui.QColor(COLOR_R,COLOR_G,COLOR_B), 8, QtCore.Qt.SolidLine)
		qp.setPen(pen)
		qp.drawLine(self.pos_x+SIZE/2-2,0,self.pos_x+SIZE/2-2,self.s_height)
		qp.setPen(QtGui.QPen(QtGui.QColor(COLOR_R,COLOR_G,COLOR_B), 4, QtCore.Qt.SolidLine))
		r_s=3
		a=3
		r = QtCore.QRectF(self.pos_x-SIZE/2-a,self.s_height/2,r_s,r_s)
		qp.drawEllipse(r)
		r = QtCore.QRectF(self.pos_x-SIZE/2-a,self.s_height/2-r_s*3,r_s,r_s)
		qp.drawEllipse(r)
		r = QtCore.QRectF(self.pos_x-SIZE/2-a,self.s_height/2+r_s*3,r_s,r_s)
		qp.drawEllipse(r)
		##
		###
		if self.current_state == "half_open":
			qp.setBrush(QtGui.QColor(COLOR_R,COLOR_G,COLOR_B))
			qp.drawRect(0,0,self.pos_x+SIZE/2,OPEN_STATE_TOP)
			rect = QtCore.QRectF(50,0,150,50)
			qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 3, QtCore.Qt.SolidLine))
			####DRAW BUTTONS
			qp.setBrush(QtGui.QColor(250,250,250,100))
			qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 2, QtCore.Qt.SolidLine))
			###Apps
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
				
				apps = Apps.find_info(conf['dock-apps'])
				####OFF WE GOOO!
				for i,a in enumerate(apps):
					ico = Apps.ico_from_name(str(a['icon']))
					if ico!=None:
						ico.paint(qp,6,OPEN_STATE_TOP+ICO_TOP*i+10,ICO_TOP-5,ICO_TOP-5)
			except KeyError:
				print 'No Dock apps'
			
			#Open Windows Button
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/open-apps.svg")
			icon.paint(qp,10,self.s_height-ICO_TOP*2-10,ICO_TOP-10,ICO_TOP-10)
			rect = QtCore.QRectF(10,self.s_height-ICO_TOP*2-10,ICO_TOP-10,ICO_TOP-10)
			qp.setFont(QtGui.QFont('Hermeneus One',14))
			qp.drawText(rect, QtCore.Qt.AlignCenter, str(len(self.open_windows)))
			
			#Quit Button
			icon = QtGui.QIcon("/usr/share/duck-launcher/icons/quit.svg")
			icon.paint(qp,10,self.s_height-ICO_TOP,ICO_TOP-10,ICO_TOP-10)	
		##
		##
		if self.current_state=="open":
			
			if self.activity=="apps":
				###page_buttons
				max_apps=  math.trunc(len(Apps.info())/self.apps_per_page)+1
				for i in range(0, max_apps):
						btn_size = 20
						x_pos = self.s_width/6-btn_size+(btn_size*i)
						rect = QtCore.QRectF(x_pos,2,btn_size,btn_size)
						qp.drawRect(rect)
						qp.drawText(rect,QtCore.Qt.AlignCenter,str(i+1))
				###app_buttons
				for i, app in enumerate(Apps.info()):
						app_page = math.trunc(i/self.apps_per_page)
						if app_page==self.app_page_state:
							qp.setBrush(QtGui.QColor(COLOR_R,COLOR_G,COLOR_B))
							row_pos = math.trunc(i/self.apps_per_row)
							x_pos = ICON_SIZE*(i-(row_pos*self.apps_per_row))+30
							y_pos = row_pos*ICON_SIZE+30-(app_page*(ICON_SIZE*self.apps_per_col))
							try:		
								string = str(app['icon']).replace('\n','')
								da_icon=Apps.ico_from_name(string)
								if da_icon!=None:
									da_icon.paint(qp,x_pos+10,y_pos+10,ICON_SIZE-30,ICON_SIZE-30)	
							except KeyError:
								i = QtGui.QImage('images/apps.png')
								rect= QtCore.QRectF(x_pos+10,y_pos+10,ICON_SIZE-30,ICON_SIZE-30)
								qp.drawImage(rect,i)
							qp.setPen(QtGui.QColor(250,250,250))
							text_rect = QtCore.QRectF(x_pos+5,y_pos+ICON_SIZE-20,ICON_SIZE+4,30)
							qp.setFont(QtGui.QFont('Hermeneus One',8))
							qp.drawText(text_rect,str(app["name"]))
				
			###	
			if self.activity=="files":
				qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 3, QtCore.Qt.SolidLine))
				qp.drawText(QtCore.QRectF(10,10,self.s_width/3,200),"Files are not available yet.")
			if self.activity=="settings":
				qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 3, QtCore.Qt.SolidLine))
				qp.drawText(QtCore.QRectF(20,20,self.s_width/3,200),"Settings are not available yet..")
			if self.activity=="star":
				qp.setPen(QtGui.QPen(QtGui.QColor(250,250,250), 3, QtCore.Qt.SolidLine))
				#qp.drawText(QtCore.QRectF(20,20,self.s_width/3,200),"'Star' is not available yet...")
				blocks=conf['blocks']
				for i,b in enumerate(blocks):
					h=20+ICON_SIZE*3*i
					qp.setFont(QtGui.QFont('Hermeneus One',16))
					qp.drawText(QtCore.QRectF(20, h,self.s_width/3,200),b['name'])
					#apps
					b_apps = Apps.find_info(b['apps'])
					for j, a in enumerate(b_apps):
						qp.setFont(QtGui.QFont('Hermeneus One',10))
						ico = Apps.ico_from_name(a['icon'])
						if ico!=None:
							ico.paint(qp,30+ICON_SIZE*j, 40+h,ICON_SIZE-30,ICON_SIZE-30)
						qp.drawText(QtCore.QRectF(30+ICON_SIZE*j, ICON_SIZE+10+h, ICON_SIZE,40),a['name'])
					#dirs
					for k, d in enumerate(b['directories']):
						ico=QtGui.QIcon('/usr/share/duck-launcher/icons/folder.svg')
						ico.paint(qp,30+ICON_SIZE*k, ICON_SIZE+50+h, ICON_SIZE-30, ICON_SIZE-30)
						d_name=d.split('/')[-1]
						qp.drawText(QtCore.QRectF(30+ICON_SIZE*k, (2*ICON_SIZE)+20+h, ICON_SIZE,40),d_name)
					#files
					for k, f in enumerate(b['files']):
						ico=QtGui.QIcon('/usr/share/duck-launcher/icons/file.svg')
						ico.paint(qp,30+ICON_SIZE*k, (2*ICON_SIZE)+50+h, ICON_SIZE-30, ICON_SIZE-30)
						f_name=f.split('/')[-1]
						qp.drawText(QtCore.QRectF(30+ICON_SIZE*k, (3*ICON_SIZE)+20+h, ICON_SIZE,40),f_name)
	def mouseMoveEvent(self,e):
		if self.current_state!='open':
			self.current_state="nothing"
		if self.current_state=='nothing':
			if e.x()>(self.pos_x-SIZE):
				self.move=True
			if self.move==True:
				self.update_pos(e.x())
	def mouseReleaseEvent(self,e):
		self.move=False
		###sets position to right one
		pos_list = [HALF_OPEN_POS, self.s_width/3]
		closest = min(pos_list, key=lambda x: abs(x-self.pos_x))
		if closest<self.pos_x:
			while closest<self.pos_x:
				self.pos_x-=5
				self.setGeometry(0,self.top_pos,self.pos_x+SIZE/2,self.s_height)
				QtGui.QApplication.processEvents()
				self.update()
			self.pos_x=closest
			QtGui.QApplication.processEvents()
			self.update()
		elif closest>self.pos_x:
			while closest>self.pos_x:
				self.pos_x+=5
				self.setGeometry(0,self.top_pos,self.pos_x+SIZE/2,self.s_height)
				QtGui.QApplication.processEvents()
				self.update()
			self.pos_x=closest
			QtGui.QApplication.processEvents()
			self.update()
		##set the current state
		if closest==HALF_OPEN_POS:
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
			if self.pos_x-SIZE<x_m<self.pos_x and self.move==False:
				self.close_it()
			###app events
			if self.activity == "apps":
				max_apps=  math.trunc(len(Apps.info())/self.apps_per_page)+1
				##Change Page
				for i in range(0,max_apps):
						btn_size = 20
						x_pos = self.s_width/6-btn_size+(btn_size*i)
						if x_pos<x_m<x_pos+btn_size and 2<y_m<2+btn_size:
							self.app_page_state=i
							self.update()
							QtGui.QApplication.processEvents()	
				## launch apps
				for i, app in enumerate(Apps.info()):
					app_page = math.trunc(i/self.apps_per_page)
					if app_page==self.app_page_state:
						row_pos = math.trunc(i/self.apps_per_row)
						x_pos = ICON_SIZE*(i-(row_pos*self.apps_per_row))+30
						y_pos = row_pos*ICON_SIZE+30-(app_page*(ICON_SIZE*self.apps_per_col))
						if x_pos<x_m<(x_pos+ICON_SIZE) and y_pos<y_m<(y_pos+ICON_SIZE):
							print "It should launch:  " + app["name"] + "  with  " + app["exec"]
							thread = Launch(parent=self)
							thread.app=app["exec"]
							thread.start()
							self.close_it()
						
		if self.current_state=="half_open":
			##buttons
			if 0<x_m<HALF_OPEN_POS:
				if 0<y_m<ICO_TOP:
					self.activity="apps"
					self.open_it()
				if ICO_TOP<y_m<ICO_TOP*2:
					self.activity="files"
					self.open_it()
				if ICO_TOP*2<y_m<ICO_TOP*3:
					self.activity="settings"
					self.open_it()
				if ICO_TOP*3<y_m<ICO_TOP*4:
					self.activity="star"
					self.open_it()
				try:
				
					apps = Apps.find_info(conf['dock-apps'])
					####OFF WE GOOO!
					for i,a in enumerate(apps):
						if OPEN_STATE_TOP+ICO_TOP*i+10<y_m<OPEN_STATE_TOP+ICO_TOP*(i+1)+10:
							print "It should launch:  " + a["name"] + "  with  " + a["exec"]
							thread = Launch(parent=self)
							thread.app=a["exec"]
							thread.start()
							self.close_it()
				except KeyError:
					pass
				if  self.s_height-ICO_TOP*2-20<y_m<self.s_height-ICO_TOP-20:
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
				if  self.s_height-ICO_TOP*2-20>y_m<self.s_height-ICO_TOP-20:
					self.open_win.close()
				if  self.s_height-ICO_TOP<y_m<self.s_height:
					sys.exit()
				
	def wheelEvent(self,e):
		if self.activity == 'apps':
			value= int(e.delta()/120)
			max_pages=math.trunc(len(Apps.info())/self.apps_per_page)
			if value<0 and self.app_page_state>0:
				self.app_page_state-=1
			if value>0 and self.app_page_state<max_pages:
				self.app_page_state+=1
			self.update()
			QtGui.QApplication.processEvents()
	###ANIMATIONS	
	def update_pos(self,pos):
		if pos>4:
			self.pos_x=pos
			self.setGeometry(0,self.top_pos,self.pos_x+SIZE/2,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
	def open_it(self):
		while self.pos_x<self.s_width/3:
			self.current_state='nothing'
			self.pos_x+=1.5
			self.setGeometry(0,self.top_pos,self.pos_x+SIZE/2,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
		self.current_state="open"	
		self.update()
	def close_it(self):
		while self.pos_x>HALF_OPEN_POS:
			self.pos_x-=1
			self.current_state="nothing"
			self.setGeometry(0,self.top_pos,self.pos_x+SIZE/2,self.s_height)
			self.update()
			QtGui.QApplication.processEvents()
		self.current_state="half_open"	
		self.update()		
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	win = Launcher()
	win.show()
	win.raise_()
	sys.exit(app.exec_())
