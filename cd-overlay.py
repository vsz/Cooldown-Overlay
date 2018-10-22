from classes import *

# Initialize
actionList = []
groupList = []
equipmentList = []
equipmentSlotList = []

## Use debug = True to see keys you are pressing (good to configure hotkeys!)
debug = False

## Key to reset all countdowns
resetKey = '-'

## Add your tracked actions here
# Objects
actionList.append(TrackedAction('Potion',TextColor.BLACK,[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['1'],visible=False))

# Attack Runes
actionList.append(TrackedAction('Rune',TextColor.rgb2hex((255,100,0)),[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,[']'],ut=UseType.CROSSHAIR,visible=True))
actionList.append(TrackedAction('SD',TextColor.RED,[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,[';'],visible=False))
actionList.append(TrackedAction('FireWall',TextColor.RED,[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,['shift+!'],ut=UseType.CROSSHAIR,visible=False))
actionList.append(TrackedAction('FireBomb',TextColor.RED,[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,['shift+@'],ut=UseType.CROSSHAIR,visible=False))

# Attack Spells
actionList.append(TrackedAction('Strike',TextColor.RED,[CooldownGroup.ATTACK],ActionType.ATKREGULAR,['['],visible=False))

actionList.append(TrackedAction('StrongIce',TextColor.rgb2hex((0,150,255)),[CooldownGroup.ATTACK,CooldownGroup.STRONGSTRIKE],ActionType.ATKCOOLDOWN,['shift+{'],8.0,visible=True))
actionList.append(TrackedAction('StrongTerra',TextColor.rgb2hex((0,255,137)),[CooldownGroup.ATTACK,CooldownGroup.STRONGSTRIKE],ActionType.ATKCOOLDOWN,['F9'],8.0,visible=True))

actionList.append(TrackedAction('IceWave',TextColor.rgb2hex((0,150,255)),[CooldownGroup.ATTACK],ActionType.ATKCOOLDOWN,['shift+}'],8.0,visible=True))
actionList.append(TrackedAction('TerraWave',TextColor.rgb2hex((0,255,137)),[CooldownGroup.ATTACK],ActionType.ATKCOOLDOWN,['F10'],4.0,visible=True))

actionList.append(TrackedAction('UltimateIce',TextColor.rgb2hex((0,150,255)),[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F11'],30.0))
#actionList.append(TrackedAction('UltimateTerra',TextColor.rgb2hex((0,137,255)),[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F11'],30.0))

actionList.append(TrackedAction('Ice UE',TextColor.ORANGE,[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F12'],40.0))
#actionList.append(TrackedAction('Terra UE',TextColor.ORANGE,[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F12'],40.0))

# Heal
actionList.append(TrackedAction('Exura',TextColor.LBLUE,[CooldownGroup.HEAL],ActionType.HEALREGULAR,['3'],visible=False))
actionList.append(TrackedAction('Exura Gran',TextColor.LBLUE,[CooldownGroup.HEAL],ActionType.HEALREGULAR,['2'],visible=False))

# Support
#actionList.append(TrackedAction('Magic Shield',TextColor.WHITE,[CooldownGroup.SUPPORT],ActionType.SUPPORTEFFECT,['4'],200.0))
actionList.append(TrackedAction('Haste',TextColor.GRAY,[CooldownGroup.SUPPORT],ActionType.SUPPORTEFFECT,['5'],22.0))
actionList.append(TrackedAction('MWall',TextColor.RED,[CooldownGroup.SUPPORT,CooldownGroup.OBJECT],ActionType.ATKRUNE,['shift+#'],ut=UseType.CROSSHAIR,visible=False))

## Equipment to be tracked
# Rings
equipmentList.append(TrackedEquipment('LifeRing', TextColor.DGREEN,[CooldownGroup.NONE],ActionType.EQUIPMENT,['F2'],1200.0,et=EquipmentType.RING))
equipmentList.append(TrackedEquipment('RingHealing', TextColor.rgb2hex((227,115,32)),[CooldownGroup.NONE],ActionType.EQUIPMENT,['F3'],450.0,et=EquipmentType.RING))
equipmentList.append(TrackedEquipment('EnergyRing', TextColor.LBLUE,[CooldownGroup.NONE],ActionType.EQUIPMENT,['4'],600.0,iv=355.0,et=EquipmentType.RING))
equipmentList.append(TrackedEquipment('OtherRing', TextColor.ORANGE,[CooldownGroup.NONE],ActionType.EQUIPMENT,['F4','F5','F6'],et=EquipmentType.RING,expires=False,visible=False))

## DO NOT DELETE GROUPS. IF YOU DONT WANT TO SEE IT, JUST SET 'visible=False' IN ARGUMENTS
groupList.append(TrackedGroup('Potion',TextColor.PINK,CooldownGroup.OBJECT,1.0))
groupList.append(TrackedGroup('Attack',TextColor.RED,CooldownGroup.ATTACK,2.0))
groupList.append(TrackedGroup('Healing',TextColor.LBLUE,CooldownGroup.HEAL,1.0))
groupList.append(TrackedGroup('Support',TextColor.DGREEN,CooldownGroup.SUPPORT,2.0,visible=False))
groupList.append(TrackedGroup('Conjure',TextColor.BLACK,CooldownGroup.CONJURE,2.0,visible=False))
groupList.append(TrackedGroup('Special',TextColor.ORANGE,CooldownGroup.SPECIAL,4.0))
groupList.append(TrackedGroup('StrongStrike',TextColor.ORANGE,CooldownGroup.STRONGSTRIKE,8.0,visible=False))

## DO NOT DELETE EQUIPMENT SLOTS
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.RING))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.BOOTS))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.WEAPON))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.HELMET))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.SHIELD))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.ARMOR))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.LEGS))

