from classes import *
		
def setupMode():
	print('Setup Mode: For best results, switch to Nobleman or Noblewoman')
	print('Position your mouse on the bottom right corner of their hair')
	print("Press 'Tab' to see the coords, 'Space' to set them, 'R' to set the radius")
	print('For radius, position the cursor on the outer edge of the HP arc as close to the centre as possible')
	print("Press 'S' to save and 'Esc' to quit")
	config = ''
	while(True):
		s = keyboard.read_hotkey(suppress=False)
		#get coords of mouse and set as x,y
		x,y = mouse.get_position()
		#tab for testing/figuring out
		if s ==('tab'):
			print('X:',x ,' Y:',y)
			s = ''
		#sets the x,y for the centre of the circle	
		if s == ('space'):
			xSaved = x
			ySaved = y
			config = {"X": xSaved, "Y": ySaved}
			print(config)
			s = ''
		#determines the radius based on the ingame HUD	
		if s == ('r'):
			radius = xSaved - x
			config['R'] = radius
			print(config)
			s = ''
		#saves box top left x,y
		if s == ('b'):
			config['TLX'] = x
			config['TLY'] = y
			print(config)
			s = ''
		#saves box bottom right x,y
		if s == ('n'):
			config['BRX'] = x
			config['BRY'] = y
			print(config)
			s = ''
		#saves settings	
		if s == ('s'):
			if config == '':
				print("Config is empty!")
			else: 
				setupMode2 = SetupMode()
				setupMode2.writeJSON(config)
				print('Settings saved!')
		#closes setup		
		if s == ('esc'):
			print('Closing program in 3 seconds')
			time.sleep(3)
			exit()

def main():
	setupMode()
	
if __name__ == '__main__':
	main()