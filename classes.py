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
import sys
import json
import re

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

class ChatMode:
	OFF = 'chatOff'
	ON = 'chatOn'

class ArcPlacement(Enum):
	NONE = 0
	RIGHT = 1
	LEFT = 2
	BOTH = 3

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
	FIELD = 8
	NONE = 9

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

class OptionsHandler:
	def __init__(self, characterName, chatMode=ChatMode.OFF):
		self.getUserOptions()
		self.getCharacterHotkeySet(characterName)
		self.createHotkeyBindingList(chatMode)
		self.createGroupList()
		self.createActionList()
		self.determinePosition()

	def determinePosition(self):
		self.position = self.userOptions['position']

	def printActionList(self):
		for action in self.actionList:
			print(action)

	def getUserOptions(self):
		with open('config.json', 'r', encoding='utf-8') as f:
			self.userOptions = json.load(f)['useroptions']

		self.path = self.userOptions['clientoptions']['path']
		self.filename = self.userOptions['clientoptions']['filename']
		self.autoposition = self.userOptions['autoposition']

	def createGroupList(self):
		self.groupList = []
		
		# Get group information from file
		with open('config.json', 'r') as f:
			groups = json.load(f)['groups']

		# Populate group list
		for g in groups:
			name = groups[g]['displayinfo']['name']
			color = ColorCode.rgb2hex(groups[g]['displayinfo']['color'])
			cdg = CooldownGroup[g.upper()]
			cooldown = groups[g]['info']['cooldown']
			visible = groups[g]['displayinfo']['text']

			tg = TrackedGroup(name,color,cdg,cooldown,visible=visible)
			self.groupList.append(tg)

	def createActionList(self):
		self.actionList = []

		# Load objects and spells information from file
		with open('config.json','r') as f:
			data = json.load(f)
			items = data['items']
			spells = data['spells']

		for hk in self.hotkeyList:
			# Objects
			if 'useObject' in hk.action:
				itemId = str(hk.action['useObject'])
				if itemId in items:
					name = items[itemId]['displayinfo']['name']
					color = ColorCode.rgb2hex(items[itemId]['displayinfo']['color'])
					cdg = [CooldownGroup[g.upper()] for g in items[itemId]['info']['groups']]
					hotkey = [hk.hotkey]
					if hk.action['useType'].startswith('UseOn'):
						usetype = UseType.TARGET
					elif hk.action['useType'].startswith('Select'):
						usetype = UseType.CROSSHAIR
					text = items[itemId]['displayinfo']['text']
					arc = ArcPlacement[items[itemId]['displayinfo']['arc'].upper()]

					ta = TrackedAction(name,color,cdg,ActionType.ATKRUNE,hotkey,ut=usetype,visible=text,ap=arc)
					self.actionList.append(ta)

			# Spells
			if 'chatText' in hk.action:
				spell = hk.action['chatText']
				if hk.action['chatText'] in spells:
					name = spells[spell]['displayinfo']['name']
					color = ColorCode.rgb2hex(spells[spell]['displayinfo']['color'])
					cdg = [CooldownGroup[g.upper()] for g in spells[spell]['info']['groups']]
					hotkey = [hk.hotkey]
					cooldown = spells[spell]['info']['cooldown']
					duration = spells[spell]['info']['duration']
					text = spells[spell]['displayinfo']['text']
					arc = ArcPlacement[spells[spell]['displayinfo']['arc'].upper()]

					ta = TrackedAction(name,color,cdg,ActionType.ATKRUNE,hotkey,max(cooldown,duration),visible=text,ap=arc)
					self.actionList.append(ta)

	def getCharacterHotkeySet(self,characterName):
		with open(self.path+self.filename, 'r') as f:
			hotkeySets = json.load(f)['hotkeyOptions']['hotkeySets']
			if characterName in hotkeySets:
				self.hotkeySet = hotkeySets[characterName]
			else:
				raise Exception("Character name not found in hotkeys.")
			

	def createHotkeyBindingList(self,chatMode):
		hkList = []
		for action in self.hotkeySet[chatMode]:
			s = action['actionsetting']['action']
			
			# Checks if binding is a button in action bar
			if s.startswith('TriggerActionButton'):
				[bar, button] = [int(x) for x in re.findall('\d+', s)]

				# Looks for an actionsetting in the clientoption mappings
				for mapping in self.hotkeySet['actionBarOptions']['mappings']:
					if [bar, button] == [mapping['actionBar'], mapping['actionButton']] and 'actionsetting' in mapping.keys():
						actionsetting = mapping['actionsetting']
						hotkey = action['keysequence']

						# Appends hotkey binding
						hkList.append(HotkeyBinding(bar,button,hotkey,actionsetting))

		self.hotkeyList = hkList

	def printHotkeyList(self):
		for hk in self.hotkeyList:
			hk.print()

