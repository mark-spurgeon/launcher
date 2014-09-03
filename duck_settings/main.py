<<<<<<< HEAD
#! /usr/bin/python
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
=======

>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
import sys
import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
<<<<<<< HEAD
from kivy.uix.filechooser import  FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView, ListItemButton
=======
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView, ListItemButton, ListItemLabel
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.models import SelectableDataItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
<<<<<<< HEAD
#from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.treeview import TreeView,TreeViewNode
#from kivy.uix.colorpicker import ColorPicker
=======
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.treeview import TreeView,TreeViewLabel,TreeViewNode
from kivy.uix.colorpicker import ColorPicker
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
from kivy.properties import (NumericProperty, BoundedNumericProperty,
                             ListProperty, ObjectProperty,
                             ReferenceListProperty, StringProperty,
                             AliasProperty)
from kivy.clock import Clock
<<<<<<< HEAD
#from kivy.graphics import Mesh, InstructionGroup, Color
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.logger import Logger
#from math import cos, sin, pi, sqrt, atan
from colorsys import rgb_to_hsv, hsv_to_rgb
from kivy.config import Config

from traceback import print_exc
import dbus
import dbus.mainloop.glib
try: 
	import cPickle as pickle
except:
	import pickle

try:
	sys.path.append(os.path.abspath("/usr/lib/duck_launcher"))
	import Config as d_cfg
	import Apps as APPS
=======
from kivy.graphics import Mesh, InstructionGroup, Color
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.logger import Logger
from math import cos, sin, pi, sqrt, atan
from colorsys import rgb_to_hsv, hsv_to_rgb
from kivy.config import Config
#########
# Duck Launcher Modules
#########
try:
	from duck_launcher import Config as d_cfg
	from duck_launcher import Apps as APPS
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
except ImportError:
	print("[Duck Settings Error/Bug]: Module 'duck_launcher' is not present, this module should be installed.")
	sys.exit()
##############
# Update Config
##############
def updateConfig(*args):
<<<<<<< HEAD
	# Enable glib main loop support
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	# Get the session bus
	bus = dbus.SessionBus()
	try:
		# Get the remote object
		remote_object = bus.get_object("org.duck.Launcher","/DBusWidget")
		# Get the remote interface for the remote object
		iface = dbus.Interface(remote_object, "org.duck.Launcher")
	except dbus.DBusException:
		print_exc()
    		sys.exit(1)
						
	for arg in args:
		if arg.has_key('r'):
			iface.setR1(arg["r"])
		elif arg.has_key('g'):
			iface.setG1(arg["g"])
		elif arg.has_key('b'):
			iface.setB1(arg["b"])
		elif arg.has_key('r2'):
			iface.setR2(arg["r2"])
		elif arg.has_key('b2'):
			iface.setB2(arg["b2"])
		elif arg.has_key('g2'):
			iface.setG2(arg["g2"])
		elif arg.has_key('alpha'):
			iface.setAlpha(arg["alpha"])
		elif arg.has_key("size"):
			iface.setLauncherWidth(arg["size"])
		elif arg.has_key("icon-size"):
			iface.setIconSize(arg["icon-size"])
		elif arg.has_key("font"):
			iface.setFont(arg["font"])
		elif arg.has_key("animation-speed"):
			iface.setAnimationSpeed(arg["animation-speed"])
		elif arg.has_key("dock-apps"):
			if arg["dock-apps"]==[]:
				arg["dock-apps"]=None
			iface.setDockApps(arg["dock-apps"])
		elif arg.has_key("blocks"):
			new_blocks=[]
			for b in arg["blocks"]:
				if not b["apps"] or b.has_key("apps")==False:
					b["apps"]=[]
				if not b["files"] or b.has_key("files")==False:
					b["files"]=[]
				if not b["directories"] or b.has_key("directories")==False:
					b["directories"]=[]
				new_blocks.append(b)
			new_blocks_pickle = pickle.dumps(new_blocks)
			iface.setBlocks(new_blocks_pickle)
			Dict={
				"r":iface.getR1(),
				"g":iface.getG1(),
				"b":iface.getB1(),
				"r2":iface.getR2(),
				"g2":iface.getG2(),
				"b2":iface.getB2(),
				"alpha":iface.getAlpha(),
				"font":iface.getFont(),
				"animation-speed":iface.getAnimationSpeed(),
				"size":iface.getLauncherWidth(),
				"dock-apps":iface.getDockApps(),
				"icon-size":iface.getIconSize(),
				"blocks":iface.getBlocks(),
				"init-manager":iface.getInit()
				}
			d_cfg.check_dict(Dict)
