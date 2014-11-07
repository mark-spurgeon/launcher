

import os
import sys
sys.dont_write_bytecode=True
import imp

import webbrowser
import subprocess
import codecs
import urllib2
try:
	import simplejson as json
except:
	import json

def get(query, color=None, font=None):
	plugin_path=os.path.join(os.path.expanduser("~"),".duck-plugins")
	plugins=[]
	for p in os.listdir(plugin_path):
		if os.path.isdir(os.path.join(plugin_path,p)):
			if os.path.isfile(os.path.join(plugin_path,p, "plugin.py")):			
				sys.path.insert(0, os.path.join(plugin_path,p))
				plugin =imp.load_source(str(p),os.path.join(plugin_path,p,"plugin.py"))
				plugins.append((plugin,p))
	query_name=query.split(" ")[0].replace("#",'').replace(" ","").lower()
	query_val_list=[ s for s in query.split(" ") if "#{}".format(query_name) !=s.lower()]
	query_value=''
	for q in query_val_list:
		query_value+= q+" "
	query_plugs=[ a[0] for a in plugins if a[1].lower()==query_name.lower() ]
	if len(query_plugs)>0:
		print p
		plugin_to_use= query_plugs[-1]
		html=plugin_to_use.Search(query_value,color=color,font=font)
		#add home
		tmp=codecs.open("{0}/{1}/.tmp.html".format(plugin_path,query_name),"w","utf-8")
		
		tmp.write(html)
		tmp.close()
		return "{0}/{1}/.tmp.html".format(plugin_path,query_name)
		
def get_plugin_names():
	plugin_path=os.path.join(os.path.expanduser("~"),".duck-plugins")
	plugins=[]
	for p in os.listdir(plugin_path):
		if os.path.isdir(os.path.join(plugin_path,p)):
			if os.path.join(plugin_path,p, "plugin.py") and os.path.join(plugin_path,p,"__init__.py"):
				plugins.append(p)
	return plugins

class Repo():
	def __init__(self):
		self.plugins=[]
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
			r_file = urllib2.urlopen("https://raw.githubusercontent.com/the-duck/launcher-plugins/master/{}/repo.json".format(plugin))
			r_str = r_file.read()
			r_file.close()
			return json.loads(r_str)
		except:return None
	def getPluginThumnailUrl(self,plugin):
		try:
			f="https://raw.githubusercontent.com/the-duck/launcher-plugins/master/{}/thumbnail.png".format(plugin)
			r_file = urllib2.urlopen(f)
			r_str = r_file.read()
			r_file.close()
			return f
		except:return None
	def getFirst50(self):
		ps=self.getPlugins()
		if ps!=None:
			all_plugins=[]
			for p in ps[:50]:
				d = self.getPluginInfo(p["path"])
				t = self.getPluginThumnailUrl(p["path"])
				if t!=None:
					d["thumbnail"] = t
				all_plugins.append(d)
			return all_plugins
			self.plugins=all_plugins
		else:
			return self.plugins
