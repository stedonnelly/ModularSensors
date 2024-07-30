# data.py
# In the data.py file, we define the configuration for the sensors and the LED strip.
# We also define the MQTT topics and payloads for the sensor data and configuration messages.
# The data.py file is used by the main.py file to publish sensor data and configuration payloads to the MQTT broker.

NEOPIXEL_PIN = 39
NEOPIXEL_COUNT = 2550
LED_PIN = 38
colors = {
    "purple": (1, 0, 1),
    "orange": (2, 1, 0),
    "green": (0, 1, 0),
    "red": (1, 0, 0),
    "blue": (0, 0, 1),
    "off": (0, 0, 0),
}
SDA_PIN = 41
SCL_PIN = 40
I2C_ID = 1
I2C_FREQ = 100000
