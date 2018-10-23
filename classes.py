from enum import Enum
import keyboard
import mouse
import threading
import time
import datetime
import win32api
import win32con
import win32gui
import win32ui
import math

class ColorCode:		
	# Colors
	BLACK = 0x00000000
	BLUE = 0x00ff0000
	RED = 0x000000ff
	GREEN = 0x0000ff00
	WHITE = 0x00fefefe # ??
	PINK = 0x00c800c8
	LBLUE = 0x00dcc800
	DGREEN = 0x0041961e
	GRAY = 0x008c8c8c
	ORANGE = 0x000098ff
	
	def rgb2hex(rgb):
		# uses bgr in hex
		bgr = (rgb[2], rgb[1], rgb[0])
		strValue = '%02x%02x%02x' % bgr
		iValue = int(strValue, 16)
		
		return iValue

class ArcPlacement(Enum):
	NONE = 0
	RIGHT = 1
	LEFT = 2

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
	STRONGSTRIKE = 7
	NONE = 8

class EquipmentType(Enum):
	RING = 1
	AMULET = 2
	WEAPON = 3
	SHIELD = 4
	ARMOR = 5
	LEGS = 6
	HELMET = 7
	BOOTS = 8
	NONE = 9

class UseType(Enum):
	TARGET = 1
	CROSSHAIR = 2

