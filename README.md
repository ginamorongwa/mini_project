MINI PROJECT A/B
----------------

INSTALL LIBRARIES
-----------------
sudo apt-get update
sudo apt install python3-pip
sudo apt-get install python3-rpi.gpio
sudo pip3 install smbus2
sudo apt install build-essential python3-dev python3-smbus python3-pip
sudo pip3 install adafruit-circuitpython-mcp3xxx
blynk: lib-python/README.md


RUN
---
project A:
	- python3 main.py
project B:
	- python3 blynk_main.py


DIRECTORY STRUCTURE
-----------------
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