def createBlockDicts(tl):
	#print [a for a in tl]
	list_=list(tl)
	indices=[]
	for i, t in enumerate(list_):
		if "TreeViewBlock" in str(t):
			indices.append(i)
	all_blocks=[]
	for i,n in enumerate(indices):
		try:
			end=indices[i+1]
			all_blocks.append(list_[n:end])
		except:
			all_blocks.append(list_[n:])
	the_blocks_list=[]
	for b in all_blocks:
		block={}
		block["apps"]=[]
		block["files"]=[]
		block["directories"]=[]
		for i,bb in enumerate(b):
			if i==0:
				block["name"]=bb.text
			else:
				t= bb.text
				if "/" not in t:
					block["apps"].append(t)
				elif os.path.isfile(t):
					block["files"].append(t)
				elif os.path.isdir(t):
					block["directories"].append(t)
		the_blocks_list.append(block)
	return the_blocks_list
		#print(b[0].text)
=======
	conf=d_cfg.get()
	for arg in args:
		if arg.has_key('r'):
			conf["r"]=str(arg["r"])
		elif arg.has_key('g'):
			conf["g"]=str(arg["g"])
		elif arg.has_key('b'):
			conf["b"]=str(arg["b"])
		elif arg.has_key('r2'):
			conf["r2"]=str(arg["r2"])
		elif arg.has_key('b2'):
			conf["b2"]=str(arg["b2"])
		elif arg.has_key('g2'):
			conf["g2"]=str(arg["g2"])
		elif arg.has_key('alpha'):
			conf["alpha"]=str(arg["alpha"])
		elif arg.has_key("size"):
			conf["size"]=str(arg["size"])
		elif arg.has_key("icon-size"):
			conf["icon-size"]=str(arg["icon-size"])
		elif arg.has_key("font"):
			conf["font"]=str(arg["font"])
		elif arg.has_key("dock-apps"):
			conf["dock-apps"]=arg["dock-apps"]
		elif arg.has_key("blocks"):
			conf["blocks"]=arg["blocks"]
	d_cfg.check_dict(conf) # Checks and creates a new configuration file
	#duck_client.update()
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
##############
# Kivy Widgets
#############
class ColorPickerCustom(RelativeLayout):
    font_name = StringProperty('data/fonts/DroidSansMono.ttf')
    color = ListProperty((1, 1, 1, 1))
    hsv = ListProperty((1, 1, 1))
    def _get_hex(self):
        return get_hex_from_color(self.color)

    def _set_hex(self, value):
        self.color = get_color_from_hex(value)[:4]

    hex_color = AliasProperty(_get_hex, _set_hex, bind=('color', ))
    wheel = ObjectProperty(None)
    # now used only internally.
    foreground_color = ListProperty((1, 1, 1, 1))

    def on_color(self, instance, value):
        if not self._updating_clr:
            self._updating_clr = True
            self.hsv = rgb_to_hsv(*value[:3])
            self._updating_clr = False

    def on_hsv(self, instance, value):
        if not self._updating_clr:
            self._updating_clr = True
            self.color[:3] = hsv_to_rgb(*value)
            self._updating_clr = False

    def _trigger_update_clr(self, mode, clr_idx, text):
        self._upd_clr_list = mode, clr_idx, text
        Clock.unschedule(self._update_clr)
        Clock.schedule_once(self._update_clr)

    def _update_clr(self, dt):
        mode, clr_idx, text = self._upd_clr_list
        try:
            text = max(0, min(254, float(text)))
            if mode == 'rgb':
                self.color[clr_idx] = float(text) / 255.
            else:
                self.hsv[clr_idx] = float(text) / 255.
        except ValueError:
            Logger.warning('ColorPicker: invalid value : {}'.format(text))

    def _update_hex(self, dt):
        if len(self._upd_hex_list) != 9:
            return
        self.hex_color = self._upd_hex_list

    def _trigger_update_hex(self, text):
        self._upd_hex_list = text
        Clock.unschedule(self._update_hex)
        Clock.schedule_once(self._update_hex)

    def __init__(self, **kwargs):
        self._updating_clr = False
        super(ColorPickerCustom, self).__init__(**kwargs)

