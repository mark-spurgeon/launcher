import os
import sys
sys.dont_write_bytecode=True
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import webbrowser
import subprocess

import dbus
import dbus.service
import dbus.mainloop.glib

from jinja2 import Template
import math
sys.path.append(os.path.abspath("/usr/lib/duck_launcher"))
import Apps
from Plugins import Repo

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
		self.setWindowTitle("Duck Launcher Settings")
		self.setWindowIcon(QIcon().fromTheme("duck-settings"))
		self.setWindowFlags(Qt.FramelessWindowHint)#Qt.FramelessWindowHint|Qt.X11BypassWindowManagerHint)
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
		self.moving=False
		self.resizing=False
		self.closed_pressed=False

		palette = self.view.palette()
		palette.setBrush(QPalette.Base, Qt.transparent)
		self.view.page().setPalette(palette)
		self.view.setAttribute(Qt.WA_OpaquePaintEvent, False)
		self.view.setContextMenuPolicy(Qt.NoContextMenu)

		self.plugin_name=""
		self.html= "<html><h1 style='background:white;test-align:center;'>Plugin hasn't been loaded</h1></html>"
		self.view.setHtml(self.html)
		self.view.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		self.view.connect(self.view, SIGNAL("linkClicked(const QUrl&)"), self.link_clicked)
		self.view.page().mainFrame().javaScriptWindowObjectCleared.connect(self.populateJavaScriptWindowObject)		

		self.move(300,200)
		self.resize(700,550)
		self.view.move(1,41)
		self.view.resize(self.width()-2,self.height()-60)
		self.view.show()
		#self.view.hide()
	def setHtml(self,v):
		self.html=v
		self.view.setHtml(self.html)
		#self.view.load(QUrl(self.html))
		self.update()
		QApplication.processEvents()
	def paintEvent(self, event):
		QWidget.paintEvent(self, event)
		qp = QPainter(self)
		qp.fillRect(event.rect(), Qt.transparent)
		qp.setRenderHints(QPainter.Antialiasing |QPainter.SmoothPixmapTransform)
		#Window base
		qp.setBrush(QColor(60,60,62))
		qp.setPen(QPen(QColor(90,90,90),2))
		qp.drawRoundedRect(QRect(0,0,self.width(),self.height()), 6,6)
		#title
		qp.setPen(QPen(QColor(250,250,250),2))
		qp.setFont(QFont("Droid Sans",10))
		t_rect=QRect(5,0,160,35)
		qp.drawText(t_rect, Qt.AlignCenter, "Duck Launcher Settings")
		#
		if self.closed_pressed==True:
		
			i = QIcon("/usr/share/duck-launcher/default-theme/settings-save-pressed.svg")
			i.paint(qp, self.width()-90,0,80,40)
		else:
			i = QIcon("/usr/share/duck-launcher/default-theme/settings-save.svg")
			i.paint(qp, self.width()-90,0,80,40)			
		#

		h = QIcon("/usr/share/duck-launcher/default-theme/settings-handle.svg")
		h.paint(qp, self.width()-15,self.height()-15,12,12)
		qp.end()

	def mousePressEvent(self, e):
		self.offset =e.pos()
		if e.x()>self.width()-80 and e.y()<40:
			self.closed_pressed=True
		else:
			self.closed_pressed=False
		self.update()
		QApplication.processEvents()
	def mouseMoveEvent(self, e):
		if e.y()<30 and self.resizing==False and self.closed_pressed==False:
			self.moving=True
		elif e.x()>self.width()-85 and e.y()>self.height()-20:
			self.resizing=True
		if self.width()<200:
			self.resize(202,self.height())
			self.resizing=False
		if self.height()<200:
			self.resize(self.width(),202)
			self.resizing=False


		if self.moving==True:
			self.move(e.globalX()-self.offset.x(),e.globalY()-self.offset.y())
		if self.resizing==True:
			self.resize(e.x()+7,e.y()+5)
			self.view.resize(self.width()-2,self.height()-60)
			self.update()
		self.update()
		QApplication.processEvents()
	def mouseReleaseEvent(self,e):
		self.moving=False
		self.resizing=False
		self.closed_pressed=False
		if e.x()>self.width()-80 and e.y()<40:
			self.close()
			qApp.quit()
		self.update()
		QApplication.processEvents()
	def populateJavaScriptWindowObject(self):
		self.view.page().mainFrame().addToJavaScriptWindowObject('duck', self)
	def link_clicked(self, url):
		str_url=str(url.toString())
		if "%TERMINAL%" in str_url:
			command=str_url.split("%TERMINAL%")
			command = [a for a in command if "file://" not in a]
			command= command[0].split(" ")
			command=[a for a in command if a ]
			t=LaunchCommand(parent=self,call=command)
			t.start()
		elif "NONE" in str_url:
			pass
		else:
			webbrowser.open(str(url.toString()))

	#THESE ARE PYTHON FUNCTIONS CALLED BY JAVASCRIPT
	@pyqtSlot(str)
	def printText(self,msg):
		print("text:",str(msg))
	@pyqtSlot(str,str)
	def change(self,thing, value):
		print "Changing: ", thing, value
		iface=None
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		# Get the session bus
		bus = dbus.SessionBus()
		
		try:
			# Get the remote object
			remote_object = bus.get_object("org.duck.Launcher","/DBusWidget")		
			# Get the remote interface for the remote object
			iface = dbus.Interface(remote_object, "org.duck.Launcher")
			if thing=="red1":
				iface.setR1(int(value))
			if thing=="green1":
				iface.setG1(int(value))
			if thing=="blue1":
				iface.setB1(int(value))
			if thing=="red2":
				iface.setR2(int(value))
			if thing=="green2":
				iface.setG2(int(value))
			if thing=="blue2":
				iface.setB2(int(value))
			if thing=="alpha":
				iface.setAlpha(int(value))
			if thing=="font":
				iface.setFont(str(value))
			if thing=="size":
				iface.setLauncherWidth(int(value))
			if thing=="icon-size":
				iface.setIconSize(int(value))
			if thing=="speed":
				iface.setAnimationSpeed(float(value))
			if thing=="dock-add-app":
				dApps=[str(a) for a in iface.getDockApps()]
				dApps.append(str(value))
				iface.setDockApps(dbus.Array(dApps))
			if thing=="dock-remove-app":
				dApps=[str(a) for a in iface.getDockApps() if a!=str(value)]
				iface.setDockApps(dbus.Array(dApps))
			if thing=="dock-move-up":
				dApps=[str(a) for a in iface.getDockApps()]
				l = moveUpList(str(value), dApps)
				iface.setDockApps(dbus.Array(l))
			if thing=="dock-move-down":
				dApps=[str(a) for a in iface.getDockApps()]
				l = moveDownList(str(value), dApps)
				iface.setDockApps(dbus.Array(l))
		except:
			pass
	@pyqtSlot()
	def getPlugins(self):
		return Repo().getFirst50()

