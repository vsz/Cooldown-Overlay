from classes import *

# Initialize
actionList = []
groupList = []
equipmentList = []
equipmentSlotList = []

## Key to reset all countdowns
resetKey = '-'

## Key to change Arcs when mounted
mountKey = '='

## DO NOT DELETE EQUIPMENT SLOTS
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.RING))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.BOOTS))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.WEAPON))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.HELMET))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.SHIELD))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.ARMOR))
equipmentSlotList.append(TrackedEquipmentSlot(EquipmentType.LEGS))

# Separators for the tracked actions section
emptyLines = []

def debugMode():
	print('Debug Mode: press hotkeys to see how to add them in the script')
	while(True):
		s = keyboard.read_hotkey(suppress=False)
		print(s)

def main(options):
	# Checks for flag
	if len(options) > 1:			
		charName = options[1]
		setup = False
	else:
		print("Starting in setup mode.")
		charName = "Knight"
		setup = True

	# Parse configs
	optionsHandler = OptionsHandler(charName)

	# Create position handler
	positionHandler = PositionHandler(optionsHandler)

	# Create transparent window
	windowHandler = WindowHandler(optionsHandler,equipmentList,emptyLines, positionHandler)

	# Thread that detects keyboard hotkeys
	tHotkeyTracker = HotkeyTracker(optionsHandler,equipmentList,windowHandler,positionHandler,resetKey,mountKey)

	# Thread that detects mouse buttons
	tMouseTracker = MouseTracker(optionsHandler,positionHandler)

	# Thread that tracks actions
	tActionTracker = ActionTracker(optionsHandler,equipmentList,equipmentSlotList)
	
	# Setup mode
	if setup:
		windowHandler.setupMode()
		tMouseTracker.setupMode()
		tHotkeyTracker.setupMode()
		tActionTracker.setupMode()

	# Start threads
	tMouseTracker.start()
	tHotkeyTracker.start()
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
	main(sys.argv)
