import win32api
import win32con
import win32gui
import win32ui
import time
import threading

## Define global variables for text
InitText = 'Starting Cooldown Overlay up.\nStay frosty.'

## Base Text
# Cooldown Groups
ItemText = 'Potion : '
AttackSpellsText = 'Attack : '
HealingSpellsText = 'Healing : '
SupportSpellsText = 'Support : '

# Spells duration
ManaShieldText = 'Mana Shield : '
HasteText = 'Haste : '

# Equipment duration
LifeRingText = 'Life Ring : '

## Cooldown and duration values
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


def main():
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

    # New code: Create and start the thread
	thr = threading.Thread(target=customDraw, args=(hWindow,))
	thr.setDaemon(False)
	thr.start()

    # Dispatch messages
	win32gui.PumpMessages()




def wndProc(hWnd, message, wParam, lParam):

    if message == win32con.WM_PAINT:
        hdc, paintStruct = win32gui.BeginPaint(hWnd)

		# Font configuration
        dpiScale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
        fontSize = 15

        # http://msdn.microsoft.com/en-us/library/windows/desktop/dd145037(v=vs.85).aspx
        lf = win32gui.LOGFONT()
        lf.lfFaceName = "Tahoma"
        lf.lfHeight = int(round(dpiScale * fontSize))
        #lf.lfWeight = 150
        # Use nonantialiased to remove the white edges around the text.
        # lf.lfQuality = win32con.NONANTIALIASED_QUALITY
        hf = win32gui.CreateFontIndirect(lf)
        win32gui.SelectObject(hdc, hf)

        rect = win32gui.GetClientRect(hWnd)
        #print(rect)
        w = rect[2]
        h = rect[3]
        pos = (int(0.8*w),int(0.2*h),int(w),int(0.5*h))
        #print(pos)
        
        win32gui.DrawText(
            hdc,
            InitText,
            -1,
            pos,
            win32con.DT_LEFT | win32con.DT_VCENTER)

        win32gui.EndPaint(hWnd, paintStruct)
        return 0

    elif message == win32con.WM_DESTROY:
        print('Being destroyed')
        win32gui.PostQuitMessage(0)
        return 0

    else:
        return win32gui.DefWindowProc(hWnd, message, wParam, lParam)


# Thread that updates values on screen
def customDraw(hWindow):
	global InitText
	time.sleep(1.0)
	InitText = AttackSpellsText + 'Ready\n' + HealingSpellsText + 'Ready\n' + SupportSpellsText + 'Ready\n\n' + ManaShieldText + 'Ready\n' + HasteText + 'Ready\n\n' + LifeRingText + 'Ready\n'
    
	while(True):
		time.sleep(0.05)
		win32gui.RedrawWindow(hWindow, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)


if __name__ == '__main__':
    main()