#
class DataItem(SelectableDataItem):
    def __init__(self, text='', is_selected=False):
        self.text =str(text)
	if self.text in d_cfg.get()["dock-apps"]:
        	self.is_selected = True
	else:
		self.is_selected=False
class DockAppsList(ListView):
	def __init__(self, *args, **kwargs):
		super(DockAppsList, self).__init__(*args, **kwargs)	
		the_apps = [DataItem(text=a["name"]) for a in APPS.info('')]
		args_converter = lambda row_index, obj: {'text': obj.text,
							'is_selected':obj.is_selected,
							'size_hint_y': None,
							'height': 20,
							'font_size':14,
							'deselected_color':[0,0,0,0],
							'selected_color':[.96,.56,.36,1],
							'background_normal':"images/button.png",
							'background_down':"images/buton.png",
							'color':[.2,.2,.2,1]}
		self.adapter=ListAdapter(data = the_apps, 
					selection_mode = 'multiple',
					args_converter=args_converter,
					allow_empty_selection = True,
					propagate_selection_to_data=True,
					cls = ListItemButton,
					sorted_keys=[])
		#self.adapter.select_list(self.adapter.data,extend=False)
		self.adapter.bind(on_selection_change=self.on_select)
	def on_select(self, *args, **kwargs):
		l = [a.text for a in args[0].selection]
		cached= [ args[0].get_view(a).text  for a in args[0].cached_views]
		new_list=[]
		#for not deleting/deleting already added apps
		for a in d_cfg.get()["dock-apps"]:
			if a in l:
				new_list.append(a)
			elif a not in l:
				#Either removed or not cached
				if a in cached:
					pass#don't add it
				elif a not in cached:
					new_list.append(a)
		#for new apps		
		for a in l:
			if a in new_list:
				pass
			else:
				new_list.append(a)
		#Update
		updateConfig({'dock-apps':new_list})
<<<<<<< HEAD
	
=======
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
class TreeViewButton(Button, TreeViewNode):
	def __init__(self, *args, **kwargs):
		super(TreeViewButton, self).__init__(*args, **kwargs)
		self.background_normal="images/button.png"
		self.background_down="images/button.png"
		self.background_color=[0,0,0,0]
		self.color=[.2,0.2,0.2,1]
		self.color_selected=[.9,.5,.3,.8]
		self.size_hint_y=None
		self.height=30
		self.bind(on_release=self.click)
		b = BoxLayout(orientation="vertical")
		l=Label(text="Keep or remove this item from the block.")
		b1=BoxLayout(padding=10)
		btn1=Button(text="Keep it",background_normal="images/button.png",background_color=[.3,.7,.3,1])
		btn1.bind(on_release=self.closePopup)
		btn2=Button(text="Remove it",background_normal="images/button.png",background_color=[.8,.2,.2,1])
		btn2.bind(on_release=self.removeItem)
		b1.add_widget(btn1)
		b1.add_widget(btn2)
		b.add_widget(l)
		b.add_widget(b1)
		self.popupWindow = Popup(title="Item: '{}'".format(self.text),
					size_hint=(None,None),
					size=(400,200),
					separator_color=[.9,.4,.2,1],
					background_color=[0,0,0,.6],
					content=b
					)
	def click(self, arg):		
		self.popupWindow.open()
	def closePopup(self, arg):
		self.popupWindow.dismiss()
	def removeItem(self, arg):	
<<<<<<< HEAD
		node = self.parentTree.selected_node
		self.parentTree.remove_node(node)
		self.popupWindow.dismiss()
		b = createBlockDicts(self.parentTree.iterate_all_nodes())
		updateConfig({"blocks":b})
