import utils
import os
import time
import threading
import busio
import digitalio
import board
import socket
import blynklib
import blynktimer
import RPi.GPIO as GPIO
from datetime import datetime
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# some global variables that are set once
eeprom = utils.utils()
power_button = 23
rate_button = 25

# some global variables that need to change as we run the program
chan1 = None			# temp sensor
tick = datetime.now()	# for runtime calculatons
sampling_rate = 5.0		# default sampling rate
power_value = True		# used to check if the system is logging
buzzer_counter = 0		# checked to trigger the buzzer

# blynk authorization code
BLYNK_AUTH = 'goHQikL3hfv-uYQcrgAl0iFkM5_0Y_uZ'


# create timer and blynk objects
blynk = blynklib.Blynk(BLYNK_AUTH)
timer = blynktimer.Timer()

# setup pins and EEProm
def setup():
	global blynk
	global chan1
	global power_button
	global rate_button
	global eeprom
	global BLYNK_AUTH

	eeprom.write_block(0, [0])

	# create the spi bus
	spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

	# create the cs (chip select)
	cs = digitalio.DigitalInOut(board.D5)

	# create the mcp object
	mcp = MCP.MCP3008(spi, cs)

	# create an analog input channel on pin 1
	chan1 = AnalogIn(mcp, MCP.P1)

	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)



# enable and disable
def power(channel):
	global power_value
	global buzzer_counter
	global tick
	global timer

	# generate new sys_timer
	tick = datetime.now()

	if (power_value == True):
		# stop timer and clear screen
		timer.cancel()
		timer.join()
		power_value = False
		os.system('clear')
		print("The logging has stopped..\nPress power button to continue sampling")
	else:
		print("Time\t\tSys Timer\tTemp\t\tBuzzer")
		power_value = True
		buzzer_counter = 0
		timer.run()			#start timer


# change sampling rate
def change_sampling_rate(channel):
	global sampling_rate
	global tick
	global buzzer_counter
	global timer

	# change sampling rate
	if sampling_rate == 2.0:
		sampling_rate = 5.0
	elif sampling_rate == 5.0:
		sampling_rate = 10.0
	else:
		sampling_rate = 2.0

	# reset timer
	tick = datetime.now()

	# stop: cancel, join
	timer.cancel()
	timer.join()

	# timer with new sampling rate
	timer.set_interval(sampling_rate, virtual_pin_handler)

	# start timer again
	timer.run()



# get temperature, value an voltage from sensor
def calculate_temperature():
	global chan1

	# get the voltage
	voltage = chan1.voltage

	# get the value
	value = chan1.value

	# convert to temperature
	temperature = (voltage-0.5)/0.01

	# return voltage and temperature
	return value, voltage, temperature



# get a valid time
def diff(h, m, s):

	if s < 0:					# check if seconds are < 0
		s = 60 + s				# take 1 from minute and convert to 60 seconds
		if m < 0:				# check if minutes are < 0
			m =  59 + m			# minutes are m-1 because seconds < 0
			if h < 0:			# check if hour is < 0
				h = 23 + h		# hour is h-1 because minutes < 0
			else:
				h = h - 1
		else:
			m = m - 1
			if h < 0:
				h = 24 + h
	else:
		if m < 0:
			m = 60 + m			# borrow 60 minute from hour
			if h < 0:
				h = 23 + h
			else:
				h = h - 1
		else:
			if h < 0:
				h = 24 + h

	tock = str(h) +":"+str(m)+":"+str(s)	# return time in HH:MM:SS format
	return tock



# calculate sys_timer
def get_runtime():
	global tick

	# get current time
	current_time = datetime.now()

	# calculate systimer
	h = int(current_time.strftime("%H")) - int(tick.strftime("%H"))
	m = int(current_time.strftime("%M")) - int(tick.strftime("%M"))
	s = int(current_time.strftime("%S")) - int(tick.strftime("%S"))

	# get a valid time
	tock = diff(h, m,s)
	sys_timer = datetime.strptime(tock, "%H:%M:%S")

	return current_time, sys_timer



