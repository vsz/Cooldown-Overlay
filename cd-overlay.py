import win32api
import win32con
import win32gui
import win32ui
import time
import threading
from pyhooked import Hook, KeyboardEvent, MouseEvent
from enum import Enum


class ActionType(Enum):
	CONSUMABLE = 1
	ATKREGULAR = 2
	ATKSPECIAL = 3
	ATKRUNE = 4
	ATKCOOLDOWN = 5
	ATKEFFECT = 6
	HEALREGULAR = 7
	HEALRUNE = 8
	HEALCOOLDOWN = 9
	HEALEFFECT = 10
	SUPPORTREGULAR = 11
	SUPPORTRUNE = 12
	SUPPORTCOOLDOWN = 13
	SUPPORTEFFECT = 14
	CONJUREREGULAR = 15
	EQUIPMENT = 16
	
class CooldownGroup(Enum):
	OBJECT = 1
	ATTACK = 2
	HEAL = 3
	SUPPORT = 4
	SPECIAL = 5
	CONJURE = 6
	NONE = 7

class TrackedGroup:
	labelText = str()
	cooldownGroup = CooldownGroup
	time = 0.0
	actionList = []
	
	def __init__(self,lt,cg):
		self.labelText = lt
		self.cooldownGroup = cg

class TrackedAction:
	labelText = str()
	cooldownGroups = []
	actionType = ActionType
	keys = []
	time = 0.0 #can be cooldown or duration
	countdown = 0.0
	keyPress = False
	triggered = False
	running = False
	
	def __init__(self,lt,cg,at,keys,t,iv):
		self.labelText = lt
		self.actionType = at
		self.keys = keys
		self.time = t
		self.countdown = iv

	def pressKey(self):
		self.keyPress = True
		
		
	def track(self,Ts):
		if self.keyPress :
			self.running = True
			self.countdown = self.time
			self.keyPress = False
		
		if self.running : self.countdown = self.countdown - Ts
		
		# stops timer if it runs out
		if self.running and self.countdown < Ts :
			self.countdown = 0.0
			self.running = False
			
#groupList = []
#groupList.append(TrackedGroup('Attack',CooldownGroup.ATKSPELL))

