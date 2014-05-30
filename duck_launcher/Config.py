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
	"font":"Hermeneus One",
	"size":40,
	"dock-apps":["Firefox Web Browser"],
	"icon-size":95,
	"blocks":[{"name":"Example","apps":["Firefox Web Browser"], "files":[], "directories":[]}]
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
	create_from_info(d)
	return d
def create_from_info(dict):
	'''
	sheet = cssutils.css.CSSStyleSheet()
	#base
	r1=cssutils.css.CSSStyleRule(selectorText="Base")
	mcolor="main-color:{0},{1},{2} ; ".format(dict["r"], dict["g"],dict["b"])
	scolor="second-color:{0},{1},{2} ; ".format(dict["r2"], dict["g2"],dict["b2"])
	size= "size:{};".format(dict["size"])
	alpha= "alpha:{};".format(dict["alpha"])
	font="font:{};".format(dict["font"])
	base=mcolor+scolor+size+alpha+font
	r1.style=base
	sheet.add(r1)
	#dock
	r2=cssutils.css.CSSStyleRule(selectorText="Dock")
	all=""
	for i,a in enumerate(dict["dock-apps"]):
		str = "app{0}:{1};".format(i,a)
		all+=str

	r2.style=all
	sheet.add(r2)
	#Apps
	r3=cssutils.css.CSSStyleRule(selectorText="Apps")
	isize="icon-size:{}".format(dict["icon-size"])
	r3.style=isize
	sheet.add(r3)
	 #Blocks
	for i, b in enumerate(dict["blocks"]):
		name =  "Block{0} .{1}".format(i,b["name"])
		r = cssutils.css.CSSStyleRule(selectorText=name)
		str=''
		for i, a in enumerate(b["apps"]):
			t="app{0}:{1};".format(i,a)
			str+=t
		for i,f in enumerate(b["files"]):
			t="file{0}:url({1});".format(i,f)
			str+=t
		for i,d in enumerate(b["directories"]):
			t="directory{0}:url({1});".format(i,d)
			str+=t
		r.style=str
		sheet.add(r)
	TEXT=sheet.cssText
	#etc..
	'''
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
	'''
	#disable warnings
	import logging
	cssutils.log.setLevel(logging.CRITICAL)
	#parse
	sheet = cssutils.parseString(STRING)
	dict={}
	blocks=[]
	dict["dock-apps"]=[]
	for r in sheet:
		if r.selectorText == "Base":
			#main-color
			for a in  r.style:
				if a.name == "main-color":
					v= a.value
					dict["r"] = v.split(',')[0]
					dict["g"] = v.split(',')[1]
					dict["b"] = v.split(',')[2]
				if a.name=="second-color":
					v= a.value
					dict["r2"] = v.split(',')[0]
					dict["g2"] = v.split(',')[1]
					dict["b2"] = v.split(',')[2]
				if a.name=="alpha":
					has_alpha="yes"
					dict["alpha"]=a.value
				if a.name=="font":
					dict["font"]=a.value
				if a.name=="size":
					dict["size"]=a.value
		if r.selectorText == "Dock":
			for b in r.style:
				if "app" in b.name:
					dict["dock-apps"].append(str(b.value))
		if r.selectorText == "Apps":
			for a in r.style:
				if a.name=="icon-size":
					dict["icon-size"]=a.value
		if "Block" in r.selectorText:
			b={}
			b['name'] = r.selectorText.split('.')[1]
			apps=[]
			files=[]
			dirs=[]
			for a in r.style:
				if "app" in a.name:
					apps.append(a.value)
				if "file" in  a.name:
					value=a.value.replace("url(","").replace(")","")
					files.append(value)
				if "directory" in a.name:
					value=a.value.replace("url(","").replace(")","")
					dirs.append(value)
			b["apps"]=apps
			b["files"]=files
			b["directories"]=dirs
			blocks.append(b)
	dict["blocks"]=blocks
	return check_dict(dict)
	'''
	try:
		theDict=json.loads(open(cfg).read())
	except ValueError:
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
	dlist = conf["dock-apps"]
	if a in dlist:
		dlist = dlist.remove(a)
	conf["dock-apps"]=dlist
	lastDict = check_dict(conf)
	
