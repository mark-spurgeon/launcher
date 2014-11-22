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
import gtk
from xdg import IconTheme
from PyQt4.QtGui import QIcon
import Apps
folders = [
	"downloads",
	"music",
	"pictures",
	"public",
	"images"
	]
images = [
	"svg",
	"jpg",
	"JPG",
	"png",
	"ico"
	]
def iconFromName(name,size="small"):
	icon_theme = gtk.icon_theme_get_default()
	icon_=icon_theme.lookup_icon(name, 48, 0)
	is_in_theme=False
	if icon_!=None:
		sizes=icon_theme.get_icon_sizes(name)
		if len(sizes)>0:
			highest_res= sorted(icon_theme.get_icon_sizes(name))[::-1][0]
			is_in_theme=True
			icon=icon_theme.lookup_icon(name, highest_res, 0).get_filename()
		else:
			icon=icon_theme.lookup_icon(name, 48, 0).get_filename()
	if is_in_theme==True:
		return icon
	elif os.path.isfile(name):
		return name
	else:
		found=False 
		dir_list=IconTheme.icondirs
		for d in dir_list:
			if os.path.isdir(d):
				for i in os.listdir(d)[::-1]:
					if i.startswith(name):
						path=os.path.join(d,i)
						found=True
						break
		if found==True:
			return path
		else:
			return icon_theme.lookup_icon("text-plain", 48, 0).get_filename()

def getFilesFromPath(path):
	path=str(path)
	if os.path.isdir(path):
		stuff=[]
		for f in os.listdir(path):
			if f.startswith("."):
				f=None
			elif f.endswith("~"):
				f=None
			if f!=None:
				_f={}
				_f["name"]=f
				whole_f=os.path.join(path,f)
				if os.path.exists(whole_f):
					if os.path.isdir(whole_f):
						_f["type"]="directory"
						if f.lower() in folders:
							name = str("folder-"+f.lower())
							_f["icon"] = "file://"+iconFromName(name)

						else:
							_f["icon"]="file://"+iconFromName("folder")
					elif os.path.isfile(whole_f):
						_f["type"]="file"
						ext=f.split(".")[-1:][0]
						print ext
						if ext in images :
							_f["icon"]=str(whole_f)
						else:
							name="application-"+ext
							if iconFromName(name)!=None:
								_f["icon"] = "file://"+iconFromName(name)
							
					_f["whole_path"]=str(whole_f)
				stuff.append(_f)

		return stuff
if __name__=="__main__":
	f =getFiles()
	f.directory="/home/mark"
	f.all()