=======
		new_blocks=[]
		for b in d_cfg.get()["blocks"]:
			block={}
			block["name"]=b["name"]
			block["apps"]=[]
			block["files"]=[]
			block["directories"]=[]
			if self.text in b["apps"]:
				block["apps"]=b["apps"].remove(self.text)
			if self.text in b["files"]:
				block["files"]=b["files"].remove(self.text)
			if self.text in b["directories"]:
				block["directories"]=b["directories"].remove(self.text)
			new_blocks.append(b)
		updateConfig({"blocks":new_blocks})
		node = self.parentTree.selected_node
		self.parentTree.remove_node(node)
		self.popupWindow.dismiss()
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
class AddAppList(ListView):
	def __init__(self, *args, **kwargs):
		super(AddAppList, self).__init__(*args, **kwargs)
		the_apps = [a["name"] for a in APPS.info('')]	
		args_converter = lambda row_index, obj: {'text': obj,
							'size_hint_y': None,
							'height': 20,
							'font_size':14,
							'deselected_color':[0,0,0,0],
							'selected_color':[.86,.46,.26,1],
							'background_normal':"images/button.png",
							'background_down':"images/buton.png",
							'color':[.8,.8,.8,1]}
		self.adapter=ListAdapter(data = the_apps, 
					selection_mode = 'single',
					args_converter=args_converter,
					allow_empty_selection = True,
					cls = ListItemButton,
					sorted_keys=[])
class TreeViewBlock(Button, TreeViewNode):
	def __init__(self, *args, **kwargs):
		super(TreeViewBlock, self).__init__(*args, **kwargs)
		print args
		self.background_normal="images/button.png"
		self.background_down="images/button.png"
		self.background_color=[0,0,0,0]
		self.color=[.2,0.2,0.2,1]
		self.size_hint_y=None
		self.height=30
		self.bind(on_release=self.click)
		self.color_selected=[.9,.5,.3,1]
		the_layout=BoxLayout(orientation="vertical")
		b1 = BoxLayout(size_hint_y=None, height=45, padding=5)
		l= Label(text="Title : ",font_size=16)
		t = TextInput(text=self.text, multiline=False, font_size=18)
		t.bind(on_text_validate=self.onTextChange)
		b1.add_widget(l)
		b1.add_widget(t)
		b2=BoxLayout(padding=8)
		l1=Label(text="Add ")
		b3=BoxLayout(orientation="vertical")
		btn1=Button(text="Application",font_size=14)
		btn1.bind(on_release=self.appsPopupOpen)
		btn2=Button(text="File",font_size=14)
		btn2.bind(on_release=self.filesPopupOpen)
		btn3=Button(text="Folder",font_size=14)	
		btn3.bind(on_release=self.foldersPopupOpen)
		b3.add_widget(btn1)
		b3.add_widget(btn2)
		b3.add_widget(btn3)
		l2=Label(text="To Block.")	
		b2.add_widget(l1)
		b2.add_widget(b3)	
		b2.add_widget(l2)
		rem = Button(text="Remove this block",
				size_hint_y=None,
				height=30,
				background_normal="images/button.png",
				background_color=[.8,.2,.2,1])
		rem.bind(on_release=self.removeBlock)
		the_layout.add_widget(b1)
		the_layout.add_widget(Label(text="----",size_hint_y=None,height=20))
		the_layout.add_widget(b2)
		the_layout.add_widget(rem)
		self.popupWindow = Popup(title="Block: '{}'".format(self.text),
					size_hint=(None,None),
					size=(400,230),
					separator_color=[.9,.4,.2,1],
					background_color=[0,0,0,.6],
					content=the_layout
					)
		###Apps	
		b = BoxLayout(orientation="vertical")
		self.app_list =AddAppList()
		a_btn=Button(text="Add This Application", size_hint_y=None, height=40)
		a_btn.bind(on_release=self.addApp)
		b.add_widget(self.app_list)
		b.add_widget(a_btn)
		self.appsPopup = Popup(title="Add Application to '{}'".format(self.text),
					size_hint=(None,None),
					size=(400,400),
					separator_color=[.9,.4,.2,1],
					background_color=[0,0,0,.6],
					content=b
					)
		##Files
		box = BoxLayout(orientation="vertical")
		self.f=FileChooserIconView(multiselect=False, path= os.path.expanduser("~"))
		self.f.bind(on_submit=self.addFile)
		l=Label(text="Double click on a file to add it.",size_hint_y=None,height=40)
		box.add_widget(self.f)
		box.add_widget(l)
		self.filesPopup = Popup(title="Add File to '{}'".format(self.text),
					size_hint=(None,None),
					size=(500,500),
					separator_color=[.9,.4,.2,1],
					background_color=[0,0,0,.6],
					content=box
					)
		##Folders	
		box1=BoxLayout(orientation="vertical")
		self.f2=FileChooserIconView(multiselect=False, path= os.path.expanduser("~"))
		self.f2.bind(on_entry_added=self.updateFolders)
		b=BoxLayout(size_hint_y=None, height=50, padding=5)
		self.folder_label = Label(text=self.f2.path,id="FileLabel")
		btn=Button(text="Add Folder", size_hint_x=None,width=150)
		btn.bind(on_release=self.addFolder)
		b.add_widget(self.folder_label)
		b.add_widget(btn)
		box1.add_widget(self.f2)
		box1.add_widget(b)
		self.foldersPopup = Popup(title="Add Folder to '{}'".format(self.text),
					size_hint=(None,None),
					size=(500,500),
					separator_color=[.9,.4,.2,1],
					background_color=[0,0,0,.6],
					content=box1
					)
	def onTextChange(self, *args):
