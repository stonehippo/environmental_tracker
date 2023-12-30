import os
import board
import wifi
import socketpool
import adafruit_requests
import ssl
from adafruit_si7021 import SI7021
from adafruit_veml7700 import VEML7700
import time
import alarm
from digitalio import DigitalInOut

# turn off the neopixel to save power; it's an input by default, so it's value is False
np = DigitalInOut(board.NEOPIXEL_POWER)

i2c = board.I2C()
temp_sensor = SI7021(i2c)
light_sensor = VEML7700(i2c)

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

raw_temp = temp_sensor.temperature
c = shorten(raw_temp)
h = shorten(temp_sensor.relative_humidity)
l = shorten(light_sensor.lux)

update_homebridge('backyard_temp', c)
update_homebridge('backyard_humidity', h)
update_homebridge('backyard_lux', l)

deep_sleep = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 30)
alarm.exit_and_deep_sleep_until_alarms(deep_sleep)