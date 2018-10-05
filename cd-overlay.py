import win32api
import win32con
import win32gui
import win32ui
import time
import threading
from pyhooked import Hook, KeyboardEvent, MouseEvent
from enum import Enum

## Base Text - Can be edited
ItemText = 'Potion'
AttackSpellsText = 'Attack'
HealingSpellsText = 'Healing'
SupportSpellsText = 'Support'
ManaShieldText = 'Mana Shield'
HasteText = 'Haste'
LifeRingText = 'Life Ring'

## Cooldown and base duration values - Can be edited
ItemCD = 1.0
AttackSpellsCD = 2.0
HealingSpellsCD = 1.0
SupportSpellsCD = 2.0
ManaShieldDuration = 200.0
HasteDuration = 22.0
LifeRingDuration = 600.0

## Key bindings - Can be edited
ItemKeys = ['1','Oem_5','Oem_1']
AttackSpellsKeys = ['Oem_5','Oem_6','Oem_1']
HealingSpellsKeys = ['2','3']
SupportSpellsKeys = ['4','5']
ManaShieldKeys = ['4']
HasteKeys = ['5']

## Timer initial values
ItemTimer = 0.0
AttackSpellsTimer = 0.0
HealingSpellsTimer = 0.0
SupportSpellsTimer = 0.0
ManaShieldTimer = 0.0
HasteTimer = 0.0
LifeRingTimer = 0.0

## Key Press
ItemKeyPressed = False
AttackSpellsKeyPressed = False
HealingSpellsKeyPressed = False
SupportSpellsKeyPressed = False
ManaShieldKeyPressed = False
HasteKeyPressed = False
LifeRingKeyPressed = False

class CooldownGroup(Enum):
	ATKSPELL = 1
	HEALSPELL = 2
	SUPSPELL = 3
	SPCLSPELL = 4
	CNJRSPELL = 5
	NOGROUP = 6 # Does not trigger any group cooldown (equip rings, amulets)
	
class ActionType(Enum):
	OBJECT = 1
	SPELLREGULAR = 2 # Spell CD = Group CD
	SPELLCD = 3
	SPELLEFFECT = 4
	RUNETARGET = 5
	RUNECROSSHAIR = 6
	WEARABLE = 7		

class TrackedAction():
	labelText = str()
	cooldownGroup = CooldownGroup
	actionType = ActionType
	key = str()
	time = 0.0 #can be cooldown or duration
	initial_value = 0.0
	
	def __init__(self,lt,cg,at,key,t,iv):
		self.labelText = lt
		self.cooldownGroup = cg
		self.actionType = at
		self.key = key
		self.time = t
		self.initial_value = iv

aPotion = TrackedAction('Potion',CooldownGroup.NOGROUP,ActionType.OBJECT,'1',1.0,0.0)
#aAtkSpell = TrackedAction('AtkSpell',CooldownGroup.ATKSPELL,ActionType.SPELLREGULAR,'Oem_6',2.0,0.0)

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


def createLabel(hdc, text, pos, color=0x008c8c8c):
    win32gui.SetTextColor(hdc, color)
    win32gui.DrawText(hdc,text,-1,pos,win32con.DT_LEFT | win32con.DT_VCENTER)


def createTimer(hdc, pos, initialValue=0.0, color=0x008c8c8c):
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

        # RECT: left, top, right, bottom
        pos1 = (pleft,ptop,pright,pbottom)
        pos2 = (pleft,ptop+spc,pright,pbottom)
        pos3 = (pleft,ptop+2*spc,pright,pbottom)
        pos4 = (pleft,ptop+3*spc,pright,pbottom)
        pos5 = (pleft,ptop+5*spc,pright,pbottom)
        pos6 = (pleft,ptop+6*spc,pright,pbottom)

        ## Labels
        createLabel(hdc, ItemText, pos1, pink)
        createLabel(hdc, AttackSpellsText, pos2, red)
        createLabel(hdc, HealingSpellsText, pos3, lblue)
        createLabel(hdc, SupportSpellsText, pos4, dgreen)
        createLabel(hdc, ManaShieldText, pos5, white)
        createLabel(hdc, HasteText, pos6, gray)

        ## Timers
        createTimer(hdc, pos1, ItemTimer, pink)
        createTimer(hdc, pos2, AttackSpellsTimer, red)
        createTimer(hdc, pos3, HealingSpellsTimer, lblue)
        createTimer(hdc, pos4, SupportSpellsTimer, dgreen)
        createTimer(hdc, pos5, ManaShieldTimer, white)
        createTimer(hdc, pos6, HasteTimer, gray)

        win32gui.EndPaint(hWnd, paintStruct)
        return 0

    elif message == win32con.WM_DESTROY:
        print('Being destroyed')
        win32gui.PostQuitMessage(0)
        return 0

    else:
        return win32gui.DefWindowProc(hWnd, message, wParam, lParam)


