import win32api
import win32con
import win32gui
import win32ui
import time
import threading
from pyhooked import Hook, KeyboardEvent, MouseEvent

## Define global variables
InitText = 'Starting Cooldown Overlay up.\nStay frosty.'

## Base Text
# Cooldown Groups
ItemText = 'Potion'
AttackSpellsText = 'Attack'
HealingSpellsText = 'Healing'
SupportSpellsText = 'Support'

# Spells duration
ManaShieldText = 'Mana Shield'
HasteText = 'Haste'

# Equipment duration
LifeRingText = 'Life Ring'

## Cooldown and base duration values
# Cooldown Groups
ItemCD = 1.0
AttackSpellsCD = 2.0
HealingSpellsCD = 1.0
SupportSpellsCD = 2.0

# Spells duration
ManaShieldDuration = 200.0
HasteDuration = 22.0

# Equipment duration
LifeRingDuration = 600.0

## Timer values
# Timer Groups
ItemTimer = 1.0
AttackSpellsTimer = 2.0
HealingSpellsTimer = 1.0
SupportSpellsTimer = 2.0

# Spells timer
ManaShieldTimer = 200.0
HasteTimer = 22.0

# Equipment timer
LifeRingTimer = 600.0

## Key Press
# Cooldown Groups
ItemKeyPressed = False
AttackSpellsKeyPressed = False
HealingSpellsKeyPressed = False
SupportSpellsKeyPressed = False

# Spells duration
ManaShieldKeyPressed = False
HasteKeyPressed = False

# Equipment duration
LifeRingKeyPressed = False

def createWindow():
	#get instance handle
	hInstance = win32api.GetModuleHandle()

    # the class name
	className = 'Cooldown Overlay'

    # create and initialize window class
	wndClass                = win32gui.WNDCLASS()
	wndClass.style          = win32con.CS_HREDRAW | win32con.CS_VREDRAW
	wndClass.lpfnWndProc    = wndProc
	wndClass.hInstance      = hInstance
	wndClass.hIcon          = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
	wndClass.hCursor        = win32gui.LoadCursor(None, win32con.IDC_ARROW)
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
		wndClassAtom,                   #it seems message dispatching only works with the atom, not the class name
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
		
		pos11 = (int(0.751*w),int(0.1*h),int(w),int(0.55*h))
		pos21 = (int(0.751*w),int(0.115*h),int(w),int(0.55*h))
		pos31 = (int(0.751*w),int(0.130*h),int(w),int(0.55*h))
		pos41 = (int(0.751*w),int(0.145*h),int(w),int(0.55*h))
		pos51 = (int(0.751*w),int(0.175*h),int(w),int(0.55*h))
		pos61 = (int(0.751*w),int(0.19*h),int(w),int(0.55*h))
		
		pos12 = (int(0.742*w),int(0.1*h),int(0.8165*w),int(0.55*h))
		pos22 = (int(0.742*w),int(0.115*h),int(0.8165*w),int(0.55*h))
		pos32 = (int(0.742*w),int(0.130*h),int(0.8165*w),int(0.55*h))
		pos42 = (int(0.742*w),int(0.145*h),int(0.8165*w),int(0.55*h))
		pos52 = (int(0.742*w),int(0.175*h),int(0.8165*w),int(0.55*h))
		pos62 = (int(0.742*w),int(0.19*h),int(0.8165*w),int(0.55*h))
		
		# # Base Text
		# Item Text
		win32gui.SetTextColor(hdc, pink)
		win32gui.DrawText(hdc,ItemText,-1,pos11,win32con.DT_LEFT | win32con.DT_VCENTER)

		# Attack Spell Text
		win32gui.SetTextColor(hdc, red)
		win32gui.DrawText(hdc,AttackSpellsText,-1,pos21,win32con.DT_LEFT | win32con.DT_VCENTER)

		# Healing Spell Text
		win32gui.SetTextColor(hdc, lblue)
		win32gui.DrawText(hdc,HealingSpellsText,-1,pos31,win32con.DT_LEFT | win32con.DT_VCENTER)
			
		# Support Spell Text
		win32gui.SetTextColor(hdc, dgreen)
		win32gui.DrawText(hdc,SupportSpellsText,-1,pos41,win32con.DT_LEFT | win32con.DT_VCENTER)
			
		# Mana Shield Text
		win32gui.SetTextColor(hdc, white)
		win32gui.DrawText(hdc,ManaShieldText,-1,pos51,win32con.DT_LEFT | win32con.DT_VCENTER)
		
		# Haste Text
		win32gui.SetTextColor(hdc, gray)
		win32gui.DrawText(hdc,HasteText,-1,pos61,win32con.DT_LEFT | win32con.DT_VCENTER)


		## Timers
		# Item Timer
		win32gui.SetTextColor(hdc, pink)
		win32gui.DrawText(hdc,'{0:.1f}'.format(ItemTimer),-1,pos12,win32con.DT_RIGHT | win32con.DT_VCENTER)

		# Attack Timer
		win32gui.SetTextColor(hdc, red)
		win32gui.DrawText(hdc,'{0:.1f}'.format(AttackSpellsTimer),-1,pos22,win32con.DT_RIGHT | win32con.DT_VCENTER)

		# Healing Spell Timer
		win32gui.SetTextColor(hdc, lblue)
		win32gui.DrawText(hdc,'{0:.1f}'.format(HealingSpellsTimer),-1,pos32,win32con.DT_RIGHT | win32con.DT_VCENTER)
			
		# Support Spell Timer
		win32gui.SetTextColor(hdc, dgreen)
		win32gui.DrawText(hdc,'{0:.1f}'.format(SupportSpellsTimer),-1,pos42,win32con.DT_RIGHT | win32con.DT_VCENTER)
			
		# Mana Shield Timer
		win32gui.SetTextColor(hdc, white)
		win32gui.DrawText(hdc,'{0:.1f}'.format(ManaShieldTimer),-1,pos52,win32con.DT_RIGHT | win32con.DT_VCENTER)
		
		# Haste Timer
		win32gui.SetTextColor(hdc, gray)
		win32gui.DrawText(hdc,'{0:.1f}'.format(HasteTimer),-1,pos62,win32con.DT_RIGHT | win32con.DT_VCENTER)


		win32gui.EndPaint(hWnd, paintStruct)
		return 0

	elif message == win32con.WM_DESTROY:
		print('Being destroyed')
		win32gui.PostQuitMessage(0)
		return 0

	else:
		return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

