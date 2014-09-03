# -*- coding: utf-8 -*-
#########
#Copyright (C) 2014  Mark Spurgeon <markspurgeon96@hotmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########
from PySide import QtCore,QtGui
import sys
import Config
import Apps
class AddApp(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self, None)
		self.parent=None
		vbox=QtGui.QVBoxLayout()
		self.list=QtGui.QListView()
		self.model = QtGui.QStandardItemModel()
		for app in Apps.info(''):
			a = QtGui.QStandardItem(app["name"])
			a.setAccessibleText(app["name"])
			self.model.appendRow(a)
		self.model.itemChanged.connect(self.change_app)
		self.list.setModel(self.model)
		vbox.addWidget(self.list)
		self.list.clicked.connect(self.change_app)
		self.setLayout(vbox)
		self.setGeometry(300, 300, 600, 300)
		self.setWindowTitle('Choose your application')
	def change_app(self, index):
		self.parent.App = self.model.item(index.row()).accessibleText()
		self.close()
class AddToBlock(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self, None)
		self.parent=None
		self.block=''
		self.File=''
		self.Folder=''
		self.App=''
		self.choice='app'
		self.app_win=AddApp()
		self.app_win.parent=self
		self.initUI()
		self.conf=Config.get()
	def initUI(self):
		vbox=QtGui.QVBoxLayout()
		#Options
		radio_btn = QtGui.QRadioButton('App',self)
		radio_btn.setChecked(True)
		radio_btn.toggled.connect(self.setToApp)
		vbox.addWidget(radio_btn)
		radio_btn2 = QtGui.QRadioButton('File',self)
		radio_btn2.toggled.connect(self.setToFile)
		vbox.addWidget(radio_btn2)
		radio_btn3 = QtGui.QRadioButton('Folder',self)
		radio_btn3.toggled.connect(self.setToFolder)
		vbox.addWidget(radio_btn3)
		#
		btn = QtGui.QPushButton('Choose', self)
		vbox.addWidget(btn)
		btn.clicked.connect(self.changeValue)
		
		btn = QtGui.QPushButton('Add', self)
		vbox.addWidget(btn)
		btn.clicked.connect(self.add)
		self.setLayout(vbox)
		self.setGeometry(300, 300, 300, 150)
		self.setWindowTitle('Add Stuff to block')
	def changeValue(self):
		if self.choice=='file':
			file = QtGui.QFileDialog()
			file.move(20, 20)
			fname, _ = file.getOpenFileName(self, 'Open file','/home')
			self.File=fname
		elif self.choice=='folder':
			folder = QtGui.QFileDialog()
			folder.setFileMode(QtGui.QFileDialog.Directory)
			folder.setOption(QtGui.QFileDialog.ShowDirsOnly)
			folder.move(20, 20)
			fname = folder.getExistingDirectory(self, 'Open folder','/home')
			self.Folder=fname
		elif self.choice=='app':
			self.app_win.show()
	def setToFolder(self, item):
		if item:
			self.choice='folder'
			self.update()
	def setToFile(self,item):
		if item:
			self.choice='file'
			self.update()
	def setToApp(self, item):
		if item:
			self.choice='app'
			self.update()
	
	def add(self):
		for block in self.parent.conf['blocks']:
			if self.block==block['name']:
				if self.choice=='app' and self.App!='':
					print('Adding:{0} to {1}'.format(self.App, block['name']))
					block['apps'].append(str(self.App))
				if self.choice=='file' and self.File!='':
					print('Adding:{0} to {1}'.format(self.File, block['name']))
					block['files'].append(str(self.File))
				if self.choice=='folder' and self.Folder!='':
					print('Adding:{0} to {1}'.format(self.Folder, block['name']))
					block['directories'].append(str(self.Folder))
		self.parent.updateBlocks()
		self.parent.update_settings()
		self.update()
		self.close()
class AddBlock(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self, None)
		self.parent=None
		self.initUI()
		self.conf=Config.get()
	def initUI(self):
		self.btn = QtGui.QPushButton('Add', self)
		self.btn.move(20, 50)
		self.btn.clicked.connect(self.add)
		self.le = QtGui.QLineEdit(self)
		self.le.move(20, 20)
		self.setGeometry(300, 300, 290, 150)
		self.setWindowTitle('Input dialog')
	def add(self):
		block= self.le.text()
		dict={'name':str(block),'apps':[],'files':[], 'directories':[]}
		self.conf['blocks'].append(dict)
		self.parent.conf=self.conf
		Config.create_from_info(self.conf)
		self.parent.updateBlocks()
		self.parent.update_settings()
		self.update()
		self.close()