<<<<<<< HEAD
		for b in pickle.loads(d_cfg.get()['blocks']):
			if  b["name"] == self.text:
				b["name"]=args[0].text
				self.text=args[0].text
				blocks=createBlockDicts(self.parentTree.iterate_all_nodes())
				updateConfig({'blocks':blocks})
=======
		new_list=[]
		for b in d_cfg.get()['blocks']:
			if  b["name"] == self.text:
				b["name"]=args[0].text
				self.text=args[0].text
			new_list.append(b)
		
		updateConfig({'blocks':new_list})
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
	def appsPopupOpen(self,*args):
		self.popupWindow.dismiss()
		self.appsPopup.open()
	def filesPopupOpen(self,*args):
		self.popupWindow.dismiss()
		self.filesPopup.open()
	def foldersPopupOpen(self,*args):
		self.popupWindow.dismiss()
		self.foldersPopup.open()
	def addApp(self, *args):
		s =   self.app_list.adapter.selection[0].text
		if s!=None:
<<<<<<< HEAD
=======
			new_blocks=[]
			for b in d_cfg.get()["blocks"]:	
				if b["name"]==self.text:
					b["apps"].append(s)
				new_blocks.append(b)
			updateConfig({"blocks" : new_blocks})
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
			#Update
			node= self.parentTree.selected_node
			new=TreeViewButton(text=s)
			new.parentTree=self.parentTree
			self.parentTree.add_node(new,node)
			self.appsPopup.dismiss()
<<<<<<< HEAD
			blocks= createBlockDicts(self.parentTree.iterate_all_nodes())
			updateConfig({"blocks":blocks})
	def addFile(self,*args):
		for b in pickle.loads(d_cfg.get()["blocks"]):
			if b["name"]==self.text:
				#Update Tree
				node= self.parentTree.selected_node
				new=TreeViewButton(text=str(args[1][0]))
				new.parentTree=self.parentTree
				self.parentTree.add_node(new,node)
				self.filesPopup.dismiss()
				blocks= createBlockDicts(self.parentTree.iterate_all_nodes())
				updateConfig({"blocks":blocks})
	def addFolder(self,*args):
		p = self.f2.path
		if os.path.exists(p):
=======
	def addFile(self,*args):
		new_blocks=[]
		for b in d_cfg.get()["blocks"]:	
			if b["name"]==self.text:
				if str(args[1][0]) not in b["files"]:
					b["files"].append(str(args[1][0]))
					#Update Tree
					node= self.parentTree.selected_node
					new=TreeViewButton(text=str(args[1][0]))
					new.parentTree=self.parentTree
					self.parentTree.add_node(new,node)
					self.filesPopup.dismiss()
			new_blocks.append(b)
		updateConfig({"blocks":new_blocks})
	def addFolder(self,*args):
		p = self.f2.path
		if os.path.exists(p):
			new_blocks=[]
			for b in d_cfg.get()["blocks"]:
				if b["name"]==self.text:
					b["directories"].append(p)
				new_blocks.append(b)
			updateConfig({'blocks':new_blocks})
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
			#Update
			node= self.parentTree.selected_node
			new=TreeViewButton(text=p)
			new.parentTree=self.parentTree
			self.parentTree.add_node(new,node)
			self.foldersPopup.dismiss()
