import sys
sys.dont_write_bytecode=True
from jinja2 import Template
import os

#Search event
def Search(query, color=None,font=None):
	static="/usr/share/duck-launcher/plugins/settings/"
	s = str(open("{}duck-settings.html".format(static),"r").read())
	t=Template(s)
	return t.render(color=(255,255,255),font=font,static="file://{}".format(static))

#JS function events
def onFormSubmit(elements):
	for e in elements:
		if e.has_key("name") and e["name"]=="who":
			print e["value"]
def onDataSent(object, value):
	if object=="openFile":
		import webbrowser
		webbrowser.open(value)
