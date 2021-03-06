<pre>
MINI PROJECT A/B
----------------
Objective for Mini-Project A environment logger. Mini-Project B is an add-on to
Mini-Project A which involves minimal work to extend the functionality of the monitoring
system.

Generally speaking, an environment logger interacts with the world around it by measuring
various factors from GPS location to air pollution. While a single sensor is useful to monitor
a single location, many can be scattered around a broader area to monitor that area as well
as any patterns emerging in that broader area. This data can be used to track changes over
time to forecast effects or make inferences between locations and how they might affect each
other. In these mini-projects there is not much data to track and there arent many potential
effects to forecast, though the principles remains the same.

Project A and B differ in how that data is presented to end users. Project A is simply accessed
through a terminal. Project B will add reporting data to Blynk, an app that can be installed
on smartphones. The environment logger can also be controlled via the Blynk app.


INSTALL LIBRARIES
-----------------
$ sudo apt-get update
$ sudo apt install python3-pip
$ sudo apt-get install python3-rpi.gpio
$ sudo pip3 install smbus2
$ sudo apt install build-essential python3-dev python3-smbus python3-pip
$ sudo pip3 install adafruit-circuitpython-mcp3xxx
blynk: lib-python/README.md


RUN
---
project A:
	- python3 main.py
project B:
	- python3 blynk_main.py


DIRECTORY STRUCTURE
-------------------
/MiniProject
	Directory:
	/lib-python
	
	Files:
	/README.md
	/blynk_main.py
	/main.py
	/utils.py


FILE STRUCTURE
--------------
utils.py: 
	contains methods to read and write from and to EEPROM
	used by both main and blynk_main
main.py:
	contains main method for project A
	call a mthod that starts a Timer thread
blynk_main.py:
	contains main method for project B
	starts blynk thread and
	blynktimer thread
</pre>
