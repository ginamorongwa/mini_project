MINI PROJECT A/B
----------------
Objective for Mini-Project A environment logger. Mini-Project B is an add-on to
Mini-Project A which involves minimal work to extend the functionality of the monitoring
system. <br/>

Generally speaking, an environment logger interacts with the world around it by measuring
various factors from GPS location to air pollution. While a single sensor is useful to monitor
a single location, many can be scattered around a broader area to monitor that area as well
as any patterns emerging in that broader area. This data can be used to track changes over
time to forecast effects or make inferences between locations and how they might affect each
other. In these mini-projects there is not much data to track and there arent many potential
effects to forecast, though the principles remains the same. <br/>

Project A and B differ in how that data is presented to end users. Project A is simply accessed
through a terminal. Project B will add reporting data to Blynk, an app that can be installed
on smartphones. The environment logger can also be controlled via the Blynk app.

INSTALL LIBRARIES
-----------------
$ sudo apt-get update <br/>
$ sudo apt install python3-pip <br/>
$ sudo apt-get install python3-rpi.gpio <br/>
$ sudo pip3 install smbus2 <br/>
$ sudo apt install build-essential python3-dev python3-smbus python3-pip <br/>
$ sudo pip3 install adafruit-circuitpython-mcp3xxx <br/>
blynk: lib-python/README.md


RUN
---
project A: <br/>
	- python3 main.py <br/>
project B: <br/>
	- python3 blynk_main.py <br/>


DIRECTORY STRUCTURE
-----------------
/MiniProject <br/>
	Directory: <br/>
	/lib-python <br/>
	
	Files: <br/>
	/README.md <br/>
	/blynk_main.py <br/>
	/main.py <br/>
	/utils.py <br/>

FILE STRUCTURE
--------------
utils.py: <br/>
	contains methods to read and write from and to EEPROM <br/><br/>
	used by both main and blynk_main <br/>
main.py: <br/>
	contains main method for project A <br/>
	call a mthod that starts a Timer thread <br/>
blynk_main.py: <br/>
	contains main method for project B <br/>
	starts blynk thread and <br/>
	blynktimer thread <br/>