<<<<<<< HEAD
			blocks= createBlockDicts(self.parentTree.iterate_all_nodes())
			print blocks
			updateConfig({"blocks":blocks})
	def updateFolders(self,*args):
		self.folder_label.text = self.f2.path
	def removeBlock(self,*args):
		try:
			self.parentTree.remove_node(self)
			blocks= createBlockDicts(self.parentTree.iterate_all_nodes())
			updateConfig({"blocks":blocks})
=======
	def updateFolders(self,*args):
		self.folder_label.text = self.f2.path
	def removeBlock(self,*args):
		new_blocks=[]
		for b in d_cfg.get()["blocks"]:
			if b["name"]!=self.text:
				new_blocks.append(b)
		updateConfig({"blocks":new_blocks})
		try:
			self.parentTree.remove_node(self)
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
		except:pass
		self.popupWindow.dismiss()
	def click(self,*args):		
		self.popupWindow.open()
class AddBlockButton(Button):
	def __init__(self, *args, **kwargs):
		super(AddBlockButton, self).__init__(*args, **kwargs)
		self.bind(on_release=self.openPopup)
		box=BoxLayout(padding=10)
		self.Input=TextInput(text="New Block", multiline=False, font_size=18)
		self.Input.bind(on_text_validate=self.addBlock)
		b=Button(text="Add it")
		b.bind(on_release=self.addBlock)	
		box.add_widget(self.Input)
		box.add_widget(b)
		self.addPopup = Popup(title="Add A New Block",
					size_hint=(None,None),
					size=(400,115),
					separator_color=[.9,.4,.2,1],
					background_color=[0,0,0,.6],
					content=box
					)
	def openPopup(self,*args):
		self.addPopup.open()
	def addBlock(self,*args):
		tree = self.parentLayout.ids["blockstree"]
		b=TreeViewBlock(text=self.Input.text,is_open=True)
		b.parentTree=tree
		tree.add_node(b)
<<<<<<< HEAD
		blocks= createBlockDicts(tree.iterate_all_nodes())
		#Update Blocks
		updateConfig({"blocks":blocks})
=======
		#Update Blocks
		new_blocks=d_cfg.get()["blocks"]
		new_blocks.append({'name':self.Input.text, "apps":[],"directories":[],"files":[]})
		updateConfig({"blocks":new_blocks})
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
		self.addPopup.dismiss()
class BlocksTree(TreeView):
	def __init__(self, *args, **kwargs):
		super(BlocksTree, self).__init__(*args, **kwargs)
		self.hide_root=True	
		self.indent_level=100
<<<<<<< HEAD
		for b in pickle.loads(d_cfg.get()["blocks"]):
			if isinstance(b["name"],list):
				name=''
				for b in b["name"]:
					name.join(str(b))
			else:
				name=b["name"]
			t = TreeViewBlock(text=name,is_open=True, parent_node="Root")
			t.parentTree=self
			self.add_node(t)
			#tv.add_node(t)
			if b.has_key("apps"):
				for a in b["apps"]:
					s = TreeViewButton(text=a,parent_node=name)
					s.parentTree=self
					self.add_node(s,t)
			if b.has_key("directories"):
				for a in b["directories"]:
					r = TreeViewButton(text=a, parent_node=name)
					r.parentTree=self
					self.add_node(r,t)
			if b.has_key("files"):
				for a in b["files"]:
					u  = TreeViewButton(text=a,parent_node=name)
					u.parentTree=self
					self.add_node(u,t)
	def callback(self,*args):
		pass
