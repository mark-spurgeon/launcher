

import os
import sys
sys.dont_write_bytecode=True
import imp

import webbrowser
import subprocess



def get(query):
	plugin_path=os.path.join(os.path.expanduser("~"),".duck-plugins")
	plugins=[]
	for p in os.listdir(plugin_path):
		if os.path.isdir(os.path.join(plugin_path,p)):
			if os.path.isfile(os.path.join(plugin_path,p, "plugin.py")) and os.path.isfile(os.path.join(plugin_path,p,"__init__.py")):			
				sys.path.insert(0, os.path.join(plugin_path,p))
				plugin =imp.load_source(str(p),os.path.join(plugin_path,p,"plugin.py"))
				plugins.append(plugin)
	query_name=query.split(" ")[0].replace("#",'').replace(" ","").lower()
	query_val_list=[ s for s in query.split(" ") if "#{}".format(query_name) !=s.lower()]
	query_value=''
	for q in query_val_list:
		query_value+= q+" "
	
	query_plugs=[ a for a in plugins if a.info["name"].lower()==query_name.lower()]
	#print query_value,query_name, query_plugs
	if len(query_plugs)>0:
		plugin_to_use= query_plugs[-1]
		html=plugin_to_use.Search(query_value)
		#add home
		tmp=open("{0}/{1}/.tmp.html".format(plugin_path,query_name),"w")
		
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
