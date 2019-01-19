# Cooldown-Overlay
This script was made to be used with the Tibia Client. It tracks individual and group cooldowns and spell effect duration and prints it on the screen as an overlay. The overlay is transparent and you cannot interact with it with your mouse.

To use the script, some basic Python and programming is desirable, but not necessary. You only need to configure your hotkeys once and run the script whenever you want to play the game.

# Features
* Transparent window
* Text color selection
* Key modifiers for hotkeys: Control ('control'), Shift ('shift'), Alt ('alt')
* Support for actions used with crosshairs, timers only start after a left click
* Support for cooldown groups

# Configuration
## Action configuration
Actions are added to tracked list using:

actionList.append(TrackedAction(text,color,cooldownGroups,actionType,keys,time,initialValue,useType,visibility))
* **text** 
	* The text to be displayed left of the timer. 
	* Expected format - example : string - 'ActionName'
	* Can be pretty much anything inside ''
	
* **color** 
	* The color of the text and timer. 
	* Expected format - example : Class TextColor.COLOR - TextColor.BLACK
	* Possible options:
		* TextColor.BLACK
		* TextColor.BLUE
		* TextColor.RED
		* TextColor.GREEN
		* TextColor.WHITE
		* TextColor.PINK
		* TextColor.DGREENGRAY
		* TextColor.ORANGE
		* You can add your own by using TextColor.rgb2hex(R,G,B), where R,G,B range between 0 and 255.		
	
* **cooldownGroups** 
	* Groups activated by hotkey.
	* Expected format - example : List of Class CooldownGroup.GROUP - [CooldownGroup.OBJECT,CooldownGroup.ATTACK]
	* Possible options:
		* CooldownGroup.OBJECT
		* CooldownGroup.ATTACK
		* CooldownGroup.HEAL
		* CooldownGroup.SUPPORT
		* CooldownGroup.SPECIAL
		* CooldownGroup.CONJURE
		* CooldownGroup.NONE
			
* **actionType**
	* Type of action. Currently Not supported
	* Expected format - example : Class ActionType - ActionType.CONSUMABLE
	* I will expand on this when I implement it. If you are curious you can check the class ActionType in classes.py
	
* **keys** 
	* Hotkeys configured for action.
	* Expected format - example : List of string - ['1','F1']
	* You can set the variable debug = True on the first lins of the code to have your keypresses be printed on the command prompt. It is useful to configure your hotkeys on the overlay.
	
* **time**
	* Time for the action. Can be cooldown or effect duration. If it is a simple object or attack, does not need to be configured for regular spells, just for actions with larger cooldowns (like special spells) and for spells you want to track duration.
	* Expected format - example : float - 3.0
	
* **initialValue**
	* Timer initial value. Currently not supported but will be used for tracking rings and such.
	* Expected format - example : float - 2.1
	
* **useType**
	* Type of use, can be either 'on target' or 'with crosshair'. By default is set to use 'on target'
	* Expected format - example : Class UseType - UseType.CROSSHAIR
	* Possible options:
		* UseType.TARGET
		* UseType.CROSSHAIR
	
* **visibility**
	* Determines if the action is displayed on screen or not. Can be set to True or False. By default, visibility is set to True.
	* Expected format - example : boolean - True
	

Some examples:

**actionList.append(TrackedAction('Potion',TextColor.PINK,[CooldownGroup.OBJECT],ActionType.CONSUMABLE,['1','2'],t=1.0,iv=0.5,ut=UseType.TARGET,visible=True))**
* Text is Potion, displayed in pink.
* Triggers items cooldown group with hotkey '1' OR '2'.
* Timer is reset to 1.0 and has initial value of 0.5 on first use. 
* It is used on target and is displayed on screen.

**actionList.append(TrackedAction('StrongWave',TextColor.RED,[CooldownGroup.ATTACK],ActionType.ATKCOOLDOWN,['F1'],8.0,modifiers=['Lshift']))**
* Text is StrongWave, displayed in red.
* Triggers attack cooldown group with hotkey LeftShift + 'F1' (See last argument modifiers)
* Timer is reset to 8.0, no initial value specified.
* By default, visible is set to True and UseType is set to TARGET, so the action is displayed on screen and is used on target.

**actionList.append(TrackedAction('AoE Rune',TextColor.DGREEN,[CooldownGroup.ATTACK,CooldownGroup.OBJECT],ActionType.ATKRUNE,['3'],ut=UseType.CROSSHAIR,visible=False))**
* Text is AoE Rune, displayed in dark green.
* Triggers attack and item group cooldown with hotkey '3'.
* Timer is not set to any specific values, so group cooldown applies only. No initial value is specified either so by default it is set to 0.0
* UseType is set to CROSSHAIR, meaning the timer will only trigger if the hotkey press is followed by a Left Mouse Click. Timer is not triggered if the hotkey press is followed by a Right Mouse Click.
* Visibility is set to False, but using the hotkey followed by the Left Mouse Click will trigger both the Attack and Item group cooldown.

## Group configuration
Groups are always tracked, and can be set to be visible or not using the 'visible' input argument.
Examples of visible and not visible group:  
**groupList.append(TrackedGroup('Healing',TextColor.LBLUE,CooldownGroup.HEAL,1.0))**  
**groupList.append(TrackedGroup('Support',TextColor.DGREEN,CooldownGroup.SUPPORT,2.0,visible=False))**

# Running the script
1. Download the latest release zip file. Unzip it to a local folder.
1. To run the script, you'll need to have python3 installed, as well as two libraries: pywin32 and pyhooked.
	1. It is recommended that you install pip to manage your libraries. If you have pip installed, you can open the command line, navigate to the script folder and type 'pip install -r requirements.txt' to get the correct versions of the libraries used to run the script.
1. After installing python3 and the required libraries, open the command prompt, navigate to the script folder and type 'python cd-overlay.py'
	1. To configure placement of text and arc on screen, run the overlay on setup mode using 'python cd-overlay.py setup'
1. Enjoy! You can also create shortcuts in the script folder with the same commands you use to execute the script on the command prompt.



# Development Roadmap
* Hotkey for resetting all timers
* Improve keypress detection with modifiers
* Hotkey for hiding the overlay
* Support for wearable items
* Persistent timers
* Timers for bosses

# Contact
For suggestions and questions, send a PM to /u/bunkbedlover on Reddit.
