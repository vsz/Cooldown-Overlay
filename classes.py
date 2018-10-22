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
	
	def __init__(self,lt,color,cg,at,keys,t=0.0,iv=0.0,et=EquipmentType.NONE,ut=UseType.TARGET,visible=True):
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
		
	def __str__(self):
		stringKey = ""
		for key in self.keys:
			stringKey = stringKey + key + " "
		return (self.labelText + " tracked on hotkey(s) " + stringKey)

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
	
