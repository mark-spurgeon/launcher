import sys
sys.dont_write_bytecode=True
from jinja2 import Template
import os

def Search(query, color=None, font=None):
	static="/usr/share/duck-launcher/plugins/duck-launcher/"
	s = str(open("{}index.html".format(static),"r").read())
	t=Template(s)
	return t.render(static="file://{}".format(static))