=======
		for b in d_cfg.get()["blocks"]:
			t = TreeViewBlock(text=b["name"],is_open=True, parent_node="Root")
			t.parentTree=self
			self.add_node(t)
			#tv.add_node(t)
			for a in b["apps"]:
				s = TreeViewButton(text=a,parent_node=b["name"])
				s.parentTree=self
				self.add_node(s,t)
			for a in b["directories"]:
				r = TreeViewButton(text=a, parent_node=b["name"])
				r.parentTree=self
				self.add_node(r,t)
				
			for a in b["files"]:
				u  = TreeViewButton(text=a,parent_node=b["name"])
				u.parentTree=self
				self.add_node(u,t)
	def callback(self,*args):
		print "WELL"
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
class ThirdScreen(Screen):
	pass
class SecondScreen(Screen):
	pass
class FirstScreen(Screen):
	pass
class MainWidget(ScreenManager):
	def __init__(self):
		super(MainWidget,self).__init__()
class Window(App):
	# Config Values
	cfg= d_cfg.get()
	red=float(cfg["r"])/255
	green=float(cfg["g"])/255
	blue=float(cfg["b"])/255

	red2=float(cfg["r2"])/255
	green2=float(cfg["g2"])/255
	blue2=float(cfg["b2"])/255
	alpha=float(cfg["alpha"])/255
	launcher_size=int(cfg["size"])
	icon_size=int(cfg["icon-size"])
<<<<<<< HEAD
	font=cfg["font"]
	animation_speed=float(cfg["animation-speed"])
=======
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
		
	####
	def build(self):
		screen = ScreenManager(transition=SwapTransition())
		screen.add_widget(FirstScreen())
		screen.add_widget(SecondScreen())
		screen.add_widget(ThirdScreen())
		return screen
	def changeForegroundColor(self,color):
		r=int(255*color[0])
		g=int(255*color[1])	
		b=int(255*color[2])
		updateConfig({"r":r},{"g":g},{"b":b})
	def changeBackgroundColor(self,color):
		r2=int(255*color[0])
		g2=int(255*color[1])	
		b2=int(255*color[2])
		updateConfig({"r2":r2},{"g2":g2},{"b2":b2})
	def changeBackgroundAlpha(self,value):
		a=int(255*value)
		updateConfig({"alpha":a})
	def changeLauncherWidth(self,value):
		size=int(value)
		updateConfig({"size":size})
	def changeIconSize(self,value):
		icon_size=int(value)
		updateConfig({"icon-size":icon_size})
<<<<<<< HEAD
	def changeAnimationSpeed(self,value):
		animation_speed=float(value)
		updateConfig({"animation-speed":animation_speed})
	def changeFont(self,value):
		font=str(value)
		updateConfig({"font":font})
	def on_stop(self):
		print "[Duck Settings] Quiting and saving configuration"
		#update config file
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		# Get the session bus
		bus = dbus.SessionBus()
		# Get the remote object
		remote_object = bus.get_object("org.duck.Launcher","/DBusWidget")
		# Get the remote interface for the remote object
		iface = dbus.Interface(remote_object, "org.duck.Launcher")
		Dict={
			"r":iface.getR1(),
			"g":iface.getG1(),
			"b":iface.getB1(),
			"r2":iface.getR2(),
			"g2":iface.getG2(),
			"b2":iface.getB2(),
			"alpha":iface.getAlpha(),
			"font":iface.getFont(),
			"animation-speed":iface.getAnimationSpeed(),
			"size":iface.getLauncherWidth(),
			"dock-apps":iface.getDockApps(),
			"icon-size":iface.getIconSize(),
			"blocks":iface.getBlocks(),
			"init-manager":iface.getInit()
			}
		d_cfg.check_dict(Dict)
if __name__=="__main__":
	Config.set('graphics','width','725')
=======

	#TODO : font, dock-apps, blocks


if __name__=="__main__":
	Config.set('graphics','width','750')
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
	Config.set('graphics','height','600')
	Config.set('graphics','resizable','0')
	Config.set('kivy','exit_on_escape','0')
	Config.set('kivy', 'window_icon', '/usr/share/duck-launcher/icons/duck-settings.png')
<<<<<<< HEAD
	Config.set('kivy', 'log_level', 'error')
=======
	Config.set('kivy', 'log_level', 'critical')
>>>>>>> 86af556d16439afcb5d5a16d03cf98ebf6a5d387
	Config.set("input", "mouse", "mouse,disable_multitouch")
	win = Window()
	win.title='Duck Launcher Settings'
	win.run()
