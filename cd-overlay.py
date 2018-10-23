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

## Key to change Arcs when mounted
mountKey = '+'

## Add your tracked actions here
actionList.append(TrackedAction('Strike',ColorCode.RED,[CooldownGroup.ATTACK],ActionType.ATKREGULAR,['['],visible=False,ap=ArcPlacement.RIGHT))

# Objects
actionList.append(TrackedAction('Potion',ColorCode.PINK,[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['1'],visible=False,ap=ArcPlacement.RIGHT))

# Attack Runes
actionList.append(TrackedAction('Rune',ColorCode.rgb2hex((255,100,0)),[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,[']'],ut=UseType.CROSSHAIR,visible=False))
actionList.append(TrackedAction('SD',ColorCode.RED,[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,[';'],visible=False))
actionList.append(TrackedAction('FireWall',ColorCode.RED,[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,['shift+!'],ut=UseType.CROSSHAIR,visible=False))
actionList.append(TrackedAction('FireBomb',ColorCode.RED,[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,['shift+@'],ut=UseType.CROSSHAIR,visible=False))

# Attack Spells
actionList.append(TrackedAction('StrongIce',ColorCode.rgb2hex((0,150,255)),[CooldownGroup.ATTACK,CooldownGroup.STRONGSTRIKE],ActionType.ATKCOOLDOWN,['shift+{'],8.0,visible=False))
actionList.append(TrackedAction('StrongTerra',ColorCode.rgb2hex((0,255,137)),[CooldownGroup.ATTACK,CooldownGroup.STRONGSTRIKE],ActionType.ATKCOOLDOWN,['F9'],8.0,visible=False))

actionList.append(TrackedAction('IceWave',ColorCode.rgb2hex((0,150,255)),[CooldownGroup.ATTACK],ActionType.ATKCOOLDOWN,['shift+}'],8.0,visible=True))
actionList.append(TrackedAction('TerraWave',ColorCode.rgb2hex((0,255,137)),[CooldownGroup.ATTACK],ActionType.ATKCOOLDOWN,['F10'],4.0,visible=True))

actionList.append(TrackedAction('UltimateIce',ColorCode.rgb2hex((0,150,255)),[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F11'],30.0))
#actionList.append(TrackedAction('UltimateTerra',ColorCode.rgb2hex((0,137,255)),[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F11'],30.0))

actionList.append(TrackedAction('Ice UE',ColorCode.ORANGE,[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F12'],40.0))
#actionList.append(TrackedAction('Terra UE',ColorCode.ORANGE,[CooldownGroup.ATTACK,CooldownGroup.SPECIAL],ActionType.ATKCOOLDOWN,['F12'],40.0))

# Heal
actionList.append(TrackedAction('Exura',ColorCode.LBLUE,[CooldownGroup.HEAL],ActionType.HEALREGULAR,['3'],visible=False,ap=ArcPlacement.LEFT))
actionList.append(TrackedAction('Exura Gran',ColorCode.LBLUE,[CooldownGroup.HEAL],ActionType.HEALREGULAR,['2'],visible=False))

# Support
#actionList.append(TrackedAction('Magic Shield',ColorCode.WHITE,[CooldownGroup.SUPPORT],ActionType.SUPPORTEFFECT,['4'],200.0))
actionList.append(TrackedAction('Haste',ColorCode.GRAY,[CooldownGroup.SUPPORT],ActionType.SUPPORTEFFECT,['5'],22.0))
actionList.append(TrackedAction('MWall',ColorCode.RED,[CooldownGroup.SUPPORT,CooldownGroup.OBJECT],ActionType.ATKRUNE,['shift+#'],ut=UseType.CROSSHAIR,visible=False))

## Equipment to be tracked
# Rings
equipmentList.append(TrackedEquipment('LifeRing', ColorCode.DGREEN,[CooldownGroup.NONE],ActionType.EQUIPMENT,['F2'],1200.0,et=EquipmentType.RING))
equipmentList.append(TrackedEquipment('RingHealing', ColorCode.rgb2hex((227,115,32)),[CooldownGroup.NONE],ActionType.EQUIPMENT,['F3'],450.0,et=EquipmentType.RING))
equipmentList.append(TrackedEquipment('EnergyRing', ColorCode.LBLUE,[CooldownGroup.NONE],ActionType.EQUIPMENT,['4'],600.0,iv=355.0,et=EquipmentType.RING))
equipmentList.append(TrackedEquipment('OtherRing', ColorCode.ORANGE,[CooldownGroup.NONE],ActionType.EQUIPMENT,['F4','F5','F6','F7'],et=EquipmentType.RING,expires=False,visible=False))

## DO NOT DELETE GROUPS. IF YOU DONT WANT TO SEE IT, JUST SET 'visible=False' IN ARGUMENTS
groupList.append(TrackedGroup('Potion',ColorCode.PINK,CooldownGroup.OBJECT,1.0,visible=False))
groupList.append(TrackedGroup('Attack',ColorCode.RED,CooldownGroup.ATTACK,2.0,visible=False))
groupList.append(TrackedGroup('Healing',ColorCode.LBLUE,CooldownGroup.HEAL,1.0,visible=False))
groupList.append(TrackedGroup('Support',ColorCode.DGREEN,CooldownGroup.SUPPORT,2.0,visible=False))
groupList.append(TrackedGroup('Conjure',ColorCode.BLACK,CooldownGroup.CONJURE,2.0,visible=False))
groupList.append(TrackedGroup('Special',ColorCode.ORANGE,CooldownGroup.SPECIAL,4.0,visible=False))
groupList.append(TrackedGroup('StrongStrike',ColorCode.rgb2hex((0,150,255)),CooldownGroup.STRONGSTRIKE,8.0,visible=True))

## DO NOT DELETE EQUIPMENT SLOTS
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.RING))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.BOOTS))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.WEAPON))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.HELMET))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.SHIELD))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.ARMOR))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.LEGS))

# Separators for the tracked actions section
emptyLines = [3,5];

## Display configuration
# Text position (Left, Top, Right, Bottom, Spacing)
tleft = 1443
ttop = 108
tright = 1567
tbottom = 594
tspc = 16

# Arc Position (Xcenter, Ycenter, Radius, Width)
# normal position
axc = 944
ayc = 428
# mounted position
axcm = 944+16
aycm = 428+15

aradius = 171
awidth = 6

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
	windowHandler = WindowHandler(actionList,groupList,equipmentList,emptyLines)
	windowHandler.setTextPosition((tleft,ttop,tright,tbottom),tspc)
	windowHandler.setArcPosition((axc,ayc))
	windowHandler.setArcMountedPosition((axcm,aycm))
	windowHandler.setArcProperties(aradius,awidth)

	# Create threads
	# Thread that detects keyboard hotkeys
	tHotkeyTracker = HotkeyTracker(actionList,equipmentList,groupList,windowHandler,resetKey,mountKey)
	tHotkeyTracker.start()

	# Thread that detects mouse buttons
	tMouseTracker = MouseTracker(actionList)
	tMouseTracker.start()
	
	# Thread that tracks actions
	tActionTracker = ActionTracker(actionList,equipmentList,groupList,equipmentSlotList)
	tActionTracker.start()

	try:
		while(True):
			win32gui.RedrawWindow(windowHandler.hWindow, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)
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

		win32gui.DestroyWindow(windowHandler.hWindow)
		print("Overlay window destroyed")
		print("Closing...")	

if __name__ == '__main__':
	main()