def updateTimers(hWindow):
    # Global variables
    global ItemTimer, AttackSpellsTimer, HealingSpellsTimer, SupportSpellsTimer, ManaShieldTimer, HasteTimer
    global ItemKeyPressed, AttackSpellsKeyPressed, HealingSpellsKeyPressed, SupportSpellsKeyPressed, ManaShieldKeyPressed, HasteKeyPressed
    global ItemCD, AttackSpellsCD, HealingSpellsCD, SupportSpellsCD, ManaShieldDuration, HasteDuration

    # initialize variables
    StartItemTimer = False
    StartAttackSpellsTimer = False
    StartHealingSpellsTimer = False
    StartSupportSpellsTimer = False
    StartManaShieldTimer = False
    StartHasteTimer = False

    # Window and Timer update period
    Ts = 0.05

    while(True):
        # Start Timers for pressed keys and reset command
        # Item
        if ItemKeyPressed:
            StartItemTimer = True
            ItemTimer = ItemCD
            ItemKeyPressed = False

        # Attack Spells
        if AttackSpellsKeyPressed:
            StartAttackSpellsTimer = True
            AttackSpellsTimer = AttackSpellsCD
            AttackSpellsKeyPressed = False

        # Healing Spells
        if HealingSpellsKeyPressed:
            StartHealingSpellsTimer = True
            HealingSpellsTimer = HealingSpellsCD
            HealingSpellsKeyPressed = False

        # Support Spells
        if SupportSpellsKeyPressed:
            StartSupportSpellsTimer = True
            SupportSpellsTimer = SupportSpellsCD
            SupportSpellsKeyPressed = False

        # Mana Shield
        if ManaShieldKeyPressed:
            StartManaShieldTimer = True
            ManaShieldTimer = ManaShieldDuration
            ManaShieldKeyPressed = False

        # Haste
        if HasteKeyPressed:
            StartHasteTimer = True
            HasteTimer = HasteDuration
            HasteKeyPressed = False

        # Decrements timers
        if StartItemTimer: ItemTimer = ItemTimer - Ts
        if StartAttackSpellsTimer: AttackSpellsTimer = AttackSpellsTimer - Ts
        if StartHealingSpellsTimer: HealingSpellsTimer = HealingSpellsTimer - Ts
        if StartSupportSpellsTimer: SupportSpellsTimer = SupportSpellsTimer - Ts
        if StartManaShieldTimer: ManaShieldTimer = ManaShieldTimer - Ts
        if StartHasteTimer: HasteTimer = HasteTimer - Ts

        # Redraw Window
        win32gui.RedrawWindow(hWindow, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)

        # Waits fixed time to update
        time.sleep(Ts)

        # Resets timers when zero is reached

        # Item
        if StartItemTimer and ItemTimer < Ts:
            ItemTimer = 0.0
            StartItemTimer = False

        # Attack Spells
        if StartAttackSpellsTimer and AttackSpellsTimer < Ts:
            AttackSpellsTimer = 0.0
            StartAttackSpellsTimer = False

        # Healing Spells
        if StartHealingSpellsTimer and HealingSpellsTimer < Ts:
            HealingSpellsTimer = 0.0
            StartHealingSpellsTimer = False

        # Support Spells
        if StartSupportSpellsTimer and SupportSpellsTimer < Ts:
            SupportSpellsTimer = 0.0
            StartSupportSpellsTimer = False

        # Mana Shield
        if StartManaShieldTimer and ManaShieldTimer < Ts:
            ManaShieldTimer = 0.0
            StartManaShieldTimer = False

        # Haste
        if StartHasteTimer and HasteTimer < Ts:
            HasteTimer = 0.0
            StartHasteTimer = False


def handle_events(args):
    global ItemKeyPressed, AttackSpellsKeyPressed, HealingSpellsKeyPressed, SupportSpellsKeyPressed, ManaShieldKeyPressed, HasteKeyPressed
    global ItemKeys, AttackSpellsKeys, HealingSpellsKeys, SupportSpellsKeys, ManaShieldKeys, HasteKeys

    if isinstance(args, KeyboardEvent):
        #print(args.pressed_key)

        # Item Key Pressed
        if any(i in ItemKeys for i in args.pressed_key): ItemKeyPressed = True

        # Attack Key Pressed
        if any(i in AttackSpellsKeys for i in args.pressed_key): AttackSpellsKeyPressed = True

        # Healing Key Pressed
        if any(i in HealingSpellsKeys for i in args.pressed_key): HealingSpellsKeyPressed = True

        # Support Key Pressed
        if any(i in SupportSpellsKeys for i in args.pressed_key): SupportSpellsKeyPressed = True

        # ManaShield Key Pressed
        if any(i in ManaShieldKeys for i in args.pressed_key): ManaShieldKeyPressed = True

        # Haste Key Pressed
        if any(i in HasteKeys for i in args.pressed_key): HasteKeyPressed = True


def keylogger():
    hk = Hook()
    hk.handler = handle_events
    hk.hook()  # hook into the events, and listen to the presses


def main():
    # Create transparent window
    hWindow = createWindow()

    # Thread that detects keypresses
    tKeylogger = threading.Thread(target = keylogger)
    tKeylogger.setDaemon(False)
    tKeylogger.start()

    # Thread that updates values on window
    tTimers = threading.Thread(target=updateTimers, args=(hWindow,))
    tTimers.setDaemon(False)
    tTimers.start()

    # Dispatch messages
    win32gui.PumpMessages()


if __name__ == '__main__':
    main()