class WindowHandler:
	def __init__(self,actionList,groupList,equipmentList,emptyLines):
		self.actionList = actionList
		self.groupList = groupList
		self.equipmentList = equipmentList
		self.emptyLines = emptyLines
		self.hWindow = self.createWindow()

	def createWindow(self):
		#get instance handle
		hInstance = win32api.GetModuleHandle()

		# the class name
		className = 'Cooldown Overlay'

		# create and initialize window class
		wndClass				= win32gui.WNDCLASS()
		wndClass.style			= win32con.CS_HREDRAW | win32con.CS_VREDRAW
		wndClass.lpfnWndProc	= self.wndProc
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

	def drawTextLabel(self, hdc, pos, color=ColorCode.BLACK,text=''):
		win32gui.SetTextColor(hdc, color)
		win32gui.DrawText(hdc,text,-1,pos,win32con.DT_LEFT | win32con.DT_VCENTER)

	def drawTimerLabel(self, hdc, pos, color=ColorCode.BLACK,initialValue=0.0):
		win32gui.SetTextColor(hdc, color)
		win32gui.DrawText(hdc,'{0:.1f}'.format(initialValue),-1,pos,win32con.DT_RIGHT | win32con.DT_VCENTER)

	def drawRightArc(self, hdc, pos, radius, width, span, percent, color=ColorCode.BLACK):
		
		if percent > 0.0:
			# Get arc center coordinates
			xc = pos[0]
			yc = pos[1]
			
			# Calculate a2
			a1 = math.radians(span/2)
			a2 = math.asin(radius*math.sin(a1)/(radius+width))
			
			# calculate displacement on x and y axis
			dx = radius*math.cos(a2)
			dy = radius*math.sin(a2)
			
			# calculate starting point coordinates
			xs = int(xc + dx)
			ys = int(yc + dy)
			a2d = math.degrees(a2)
			
			# determines arc span
			span = 2*a2d
			
			# sets the percentage to be drawn
			n = percent
			
			# sets arc fill color
			sb = win32gui.CreateSolidBrush(color)
			win32gui.SelectObject(hdc, sb)
			
			# sets arc stroke
			sp = win32gui.CreatePen(win32con.PS_SOLID,1,ColorCode.BLACK)
			win32gui.SelectObject(hdc,sp)

			# draws the outline of the arc
			win32gui.BeginPath(hdc)
			win32gui.MoveToEx(hdc,xs,ys)
			win32gui.AngleArc(hdc,xc,yc,radius+width,-a2d,int(n*span))
			win32gui.AngleArc(hdc,xc,yc,radius,int(a2d-(1-n)*span),-int(n*span))
			win32gui.EndPath(hdc)
			
			# fills the arc with outer stroke
			win32gui.StrokeAndFillPath(hdc)
		
			# returns the next arc span and radius
			return span,(radius+width)
		else:
			# if its not drawn, returns original arc span and radius
			return span,radius

	def drawLeftArc(self, hdc, pos, radius, width, span, percent, color=ColorCode.BLACK):
		
		if percent > 0.0:
			# Get arc center coordinates
			xc = pos[0]
			yc = pos[1]
			
			# Calculate a2
			a1 = math.radians(span/2)
			a2 = math.asin(radius*math.sin(a1)/(radius+width))
			
			# calculate displacement on x and y axis
			dx = radius*math.cos(a2)
			dy = radius*math.sin(a2)
			
			# calculate starting point coordinates
			xs = int(xc - dx)
			ys = int(yc + dy)
			a2d = math.degrees(a2)
			
			# determines arc span
			span = 2*a2d
			
			# sets the percentage to be drawn
			n = percent
			
			# sets arc fill color
			sb = win32gui.CreateSolidBrush(color)
			win32gui.SelectObject(hdc, sb)

			# draws the outline of the arc
			win32gui.BeginPath(hdc)
			win32gui.MoveToEx(hdc,xs,ys)
			win32gui.AngleArc(hdc,xc,yc,radius+width,180+a2d,-int(n*span))
			win32gui.AngleArc(hdc,xc,yc,radius,int(180-a2d+(1-n)*span),int(n*span))
			win32gui.EndPath(hdc)
			
			# fills the arc with outer stroke
			win32gui.StrokeAndFillPath(hdc)
		
			# returns the next arc span and radius
			return span,(radius+width)
		else:
			# if its not drawn, returns original arc span and radius
			return span,radius

	def wndProc(self,hWnd,message, wParam, lParam):

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
			
			br=win32gui.CreateSolidBrush(win32api.RGB(255,0,0))
			win32gui.SelectObject(hdc, br)
			
			# Get relative dimensions
			rect = win32gui.GetClientRect(hWnd)
			w = rect[2]
			h = rect[3]

			# Bars
			# Positions the bars
			xc = int(w/2.033)
			yc = int(h/2.522)
			r = 171
			dr = 6
			alpha = 90
			
			## Text
			# Positions the text
			pleft = int(0.752*w)
			ptop = int(0.1*h)
			pright = int(0.8165*w)
			pbottom = int(0.55*h)
			spc = int(0.015*h)
			
			# Filter what do draw
			groupsToDraw = [g for g in self.groupList if g.visible]
			actionsToDraw = [a for a in self.actionList if a.visible]
			equipmentToDraw = [e for e in self.equipmentList if e.visible]
			rightArcToDraw = [a for a in self.actionList if a.arcPlacement == ArcPlacement.RIGHT]
			leftArcToDraw = [a for a in self.actionList if a.arcPlacement == ArcPlacement.LEFT]

			sr = alpha
			rr = r
			for idx,action in enumerate(rightArcToDraw):
				sr,rr = self.drawRightArc(hdc,(xc,yc),rr,dr,sr,action.getPercentage(), action.color)

			sl = alpha
			rl = r
			for idx,action in enumerate(leftArcToDraw):
				sl,rl = self.drawLeftArc(hdc,(xc,yc),rl,dr,sl,action.getPercentage(), action.color)

			for idx,group in enumerate(groupsToDraw):
				pos = (pleft,ptop+idx*spc,pright,pbottom)
				self.drawTextLabel(hdc,pos,group.color,group.labelText)
				self.drawTimerLabel(hdc,pos,group.color,group.countdown)		
			
			k=idx+2
			for idx,action in enumerate(actionsToDraw):
				if (idx+1) in self.emptyLines : k=k+1
				
				pos = (pleft,ptop+(idx+k)*spc,pright,pbottom)
				self.drawTextLabel(hdc,pos,action.color,action.labelText)
				self.drawTimerLabel(hdc,pos,action.color,action.countdown)

			k=k+idx+2
			for idx,equip in enumerate(equipmentToDraw):
				#if (idx+1) in emptyLines : k=k+1

				pos = (pleft,ptop+(idx+k)*spc,pright,pbottom)
				self.drawTextLabel(hdc,pos,equip.color,equip.labelText)
				self.drawTimerLabel(hdc,pos,equip.color,equip.countdown)
				

			win32gui.EndPaint(hWnd, paintStruct)
			return 0

		elif message == win32con.WM_DESTROY:
			win32gui.PostQuitMessage(0)
			return 0

		else:
			return win32gui.DefWindowProc(hWnd, message, wParam, lParam)
	

