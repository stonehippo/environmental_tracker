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
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout

# turn off the neopixel to save power; it's an input by default, so it's value is False
np = DigitalInOut(board.NEOPIXEL_POWER)

displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA)

display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

main_group = displayio.Group()
display.show(main_group)
layout = GridLayout(
    x=0,
    y=0,
    width=128,
    height=32,
    grid_size=(1, 2),
    cell_padding=0,
    divider_lines=False
)

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

location = os.getenv("SENSOR_LOCATION")

env_label = label.Label(terminalio.FONT, text="", color=0xffffff, x=0, y=0)
layout.add_content(env_label, grid_position=(0,0), cell_size=(1,1))

status_label = label.Label(terminalio.FONT, text="", color=0xffffff, x=0, y=0)
layout.add_content(status_label, grid_position=(0,1), cell_size=(1,1))

main_group.append(layout)

def update_display(temp_c, temp_f, rel_humidity, lux, batt):
    env_text ="%0.1fF/%0.1fC @ %0.1f%%rH" % (temp_f, temp_c, rel_humidity)
    status_text = f"{lux}lux batt@{batt}% "

    #print(temp_text)
    env_label.text = env_text
    #print(rel_hum_text)
    status_label.text = status_text

while True:
	raw_temp = temp_sensor.temperature
	c = shorten(raw_temp)
	f = shorten(celcius_to_fahrenheit(raw_temp))
	h = shorten(temp_sensor.relative_humidity)
	l = shorten(light_sensor.lux)
	b = batt.cell_percent
	t = r.datetime

	print(f'{t.tm_mon}/{t.tm_mday}@{t.tm_hour}:{t.tm_min}:{t.tm_sec}: temp: {c}°C/{f}°F, humidity: {h}%, lux: {l}, batt: {b}%')
	update_homebridge(f'{location}_temp', c)
	update_homebridge(f'{location}_humidity', h)
	update_homebridge(f'{location}_lux', l)

	update_display(c,f,h,l,b)

	time.sleep(30)