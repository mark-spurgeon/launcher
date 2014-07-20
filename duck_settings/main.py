
import sys
import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView, ListItemButton, ListItemLabel
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.models import SelectableDataItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.treeview import TreeView,TreeViewLabel,TreeViewNode
from kivy.uix.colorpicker import ColorPicker
from kivy.properties import (NumericProperty, BoundedNumericProperty,
                             ListProperty, ObjectProperty,
                             ReferenceListProperty, StringProperty,
                             AliasProperty)
from kivy.clock import Clock
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
except ImportError:
	print("[Duck Settings Error/Bug]: Module 'duck_launcher' is not present, this module should be installed.")
	sys.exit()
##############
# Update Config
##############
def updateConfig(*args):
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
		new_list=[]
		for b in d_cfg.get()['blocks']:
			if  b["name"] == self.text:
				b["name"]=args[0].text
				self.text=args[0].text
			new_list.append(b)
		
		updateConfig({'blocks':new_list})
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
			new_blocks=[]
			for b in d_cfg.get()["blocks"]:	
				if b["name"]==self.text:
					b["apps"].append(s)
				new_blocks.append(b)
			updateConfig({"blocks" : new_blocks})
			#Update
			node= self.parentTree.selected_node
			new=TreeViewButton(text=s)
			new.parentTree=self.parentTree
			self.parentTree.add_node(new,node)
			self.appsPopup.dismiss()
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
			#Update
			node= self.parentTree.selected_node
			new=TreeViewButton(text=p)
			new.parentTree=self.parentTree
			self.parentTree.add_node(new,node)
			self.foldersPopup.dismiss()
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
		#Update Blocks
		new_blocks=d_cfg.get()["blocks"]
		new_blocks.append({'name':self.Input.text, "apps":[],"directories":[],"files":[]})
		updateConfig({"blocks":new_blocks})
		self.addPopup.dismiss()
class BlocksTree(TreeView):
	def __init__(self, *args, **kwargs):
		super(BlocksTree, self).__init__(*args, **kwargs)
		self.hide_root=True	
		self.indent_level=100
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

	#TODO : font, dock-apps, blocks


if __name__=="__main__":
	Config.set('graphics','width','750')
	Config.set('graphics','height','600')
	Config.set('graphics','resizable','0')
	Config.set('kivy','exit_on_escape','0')
	Config.set('kivy', 'window_icon', '/usr/share/duck-launcher/icons/duck-settings.png')
	Config.set('kivy', 'log_level', 'critical')
	Config.set("input", "mouse", "mouse,disable_multitouch")
	win = Window()
	win.title='Duck Launcher Settings'
	win.run()
