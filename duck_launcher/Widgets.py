from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
import os
import webbrowser
import notify2 
import subprocess
import Files
import Plugins
class Launch(QThread):
	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		self.app=""
		self.parent=parent
	def run(self):
		exec_list=self.app.split(" ")
		subprocess.call(exec_list)
		QApplication.processEvents()

class installPlugin(QThread):
	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		self.plugin=""
		self.parent=parent
	def run(self):
		rep=Plugins.Repo()
		rep.installPlugin(str(self.plugin))
		QApplication.processEvents()
class removePlugin(QThread):
	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		self.plugin=""
		self.parent=parent
	def run(self):
		rep=Plugins.Repo()
		rep.removePlugin(str(self.plugin))
		QApplication.processEvents()
class imgWidget(QWidget):
	def __init__(self,parent=None,img=None):
		QWidget.__init__(self,parent)
		self.img=img
		self.ico=QtGui.QIcon(self.img)
		self.setUpdatesEnabled(True)
		self.pixmap_opacity=0.0
	def showEvent(self,e):
		self.timeline =QTimeLine()
		self.timeline.valueChanged.connect(self.animate)
		self.timeline.finished.connect(self.animateFinished)
		self.timeline.setDuration(200)
		self.timeline.start()
	def hideEvent(self,e):
		self.pixmap_opacity=0
	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setClipRegion(event.region())
		qp.setOpacity(self.pixmap_opacity)
		qp.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		qp.fillRect(event.rect(), QtCore.Qt.transparent)
		if self.ico!=None:
			self.ico.paint(qp,event.rect())
		else:
			pass
		qp.end()

	def sizeHint(self):
		return QtCore.QSize(100, 100)
	def moveEvent(self,e):
		pass
	def animate(self,val):
		self.pixmap_opacity +=0.3
		if self.pixmap_opacity>1:
			self.pixmap_opacity=1
		self.repaint()
		QtGui.qApp.processEvents()
	def animateFinished(self):
		self.pixmap_opacity=1
		self.repaint()
		QtGui.qApp.processEvents()
class WebPluginFactory(QWebPluginFactory):

    def __init__(self, parent = None):
        QWebPluginFactory.__init__(self, parent)
    def create(self, mimeType, url, names, values):
        if mimeType == "duck/image":
        	src=url
        	
        	return imgWidget(img=src)
    
    def plugins(self):
        plugin = QWebPluginFactory.Plugin()
        plugin.name = "Duck image"
        plugin.description = "Lets all the svg files to be rendered"
        mimeType = QWebPluginFactory.MimeType()
        mimeType.name = "duck/image"
        mimeType.description = "PyQt widget"
        mimeType.fileExtensions = ["JPG"]
        plugin.mimeTypes = [mimeType]
        return [plugin]

class pluginView(QWebView):
	def __init__(self, parent = None):
		QWebView.__init__(self, parent)
		self.parent=parent
		self.thePage = self.page()
		self.theFrame=self.thePage.mainFrame()
		#Transparency
		palette = self.palette()
		palette.setBrush(QPalette.Base, Qt.transparent)
		self.thePage.setPalette(palette)
		#
		self.thePage.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		self.theFrame.javaScriptWindowObjectCleared.connect(self._populateJavaScriptWindowObject)
		self.setAttribute(Qt.WA_OpaquePaintEvent, False)
		self.setContextMenuPolicy(Qt.NoContextMenu)
		self.connect(self, SIGNAL("linkClicked(const QUrl&)"), self._linkClicked)
		self.setHtml("<body style='background:rgb(230,100,80);'><input type='text' placehodler='aaa'></input></body>")
		self.hide()	

		#self.factory=WebPluginFactory()
		#self.thePage.setPluginFactory(self.factory)
	def showEvent(self,e):
		palette = self.palette()
		palette.setBrush(QPalette.Base, Qt.transparent)
		self.thePage.setPalette(palette)
		self.parent.setAttribute(Qt.WA_X11NetWmWindowTypeDock,False)
		self.setAttribute(Qt.WA_X11NetWmWindowTypeDock,False)
		self.parent.update()
		self.update()
	def _linkClicked(self, url):
		str_url=str(url.toString())
		print str_url
		webbrowser.open(str(url.toString()))
		self.parent.close_it()
	def _populateJavaScriptWindowObject(self):
		self.theFrame.addToJavaScriptWindowObject('Duck', self)
	@pyqtSlot()
	def submitForm(self):
		elements=[]
		for e in self.theFrame.findAllElements("*"):
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


		if "#" in self.parent.current_text.split(" ")[0]:
			plugins_list=[]						
			for p in Plugins.get_plugin_names():
				if str(self.parent.current_text.split(" ")[0]).lower().replace("#","") in p:
					plugins_list.append(p)
			if plugins_list:
				plugin_name=plugins_list[0]
				pl=Plugins.getCurrentPluginModule(plugin_name)
				try:
					pl.onFormSubmit(elements)
				except:
					print("[Duck Launcher] No 'onFormSubmit()' method present in the plugin.")
	@pyqtSlot(str,str)
	def sendData(self, thing, value):
		print "data : " , thing, value
		if "#" in self.parent.current_text.split(" ")[0]:
			plugins_list=[]						
			for p in Plugins.get_plugin_names():
				if str(self.parent.current_text.split(" ")[0]).lower().replace("#","") in p:
					plugins_list.append(p)
			if plugins_list:
				plugin_name=plugins_list[0]	
				pl=Plugins.getCurrentPluginModule(plugin_name)
				try:
					pl.onDataSent(thing, value)
				except:
					print("[Duck Launcher] No 'onDataSent()' method present in the plugin.")
	@pyqtSlot(str)
	def _filesGetFromPath(self,path):
		if str(self.parent.current_text).lower().startswith("#files"):
			if os.path.isdir(path):
				stuff = Files.getFilesFromPath(path)
			elif path=="HOME":
				home=os.path.expanduser("~")
				stuff= Files.getFilesFromPath(home)
			else:
				stuff=[]
			self.theFrame.evaluateJavaScript("setNewFiles({})".format(stuff))
	@pyqtSlot(str)
	def _pluginInstallPlugin(self,plugin):
		notify2.init("duck-launcher")
		n=notify2.Notification("The plugin '{}' is installing".format(plugin),
			"",
			"dialog-information")
		n.show()
		self.parent.close_it()
		t = installPlugin(parent=self.parent)
		t.plugin=plugin
		t.start()
		self.parent.close_it()
	@pyqtSlot(str)
	def _pluginRemovePlugin(self,plugin):
		notify2.init("duck-launcher")
		n=notify2.Notification("The plugin '{}' is uninstalling".format(plugin),
			"",
			"dialog-information")
		n.show()
		self.parent.close_it()
		t = removePlugin(parent=self.parent)
		t.plugin=plugin
		t.start()