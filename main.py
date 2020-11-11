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
power_value = False

# some global variables that need to change as we run the program
#chan0 = None			# ldr
chan1 = None			# temp sensor
tick = time.localtime()	#time.time()		# for runtime calculatons
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
	GPIO.setup(, GPIO.OUT)
	led = GPIO.PWM(, 100)

	# setup buzzer
	GPIO.setup(, GPIO.OUT)
	buzzer = GPIO.PWM(, 50)

	# setup the buttons
	GPIO.setup(power_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(rate_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	# add action listeners for the button
	GPIO.add_event_detect(power_button, GPIO.RISING, callback=power, bouncetime=300)
	GPIO.add_event_detect(rate_button, GPIO.RISING, callback=change_sampling_rate, bouncetime=300)



# enable and disable
def power(channel):
	#print("POWER")
	global power_value
	global thread
	global tick

	tick = time.localtime()

	if (power_value):
		# stop thread and clear screen
		thread.cancel()
		thread.join()
	else:
    	print("Time\tSys Timer\tTemp\tBuzzer")
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
	tick = time.localtime()

	# stop: cancel, join
	thread.cancel()
	thread.join()

	# start thread again
	my_thread()



def calculate_temperature():
	global chan

	# get the voltage
	voltage = chan.voltage

	# get the value
	value = chan.value

	# convert to temperature
	temperature = (voltage * (value / 1023) - 0.5) / 0.01

	# return voltage and temperature
	return voltage, temperature


def get_runtime():
	global tick

	# calculate runtime
	current_time = time.localtime()	#time.time()
	tock = current_time - tick

	# return runtime
	return current_time, sys_timer


def fetch_data(start, temp_count):
	temp_list = eeprom.read_block(start, step_count * 4)
	temperatures = [[0]*2]*0
	for i in range(0, temp_count):
		entry = []
		for j in range(0, 4):
			entry.append(temp_list[4*i+j])
		temperaures.append(entry)
	return temperatures


def update_eeprom(new_reading):
	global eeprom

	# get however many temperatures there are
	temp_count = eeprom.read_byte(0)

	temperatures = None

	if temp_count == 0:
		temperaturs = [[0]*2]*0			# initialise an empty 2d list
	elif temp > 0 and temp < 20:
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

	for reading in temperature:
		for item in reading:
			data_to_write.append(item)
	eeprom.write_block(1, data_to_write)


# runtime thread
def my_thread():
	global thread
	#global tick
	#global chan0
	global chan1

	# set timer and start the thread
	thread = threading.Timer(sampling_rate, mythread)
	thread.daemon = True
	thread.start()

	# get runtime and temperature
	a, b = get_runtime()
	voltage, temperature = calculate_temperature()
	#value = chan.value

	current_time = datetime.strptime("%H:%M:%S", a)
	sys_timer = datetime.strptime("%H:%M:%S", b)

	hour = datetime.strptime("%H", a)
	minute = datetime.strptime("%M", a)

	new_reading = [hour, minute, voltage, temperature]
	update_eeprom(new_reading)

	# display
	print("%s\t\t%s\t\t\t%.2f C" %(current_time, sys_timer, temperature))



if __name__ == "__main__":
	global led
	global buzzer
	global eeprom

	try:
		eeprom.write_block(0, 0)
		setup()
		#print("Time\tSys Timer\tTemp\tBuzzer")
		#my_thread()

		while True:
			pass

	except Exception as e:
		pass
	finally:
		#buzzer.stop()
		#led.stop()
		GPIO.cleanup()