class Window(QtGui.QDialog):
	def __init__(self, parent):
		QtGui.QDialog.__init__(self, None)
		#
		self.parent=parent
		self.conf=Config.get()
		self.current_selection=""
		self.current_block = ""
		self.current_item=""
		self.block_win=AddBlock()
		self.block_win.parent=self
		self.add_block_win=AddToBlock()
		self.add_block_win.parent=self
		#
		self.setWindowTitle('Duck Launcher Settings')
		self.resize(650,500)
		vbox=QtGui.QVBoxLayout()
		tabs = QtGui.QTabWidget()
		#####################
		tab1 = QtGui.QWidget()
		hbox=QtGui.QVBoxLayout(tab1)
		l1 = QtGui.QLabel('Color:')
		l1.move(10,10)
		hbox.addWidget(l1)	
		#Red
		l_R = QtGui.QLabel('  red: ')
		hbox.addWidget(l_R)
		value = int(self.conf['r'])
		percent = value*100/255
		slider1=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider1.setValue(percent)
		slider1.valueChanged[int].connect(self.change_red)
		hbox.addWidget(slider1)
		#Green
		l_G = QtGui.QLabel('  green: ')
		hbox.addWidget(l_G)
		value = int(self.conf['g'])
		percent = value*100/255
		slider2=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider2.setValue(percent)
		slider2.valueChanged[int].connect(self.change_green)
		hbox.addWidget(slider2)
		#Blue
		l_B = QtGui.QLabel('  blue: ')
		hbox.addWidget(l_B)
		value = int(self.conf['b'])
		percent = value*100/255
		slider3=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider3.setValue(percent)
		slider3.valueChanged[int].connect(self.change_blue)
		hbox.addWidget(slider3)
		#Color2
		l2 = QtGui.QLabel('Second Color:')

		hbox.addWidget(l2)	
		#Red2
		l_R = QtGui.QLabel('  red: ')
		hbox.addWidget(l_R)
		value = int(self.conf['r2'])
		percent = value*100/255
		slider1=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider1.setValue(percent)
		slider1.valueChanged[int].connect(self.change_red2)
		hbox.addWidget(slider1)
		#Green2
		l_G = QtGui.QLabel('  green: ')
		hbox.addWidget(l_G)
		value = int(self.conf['g2'])
		percent = value*100/255
		slider2=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider2.setValue(percent)
		slider2.valueChanged[int].connect(self.change_green2)
		hbox.addWidget(slider2)
		#Blue2
		l_B = QtGui.QLabel('  blue: ')
		hbox.addWidget(l_B)
		value = int(self.conf['b2'])
		percent = value*100/255
		slider3=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider3.setValue(percent)
		slider3.valueChanged[int].connect(self.change_blue2)
		hbox.addWidget(slider3)
		#Alpha
		l_B = QtGui.QLabel('Transparency: ')
		hbox.addWidget(l_B)
		value = int(self.conf['alpha'])
		percent = value*100/255
		slider3=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider3.setValue(percent)
		slider3.valueChanged[int].connect(self.change_alpha)
		hbox.addWidget(slider3)
		#Canvas
		sep = QtGui.QLabel('__________________________')
		hbox.addWidget(sep)
		l_s = QtGui.QLabel('Canvas Width:')
		hbox.addWidget(l_s)
		value = int(self.conf['size'])
		slider4=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider4.setValue(value)
		slider4.valueChanged[int].connect(self.change_size)
		hbox.addWidget(slider4)
		tabs.addTab(tab1,"Basic")
		#Tab 2
		####################
		tab2 = QtGui.QWidget()
		hbox=QtGui.QVBoxLayout(tab2)
		ico_label=QtGui.QLabel('Icon size: ')
		hbox.addWidget(ico_label)
		slider=QtGui.QSlider(QtCore.Qt.Horizontal)
		slider.setValue(int(self.conf["icon-size"])-50)
		slider.valueChanged[int].connect(self.change_icon_size)
		hbox.addWidget(slider)
		sep = QtGui.QLabel('__________________________')
		hbox.addWidget(sep)
		dock_label=QtGui.QLabel('Dock apps: ')
		hbox.addWidget(dock_label)
		list=QtGui.QListView()
		model = QtGui.QStandardItemModel(list)
		for app in Apps.info(''):
			a = QtGui.QStandardItem(app["name"])
			a.setAccessibleText(app["name"])
			a.setCheckable(True)
			if app['name'] in self.conf['dock-apps']:
				a.setCheckState(QtCore.Qt.Checked)
			model.appendRow(a)
		model.itemChanged.connect(self.change_dock_apps)
		list.setModel(model)
		hbox.addWidget(list)
		tabs.addTab(tab2,"Apps")
		#TAB 3
		######################
		tab3 = QtGui.QWidget()
		hbox=QtGui.QVBoxLayout(tab3)

		self.tree=QtGui.QTreeView()
		self.model = QtGui.QStandardItemModel()
		self.updateBlocks()
		self.tree.clicked.connect(self.block_clicked)
		hbox.addWidget(self.tree)
		button_line = QtGui.QHBoxLayout()
		btn = QtGui.QPushButton("Add Block")
		btn.clicked.connect(self.addBlock)
		button_line.addWidget(btn)
		btn = QtGui.QPushButton("Delete block")
		btn.clicked.connect(self.deleteBlock)
		button_line.addWidget(btn)
		btn = QtGui.QPushButton("Add to block")
		btn.clicked.connect(self.addToBlock)
		button_line.addWidget(btn)
		btn = QtGui.QPushButton("Delete from block")
		btn.clicked.connect(self.removeFromBlock)
		button_line.addWidget(btn)
		hbox.addLayout(button_line)
		tabs.addTab(tab3,"Star")
		#
		tabs.show()
		vbox.addWidget(tabs)
		close = QtGui.QPushButton("Save settings and close")
		close.clicked.connect(self.close)
		vbox.addWidget(close)
		self.setLayout(vbox)
		
	def change_red(self,value):
		color  = value*255/100
		self.conf['r']=str(color)
		self.update_settings()
	def change_green(self,value):
		color  = value*255/100
		self.conf['g']=str(color)
		self.update_settings()
	def change_blue(self,value):
		color  = value*255/100
		self.conf['b']=str(color)
		self.update_settings()
	def change_red2(self,value):
		color  = value*255/100
		self.conf['r2']=str(color)
		self.update_settings()
	def change_green2(self,value):
		color  = value*255/100
		self.conf['g2']=str(color)
		self.update_settings()
	def change_blue2(self,value):
		color  = value*255/100
		self.conf['b2']=str(color)
		self.update_settings()
	def change_alpha(self,value):
		color  = value*255/100
		self.conf['alpha']=str(color)
		self.update_settings()
	def change_size(self, value):
		if value<10:
			value=10
		self.conf['size']=str(value)
		self.update_settings()
	def change_icon_size(self, value):
		self.conf["icon-size"]=str(value+50)
		self.update_settings()
	def change_dock_apps(self, item):
		if item.checkState():
			print("adding: {} to dock apps ".format(item.accessibleText()))
			self.conf["dock-apps"].append(str(item.accessibleText()))
			self.update_settings()
		else:
			print("removing: {} from dock apps ".format(item.accessibleText()))
			if item.accessibleText() in self.conf['dock-apps']:
				self.conf["dock-apps"].remove(str(item.accessibleText()))
				self.update_settings()
	def block_clicked(self, item):
		parent = item.parent().data()
		if parent==None:
			self.current_selection="block"
			self.current_block=item.data()
		else:
			self.current_block=parent
			self.current_selection="item"
			self.current_item=item.data()
		self.update_settings()
	def addBlock(self):
		self.block_win.show()
	def deleteBlock(self):
		if self.current_block !='' and self.current_selection=='block':
			print("Deleting {}".format(self.current_block))
			for b in self.conf['blocks']:
				if b['name']==self.current_block:
					self.conf['blocks'].remove(b)
					self.updateBlocks()
					self.update_settings()
	def addToBlock(self):
		self.add_block_win.block=self.current_block
		self.add_block_win.update()
		self.add_block_win.show()
	def removeFromBlock(self):
		if self.current_selection=='item' and self.current_item!= '':
			print('Removing: {0} from {1}'.format(self.current_item,self.current_block))
			for b in self.conf['blocks']:
				if self.current_item in b['apps']:
					b['apps'].remove(self.current_item)
				elif self.current_item in b['files']:
					b['files'].remove(self.current_item)
				elif self.current_item in b['directories']:
					b['directories'].remove(self.current_item)
			self.updateBlocks()
			self.update_settings()
	def updateBlocks(self):
		self.model = QtGui.QStandardItemModel()
		for block in self.conf['blocks']:
			parentItem = self.model.invisibleRootItem()
			b = QtGui.QStandardItem(block['name'])
			#b.setAccessibleText(block["name"])
			parentItem.appendRow(b)
			parentItem = b
			all = Config.get_from_block(block)
			for thing in all:
				t = QtGui.QStandardItem(thing['value'])
				#t.setAccessibleText(thing['value'])
				parentItem.appendRow(t)
		self.tree.setModel(self.model)
	def update_settings(self):
		#update current config
		Config.create_from_info(self.conf)
		QtGui.QApplication.processEvents()
		self.parent.update_all()
