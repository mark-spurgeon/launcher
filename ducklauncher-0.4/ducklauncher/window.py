from PySide import QtCore,QtGui
import gtk
import wnck
import sys
import time
import Apps
def close_window(title):
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	for w in win:
		if title in w.get_name():
			w.close(int(time.time()))
	
########
def change_window_state(window_info):
	screen = wnck.screen_get_default()
	screen.force_update()
	win = screen.get_windows()
	for w in win:
		if window_info['title']  in w.get_name():
			if w.is_minimized()==False:
				w.minimize()
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
					window={}
					window['title'] =w.get_name()
					window['app']=w.get_application().get_name()
					windows.append(window)
						
	return windows
	
class open_windows(QtGui.QMainWindow):
	def __init__(self, size, height,r,g,b):
		QtGui.QMainWindow.__init__(self, None,QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint|QtCore.Qt.X11BypassWindowManagerHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.size=size
		self.height=height
		self.r=r
		self.g=g
		self.b=b
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.ico_size=self.size*1.3
		self.setGeometry(self.size+10,self.height-self.ico_size*2-10,self.ico_size*self.win_len*1.3+20,self.ico_size*1.8)
	def paintEvent(self,e):
		qp=	QtGui.QPainter()
		qp.begin(self)
		qp.setBrush(QtGui.QColor(self.r,self.g,self.b))
		qp.drawRect(10,0,self.ico_size*self.win_len*1.3+10,self.ico_size*1.8)
		half_height=self.ico_size*0.9
		qp.setPen(QtGui.QPen(QtGui.QColor(self.r,self.g,self.b), 7, QtCore.Qt.SolidLine))
		qp.drawLine(10,half_height-5,3,half_height)
		qp.drawLine(10,half_height+5,3,half_height)
		qp.setPen(QtGui.QPen(QtGui.QColor(240,240,240), 2, QtCore.Qt.SolidLine))
		qp.setFont(QtGui.QFont('Hermeneus One',8))
		for i,w in enumerate(self.windows):
			ico = Apps.ico_from_app(w['app'])
			if ico!=None:
				ico.paint(qp,20+self.ico_size*i*1.3, self.ico_size*0.5, self.ico_size-2, self.ico_size-2)
			else:
				ico2 = Apps.ico_from_app(w['title'])
				if ico2!=None:
					ico2.paint(qp,20+self.ico_size*i*1.3, self.ico_size*0.5, self.ico_size-2, self.ico_size-2)
				else:
					ico2=QtGui.QIcon("/usr/share/duck-launcher/icons/apps.svg")
					ico2.paint(qp,20+self.ico_size*i*1.3, self.ico_size*0.5, self.ico_size-2, self.ico_size-2)
			
			close_icon=QtGui.QIcon('/usr/share/duck-launcher/icons/close.svg')
			close_icon.paint(qp,self.ico_size*(i+1)*1.3-20,self.ico_size*1.4,16,16)
		
		##close
		close_icon=QtGui.QIcon('/usr/share/duck-launcher/icons/close.svg')
		close_icon.paint(qp,self.ico_size*self.win_len*1.3+2,2,16,16)
	def mousePressEvent(self,e):
		x_m,y_m=e.x(),e.y()
		for i,w in enumerate(self.windows):
			if 20+self.ico_size*i*1.3<x_m<20+self.ico_size*(i+1)*1.3 and self.ico_size*0.5<y_m<self.ico_size*1.5-2:
				change_window_state(w)
			if self.ico_size*(i+1)*1.3-20<x_m<self.ico_size*(i+1)*1.3-4 and self.ico_size*1.5-2<y_m:
				print "closing ",w['title'] 
				close_window(w['title'])
				self.update_apps()
		if self.ico_size*self.win_len*1.3+2<x_m<self.ico_size*self.win_len*1.33+16 and 0<y_m<16:
			self.close()
		
		self.update_apps()
	def update_apps(self):
		self.windows = get_open_windows()
		self.win_len=len(self.windows)
		self.setGeometry(self.size+10,self.height-self.ico_size*2-10,self.ico_size*self.win_len*1.3+20,self.ico_size*1.8)
		self.update()
		QtGui.QApplication.processEvents()

if __name__=='__main__':
	print get_open_windows()
