
import sys
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
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
			conf["dock-apps"]=str(arg["dock-apps"])
		elif arg.has_key("blocks"):
			conf["blocks"]=str(arg["blocks"])
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
class DockAppWidget(BoxLayout):
	def __init__(self, *args, **kwargs):
		super(DockAppWidget, self).__init__(*args, **kwargs)
		self.text=""
		l = Label(text=self.text, color=[.2,.2,.2,1],background_color=[.3,.3,.3,1],size_hint_y=None, height=20)
		btns =BoxLayout()
		b_left=Button(size_hint_y=None, height=50,background_normal="left.png")
		b_right=Button(size_hint_y=None, height=50,background_normal="right.png")
		b_remove=Button(size_hint_y=None, height=50,background_normal="remove.png")
		btns.add_widget(b_left)
		btns.add_widget(b_right)
		btns.add_widget(b_remove)
		
		self.add_widget(l)
		self.add_widget(btns)
class DockAppsLayout(RelativeLayout):
	def __init__(self, *args, **kwargs):
		super(DockAppsLayout, self).__init__(*args, **kwargs)	
		for a in d_cfg.get()["dock-apps"]:
			d =DockAppWidget(size_hint=(None,None),width=150,height=200)
			d.text=a
			self.add_widget(d)
class TreeViewButton(Button, TreeViewNode):
	pass	
class BlocksTree(TreeView):
	def __init__(self, *args, **kwargs):
		super(BlocksTree, self).__init__(*args, **kwargs)
		self.hide_root=True
		for b in d_cfg.get()["blocks"]:
			n = self.add_node(TreeViewLabel(text=b["name"], color=[.2,0.2,0.2,1],color_selected=[.95,.45,.25,.8],is_open=True))
			for a in b["apps"]:
				self.add_node(TreeViewLabel(text=a, color=[0.2,0.2,0.2,1],color_selected=[.9,.5,.3,.5] ) ,n)
			for a in b["directories"]:
				self.add_node(TreeViewLabel(text="a", color=[0.2,0.2,0.2,1],color_selected=[.9,.5,.3,.5] ) ,n)
			for a in b["files"]:
				self.add_node(TreeViewLabel(text="a", color=[0.2,0.2,0.2,1],color_selected=[.9,.5,.3,.5] ) ,n)
	def on_node_expand(self,node):
		print node.text
	def on_node_touchdown(self,touch):
		print touch
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
		screen = ScreenManager()
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
	#Config.set('graphics','resizable','0')
	Config.set('kivy','exit_on_escape','0')
	Config.set('kivy', 'window_icon', '/usr/share/duck-launcher/icons/duck-settings.png')
	#Config.set('kivy', 'log_level', 'critical')
	win = Window()
	win.title='Duck Launcher Settings'
	win.run()
