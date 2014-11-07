import sys
sys.dont_write_bytecode=True
from jinja2 import Template
import os

info = {"name":"duck-launcher", #--> this is what defines the app in the search query( "#plugin_name ..." ). 
	"author":"John Smith",
	"version":"0.1.2"
	}

def Search(query, color=None, font=None):
	home=os.path.expanduser("~")
	s = str(open("{}/.duck-plugins/duck-launcher/index.html".format(home),"r").read())
	t=Template(s)
	return t.render()

#
def onFormSubmit(elements):
	for e in elements:
		if e.has_key("id") and e["id"]=="name":
			print e["value"]