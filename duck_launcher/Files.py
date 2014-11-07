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
from PyQt4.QtGui import QIcon
images = [
	"jpg",
	"JPG",
	"png",
	"svg"
]
videos = [
	"mp4",	
	"avi"
]
sounds = [
	"mp3",
	"wav"
]
class getFiles():
	def __init__(self):
		self.directory=os.getenv("HOME")#varies
		self.default=os.getenv("HOME")#Doesn't vary
	def all(self):
		all=[]
		for f in os.listdir(self.directory):
			if f.startswith("."):
				f=None
			elif f.endswith("~"):
				f=None
			if f!=None:
				dict={}
				dict["name"]=f
				whole_f=os.path.join(self.directory,f)
				if os.path.exists(whole_f):
					if os.path.isdir(whole_f):
						dict["type"]="directory"
					elif os.path.isfile(whole_f):
						dict["type"]="file"
					dict["whole_path"]=str(whole_f)
					all.append(dict)
				else:print("Path doesn't exist")
		return all
		#return [{"type":"folder", "name":"name", "whole_path":"/home/usr/folder"}, ..]
def getFileIcon(name):
	#extension
	icon_theme = gtk.icon_theme_get_default()
	icon_=icon_theme.lookup_icon(name, 48, 0)
	ext=name.split('.')[-1:][0]
	icon=QIcon.fromTheme(name)
	if not icon.isNull():
		return icon	
	elif ext in images:	
		if os.path.isfile(name):
			return QIcon(name)
		'''
	elif ext in images:	
		if os.path.isfile(name):
			return QIcon("/usr/share/duck-launcher/icons/files/file-picture.svg")
		'''
	elif ext in videos:
		if os.path.isfile(name):
			return QIcon("/usr/share/duck-launcher/icons/files/file-video.svg")#will be video file icon
		else:
			return QIcon("/usr/share/duck-launcher/icons/file.svg")		
	elif ext in sounds:
		if os.path.isfile(name):
			return QIcon("/usr/share/duck-launcher/icons/files/file-sound.svg")#will be sound file icon
		else:
			return QIcon("/usr/share/duck-launcher/icons/file.svg")
	else:
		return QIcon("/usr/share/duck-launcher/icons/file.svg")
if __name__=="__main__":
	f =getFiles()
	f.directory="/home/mark"
	f.all()