# fetch data from eeprom
def fetch_data(start, temp_count):
	temp_list = eeprom.read_block(start, temp_count * 20)		# a single reading consists of 20 characters
	temperatures = [[0]*2]*0									# create a 2d empty list
	for i in range(0, temp_count):
		entry = []												# store a reading (with 20 characters)
		for j in range(0, 20):
			if chr(temp_list[20*i+j]) != '\x00':				# don't take item having \x00
				entry.append(chr(temp_list[20*i+j]))
		if entry != []:											# don't add empty lists
			temperatures.append(entry)

	return temperatures											# return list containing readings




''' calls methods 'fetch_data' and save_data to
	get data and save data from and to respectively.
	checks the number of readings in the eeprom
	if number is 0:
		- an empty 2d list is created
	elif number between 1 and 19 (inclusive)
		- all readings are fetched from the eeprom
	else
		- the last 19 reading are fetched from the eeprom
	adds new reading to list and
	call 'save_data' method to write to eeprom
'''
def update_eeprom(new_reading):
	global eeprom

	# get however many temperatures there are
	temp_count = eeprom.read_byte(0)

	temperatures = None

	if temp_count == 0:
		temperatures = [[0]*2]*0			# initialise an empty 2d list
	elif temp_count > 0 and temp_count < 20:
		temperatures = fetch_data(1, temp_count)	# get all temperatures
	else:
		temperatures = fetch_data(2, temp_count)	# get last 19 temperatures

	temperatures.append(new_reading)

	save_data(temp_count, temperatures)



# write data to eeprom
def save_data(temp_count, temperatures):
	temp_count = temp_count + 1
	eeprom.write_block(0, [temp_count])			# used to check the number of readings
	data_to_write = []							# store in a 1d list

	for reading in temperatures:
		for item in reading:
			data_to_write.append(ord(item))
	eeprom.write_block(1, data_to_write)		# write to eeprom



@timer.register(vpin_num=11, interval=sampling_rate, run_once=False)
def virtual_pin_handle(vpin_num):
	global blynk
	global sampling_rate
	global buzzer_counter

	# get systimer, voltage and temperature
	a, b = get_runtime()
	value, voltage, temperature = calculate_temperature()
	value = str(value)

	# get the time in HH:MH:SS format
	current_time = a.strftime("%H:%M:%S")
	sys_timer = b.strftime("%H:%M:%S")

	# store current time , value from sensor, voltage and temperature
	new_reading = []

	# apend current time
	for c in range(0, len(current_time)):
		new_reading.append(current_time[c])

	# append value from the sensor
	for q in range(0, len(value)):
		new_reading.append(value[q])

	# round coltage to 1 decimal place and append to list
	volt = str(round(voltage, 1))
	for v in range(0, len(volt)):
		new_reading.append(volt[v])

	# round temperature to 2 decimal places and append to list
	temp = str(round(temperature, 2))
	if temp[2] == ".":						# check if there are 2 digits before decimal point
		new_reading.append(temp[0])
		new_reading.append(temp[1])
		new_reading.append(temp[3])
		if len(temp) == 5:					# check if there are 2 values after decimal point
			new_reading.append(temp[4])
		else:
			new_reading.append("0")			# add 0 at the end for number to have 2 decimal places
	else:
		new_reading.append("0")				# add 0 at the beginning for number to have 2 digits before decimal point
		new_reading.append(temp[0])
		new_reading.append(temp[2])
		if len(temp) == 4:
			new_reading.append(temp[3])
		else:
			new_reading.append("0")

	# add new reading to eeprom
	update_eeprom(new_reading)

	''' display results to blynk terminal, and gauge
		and check if:
			- this is the first reading or
			- this reading is a multiple of 5
	'''
	if buzzer_counter == 0 or buzzer_counter % 5 == 0:
		print_str = current_time+" "+sys_timer+" "+round(temperature, 2)+" C "
		blynk.virtual_write(6, print_str)	# terminal
	else:
		print_str = current_time+" "+sys_timer+" "+round(temperature, 2)+" C"
		blynk.virtual_write(6, print_str)

	buzzer_counter = buzzer_counter + 1
	blynk.virtual_write(11, round(temperature, 2))	# update gauge



def clean():
	GPIO.cleanup()



if __name__ == "__main__":
	try:
		setup()
		print("Time\t\tSys Timer\tTemp\t\tBuzzer")
		while True:
			blynk.run()
			timer.run()
	except KeyboardInterrupt as k:
		print(" ")
	except Exception as e:
		print(e)
	finally:
		clean()