class HotkeyBinding:
	def __init__(self, bar, button, hotkey, action):
		self.bar = bar
		self.button = button
		self.hotkey = hotkey
		self.action = action

	def print(self):
		print('Bar %s, Button %s, Hotkey %s, Action : %s'%(self.bar, self.button, self.hotkey, self.action))

class PositionHandler:
	def __init__(self,optionsHandler):
		self.optionsHandler = optionsHandler
		self.position = self.optionsHandler.position
		
	def savePositionToFile(self):
		with open('config.json', 'r') as f:
			data = json.load(f)
			data['useroptions']['position'] = self.position
			
		with open('config.json', 'w') as f:
			json.dump(data, f)
		print ('File saved!')
		
	def moveArcsRight(self):
		self.position['axc'] += 1

	def moveArcsLeft(self):
		self.position['axc'] -= 1

	def moveArcsUp(self):
		self.position['ayc'] -= 1

	def moveArcsDown(self):
		self.position['ayc'] += 1

	def increaseArcRadius(self):
		self.position['aradius'] += 1

	def decreaseArcRadius(self):
		self.position['aradius'] -= 1

	def increaseArcWidth(self):
		self.position['awidth'] += 1

	def decreaseArcWidth(self):
		self.position['awidth'] -= 1

	def moveTextLeft(self):
		self.position['tleft'] -= 1
		self.position['tright'] -= 1

	def moveTextRight(self):
		self.position['tleft'] += 1
		self.position['tright'] += 1

	def moveTextUp(self):
		self.position['ttop'] -= 1
		self.position['tbottom'] -= 1

	def moveTextDown(self):
		self.position['ttop'] += 1
		self.position['tbottom'] += 1

	def increaseTextUpperLimit(self):
		self.position['ttop'] -= 1

	def increaseTextLowerLimit(self):
		self.position['tbottom'] += 1

	def increaseTextLeftLimit(self):
		self.position['tleft'] -= 1

	def increaseTextRightLimit(self):
		self.position['tright'] += 1

	def decreaseTextUpperLimit(self):
		self.position['ttop'] += 1

	def decreaseTextLowerLimit(self):
		self.position['tbottom'] -= 1

	def decreaseTextLeftLimit(self):
		self.position['tleft'] += 1

	def decreaseTextRightLimit(self):
		self.position['tright'] -= 1

	def increaseTextSpacing(self):
		self.position['tspc'] += 1

	def decreaseTextSpacing(self):
		self.position['tspc'] -= 1

	def moveTextToPosition(self):
		tWidth = self.position['tright'] - self.position['tleft']
		tHeight = self.position['tbottom'] - self.position['ttop']

		xc,yc = mouse.get_position()

		self.position['tleft'] = xc
		self.position['tright'] = xc + tWidth
		self.position['ttop'] = yc
		self.position['tbottom'] = yc + tHeight

	def moveArcToPosition(self):
		xc,yc = mouse.get_position()

		self.position['axc'] = xc
		self.position['ayc'] = yc

	def getTextPosition(self):
		tPosition = (self.position['tleft'], self.position['ttop'], self.position['tright'], self.position['tbottom'],self.position['tspc'])
		return tPosition
	
	def getTextSpacing(self): 
		tSpacing = self.position['tspc']
		return tSpacing
		
	def getArcPosition(self):
		aPosition = (self.position['axc'], self.position['ayc'])
		return aPosition
		
	def getArcMountedPosition(self):
		aMountedPosition = (self.position['axcm'], self.position['aycm'])
		return aMountedPosition

	def getArcProperties(self):
		aProperties = (self.position['aradius'], self.position['awidth'])
		return aProperties

	def setAsArcMountedPosition(self):
		self.position['axcm'] = self.position['axc']
		self.position['aycm'] = self.position['ayc']

