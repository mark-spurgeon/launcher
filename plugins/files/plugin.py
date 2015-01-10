import sys
sys.dont_write_bytecode=True
from jinja2 import Template
import os
import notify2
import webbrowser 
#Search event
def Search(query, color=None,font=None):
	home=os.path.expanduser("~")
	static="/usr/share/duck-launcher/plugins/files/"
	s = str(open("{}index.html".format(static),"r").read())
	t=Template(s)
	return t.render(path=home,color=(255,255,255),font=font,static="file://{}".format(static))

#JS function events
def onFormSubmit(elements):
	pass
def onDataSent(object, value):
	if object=="openFile":
		webbrowser.open(value)