def customDraw(hWindow):
	# Global variables
	global ItemTimer, AttackSpellsTimer, HealingSpellsTimer, SupportSpellsTimer, ManaShieldTimer, HasteTimer, ItemKeyPressed, AttackSpellsKeyPressed, HealingSpellsKeyPressed, SupportSpellsKeyPressed, ManaShieldKeyPressed, HasteKeyPressed

	# initialize variables
	StartTimer = False
	
	while(True):
		if HasteKeyPressed :
			StartTimer = True
			HasteTimer = HasteDuration
			HasteKeyPressed = False
		
		if StartTimer :
			HasteTimer = HasteTimer - 0.1
		
		
		win32gui.RedrawWindow(hWindow, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)
		
		# Waits fixed time to update
		time.sleep(0.1)
		
		if StartTimer and HasteTimer < 0.1 :
			HasteTimer = HasteDuration
			StartTimer = False
		

# Function for detecting keypress
def handle_events(args):
	global ItemKeyPressed, AttackSpellsKeyPressed, HealingSpellsKeyPressed, SupportSpellsKeyPressed, ManaShieldKeyPressed, HasteKeyPressed
	if isinstance(args, KeyboardEvent):
		# print(args.pressed_key)
		if '5' in args.pressed_key:
			HasteKeyPressed = True

def customKeylogger():
	hk = Hook()
	hk.handler = handle_events 
	hk.hook()  # hook into the events, and listen to the presses

def main():
	# Create transparent window
	hWindow = createWindow()
	
	# Thread that detects keypresses
	tKeylogger = threading.Thread(target = customKeylogger)
	tKeylogger.setDaemon(False)
	tKeylogger.start()
	
	# Thread that updates values on window
	tDraw = threading.Thread(target=customDraw, args=(hWindow,))
	tDraw.setDaemon(False)
	tDraw.start()

	# Dispatch messages
	win32gui.PumpMessages()

if __name__ == '__main__':
	main()
