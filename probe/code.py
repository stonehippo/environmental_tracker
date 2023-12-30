import os
import board
import busio
import wifi
import socketpool
import adafruit_requests
import ssl
from adafruit_si7021 import SI7021
from adafruit_veml7700 import VEML7700
from adafruit_lc709203f import LC709203F, PackSize
import time
import rtc
import adafruit_ntp
from digitalio import DigitalInOut

# turn off the neopixel to save power; it's an input by default, so it's value is False
np = DigitalInOut(board.NEOPIXEL_POWER)

i2c = busio.I2C(board.SCL, board.SDA)
temp_sensor = SI7021(i2c)
light_sensor = VEML7700(i2c)
batt = LC709203F(i2c)
batt.pack_size = PackSize.MAH1000

def celcius_to_fahrenheit(temperature):
	return temperature * 1.8 + 32

def shorten(value):
	return round(value, 1)

def wifi_connect():
    wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    return (pool, requests)

# post results to Homebridge
host = os.getenv("HOMEBRIDGE_HOSTNAME")
port = int(os.getenv("HOMEBRIDGE_WEBHOOK_PORT"))
def update_homebridge(accessory, value):
	try:
		requests.get(f"{host}:{port}/?accessoryId={accessory}&value={value}")
	except:
		print("Could not connect to Homebridge")

pool, requests = wifi_connect()
ntp = adafruit_ntp.NTP(pool, tz_offset=int(os.getenv("TIMEZONE_OFFSET")))
r = rtc.RTC()
r.datetime = ntp.datetime

while True:
	raw_temp = temp_sensor.temperature
	c = shorten(raw_temp)
	f = shorten(celcius_to_fahrenheit(raw_temp))
	h = shorten(temp_sensor.relative_humidity)
	l = shorten(light_sensor.lux)
	b = batt.cell_percent
	t = r.datetime

	print(f'{t.tm_mon}/{t.tm_mday}@{t.tm_hour}:{t.tm_min}:{t.tm_sec}: temp: {c}°C/{f}°F, humidity: {h}%, lux: {l}, batt: {b}%')
	update_homebridge('backyard_temp', c)
	update_homebridge('backyard_humidity', h)
	update_homebridge('backyard_lux', l)

	time.sleep(30)