class ActionTracker(threading.Thread):
	def __init__(self,actionList,equipmentList,groupList,equipmentSlotList):
		self.actionList = actionList
		self.equipmentList = equipmentList
		self.groupList = groupList
		self.equipmentSlotList = equipmentSlotList
		self.abort = False
		threading.Thread.__init__(self)
		
	def run(self):
		# Window and Timer update period
		Ts = 0.05
		
		# Initialize
		for group in self.groupList:
			group.setActionList(self.actionList)
			
		for slot in self.equipmentSlotList:
			slot.setEquipmentList(self.equipmentList)
		
		print("Tracked Actions")
		for action in self.actionList:
			print(action)
		
		print("\nTracked Equipment")
		for equip in self.equipmentList:
			print(equip)
		
		ctime1 = datetime.datetime.now()
		
		while(not self.abort) :
			# Tracks ellapsed time
			ctime2 = datetime.datetime.now()
			delta = ctime2-ctime1
			ctime1 = ctime2
			et = delta.seconds+0.000001*delta.microseconds
			
			#print(et)
			for equipSlot in self.equipmentSlotList:
				equipSlot.track(et)
			
			for equip in self.equipmentList:
				equip.track(et)
							
			for group in self.groupList:
				group.track(et)
			
			for action in self.actionList:
				action.track(et)
				
			time.sleep(Ts)

