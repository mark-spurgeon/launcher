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
import Config
import os
from PySide.QtGui import QIcon
import glob
from xdg import DesktopEntry as _d
APPS=None
def info(filter_):
	appList=[]
	a=False
	all_apps=glob.glob("/usr/share/applications/*.desktop")
	for a in glob.glob("/usr/share/applications/kde4/*.desktop"):
	      all_apps.append(a)
<<<<<<< HEAD
	for a in glob.glob("{}/.local/share/applications/*.desktop".format(os.path.expanduser("~"))):
=======
	for a in glob.glob("{}/.local/share/applications/*.desktop".format(os.environ.get('~'))):
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
	      all_apps.append(a)
	for f in all_apps:
		try:
			if filter_ !="" and filter_.lower() in str(_d.DesktopEntry(unicode(f)).getName()).lower():
				show=True
			elif filter_=='':
				show=True
			else:show=False
			showTerminal= _d.DesktopEntry(unicode(f)).getTerminal()
			dNotShowIn= _d.DesktopEntry(unicode(f)).getNotShowIn()
			dNoDisplay = _d.DesktopEntry(unicode(f)).getNoDisplay()
			dHidden = _d.DesktopEntry(unicode(f)).getHidden()
			dType = _d.DesktopEntry(unicode(f)).getType()
			if dNoDisplay==False and dHidden==False and dType=="Application" and show==True and os.environ.get("XDG_CURRENT_DESKTOP") not in dNotShowIn:  
				app={}
				OnlyShowIn =  _d.DesktopEntry(unicode(f)).getOnlyShowIn()
				current_desk=os.environ.get('XDG_CURRENT_DESKTOP')
				if len(OnlyShowIn)==0 or current_desk in OnlyShowIn:
					app["name"]=str(_d.DesktopEntry(unicode(f)).getName())
					e = str(_d.DesktopEntry(unicode(f)).getExec())
					try:
						pos= e.index("%")
						e= e[:pos-1]
					except ValueError:
						pass
					if showTerminal==True:
						app["exec"]="xterm -e {}".format(e)
					else:
						app["exec"]=e
					app["icon"]=str(_d.DesktopEntry(unicode(f)).getIcon())	
					appList.append(app)
		except UnicodeEncodeError:
			pass
	return sorted(appList,key=lambda x:x["name"])
	APPS=sorted(appList,key=lambda x:x["name"])
def ico_from_name(name):
	icon=QIcon.fromTheme(name)
	if not name:
		return QIcon("/usr/share/duck-launcher/icons/apps.svg")
	elif os.path.isabs(name):
		return QIcon(name)
	elif not icon.isNull():
		return icon
	else:
		found=False 
		dir_list=["/usr/share/pixmaps","{}/.local/share/icons/hicolor/256x256/apps".format(os.path.expanduser("~")),
				"{}/.local/share/icons/hicolor/128x128/apps".format(os.path.expanduser("~")),
				"{}/.local/share/icons/hicolor/48x48/apps".format(os.path.expanduser("~"))]
		for d in dir_list:
			for i in os.listdir(d)[::-1]:
				if i.startswith(name):
					path=os.path.join(d,i)
					found=True
					break
		if found==True:
			return QIcon(path)
		else:
			return QIcon("/usr/share/duck-launcher/icons/apps.svg")
def ico_from_app(app_name):
	global APPS
	if APPS==None:
		APPS=info('')
	for a in APPS:
		if app_name.lower() in a['name'].lower():
			return ico_from_name(a['icon'])
def find_info(apps):
	global APPS
	a_list=[]
	if apps!=None:
		for a in apps:
			in_apps=False
			a_dict={}
			if APPS==None:
				APPS=info('')
			for app in APPS:
				if a in app['name']:
					in_apps=True
					a_dict = app
			if in_apps==True:
				a_list.append(a_dict)
			elif in_apps==False:
				Config.removeFromDockApps(a)
	return a_list
