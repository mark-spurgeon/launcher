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
from PyQt4 import QtCore,QtGui
from PyQt4.QtGui import QIcon
import gtk
import wnck
#from gi.repository import Gtk
#from gi.repository import Wnck as wnck
import time
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
	def __init__(self,parent=None,win_info=None):
		QtCore.QThread.__init__(self,parent)
		self.win_info=win_info
		self.parent=parent
	def run(self):
		gtk.main_iteration_do(False)
		screen = wnck.screen_get_default()
		screen.force_update()
		active= screen.get_active_window()
		if active.get_name()=="ducklauncher!!!":
			active= screen.get_previously_active_window()
		w=wnck.window_get(self.win_info ['id'])
		if w!=None:
			try:
				if w.is_minimized():
					w.activate(gtk.get_current_event_time())
				elif w.get_xid()==active.get_xid():
					w.minimize()
				else:
					w.activate(gtk.get_current_event_time())
			except AttributeError:
				w.activate(gtk.get_current_event_time())
		else:
			print("[Duck Launcher] Error:")
########
def get_open_windows():
	gtk.main_iteration_do(False)
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows_stacked()
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
					
					#print w.get_class_group().get_name()
					ico = Apps.ico_from_app(w.get_application().get_icon_name())
					if ico==None:
						ico = Apps.ico_from_app(w.get_application().get_name())
					if ico==None:
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
						img_name=str(window["title"]).replace(" ","").replace(".","").lower()
						img_path="{0}/{1}.png".format(home,img_name)					
						img.save(img_path)
						ico=img_path
					window['icon']=ico


					windows.append(window)
	return windows


class openWindowsThread(QtCore.QThread):
	def __init__(self):
		QtCore.QThread.__init__(self, parent=None)
		self.windows=get_open_windows()
		self.newWindowSignal = QtCore.SIGNAL("new-window")
		self.removeWindowSignal = QtCore.SIGNAL("remove-window")
        def run(self):
        	while 1 : 
        		try:
        			time.sleep(1)
        			new_windows=get_open_windows()
        			if len(self.windows)<len(new_windows):
        				n = [a for a in new_windows if a not in self.windows]
        				self.emit(self.newWindowSignal, n[0])
        				self.windows=new_windows
        			elif len(self.windows)>len(new_windows):
        				n = [a for a in self.windows if a in new_windows]
        				self.emit(self.removeWindowSignal, n)
        				self.windows=new_windows
        			else:
          				n = [a for a in self.windows if a in new_windows]
        				self.emit(self.removeWindowSignal, n)
        				self.windows=new_windows
        		except:
        			print("[Duck Launcher] Error:" , sys.exc_info()[0])

