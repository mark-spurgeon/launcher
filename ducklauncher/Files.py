import os
from gtk import icon_theme_get_default
class getFiles():
	def __init__(self):
		self.directory=os.getenv("HOME")#varies
		self.default=os.getenv("HOME")#Doesn't vary
	def all(self):
		all=[]
		for f in os.listdir(self.directory): 
			if f.startswith("."):
				f=None
			if f!=None:
				dict={}
				dict["name"]=f
				whole_f=os.path.join(self.directory,f)
				if os.path.exists(whole_f):
					if os.path.isdir(whole_f):
						dict["type"]="directory"
					elif os.path.isfile(whole_f):
						dict["type"]="file"
					dict["whole_path"]=str(whole_f)
					all.append(dict)
				else:print "Path doesn't exist"
		return all
		#return [{"type":"folder", "name":"name", "whole_dir":"/home/usr/folder"}, ..]
def getFileIcon(file):
	iconTheme = icon_theme_get_default()
	iconInfo = iconTheme.lookup_icon(file, 48, 0)
	if iconInfo != None:
		return iconInfo.get_filename()
	else:
		return None
if __name__=="__main__":
	f =getFiles()
	f.directory="/home/mark"
	f.all()