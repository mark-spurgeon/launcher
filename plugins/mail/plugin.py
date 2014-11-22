import sys
sys.dont_write_bytecode=True
from jinja2 import Template
import os

#Search event
def Search(query, color=None,font=None):
	home=os.path.expanduser("~")
	s = str(open("{}/.duck-plugins/mail/index.html".format(home),"r").read())
	t=Template(s)
	return t.render(who=query,color=color)

#JS function events
def onFormSubmit(elements):
	for e in elements:
		if e.has_key("name") and e["name"]=="who":
			print e["value"]
def onDataSent(object, value):
	print "object '{0}' has changed its value to: {1}".format(object, value)