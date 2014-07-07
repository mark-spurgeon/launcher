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
	for f in glob.glob("/usr/share/applications/*.desktop"):
		try:
			if filter_ !="" and filter_.lower() in str(_d.DesktopEntry(unicode(f)).getName()).lower():
				show=True
			elif filter_=='':
				show=True
			else:show=False
			dNoDisplay = _d.DesktopEntry(unicode(f)).getNoDisplay()
			dHidden = _d.DesktopEntry(unicode(f)).getHidden()
			dType = _d.DesktopEntry(unicode(f)).getType()
			if dNoDisplay==False and dHidden==False and dType=="Application" and show==True:  
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
					app["exec"]=e
					app["icon"]=str(_d.DesktopEntry(unicode(f)).getIcon())	
					appList.append(app)
		except UnicodeEncodeError:
			pass
	return sorted(appList,key=lambda x:x["name"])
	APPS=sorted(appList,key=lambda x:x["name"])
	'''
	Apps = []
	for app in Gio.app_info_get_all():
		show=True
		if filter=='':
			show=True
		else:
			show=False
		#
		if app.should_show()==False:
			show=False
			
		if show==True:
			app_info = {}
			app_info["name"] = app.get_name()
			app_info["exec"] = str(app.get_commandline())
			if '%' in app_info["exec"]:
				num = app_info["exec"].index("%")
				stuff = app_info["exec"][num:]
				app_info["exec"] = app_info["exec"].replace(stuff,'')
			##icon
			desk_file = app.get_id()
			desk_path = "/usr/share/applications/"+str(desk_file)
			if os.path.isfile(desk_path):
				f = open(desk_path,'r')
				for line in f.readlines():
					if 'Icon=' in line:
						icon_name = line.replace('Icon=','').replace('\n','')
						app_info["icon"]=str(icon_name)
			Apps.append(app_info)
	##set sorted
	return sorted(Apps,key=lambda x:x["name"])
	'''
def ico_from_name(name):
	icon=QIcon.fromTheme(name)
	if not name:
		return QIcon("/usr/share/duck-launcher/icons/apps.svg")
	elif os.path.isabs(name):
		return QIcon(name)
	elif not icon.isNull():
		return icon
	else:
		l=[]
		for i in os.listdir('/usr/share/pixmaps')[::-1]:
			if i.startswith(name):
				path=os.path.join("/usr/share/pixmaps",i)
				l.append(path)
		if len(l)>0:
			return QIcon(l[0])
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
