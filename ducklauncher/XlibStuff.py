import Xlib
from Xlib import display as D
def fix_window(winId,left,right,top,bottom):
        set = False
        while set == False:
            try:
                window = reserveSpace(winId)
                if window != None:
                    window.now(left,right,top,bottom)
                    set = True
                else:
                    self.sleep(1)
            except:
                raise
class reserveSpace():
	def __init__(self, winId):
		self._display = D.Display()
		self._win = self._display.create_resource_object('window', winId)
	def now(self, left,right,top,bottom):
		self._win.change_property(self._display.intern_atom('_NET_WM_STRUT'), self._display.intern_atom('CARDINAL'),32, [left,right,top,bottom])
		self._display.sync()