from PySide import QtCore,QtGui
import gtk
import wnck
import sys
import time
import Apps
import Config
def close_window(title):
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	for w in win:
		if title in w.get_name():
			pass#w.close(int(time.time()))
	
########
def change_window_state(window_info):
	screen = wnck.screen_get_default()
	a_win=screen.get_windows_stacked()
	screen.force_update()
	win = screen.get_windows()
	for w in win:
		if window_info['title']  in w.get_name():
			if w.is_minimized()==False:
				w.minimize()
				#w.activate(int(time.time()))
			else:
				w.activate(int(time.time()))
	
########
def get_open_windows():
	while gtk.events_pending():
		gtk.main_iteration()
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	windows=[]
	for w in win:
			if  'NORMAL' in str(w.get_window_type()):
				if not 'Conky' in w.get_name():
					if w.get_name()=="ducklauncher":
						w.pin()
					else:
						window={}
						window['title'] =w.get_name()
						window['app']=w.get_application().get_name()
						windows.append(window)
						
	return windows
	
class open_windows(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint|QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.size=int(Config.get()['size'])
		d = QtGui.QDesktopWidget()
		self.height =d.availableGeometry().height()
		self.r=int(Config.get()["r"])
		self.g=int(Config.get()["g"])
		self.b=int(Config.get()["b"])
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.ico_size=self.size
		self.setGeometry(self.size+10,self.height-self.size*2+40,self.size*self.win_len*1.3+20,self.size*2.4)
	def paintEvent(self,e):
		qp=	QtGui.QPainter()
		qp.begin(self)
		qp.setPen(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.setBrush(QtGui.QColor(int(self.r),int(self.g),int(self.b)))
		qp.drawRect(10,0,self.size*self.win_len*1.3+10,self.size*1.8)
		qp.setPen(QtGui.QColor(250,250,250))
		qp.setBrush(QtGui.QColor(250,250,250))
		qp.drawRect(9,0,5,self.size*1.8)
		half_height=self.size*0.9
		half_height=self.size*0.9
		icon=QtGui.QIcon("/usr/share/duck-launcher/icons/win.svg")
		icon.paint(qp, -10,half_height-10, 20,20)
		for i,w in enumerate(self.windows):
			ico = Apps.ico_from_app(w['app'])
			if ico==None:
				ico = Apps.ico_from_app(w['title'])
				if ico==None:
					ico=QtGui.QIcon("/usr/share/duck-launcher/icons/apps.svg")
					
			ico.paint(qp,20+self.size*i*1.3, 10, self.size*1.1, self.size*1.1)
			
			close_icon=QtGui.QIcon('/usr/share/duck-launcher/icons/close.svg')
			close_icon.paint(qp,self.size*(i+1)*1.3,self.size*1.4,13,13)
		
	def mousePressEvent(self,e):
		x_m,y_m=e.x(),e.y()
		for i,w in enumerate(self.windows):
			if 20+self.size*i*1.3<x_m<20+self.size*(i+1)*1.1 and 10<y_m<10+self.size*1.1:
				change_window_state(w)
			if self.ico_size*(i+1)*1.3<x_m<self.ico_size*(i+1)*1.3+13 and self.ico_size*1.5-2<y_m:
				print "closing ",w['title'] 
				close_window(w['title'])
				self.update_apps()
		
		self.update_apps()
	def update_apps(self):
		self.icon_size=Config.get()['size']
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.setGeometry(self.size+10,self.height-self.size*2,self.size*self.win_len*1.3+20,self.size*2.4)
		self.update()
		QtGui.QApplication.processEvents()
	def update_all(self):
		self.r=Config.get()['r']
		self.g=Config.get()['g']
		self.b=Config.get()['b']

if __name__=='__main__':
	print get_open_windows()
