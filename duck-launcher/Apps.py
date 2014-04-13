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
import gio as Gio
#from gi.repository import Gio
import os
import glob

def info(filter):
	app_names=[]
	Apps = []
	for app in Gio.app_info_get_all():
		show=True
		if app.should_show()==False:
			show=False
		if show==True:
			app_info = {}
			app_info["name"] = app.get_name()
			app_names.append(app.get_name())
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
	sorted_apps=[]
	for name in  sorted(app_names):
		for a in Apps:
			if a['name']==name:
				if filter!='' and filter.lower() in a["name"].lower():
					sorted_apps.append(a)
				elif filter=='':
					sorted_apps.append(a)
				else:pass
	return sorted_apps
	#return Apps
def ico_from_name(name):
	from PySide.QtGui import QIcon
	icon=QIcon.fromTheme(name)
	if not name:
		return QIcon("/usr/share/duck-launcher/icons/apps.svg")
	elif os.path.isabs(name):
		return QIcon(name)
		print 'name'
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
	from PySide.QtGui import QIcon
	for a in info(''):
		if app_name.upper() in a['name'].upper():
			return ico_from_name(a['icon'])
def find_info(apps):
	a_list=[]
	for a in apps:
		a_dir={}
		for app in info(''):
			if a in app['name']:
				a_dir = app
		a_list.append(a_dir)
	return a_list
if __name__=='__main__':
	info()