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
from xml.etree import ElementTree as ET
from lxml import etree
import os

def create_default_config():
	HOME = os.path.expanduser("~")
	dir =os.environ.get('XDG_CONFIG_HOME',os.path.join(HOME,'.config'))
	filename=dir+"/duck.conf"
	###generate xml file
	e = ET.Element('duck')
	##normal stuff
	base = ET.SubElement(e, 'base')
	color = ET.SubElement(base, 'color',attrib={'r':'250','g':'140','b':'40'})
	size = ET.SubElement(base,'size',attrib={'value':'50'})
	#dock apps
	dock = ET.SubElement(e,'dock')
	apps = ['Firefox Web Browser','GIMP']
	for a in apps:
		apps=ET.SubElement(dock,'app', attrib={'name':a})
	#Apps settings
	apps=ET.SubElement(e,'apps')
	ico_size=ET.SubElement(apps,'icon-size',attrib={'value':'80'})
	#Star settings
	star = ET.SubElement(e,'star')
	blocks = [{'apps': ['Firefox'],
	'files': ['/home/duck/Graphics/file.blend'],
	'directories': ['/home/duck/Graphics'],
	'name': 'Graphics'}]
	for block in blocks:
		b = ET.SubElement(star,'block', attrib={'name': block['name']})
		for app in block['apps']:
			a = ET.SubElement(b,'app', attrib={'name': app})
		for file in block['files']:
			f = ET.SubElement(b,'file', attrib={'name': file})
		for dir in block['directories']:
			d = ET.SubElement(b,'directory', attrib={'name': dir})
	
	#create file
	string = ET.tostring(e, encoding='utf8', method='xml')
	r = etree.fromstring(string)
	file_content = etree.tostring(r, pretty_print=True)
	print file_content
	the_file = open(filename, 'w')
	the_file.write(file_content)
def create_from_info(dict):
	pass

def get():
	info={}
	HOME = os.path.expanduser("~")
	dir =os.environ.get('XDG_CONFIG_HOME',os.path.join(HOME,'.config'))
	if not "duck.conf" in os.listdir(dir):
		filename = create_default_config()
		print 'a'
	
	filename=os.path.join(dir,'duck.conf')
	##parse file
	e = ET.parse(filename)
	r = e.getroot()
	for stuff in r:
		if 'base' in stuff.tag:
			for i in stuff:
				if 'color' in i.tag:
					r,g,b=int(i.attrib['r']),int(i.attrib['g']),int(i.attrib['b'])
					info['r']=r
					info['g']=g
					info['b']=b
				if 'size' in i.tag:
					info['size']=int(i.attrib['value'])
		if  'dock' in stuff.tag:
			info['dock-apps']=[]
			for i in stuff:
				info['dock-apps'].append(i.attrib['name'])
		if 'apps' in stuff.tag:
			for i in stuff:
				if 'icon-size' in i.tag:
					info['icon-size']=int(i.attrib['value'])
		if 'star' in stuff.tag:
			blocks=[]
			for b in stuff:
				block={}
				block['name'] = b.attrib['name']
				apps=[]
				files=[]
				directories=[]
				for thing in b:
					if 'app' in  thing.tag:
						apps.append(thing.attrib['name'])
					if 'file' in thing.tag:
						files.append(thing.attrib['name'])
					if 'directory' in thing.tag:
						directories.append(thing.attrib['name'])
				block['apps']=apps
				block['files']=files
				block['directories']=directories
				blocks.append(block)
			info['blocks']=blocks
	return info
if __name__=='__main__':
	print get()