class WindowHandler:
	def __init__(self,optionsHandler,equipmentList,emptyLines,positionHandler):

		self.emptyLines = emptyLines
		self.equipmentToDraw = [e for e in equipmentList if e.visible]

		# Initialize options on what do draw
		self.optionsHandler = optionsHandler
		self.updateVisibility()

		
		# Initialize positions of text and arcs
		self.positionHandler = positionHandler
		self.updatePositions()
	
		self.mounted = False
		self.setup = False

		self.hWindow = self.createWindow()
		rect = win32gui.GetClientRect(self. hWindow)
		self.setWindowSize((rect[2],rect[3]))
 
	def setupMode(self): 
		self.setup = True

	def setWindowSize(self,size):
		self.size = size

	def getWindowSize(self):
		return self.size

	def updateVisibility(self):
		# Filter what do draw
		self.groupsToDraw = [g for g in self.optionsHandler.groupList if g.visible]
		self.actionsToDraw = [a for a in self.optionsHandler.actionList if a.visible]
		self.rightArcToDraw = [a for a in self.optionsHandler.actionList if a.arcPlacement == ArcPlacement.RIGHT]
		self.leftArcToDraw = [a for a in self.optionsHandler.actionList if a.arcPlacement == ArcPlacement.LEFT]

	def updatePositions(self):
		self.setTextPosition(self.positionHandler.getTextPosition())
		self.setArcPosition(self.positionHandler.getArcPosition())
		self.setArcMountedPosition(self.positionHandler.getArcMountedPosition())
		self.setArcProperties(self.positionHandler.getArcProperties())		

	def setTextPosition(self,pos):
		self.tleft = pos[0]
		self.ttop = pos[1]
		self.tright = pos[2]
		self.tbottom = pos[3]
		self.tspc = pos[4]
		
	def setArcPosition(self,center):
		self.axc = center[0]
		self.ayc = center[1]
		
	def setArcProperties(self,properties,angle=90):
		self.aradius = properties[0]
		self.awidth = properties[1]
		self.aangle = angle
		
	def setArcMountedPosition(self,center):
		self.axcm = center[0]
		self.aycm = center[1]
		
	def changeArcPosition(self):
		if self.mounted:
			self.mounted = False
		else:
			self.mounted = True
	
	def createWindow(self):
		#get instance handle
		hInstance = win32api.GetModuleHandle()

		# the class name
		className = 'Cooldown Overlay'

		# create and initialize window class
		wndClass				= win32gui.WNDCLASS()
		wndClass.style			= win32con.CS_HREDRAW | win32con.CS_VREDRAW
		wndClass.hInstance		= hInstance
		wndClass.hIcon			= win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
		wndClass.hCursor		= win32gui.LoadCursor(None, win32con.IDC_ARROW)
		wndClass.hbrBackground	= win32gui.GetStockObject(win32con.WHITE_BRUSH)
		wndClass.lpszClassName	= className
		wndClass.lpfnWndProc	= self.wndProc

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
			
			# Update positions
			self.updatePositions()

			# Bars
			# Positions the bars
			if self.mounted:
				xc = self.axcm
				yc = self.aycm
			else:
				xc = self.axc
				yc = self.ayc

			r = self.aradius
			dr = self.awidth
			alpha = self.aangle
			
			#print(xc,yc)
			
			## Text
			# Positions the text
			pleft = self.tleft
			ptop = self.ttop
			pright = self.tright
			pbottom = self.tbottom
			spc = self.tspc
			
			#print(pleft,ptop,pright,pbottom)
			if self.setup:
				sr = alpha
				rr = r
				for _ in range(2):
					sr,rr = self.drawRightArc(hdc,(xc,yc),rr,dr,sr,1.0,ColorCode.ORANGE)

				sl = alpha
				rl = r
				for _ in range(2):
					sl,rl = self.drawLeftArc(hdc,(xc,yc),rl,dr,sl,1.0,ColorCode.ORANGE)

				for i in range(50):
					pos = (pleft,ptop+i*spc,pright,pbottom)
					self.drawTextLabel(hdc,pos,ColorCode.ORANGE,'ExampleText')
					self.drawTimerLabel(hdc,pos,ColorCode.ORANGE,float(i))

			else:
				idx = 0
				sr = alpha
				rr = r
				for idx,action in enumerate(self.rightArcToDraw):
					sr,rr = self.drawRightArc(hdc,(xc,yc),rr,dr,sr,action.getPercentage(), action.color)

				sl = alpha
				rl = r
				for idx,action in enumerate(self.leftArcToDraw):
					sl,rl = self.drawLeftArc(hdc,(xc,yc),rl,dr,sl,action.getPercentage(), action.color)

				for idx,group in enumerate(self.groupsToDraw):
					pos = (pleft,ptop+idx*spc,pright,pbottom)
					self.drawTextLabel(hdc,pos,group.color,group.labelText)
					self.drawTimerLabel(hdc,pos,group.color,group.countdown)		
				
				k=idx+2
				for idx,action in enumerate(self.actionsToDraw):
					if (idx+1) in self.emptyLines : k=k+1
					
					pos = (pleft,ptop+(idx+k)*spc,pright,pbottom)
					self.drawTextLabel(hdc,pos,action.color,action.labelText)
					self.drawTimerLabel(hdc,pos,action.color,action.countdown)

				k=k+idx+2
				for idx,equip in enumerate(self.equipmentToDraw):
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
	def __init__(self,optionsHandler,equipmentList,equipmentSlotList):
		self.optionsHandler = optionsHandler
		self.actionList = optionsHandler.actionList
		self.groupList = optionsHandler.groupList

		self.equipmentList = equipmentList
		self.equipmentSlotList = equipmentSlotList

		self.abort = False
		self.setup = False

		threading.Thread.__init__(self)
	
	def setupMode(self):
		self.setup = True

	def run(self):
		if self.setup:
			self.runSetup()
		else:
			self.runTracker()

	def runSetup(self):
		pass

	def runTracker(self):
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
	def __init__(self,optionsHandler,equipmentList,windowHandler,positionHandler,resetKey='-',mountKey='+'):
		self.optionsHandler = optionsHandler
		self.actionList = self.optionsHandler.actionList
		self.groupList = self.optionsHandler.groupList

		self.equipmentList = equipmentList
		
		self.windowHandler = windowHandler
		self.positionHandler = positionHandler
		self.resetKey = resetKey
		self.mountKey = mountKey
		self.setup = False

		threading.Thread.__init__(self)
	
	def setupMode(self):
		self.setup = True

	def runSetup(self):
		keyboard.add_hotkey('w',self.positionHandler.moveArcsUp,args=())	
		keyboard.add_hotkey('s',self.positionHandler.moveArcsDown,args=())
		keyboard.add_hotkey('a',self.positionHandler.moveArcsLeft,args=())
		keyboard.add_hotkey('d',self.positionHandler.moveArcsRight,args=())

		keyboard.add_hotkey('e',self.positionHandler.increaseArcRadius,args=())	
		keyboard.add_hotkey('ctrl+e',self.positionHandler.decreaseArcRadius,args=())
		keyboard.add_hotkey('q',self.positionHandler.increaseArcWidth,args=())
		keyboard.add_hotkey('ctrl+q',self.positionHandler.decreaseArcWidth,args=())

		keyboard.add_hotkey('up',self.positionHandler.moveTextUp,args=())	
		keyboard.add_hotkey('down',self.positionHandler.moveTextDown,args=())
		keyboard.add_hotkey('left',self.positionHandler.moveTextLeft,args=())
		keyboard.add_hotkey('right',self.positionHandler.moveTextRight,args=())

		keyboard.add_hotkey('ctrl+up',self.positionHandler.increaseTextUpperLimit,args=())	
		keyboard.add_hotkey('ctrl+down',self.positionHandler.increaseTextLowerLimit,args=())
		keyboard.add_hotkey('ctrl+left',self.positionHandler.increaseTextLeftLimit,args=())
		keyboard.add_hotkey('ctrl+right',self.positionHandler.increaseTextRightLimit,args=())

		keyboard.add_hotkey('shift+up',self.positionHandler.decreaseTextUpperLimit,args=())	
		keyboard.add_hotkey('shift+down',self.positionHandler.decreaseTextLowerLimit,args=())
		keyboard.add_hotkey('shift+left',self.positionHandler.decreaseTextLeftLimit,args=())
		keyboard.add_hotkey('shift+right',self.positionHandler.decreaseTextRightLimit,args=())

		keyboard.add_hotkey('ctrl+space',self.positionHandler.increaseTextSpacing,args=())
		keyboard.add_hotkey('shift+space',self.positionHandler.decreaseTextSpacing,args=())

		keyboard.add_hotkey('m',self.positionHandler.setAsArcMountedPosition,args=())		

		keyboard.add_hotkey('o',self.positionHandler.moveArcToPosition,args=())
		keyboard.add_hotkey('p',self.positionHandler.moveTextToPosition,args=())

		keyboard.add_hotkey('ctrl+s',self.positionHandler.savePositionToFile,args=())

		print('Arc configuration:')
		print('w,s,a,d - moves the arcs')
		print('e / ctrl+e - increases/decreases arc radius')
		print('q / ctrl+q - increases/decreases arc width')
		print('o - moves arc center to mouse position')
		print('m - sets current arc position as mounted position')

		print('\nText configuration:')
		print('arrows - moves texts position')
		print('ctrl+arrows - increases text box boundaries')
		print('shift+arrows - decreases text box boundaries')
		print('ctrl+space - increases text spacing')
		print('shift+space - decreases text spacing')
		print('p - moves top left corner of text box to mouse position')

		print('\nctrl+s - save configuration to file')

	def runTracker(self):
		keyboard.add_hotkey(self.resetKey,self.resetAllCountdowns,args=())
		keyboard.add_hotkey(self.mountKey,self.mountAction,args=())
		
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
				
				keyboard.add_hotkey(key+'+w+d',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+w+a',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+s+a',action.triggerByKey,args=())
				keyboard.add_hotkey(key+'+s+d',action.triggerByKey,args=())
				
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
	def run(self):
		if self.setup:
			self.runSetup()
		else:
			self.runTracker()
	
	def mountAction(self):
		self.windowHandler.changeArcPosition()
	
	
	def resetAllCountdowns(self):
		for action in self.actionList:
			action.resetCountdown()
			
		for group in self.groupList:
			group.resetCountdown()

