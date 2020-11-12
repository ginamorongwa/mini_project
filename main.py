import utils
import os
import time
import threading
import busio
import digitalio
import board
import RPi.GPIO as GPIO
from datetime import datetime
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

eeprom = utils.utils()
power_button = 23
rate_button = 24
buzzer = None
led = None
power_value = True

# some global variables that need to change as we run the program
#chan0 = None			# ldr
chan1 = None			# temp sensor
tick = datetime.now()	#time.localtime()	#time.time()		# for runtime calculatons
sampling_rate = 5.0		# default sampling rate
thread = None			# thread changed if the sampling rate is changed


# setup pins and EEProm
def setup():
	global buzzer
	global led
	#global chan0
	global chan1
	global power_button
	global rate_button
	global eeprom

	eeprom.write_block(0, [0])
	#time.sleep(1)

	# create the spi bus
	spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

	# create the cs (chip select)
	cs = digitalio.DigitalInOut(board.D5)

	# create the mcp object
	mcp = MCP.MCP3008(spi, cs)

	# create an analog input channel on pin 0 & 1
	#chan0 = AnalogIn(mcp, MCP.P0)
	chan1 = AnalogIn(mcp, MCP.P1)

	# setup led
	GPIO.setup(12, GPIO.OUT)
	led = GPIO.PWM(12, 100)

	# setup buzzer
	GPIO.setup(13, GPIO.OUT)
	buzzer = GPIO.PWM(13, 50)

	# setup the buttons
	GPIO.setup(power_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(rate_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	# add action listeners for the button
	GPIO.add_event_detect(power_button, GPIO.FALLING, callback=power, bouncetime=300)
	GPIO.add_event_detect(rate_button, GPIO.FALLING, callback=change_sampling_rate, bouncetime=300)



# enable and disable
def power(channel):
	print("POWER")
	global power_value
	global thread
	global tick

	tick = datetime.now()	#time.localtime()

	if (power_value):
		# stop thread and clear screen
		thread.cancel()
		thread.join()
		power_value = False
	else:
		print("Time\t\tSys Timer\tTemp\t\tBuzzer")
		power_value = True
		my_thread()

# change sampling rate
def change_sampling_rate(channel):
	power("SAMPLING RATE")
	global sampling_rate
	global thread
	global tick

	# change sampling rate
	if sampling_rate == 1.0:
		sampling_rate = 5.0
	elif sampling_rate == 5.0:
		sampling_rate = 10.0
	else:
		sampling_rate = 1.0

	# reset timer
	tick = datetime.now()	#time.localtime()

	# stop: cancel, join
	thread.cancel()
	thread.join()

	# start thread again
	my_thread()



def calculate_temperature():
	global chan1

	# get the voltage
	voltage = chan1.voltage

	# get the value
	value = chan1.value

	# convert to temperature
	temperature = (voltage-0.5)/0.01	#(voltage * (value / 1023) - 0.5) / 0.01

	# return voltage and temperature
	return voltage, temperature


def diff(h, m, s):

	if s < 0:
		s = 60 + s
		if m < 0:
			m =  59 + m
			if h < 0:
				h = 23 + h
			else:
				h = h - 1
		else:
			m = m - 1
			if h < 0:
				h = 24 + h
	else:
		if m < 0:
			m = 60 + m
			if h < 0:
				h = 23 + h
			else:
				h = h - 1
		else:
			#m = m - 1
			if h < 0:
				h = 24 + h

	tock = str(h) +":"+str(m)+":"+str(s)
	return tock


def get_runtime():
	global tick

	# calculate runtime
	current_time = datetime.now()

	h = int(current_time.strftime("%H")) - int(tick.strftime("%H"))
	m = int(current_time.strftime("%M")) - int(tick.strftime("%M"))
	s = int(current_time.strftime("%S")) - int(tick.strftime("%S"))

	tock = diff(h, m, s)	#str(h) +":"+str(m)+":"+str(s)
	sys_timer = datetime.strptime(tock, "%H:%M:%S")
	#print("tick:",tick)
	#print("current_time:",current_time)
	#print("tock:",tock)
	#time.localtime()	#time.time()
	#a = datetime.strftime("%H", time.gmtime())	#
	#b = current_time.strftime("%B")
	#print(current_time)
	#print(b)
	return current_time, sys_timer
"""
	h = int(datetime.strftime("%H", current_time)) - int(datetime.strftime("%H", tick))
	m = int(datetime.strftime("%M", current_time)) - int(datetime.strftime("%M", tick))
	s = int(datetime.strftime("%S", current_time)) - int(datetime.strftime("%S", tick))

	tock = str(h) +":"+str(m)+":"+str(s)
	sys_timer = datetime.strptime(tock, "%H:%M:%S")

	#tock = current_time - tick

	# return runtime
	return current_time, sys_timer
"""

def fetch_data(start, temp_count):
	temp_list = eeprom.read_block(start, temp_count * 4)
	temperatures = [[0]*2]*0
	for i in range(0, temp_count):
		entry = []
		for j in range(0, 4):
			#print(chr(temp_list[4*i+j]))
			entry.append(chr(temp_list[4*i+j]))
		temperatures.append(entry)
	return temperatures


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
	#temp_count = temp_count + 1
	save_data(temp_count, temperatures)


def save_data(temp_count, temperatures):
	temp_count = temp_count + 1
	eeprom.write_block(0, [temp_count])
	data_to_write = []

	for reading in temperatures:
		for item in reading:
			data_to_write.append(ord(item))
	eeprom.write_block(1, data_to_write)


# runtime thread
def my_thread():
	global thread
	#global tick
	#global chan0
	#global chan1

	# set timer and start the thread
	thread = threading.Timer(sampling_rate, my_thread)
	thread.daemon = True
	thread.start()

	# get runtime and temperature
	a, b = get_runtime()
	voltage, temperature = calculate_temperature()
	#value = chan.value

	current_time = a.strftime("%H:%M:%S")
	sys_timer = b.strftime("%H:%M:%S")

	#hour = a.strftime("%H")
	#minute = a.strftime("%M")


	temp = str(round(temperature, 2))
	#print(temp)
	new_reading = []
	if temp[2] == ".":
		new_reading.append(temp[0])
		new_reading.append(temp[1])
		new_reading.append(temp[3])
		if len(temp) == 5:
			new_reading.append(temp[4])
		else:
			new_reading.append("0")
	else:
		new_reading.append("0")
		new_reading.append(temp[0])
		new_reading.append(temp[2])
		if len(temp) == 4:
			new_reading.append(temp[3])
		else:
			new_reading.append("0")
	#new_reading = [hour, minute, voltage, temperature]
	update_eeprom(new_reading)
	#print(str(chan1.value)+" "+str(voltage)+" "+ str((voltage-0.5)/0.01))
	# display
	print("%s\t%s\t%.2f C" %(current_time, sys_timer, temperature))

def clean():
	global led
	global buzzer
	global eeprom

	led.stop()
	buzzer.stop()
	eeprom.clear(4096)
	GPIO.cleanup()



if __name__ == "__main__":
	try:
		setup()
		print("Time\t\tSys Timer\tTemp\t\tBuzzer")
		my_thread()

		while True:
			pass
	except KeyboardInterrupt as k:
		print(" ")
	except OSError as o:
		print(" ")
	except Exception as e:
		print(e)
	finally:
		clean()
