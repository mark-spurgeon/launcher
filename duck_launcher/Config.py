#! /usr/bin/python
# -*- coding: utf-8 -*-
#########
#Copyright (C) 2014  Mark Spurgeon <markspurgeon96@hotmail.com>
	
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

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
import defaultConfig

import dbus
try:
	import cPickle as pickle
except:
	print("Using python version of pickle")	
	import pickle
CONFIG={}
defaultDict=defaultConfig.Dict
def check_dict(d):
	new_d={}
	if d.has_key("r"):
		new_d["r"]=int(d["r"])
	else:
		new_d["r"]=int(defaultDict["r"])
	if d.has_key("g"):
		new_d["g"]=int(d["g"])
	else:
		new_d["g"]=int(defaultDict["g"])
	if d.has_key("b"):
		new_d["b"]=int(d["b"])
	else:
		new_d["b"]=int(defaultDict["b"])
	if d.has_key("r2"):
		new_d["r2"]=int(d["r2"])
	else:
		new_d["r2"]=int(defaultDict["r2"])
	if d.has_key("g2"):
		new_d["g2"]=int(d["g2"])
	else:
		new_d["g2"]=int(defaultDict["g2"])
	if d.has_key("b2"):
		new_d["b2"]=int(d["b2"])
	else:
		new_d["b2"]=int(defaultDict["b2"])
	if d.has_key("icon-size"):
		new_d["icon-size"]=int(d["icon-size"])
	else:
		new_d["icon-size"]=int(defaultDict["icon-size"])
	if d.has_key("size"):
		new_d["size"]=int(d["size"])
	else:
		new_d["size"]=int(defaultDict["size"])
	if d.has_key("alpha"):
		new_d["alpha"]=int(d["alpha"])
	else:
		new_d["alpha"]=int(defaultDict["alpha"])
	if d.has_key("animation-speed"):
		new_d["animation-speed"]=float(d["animation-speed"])
	else:
		new_d["animation-speed"]=float(defaultDict["animation-speed"])
	if d.has_key("dock-apps"):
		new_d["dock-apps"]=[]
		for n in d["dock-apps"]:
			new_d["dock-apps"].append(str(n))
	else:
		new_d["dock-apps"]=list(defaultDict["dock-apps"])
	if d.has_key("blocks"):
		new_d["blocks"]=str(d["blocks"])
	else:
		new_d["blocks"]=list(defaultDict["blocks"])
	if d.has_key("font"):
		new_d["font"]=str(d["font"])
	else:
		new_d["font"]=str(defaultDict["font"])
	if d.has_key("init-manager"):
		new_d["init-manager"]=str(d["init-manager"])
	else:
		new_d["init-manager"]=str(defaultDict["init-manager"])
	'''
	if "r" not in d:
		d["r"]=defaultDict["r"]
	if "g" not in d:
		d["g"]=defaultDict["g"]
	if "b" not in d:
		d["b"]=defaultDict["b"]
	if "r2" not in d:
		d["r2"]=defaultDict["r2"]
	if "g2" not in d:
		d["g2"]=defaultDict["g2"]
	if "b2" not in d:
		d["b2"]=defaultDict["b2"]
	if "alpha" not in d:
		d["alpha"]=defaultDict["alpha"]
	if "size" not in d:
		d["r"]=defaultDict["r"]
	if "dock-apps" not in d:
		d["dock-apps"]=defaultDict["dock-apps"]
	if "icon-size" not in d:
		d["icon-size"]=defaultDict["icon-size"]
	if "blocks" not in d:
		d["blocks"]=defaultDict["blocks"]
	if "font" not in d:
		d["font"]=defaultDict["font"]
	#Add speed	
	if "animation-speed" not in d:
		d["animation-speed"]=defaultDict["animation-speed"]
	
	if "init-manager" not in d:
		d["init-manager"]=defaultDict["init-manager"]
	#
	'''
	create_from_info(new_d)
	return d
def create_from_info(dict):
	HOME = os.path.expanduser("~")
	dir =os.environ.get('XDG_CONFIG_HOME',os.path.join(HOME,'.config'))
	cfg= dir+'/duck-launcher.config'
	the_file=open(cfg,"wb")
	pickle.dump(dict,the_file)
	the_file.close()
def get():
	HOME = os.path.expanduser("~")
	dir =os.environ.get('XDG_CONFIG_HOME',os.path.join(HOME,'.config'))
	cfg= dir+'/duck-launcher.config'
	if "duck-launcher.config" not in os.listdir(dir):
		create_from_info(defaultDict)
	if os.path.isdir(os.path.join(HOME,".duck-plugins"))==False:
		if os.path.isdir("/usr/lib/duck_launcher/plugins"):
			import shutil
			shutil.copytree("/usr/share/duck-launcher/plugins",os.path.join(HOME,".duck-plugins"))
	the_file=open(cfg,"rb")
	try:
		theDict=pickle.load(the_file)
		global CONFIG
		CONFIG=theDict
	except:
		if CONFIG!={}:
			theDict=CONFIG
		else:
			theDict=defaultDict
	the_file.close()
	return check_dict(theDict)
def get_from_block(block):
	all=[]
	if block.has_key("apps"):
		for f in block['apps']:
			data = {}
			data['value']=f
			data['type']='app'
			all.append(data)
	if block.has_key("directories"):
		for f in block['directories']:
			data = {}
			data['value']=f
			data['type']='directory'
			all.append(data)
	if block.has_key("files"):
		for f in block['files']:
			data = {}
			data['value']=f
			data['type']='file'
			all.append(data)
	return all
def removeFromDockApps(a):
	conf = get()
	dlist = conf["dock-apps"]
	dlist = [x for x in dlist if x != a]
	conf["dock-apps"]=dlist
	lastDict = check_dict(conf)
	
