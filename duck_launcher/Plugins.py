#! /usr/bin/python
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
import os
import sys
sys.dont_write_bytecode=True
import imp
import webbrowser
import subprocess
import codecs
import urllib2
import notify2
try:
	import simplejson as json
except:
	import json

class get():
	def __init__(self,query):
		plugin_path= "/usr/share/duck-launcher/plugins" #os.path.join(os.path.expanduser("~"),".duck-plugins")
		user_plugin_path = os.path.join(os.path.expanduser("~"),".duck-plugins")
		plugins=[]
		for p in os.listdir(plugin_path):
			if os.path.isdir(os.path.join(plugin_path,p)):
				if os.path.isfile(os.path.join(plugin_path,p, "plugin.py")):			
					sys.path.insert(0, os.path.join(plugin_path,p))
					plugin =imp.load_source(str(p),os.path.join(plugin_path,p,"plugin.py"))
					plugins.append((plugin,p))
		query_name=query.split(" ")[0].replace("#",'').replace(" ","").lower()
		query_val_list=[ s for s in query.split(" ") if "#{}".format(query_name) !=s.lower()]
		self.query_value=''
		for q in query_val_list:
			self.query_value+= q+" "
		query_plugs=[ a for a in plugins if a[1].lower()==query_name.lower() ]
		if len(query_plugs)>0:
			self.plugin_name=query_plugs[-1][1]
			self.plugin_to_use= query_plugs[-1][0]
			#html=plugin_to_use.Search(query_value,color=color,font=font)
	def isAlright(self):
		if self.plugin_name and self.plugin_to_use:
			return True
		else:
			return False
	def html(self,color=None,font=None):
		html=self.plugin_to_use.Search(self.query_value,color=color,font=font)
		return html
	def info(self):
		path = os.path.join("/usr/share/duck-launcher/plugins/",self.plugin_name,"manifest.json")
		if os.path.isfile(path):
			f= open(path,"r")
			info = json.load(f)
			f.close()
			return info
	def getColor(self,what):
		i = self.info()
		if i!=None and i.has_key("background-color") and i.has_key("foreground-color"):
			if what=="background":
				bg = i["background-color"]
			elif what=="foreground":
				bg = i["foreground-color"]

			if "rgb(" in bg:
				try:
					str_rgb = bg.replace("rgb(",'').replace(")","").replace(" ","")
					l_rgb = str_rgb.split(",")
					rgb=(int(l_rgb[0]),int(l_rgb[1]),int(l_rgb[2]))
					return rgb
				except:
					return (40,40,40)
			elif "#" in bg:
				try:
					value = bg.lstrip('#')
					lv = len(value)
					return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
				except:
					return (255,255,255)
		else:
			if what=="background":return (40,40,40)
			elif what=="foreground":return (255,255,255)
	def getLogo(self):
		path= os.path.join("/usr/share/duck-launcher/plugins", self.plugin_name,"logo.svg")
		if os.path.isfile(path):
			return path
		else:
			return None
def get_plugin_names():
	plugin_path="/usr/share/duck-launcher/plugins"
	plugins=[]
	for p in os.listdir(plugin_path):
		if os.path.isdir(os.path.join(plugin_path,p)):
			if os.path.join(plugin_path,p, "plugin.py") and os.path.join(plugin_path,p,"__init__.py"):
				plugins.append(p)
	return plugins

def getCurrentPluginModule(name):
	home=os.path.expanduser("~")
	#pl_dir=os.path.join(home,".duck-plugins")
	pl_dir="/usr/share/duck-launcher/plugins"
	if os.path.isfile(os.path.join(pl_dir,name,"plugin.py")):
		plugin =imp.load_source(str(name),os.path.join(pl_dir,name,"plugin.py"))
		return plugin



class Repo():
	def __init__(self):
		self.plugins=[]
		notify2.init("duck launcher")
	def getPlugins(self):
		try:
			r_file = urllib2.urlopen("https://api.github.com/repos/the-duck/launcher-plugins/contents")
			r_str = r_file.read()
			r_file.close()
			pl_list=[{ "path" : f["path"], "sha":f["sha"]} for f in json.loads(r_str) if f["type"]=="dir"]
			return pl_list
		except:return None
	def getPluginInfo(self,plugin):
		try:
			r_file = urllib2.urlopen("https://raw.githubusercontent.com/the-duck/launcher-plugins/master/{}/manifest.json".format(plugin))
			r_str = r_file.read()
			r_file.close()
			return json.loads(r_str)
		except:return None
	def getPluginLogoUrl(self,plugin):
		try:
			f="https://raw.githubusercontent.com/the-duck/launcher-plugins/master/{}/logo.svg".format(plugin)
			r_file = urllib2.urlopen(f)
			r_str = r_file.read()
			r_file.close()
			return f
		except:return None
	def getStatus(self,pluginDict):
		f="/usr/share/duck-launcher/plugins/{}/manifest.json".format(pluginDict["path"])
		if os.path.isfile(f):
			s = open(f,"r")
			d = json.loads(s.read())
			s.close()
			if d.has_key("version"):
				if str(pluginDict["version"]) != str(d["version"]):
					return "installed/old"
				else:
					return "installed/newest"
			else:
				return "uninstalled"
		else:
			return "uninstalled"
	def getFirst50(self):
		ps=self.getPlugins()
		if ps!=None:
			all_plugins=[]
			for p in ps[:50]:
				d = self.getPluginInfo(p["path"])
				t = self.getPluginLogoUrl(p["path"])
				a=dict(p.items()+d.items())
				u=self.getStatus(a)
				if u!=None:
					a["status"]=str(u)
				if t!=None:
					a["thumbnail"] = t

				all_plugins.append(a)
			return all_plugins
			self.plugins=all_plugins
		else:
			return self.plugins
	def installPlugin(self,plugin):
		destination=os.path.join("/usr/share/duck-launcher/plugins/",plugin)
		path_to_download= "https://github.com/the-duck/launcher-plugins/trunk/{}".format(str(plugin))
		try:
			subprocess.call(["gksudo", "duck-plugins install --repo {}".format(plugin)])
			success=True
		except Exception as e:
			success=False

		if not os.path.isdir(destination):
			success=False

		if success==True:
			n = notify2.Notification("Plugin installation successful",
                         "The plugin <b>{}</b> has been successfully installed".format(plugin),
                         "dialog-information"   # Icon nam
                        )
			n.show()
		elif success==False:
			n = notify2.Notification("Could not install plugin '{}'".format(plugin),
                         "Please check your internet connection",
                         "dialog-error"   # Icon name
                        )
			n.show()
	def removePlugin(self, plugin):
		destination=os.path.join("/usr/share/duck-launcher/plugins/",plugin)
			
		try:
			subprocess.call(["gksudo", "duck-plugins remove {}".format(plugin)])
			success=True
		except Exception:
			success=False
		if os.path.isdir(destination):
			success==False
		if success==True:
			n = notify2.Notification("The plugin'{}' has been successfully removed".format(plugin),
						"",
                         "dialog-information"   # Icon nam
                        )
			n.show()
		elif success==False:
			n = notify2.Notification("Could not remove plugin '{}'".format(plugin),
                         "Please report this bug",
                         "dialog-error"   # Icon name
                        )
			n.show()			
if __name__=="__main__":
	r = Repo()
	p = r.getFirst50()
	l = [k for k in p if k["path"]=="guardian"]
	r.installPlugin(l[0])
