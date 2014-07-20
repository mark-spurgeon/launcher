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
try:
    import simplejson as json
except ImportError:
    import json

defaultDict={
	"r":255,
	"g":92,
	"b":36,
	"r2":40,
	"g2":40,
	"b2":40,
	"alpha":200,
	"font":"Droid Sans",
	"size":40,
	"dock-apps":["Firefox Web Browser"],
	"icon-size":95,
	"blocks":[{"name":"Example","apps":["Firefox Web Browser"], "files":[], "directories":[]}],
	"init-manager":"systemd"
}
def check_dict(d):
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
	
	if "init-manager" not in d:
		d["init-manager"]=defaultDict["init-manager"]
	#
	create_from_info(d)
	return d
def create_from_info(dict):
	TEXT=json.dumps(dict,indent=2)
	HOME = os.path.expanduser("~")
	dir =os.environ.get('XDG_CONFIG_HOME',os.path.join(HOME,'.config'))
	cfg= dir+'/duck-launcher.config'
	file=open(cfg,"w")
	file.write(TEXT)
	file.close()
def get():
	HOME = os.path.expanduser("~")
	dir =os.environ.get('XDG_CONFIG_HOME',os.path.join(HOME,'.config'))
	cfg= dir+'/duck-launcher.config'
	if "duck-launcher.config" not in os.listdir(dir):
		create_from_info(defaultDict)

	try:
		theDict=json.loads(open(cfg).read())
		if isinstance(theDict["dock-apps"],list):
			pass
		else:
			theDict["dock-apps"]=[]
	except ValueError:
		print("[Duck Launcher] Error: ValueError")
		theDict=defaultDict
	return check_dict(theDict)

def get_from_block(block):
	all=[]
	for f in block['apps']:
		data = {}
		data['value']=f
		data['type']='app'
		all.append(data)
	for f in block['directories']:
		data = {}
		data['value']=f
		data['type']='directory'
		all.append(data)
	for f in block['files']:
		data = {}
		data['value']=f
		data['type']='file'
		all.append(data)
	return all
def removeFromDockApps(a):
	conf = get()
	print "removing"
	dlist = conf["dock-apps"]
	dlist = [x for x in dlist if x != a]
	print dlist
	conf["dock-apps"]=dlist
	lastDict = check_dict(conf)
	
