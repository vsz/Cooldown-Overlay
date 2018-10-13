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

class TextColor:		
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

class UseType(Enum):
	TARGET = 1
	CROSSHAIR = 2

class ActionTracker(threading.Thread):
	def __init__(self,actionList,groupList):
		self.actionList = actionList
		self.groupList = groupList
		self.abort = False
		threading.Thread.__init__(self)
		
	def run(self):
		# Window and Timer update period
		Ts = 0.05
		
		# Initialize
		for group in self.groupList:
			group.setActionList(self.actionList)
			
		ctime1 = datetime.datetime.now()
		
		while(not self.abort) :
			# Tracks ellapsed time
			ctime2 = datetime.datetime.now()
			delta = ctime2-ctime1
			ctime1 = ctime2
			et = delta.seconds+0.000001*delta.microseconds
			
			#print(et)
			for group in self.groupList :
				group.track(et)
			
			for action in self.actionList :
				action.track(et)
				
			time.sleep(Ts)

class HotkeyTracker(threading.Thread):
	def __init__(self,actionList,groupList,resetKey='-'):
		self.actionList = actionList
		self.groupList = groupList
		self.resetKey = resetKey
		threading.Thread.__init__(self)
		
	def run(self):
		keyboard.add_hotkey(self.resetKey,self.resetAllCountdowns,args=())
		
		for action in self.actionList:
			for key in action.keys:
				keyboard.add_hotkey(key,action.triggerByKey,args=())
				
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
	
class TrackedAction:
	
	def __init__(self,lt,color,cg,at,keys,t=0.0,iv=0.0,modifiers=[],ut=UseType.TARGET,visible=True):
		self.labelText = lt
		self.color = color
		self.cooldownGroups = cg
		self.actionType = at
		self.keys = keys
		self.modifiers = modifiers
		self.time = t
		self.groupTime = 0.0
		self.countdown = iv
		self.trigger = False
		self.groupTrigger = False
		self.running = False
		self.useType = ut
		self.armed = False
		self.visible = visible
		print(self.labelText + " " + str(self.useType))
		
	def __str__(self):
		return self.labelText

	def setTime(self,time):
		self.time = max(self.time,time)
	
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
	
	def resetCountdown(self):
		self.countdown = 0.0

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
	