class MouseTracker(threading.Thread):
	def __init__(self,optionsHandler,positionHandler):
		self.optionsHandler = optionsHandler
		self.actionList = self.optionsHandler.actionList
		self.positionHandler = positionHandler
		self.setup = False
		threading.Thread.__init__(self)

	def setupMode(self):
		self.setup = True

	def runTracker(self):
		mouse.on_right_click(lambda: self.rightClick())
		mouse.on_click(lambda: self.leftClick())

	def runSetup(self):
		pass

	def run(self):
		if self.setup:
			self.runSetup()
		else:
			self.runTracker()

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
			if action.trigger:
				pass
			else:
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
		
	def setScale(self,s):
		self.scale = s

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
		
		if self.trigger:
			self.run()
			if self.countdown<self.time:
				self.setScale(self.time)
			self.setCountdown(self.time)
			self.resetTrigger()
			#print(self.labelText+" Trigger by Action")
			
		elif self.groupTrigger:
			self.run()
			if self.countdown==0 or self.groupTime>self.scale: 
				self.setScale(self.groupTime)
			self.setCountdown(self.groupTime)
			self.resetGroupTrigger()
			#print(self.labelText+" Trigger by Group")
		
		if self.running : self.decrementCountdown(Ts)
		
		# stops timer if it runs out
		if self.running and self.countdown < Ts :
			self.resetCountdown()
			self.stop()
	