# Separators for the tracked actions section
emptyLines = [2,4,6,8];

def createWindow():
	#get instance handle
	hInstance = win32api.GetModuleHandle()

	# the class name
	className = 'Cooldown Overlay'

	# create and initialize window class
	wndClass				= win32gui.WNDCLASS()
	wndClass.style			= win32con.CS_HREDRAW | win32con.CS_VREDRAW
	wndClass.lpfnWndProc	= wndProc
	wndClass.hInstance		= hInstance
	wndClass.hIcon			= win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
	wndClass.hCursor		= win32gui.LoadCursor(None, win32con.IDC_ARROW)
	wndClass.hbrBackground	= win32gui.GetStockObject(win32con.WHITE_BRUSH)
	wndClass.lpszClassName	= className

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
	win32gui.ShowWindow(hWindow, win32con.SW_SHOWNORMAL)
	win32gui.UpdateWindow(hWindow)

	return hWindow

def createTextLabel(hdc, pos, color=TextColor.BLACK,text=''):
	win32gui.SetTextColor(hdc, color)
	win32gui.DrawText(hdc,text,-1,pos,win32con.DT_LEFT | win32con.DT_VCENTER)

def createTimerLabel(hdc, pos, color=TextColor.BLACK,initialValue=0.0):
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

		# Get relative dimensions
		rect = win32gui.GetClientRect(hWnd)
		w = rect[2]
		h = rect[3]

		pleft = int(0.752*w)
		ptop = int(0.1*h)
		pright = int(0.8165*w)
		pbottom = int(0.55*h)
		spc = int(0.015*h)
		
		# Filter what do draw
		groupsToDraw = [g for g in groupList if g.visible]
		actionsToDraw = [a for a in actionList if a.visible]
		equipmentToDraw = [e for e in equipmentList if e.visible]
		
		for idx,group in enumerate(groupsToDraw):
			pos = (pleft,ptop+idx*spc,pright,pbottom)
			createTextLabel(hdc,pos,group.color,group.labelText)
			createTimerLabel(hdc,pos,group.color,group.countdown)		
		
		k=idx+2
		for idx,action in enumerate(actionsToDraw):
			if (idx+1) in emptyLines : k=k+1
			
			pos = (pleft,ptop+(idx+k)*spc,pright,pbottom)
			createTextLabel(hdc,pos,action.color,action.labelText)
			createTimerLabel(hdc,pos,action.color,action.countdown)

		k=k+idx+2
		for idx,equip in enumerate(equipmentToDraw):
			#if (idx+1) in emptyLines : k=k+1

			pos = (pleft,ptop+(idx+k)*spc,pright,pbottom)
			createTextLabel(hdc,pos,equip.color,equip.labelText)
			createTimerLabel(hdc,pos,equip.color,equip.countdown)
			

		win32gui.EndPaint(hWnd, paintStruct)
		return 0

	elif message == win32con.WM_DESTROY:
		win32gui.PostQuitMessage(0)
		return 0

	else:
		return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

def debugMode():
	print('Debug Mode: press hotkeys to see how to add them in the script')
	while(True):
		s = keyboard.read_hotkey(suppress=False)
		print(s)

def main():
	# Goes in debug mode
	if debug:
		debugMode()
	
	# Create transparent window
	hWindow = createWindow()

	# Create threads
	# Thread that detects keyboard hotkeys
	tHotkeyTracker = HotkeyTracker(actionList,equipmentList,groupList,resetKey)
	tHotkeyTracker.start()

	# Thread that detects mouse buttons
	tMouseTracker = MouseTracker(actionList)
	tMouseTracker.start()
	
	# Thread that tracks actions
	tActionTracker = ActionTracker(actionList,equipmentList,groupList,equipmentSlotList)
	tActionTracker.start()

	try:
		while(True):
			win32gui.RedrawWindow(hWindow, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)
			win32gui.PumpWaitingMessages()
			time.sleep(0.05)
		
	except KeyboardInterrupt:
		print("\nScript interrupted")
				
		tActionTracker.abort = True
		tActionTracker.join()
		print("Action Tracker Stopped")
		
		tMouseTracker.join()
		print("Mouse Tracker Stopped")
		
		tHotkeyTracker.join()	
		print("Hotkey Tracker Stopped")

		win32gui.DestroyWindow(hWindow)
		print("Overlay window destroyed")
		print("Closing...")	

if __name__ == '__main__':
	main()