actionList = []
actionList.append(TrackedAction('Potion',[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['1','Oem_5','Oem_1'],1.0,0.0))
actionList.append(TrackedAction('Attack',[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['Oem_5','Oem_6','Oem_1'],2.0,0.0))
actionList.append(TrackedAction('Healing',[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['2','3'],1.0,0.0))
actionList.append(TrackedAction('Support',[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['4','5'],2.0,0.0))
actionList.append(TrackedAction('Mana Shield',[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['4'],200.0,0.0))
actionList.append(TrackedAction('Haste',[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['5'],22.0,0.0))


def createWindow():
	#get instance handle
	hInstance = win32api.GetModuleHandle()

	# the class name
	className = 'Cooldown Overlay'

	# create and initialize window class
	wndClass				= win32gui.WNDCLASS()
	wndClass.style		  = win32con.CS_HREDRAW | win32con.CS_VREDRAW
	wndClass.lpfnWndProc	= wndProc
	wndClass.hInstance	  = hInstance
	wndClass.hIcon		  = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
	wndClass.hCursor		= win32gui.LoadCursor(None, win32con.IDC_ARROW)
	wndClass.hbrBackground  = win32gui.GetStockObject(win32con.WHITE_BRUSH)
	wndClass.lpszClassName  = className

	# register window class
	wndClassAtom = None
	try:
		wndClassAtom = win32gui.RegisterClass(wndClass)
	except Exception as e:
		print (e)
		raise e

	# http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
	# Consider using: WS_EX_COMPOSITED, WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, WS_EX_TOPMOST, WS_EX_TRANSPARENT
	# The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
	exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT

	# http://msdn.microsoft.com/en-us/library/windows/desktop/ms632600(v=vs.85).aspx
	# Consider using: WS_DISABLED, WS_POPUP, WS_VISIBLE
	style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

	hWindow = win32gui.CreateWindowEx(
		exStyle,
		wndClassAtom,				   #it seems message dispatching only works with the atom, not the class name
		None, #WindowName
		style,
		0, # x
		0, # y
		win32api.GetSystemMetrics(win32con.SM_CXSCREEN), # width
		win32api.GetSystemMetrics(win32con.SM_CYSCREEN), # height
		None, # hWndParent
		None, # hMenu
		hInstance,
		None # lpParam
	)

	# http://msdn.microsoft.com/en-us/library/windows/desktop/ms633540(v=vs.85).aspx
	win32gui.SetLayeredWindowAttributes(hWindow, 0x00ffffff, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)

	# http://msdn.microsoft.com/en-us/library/windows/desktop/dd145167(v=vs.85).aspx
	#win32gui.UpdateWindow(hWindow)

	# http://msdn.microsoft.com/en-us/library/windows/desktop/ms633545(v=vs.85).aspx
	win32gui.SetWindowPos(hWindow, win32con.HWND_TOPMOST, 0, 0, 0, 0,
		win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

	# http://msdn.microsoft.com/en-us/library/windows/desktop/ms633548(v=vs.85).aspx
	#win32gui.ShowWindow(hWindow, win32con.SW_SHOW)


	# Show & update the window
	# win32gui.ShowWindow(hWindow, win32con.SW_SHOWNORMAL)
	win32gui.UpdateWindow(hWindow)

	return hWindow


def createTextLabel(hdc, pos, color=0x008c8c8c,text=''):
	win32gui.SetTextColor(hdc, color)
	win32gui.DrawText(hdc,text,-1,pos,win32con.DT_LEFT | win32con.DT_VCENTER)


def createTimerLabel(hdc, pos, color=0x008c8c8c,initialValue=0.0):
	win32gui.SetTextColor(hdc, color)
	win32gui.DrawText(hdc,'{0:.1f}'.format(initialValue),-1,pos,win32con.DT_RIGHT | win32con.DT_VCENTER)


def wndProc(hWnd, message, wParam, lParam):

	if message == win32con.WM_PAINT:
		hdc, paintStruct = win32gui.BeginPaint(hWnd)

		# Font configuration
		dpiScale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
		fontSize = 10

		# http://msdn.microsoft.com/en-us/library/windows/desktop/dd145037(v=vs.85).aspx
		lf = win32gui.LOGFONT()
		lf.lfFaceName = "Tahoma"
		lf.lfHeight = int(round(dpiScale * fontSize))
		lf.lfWeight = 700 # bold
		lf.lfQuality = win32con.NONANTIALIASED_QUALITY # Use nonantialiased to remove the white edges around the text.

		hf = win32gui.CreateFontIndirect(lf)

		win32gui.SelectObject(hdc, hf)

		# Colors
		black = 0x00000000
		blue = 0x00ff0000
		red = 0x000000ff
		green = 0x0000ff00
		white = 0x00fefefe # ??
		pink = 0x00c800c8
		lblue = 0x00dcc800
		dgreen = 0x0041961e
		gray = 0x008c8c8c

		# Get relative dimensions
		rect = win32gui.GetClientRect(hWnd)
		w = rect[2]
		h = rect[3]

		pleft = int(0.752*w)
		ptop = int(0.1*h)
		pright = int(0.8165*w)
		pbottom = int(0.55*h)
		spc = int(0.015*h)
		
		for idx,action in enumerate(actionList):
			pos = (pleft,ptop+idx*spc,pright,pbottom)
			createTextLabel(hdc,pos,dgreen,action.labelText)
			createTimerLabel(hdc,pos,dgreen,action.countdown)

		win32gui.EndPaint(hWnd, paintStruct)
		return 0

	elif message == win32con.WM_DESTROY:
		print('Being destroyed')
		win32gui.PostQuitMessage(0)
		return 0

	else:
		return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

def trackActions(hWindow):
	global actionList
	
	# Window and Timer update period
	Ts = 0.05
	
	while(True) :
		win32gui.RedrawWindow(hWindow, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)
		for action in actionList :
			action.track(Ts)
		time.sleep(Ts)

def handle_events(args):
	global actionList
	
	if isinstance(args, KeyboardEvent):
		print(args.pressed_key)
		for action in actionList :
			#print(action.keys)
			if any(i in action.keys for i in args.pressed_key): action.pressKey()		

def keylogger(handler):
	hk = Hook()
	hk.handler = handler
	hk.hook()  # hook into the events, and listen to the presses


def main():
	# Create transparent window
	hWindow = createWindow()

	# Thread that detects keypresses
	tKeylogger = threading.Thread(target = keylogger, args=(handle_events,))
	tKeylogger.setDaemon(False)
	tKeylogger.start()

	# Thread that updates values on window
	tTimers = threading.Thread(target=trackActions, args=(hWindow,))
	tTimers.setDaemon(False)
	tTimers.start()

	# Dispatch messages
	win32gui.PumpMessages()


if __name__ == '__main__':
	main()