def getConfig():
	config={}
	iface=None
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	# Get the session bus
	bus = dbus.SessionBus()
	 
	try:
		# Get the remote object
		remote_object = bus.get_object("org.duck.Launcher","/DBusWidget")		
		# Get the remote interface for the remote object
		iface = dbus.Interface(remote_object, "org.duck.Launcher")
		config["r1"]=int(iface.getR1())
		config["g1"]=int(iface.getG1())
		config["b1"]=int(iface.getB1())
		config["r2"]=int(iface.getR2())
		config["g2"]=int(iface.getG2())
		config["b2"]=int(iface.getB2())
		config["alpha"]=int(iface.getAlpha())
		config["font"]=str(iface.getFont())
		config["size"]=int(iface.getLauncherWidth())
		config["icon-size"]=int(iface.getIconSize())
		config["speed"]=int(iface.getAnimationSpeed())
		config["dock-apps"]=[str(d) for d in iface.getDockApps()]
	except:
		pass
	return config
def moveUpList(app_name, dock_apps):
	new_l=None
	dock_apps=[str(a) for a in dock_apps]
	if dock_apps.index(app_name) >0 and app_name in dock_apps:
		index=None
		for i, d in enumerate(dock_apps):
			if str(d)==str(app_name):
				index=i
				break
		if index!=None:
			new_l=dock_apps
			new_l.pop(index)
			new_l.insert(index-1,app_name)
	return new_l
def moveDownList(app_name, dock_apps):
	new_l=None
	dock_apps=[str(a) for a in dock_apps]
	if dock_apps.index(app_name) < len(dock_apps) and app_name in dock_apps:

		index=None
		for i, d in enumerate(dock_apps):
			if str(d)==str(app_name):
				index=i
				break
		if index!=None:
			new_l=dock_apps
			new_l.pop(index)
			new_l.insert(index+1,app_name)
	return new_l
if __name__=="__main__":
	app = QApplication(sys.argv)
	w = Container()
	cfg = getConfig()
	apps = Apps.info('')
	fonts= [ str(a) for a in QFontDatabase().families()]
	f=open("/usr/lib/duck_settings/template.html","r")
	t=Template(f.read())
	f.close()
	w.setHtml(t.render(cfg=cfg,fonts=fonts,apps=apps,static_url="file:///usr/share/duck-launcher/default-theme/"))
	w.show()
	sys.exit(app.exec_())
