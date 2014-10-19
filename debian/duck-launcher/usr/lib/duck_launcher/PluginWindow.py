import os
import sys
sys.dont_write_bytecode=True
import imp
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import webbrowser
import subprocess

import dbus
import dbus.service
import dbus.mainloop.glib

import Config


def getCurrentPluginModule(name):
	home=os.path.expanduser("~")
	pl_dir=os.path.join(home,".duck-plugins")
	if os.path.isfile(os.path.join(pl_dir,name,"plugin.py")):
		plugin =imp.load_source(str(name),os.path.join(pl_dir,name,"plugin.py"))
		return plugin
class LaunchCommand(QThread):
	def __init__(self,parent=None,call=None):
		QThread.__init__(self,parent)
		self.parent=parent
		self.call=call
	def run(self):	
		if self.call!=None:
			subprocess.call(self.call)
		
class Container(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		#self.setAttribute(Qt.WA_X11NetWmWindowTypeDock, True)
		self.setWindowTitle("ducklauncher!!!")
		self.setWindowFlags(Qt.WindowStaysOnTopHint)#Qt.FramelessWindowHint|Qt.X11BypassWindowManagerHint)
		d = QDesktopWidget()
		self.top_pos=0
		self.s_width = d.availableGeometry().width()
		self.s_height =d.availableGeometry().height()
		self.top_pos= d.availableGeometry().y()
		self.view = QWebView(self)
		#layout = QVBoxLayout(self)
		#layout.setGeometry(QRect(10,10,20,100))
		#self.setLayout(layout)
		#layout.addWidget(self.view)

		palette = self.view.palette()
		palette.setBrush(QPalette.Base, Qt.transparent)
		self.view.page().setPalette(palette)
		self.view.setAttribute(Qt.WA_OpaquePaintEvent, False)
		
		self.plugin_name=""
		self.html= "<html><h1 style='background:white;test-align:center;'>Plugin hasn't been loaded</h1></html>"
		self.view.setHtml(self.html)
		self.view.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		self.view.connect(self.view, SIGNAL("linkClicked(const QUrl&)"), self.link_clicked)
		self.view.page().mainFrame().javaScriptWindowObjectCleared.connect(self.populateJavaScriptWindowObject)		
		self.view.move(0,54)
		self.view.resize(self.s_width/3-int(Config.get()["size"])-21, self.s_height-64)
		self.view.show()
		#self.view.hide()
		self.move(0,0)
		self.resize(self.s_width/3-int(Config.get()["size"])-21, self.s_height)
	def setHtml(self,v):
		self.html=v
		self.view.load(QUrl(self.html))
		self.update()
		QApplication.processEvents()
	def paintEvent(self, event):
		QWidget.paintEvent(self, event)
		p = QPainter(self)
		p.fillRect(event.rect(), Qt.transparent)
		p.setPen(Qt.NoPen)
		p.end()
	@pyqtSlot()
	def submitForm(self):
		home=os.path.expanduser("~")
		plugin_name=self.html.replace(home,"").replace(".duck-plugins","").replace(".tmp.html","").replace("/","")	
		elements=[]
		for e in self.view.page().mainFrame().findAllElements("*"):
			el={}
			el["type"] = str(e.localName())
			if e.hasAttribute("id"):
				el["id"]=str(e.attribute("id"))
			if e.hasAttribute("name"):
				el["name"]=str(e.attribute("name"))
			val= e.evaluateJavaScript('this.value').toPyObject()
			if val!=None:
				el["value"]=val
			elements.append(el)
		pl=getCurrentPluginModule(plugin_name)
		try:
			pl.onFormSubmit(elements)
		except:
			print("[Duck Launcher] No 'onFormSubmit()' method present in the plugin.")
	@pyqtSlot(str,str)
	def sendData(self, thing, value):
		print "data : " , thing, value
		home=os.path.expanduser("~")
		plugin_name=self.html.replace(home,"").replace(".duck-plugins","").replace(".tmp.html","").replace("/","")	
		pl=getCurrentPluginModule(plugin_name)
		try:
			pl.onDataSent(thing, value)
		except:
			print("[Duck Launcher] No 'onDataSent()' method present in the plugin.")
	def populateJavaScriptWindowObject(self):
		self.view.page().mainFrame().addToJavaScriptWindowObject('Duck', self)
	def link_clicked(self, url):
		str_url=str(url.toString())
		if "%TERMINAL%" in str_url:
			command=str_url.split("%TERMINAL%")
			command = [a for a in command if "file://" not in a]
			command= command[0].split(" ")
			command=[a for a in command if a ]
			t=LaunchCommand(parent=self,call=command)
			t.start()
		else:
			webbrowser.open(str(url.toString()))

class DBusWidget(dbus.service.Object):
	def __init__(self,parent, name, session):
		# export this object to dbus
		self.parent=parent
		dbus.service.Object.__init__(self, name, session)
	@dbus.service.method("org.duck.LauncherWebView", in_signature='', out_signature='')
	def setHtml(self,v):
		self.parent.setHtml(str(v))
		self.parent.show()
	@dbus.service.method("org.duck.LauncherWebView", in_signature='', out_signature='')
	def setPluginName(self,v):
		self.parent.plugin_name=str(v)
		self.parent.update()
	@dbus.service.method("org.duck.LauncherWebView", in_signature='', out_signature='')
	def closeWindow(self):
		self.parent.hide()
if __name__=="__main__":
	print "LAUNCHING PLUGIN"
	app = QApplication(sys.argv)
	w = Container()
	w.setHtml(sys.argv[1])
	w.show()
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	session_bus = dbus.SessionBus(private=True)
	name = dbus.service.BusName("org.duck.LauncherWebView", session_bus)
	widget = DBusWidget(w,session_bus, '/DBusWidget')
	sys.exit(app.exec_())