class HotkeyTracker(threading.Thread):
	def __init__(self,actionList,equipmentList,groupList,resetKey='-'):
		self.actionList = actionList
		self.equipmentList = equipmentList
		self.groupList = groupList
		self.resetKey = resetKey
		threading.Thread.__init__(self)
		
	def run(self):
		keyboard.add_hotkey(self.resetKey,self.resetAllCountdowns,args=())
		
		for equip in self.equipmentList:
			for key in equip.keys:
				# cannot be equipped while walking
				keyboard.add_hotkey(key,equip.triggerByKey,args=())
		
		for action in self.actionList:
			for key in action.keys:
				keyboard.add_hotkey(key,action.triggerByKey,args=())
				
				# actions can be executed while walking
				keyboard.add_hotkey(key+'+w',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+s',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+a',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+d',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+q',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+e',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+z',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+c',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+W',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+S',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+A',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+D',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+Q',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+E',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+Z',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+C',action.triggerByKey,args=())

				#keyboard.add_hotkey(key+'+up',action.triggerByKey,args=())
				#keyboard.add_hotkey(key+'+down',action.triggerByKey,args=())
				#keyboard.add_hotkey(key+'+left',action.triggerByKey,args=())
				#keyboard.add_hotkey(key+'+right',action.triggerByKey,args=())
				
	def resetAllCountdowns(self):
		for action in self.actionList:
			action.resetCountdown()
			
		for group in self.groupList:
			group.resetCountdown()

class MouseTracker(threading.Thread):
	def __init__(self,actionList):
		self.actionList = actionList
		threading.Thread.__init__(self)
		
	def run(self):
		mouse.on_right_click(lambda: self.rightClick())
		mouse.on_click(lambda: self.leftClick())

	def rightClick(self):	
		for action in self.actionList:
			if action.useType == UseType.CROSSHAIR:
				action.triggerByRightMouse()

	def leftClick(self):
		for action in self.actionList:
			if action.useType == UseType.CROSSHAIR:
				action.triggerByLeftMouse()
				
class TrackedGroup:

	def __init__(self,lt,color,cg,time=0.0,visible=True):
		self.labelText = lt
		self.color = color
		self.cooldownGroup = cg
		self.time = time
		self.countdown = 0.0
		self.actionList = []
		self.affectedActionList = []
		self.triggered = False
		self.running = False
		self.visible = visible

	def setActionList(self,al):
		self.actionList = [a for a in al if (self.cooldownGroup in a.cooldownGroups)]
					
		for action in self.actionList:
			action.setTime(self.time)
		
		if self.cooldownGroup == CooldownGroup.SPECIAL: #HARDCODED
			self.affectedActionList = [a for a in al if (CooldownGroup.ATTACK in a.cooldownGroups)]
		
	def resetTrigger(self):
		self.triggered = False
	
	def run(self):
		self.running = True
		
	def stop(self):
		self.running = False

	def decrementCountdown(self,Ts):
		self.countdown = self.countdown - Ts
		
	def setCountdown(self,cd):
		self.countdown = max(self.countdown,cd)

	def resetCountdown(self):
		self.countdown = 0.0
			
	def trigger(self):
		self.triggered = True			
				
	def triggerGroup(self):
		for action in self.actionList:
			action.triggerByGroup()
			action.setGroupTime(self.time)
			
		for action in self.affectedActionList:
			action.triggerByGroup()
			action.setGroupTime(self.time)

	def track(self,Ts):
		for action in self.actionList:
			if action.trigger:
				self.trigger()
				self.triggerGroup()

		if self.triggered:
			self.run()
			self.setCountdown(self.time)
			self.resetTrigger()
		
		if self.running : self.decrementCountdown(Ts)
		
		# stops timer if it runs out
		if self.running and self.countdown < Ts :
			self.countdown = 0.0
			self.running = False
	
class TrackedEquipmentSlot:
	def __init__(self,et):
		self.equipmentType = et
		self.equipmentList = []
		self.equipped = False
		self.activeEquipment = None

	def setEquipmentList(self,el):
		self.equipmentList = [e for e in el if (self.equipmentType == e.equipmentType)]
	
	def unequipAllBut(self,equip):
		for e in self.equipmentList:
			if e is not equip:
				e.stop()
	
	def track(self,Ts):
		for equip in self.equipmentList:
			if equip.trigger:
				if equip.equipped:
					self.activeEquipment = None
				else:
					if self.activeEquipment is not None:
						self.activeEquipment.unequip()
					self.activeEquipment = equip
	
class TrackedEquipment:

	def __init__(self,lt,color,cg,at,keys,t=0.0,iv=0.0,et=EquipmentType.NONE,ut=UseType.TARGET,expires=True,visible=True):
		self.labelText = lt
		self.color = color
		self.cooldownGroups = cg
		self.actionType = at
		self.keys = keys
		self.time = t
		self.trigger = False
		self.equipped = False
		self.useType = ut
		self.visible = visible
		self.equipmentType = et
		self.expires = expires
		self.expired = False
		
		if self.expires:
			if iv == 0.0: 
				self.countdown = self.time
			else: 
				self.countdown = iv
		else:
			self.countdown = 0.0
		
	def __str__(self):
		stringKey = ""
		for key in self.keys:
			stringKey = stringKey + key + " "
		return (self.labelText + " tracked on hotkey(s) " + stringKey)

	def setTime(self,time):
		self.time = max(self.time,time)
		
	def resetTrigger(self):
		self.trigger = False
	
	def setTrigger(self):
		self.trigger = True	

	def equip(self):
		self.equipped = True
		
	def unequip(self):
		self.equipped = False

	def decrementCountdown(self,Ts):
		self.countdown = self.countdown - Ts
	
	def setCountdown(self,cd):
		self.countdown = max(self.countdown,cd)
	
	def resetCountdown(self):
		self.countdown = 0.0

	def setExpired(self):
		self.expired = True
		
	def resetExpired(self):
		self.expired = False
	
	def triggerByKey(self):
		#print(self.labelText + " triggered by Key")
		self.setTrigger()

	def track(self,Ts):
		
		if self.trigger:
			if self.equipped:
				self.unequip()
				#print(self.labelText+" has been unequipped")

			elif not self.equipped:
				self.equip()
				if self.time != self.countdown:
					self.countdown = self.countdown - 6.0 # re-equipping an item that is not brand-new reduces its duration by 6 seconds
				#print(self.labelText+" has been equipped")
			self.resetTrigger()
			
		if self.equipped and self.expires : self.decrementCountdown(Ts)
		
		# stops timer if it runs out
		if self.equipped and self.expires and self.countdown < Ts :
			self.setCountdown(self.time)
			self.unequip()
			self.setExpired()

class TrackedAction:
	
	def __init__(self,lt,color,cg,at,keys,t=1.0,iv=0.0,et=EquipmentType.NONE,ut=UseType.TARGET,visible=True,ap=ArcPlacement.NONE):
		self.labelText = lt
		self.color = color
		self.cooldownGroups = cg
		self.actionType = at
		self.keys = keys
		self.time = t
		self.groupTime = 0.0
		self.countdown = iv
		self.trigger = False
		self.groupTrigger = False
		self.running = False
		self.useType = ut
		self.armed = False
		self.visible = visible
		self.equipmentType = et
		self.scale=t
		self.arcPlacement = ap
		
	def __str__(self):
		stringKey = ""
		for key in self.keys:
			stringKey = stringKey + key + " "
		return (self.labelText + " tracked on hotkey(s) " + stringKey)

	def setTime(self,time):
		self.time = max(self.time,time)
		self.scale = self.time
	
	def setGroupTime(self,gtime):
		self.groupTime = max(self.groupTime,gtime)
	
	def resetGroupTime(self):
		self.groupTime = 0.0
	
	def resetGroupTrigger(self):
		self.groupTrigger = False
		self.resetGroupTime()
	
	def resetTrigger(self):
		self.trigger = False
	
	def setTrigger(self):
		self.trigger = True	
	
	def arm(self):
		self.armed = True
		#print(self.labelText + " Armed!")
		
	def unarm(self):
		self.armed = False	
	
	def run(self):
		self.running = True
		
	def stop(self):
		self.running = False

	def decrementCountdown(self,Ts):
		self.countdown = self.countdown - Ts
	
	def setCountdown(self,cd):
		self.countdown = max(self.countdown,cd)
		self.scale = self.countdown
	
	def resetCountdown(self):
		self.countdown = 0.0

	def getPercentage(self):
		return self.countdown/self.scale

	def triggerByKey(self):
		#print(self.labelText + " triggered by Key")

		if self.useType == UseType.TARGET:
			self.setTrigger()
			
		if self.useType == UseType.CROSSHAIR: 
			self.arm()

	def triggerByLeftMouse(self):		
		if self.useType == UseType.CROSSHAIR:
			if self.armed:
				self.unarm()
				self.setTrigger()

	def triggerByRightMouse(self):
		if self.useType == UseType.CROSSHAIR:
			if self.armed:
				self.unarm()
				

	def triggerByGroup(self):
		self.groupTrigger = True
	
	def track(self,Ts):
		
		if self.trigger and not self.groupTrigger:
			self.run()
			self.setCountdown(self.time)
			self.resetTrigger()
			#print(self.labelText+" Trigger by Action")
			
		if self.groupTrigger and not self.trigger:
			self.run()
			self.setCountdown(self.groupTime)
			self.resetGroupTrigger()
			#print(self.labelText+" Trigger by Group")
		
		if self.trigger and self.groupTrigger:
			self.run()
			self.setCountdown(max(self.groupTime,self.time))
			self.resetTrigger()
			self.resetGroupTrigger()
			#print(self.labelText+" Action triggered the group")
		
		if self.running : self.decrementCountdown(Ts)
		
		# stops timer if it runs out
		if self.running and self.countdown < Ts :
			self.resetCountdown()
			self.stop()
	
