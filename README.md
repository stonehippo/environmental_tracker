# environmental_tracker
A conneceted IoT sensor for tracking environmental conditions, including temperature, humidity, and light levels.

Implemented with [CircuitPython](https://circuitpython.org) and [Homebridge](http://homebridge.io).

## Configuration

The firmware makes use of CircuitPython's `settings.toml` file for all of deployment-specific information, including secrets like the WIFI SSID and password.

You'll need the following in your `settings.toml` for this to work:

```
CIRCUITPY_WIFI_SSID="Your network SSID"
CIRCUITPY_WIFI_PASSWORD="Your network password"
TIMEZONE="The timezone string for your city, e.g. America/New_York"
TIMEZONE_OFFSET="The offset for your timezone, e.g. -5 for EST/EDT"

HOMEBRIDGE_HOSTNAME="The hostname of your Homebridge instance"
HOMEBRIDGE_WEBHOOK_PORT="The port for webhooks configured in the plugin"

SENSOR_LOCATION="The name of the location you defined when you set up the sensors in the plugin"
```

You will need to set up three sensors in the Homebridge Webhooks plugin, one each for the temperature, humidity, and light level. The name of these sensors which gets used in the webhook URL will be the concatenation of the location name with a descriptive label. For example, if you make the location "backyard", the sensors need to be named:

- backyard_temp
- backyard_humidity
- backyard_lux

# Dependencies

The probe firmware depends on:

- [Adafruit CircuitPython NTP](https://github.com/adafruit/adafruit_circuitpython_ntp)
- [Adafruit CircuitPython LC709302F](https://github.com/adafruit/Adafruit_CircuitPython_LC709203F) - This is the battery monitoring circuit on my board. Some boards may ship with the [MAX1704](https://github.com/adafruit/Adafruit_CircuitPython_MAX1704x) instead.
- [Adafruit CircuitPython SI7201](https://github.com/adafruit/Adafruit_CircuitPython_SI7021) - The temperature and humidity sensor
- [Adafruit CircuitPython VEML7700](https://github.com/adafruit/Adafruit_CircuitPython_VEML7700) - The light sensor

The display firmware depends on:

- TBD

Homebridge is set up to use the [Homebridge Webhooks plugin](https://www.npmjs.com/package/homebridge-http-webhooks), which makes it trivially easy to set up the sensors on Apple's HomeKit. You can disable the Homebridge calls if you only want the probe to send its reading to the display.


## Hardware

I implemented the probe using the following hardware:

- [Adafruit Feather ESP32-S3 with 4MB Flash 2MB PSRAM](https://www.adafruit.com/product/5477)
- [Adafruit Right Angle VEML7700 Lux Sensor](https://www.adafruit.com/product/5378)
- [Adafruit Si7201 Temperature & Humidity Sensor](https://www.adafruit.com/product/3251)

I choose these components in part because I could easily assemble them using the STEMMA QT I2C interface. I also happened to have them on-hand. Other sensors with CircuitPython drivers could be swapped out pretty simply. For example, during the prototyping of the probe, I used a [BH1750 light sensor](https://www.adafruit.com/product/4681) before replacing it with the VEML7700.

## Using different hardware

The probe and display are implemented in CircuitPython, so it should be fairly easy to swap out the hardware above. For example, you could use the [no PSRAM version of the Feather ESP32-S3](https://www.adafruit.com/product/5323) for the probe without making any changes to the firmware code. Other CircuitPython-compatible boards that support WiFi are likely usable for the probe. The same should be true for the display, as long as the board has WiFi and either an integrate display or one added on that supports `displayio`. In this case, you might have to alter the display layout to fit the new screen.
