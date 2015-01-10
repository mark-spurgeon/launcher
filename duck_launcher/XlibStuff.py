# -*- coding: utf-8 -*-
#########
#Copyright (C) 2014  Mark Spurgeon <theduck.dev@gmail.com>
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
import Xlib
from Xlib import display as D
import sys
from PyQt4 import QtGui, QtCore
import Config
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
