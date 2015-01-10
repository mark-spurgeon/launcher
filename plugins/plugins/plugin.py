import sys
sys.dont_write_bytecode=True
from jinja2 import Template
import os
sys.path.append(os.path.abspath("/usr/lib/duck_launcher/"))
import Plugins
#Search event
def Search(query, color=None,font=None):
	static="/media/mark/Storage/python/Launcher/current/plugins/plugins/"
	s = str(open("{}plugins.html".format(static),"r").read())
	rep=Plugins.Repo()
	plugins=rep.getFirst50()
	t=Template(s)
	return t.render(font=font,static="file://{}".format(static),plugins=plugins)

#JS function events
def onFormSubmit(elements):
	for e in elements:
		if e.has_key("name") and e["name"]=="who":
			print e["value"]
def onDataSent(object, value):
	if object=="openFile":
		import webbrowser
		webbrowser.open(value)
