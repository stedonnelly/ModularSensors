# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import time
import network
from umqtt.simple import MQTTClient
import json
import random
from machine import Pin, I2C
import bme280
import utime
import machine
import neopixel

p2 = Pin(38, Pin.OUT, Pin.PULL_UP)
p2.value(1)

np = neopixel.NeoPixel(Pin(39), 255)

purple = (10,0,10)
orange = (10,5,0)
green = (0,10,0)
red = (10,0,0)
blue = (0,0,10)
off = (0,0,0)


def sub_cb(topic, msg):
    print((topic, msg))
    if msg.decode() == "ON":
        p2.value(1)
    if msg.decode() == "OFF":
        p2.value(0)

# WiFi settings
WIFI_SSID = 'Unifi-A'
WIFI_PASSWORD = "lxYWuZUcyrMj"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(1)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

while not wlan.isconnected():
    np[0] = orange
    np.write()
    time.sleep(0.5)
    np[0] = orange
    np.write()
    time.sleep(0.5)

def get_unique_id():
    
    return mac

print("Connected to WiFi")
np[0] = green
np.write()
mqtt_host = "192.168.1.213"

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.

mac = wlan.config('mac')  # Get the MAC address of the device

machine_id = ''.join('{:02X}'.format(b) for b in mac)

print(machine_id)
mqtt_client_id = "esp32s3_{}".format(machine_id)

# Initialize our MQTTClient and connect to the MQTT server
client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        keepalive=60)

# Connect to MQTT (without username and password for anonymous connection)

print(client.sock)
while not client.sock:
    print("Attempting to connect to MQTT")
    np[0] = purple
    np.write()
    try:
        client.connect()
    except:
        continue
print("MQTT Connected successfully")
np[0] = green
np.write()

class MQTTIssue(Exception):
    """Custom exception to represent issues with MQTT."""
    def __init__(self, message="An issue occurred with MQTT"):
        self.message = message
        super().__init__(self.message)
    

temp_config_payload = {
   "device_class":"temperature",
   "state_topic":"homeassistant/sensor/esp32_{}/temp/state".format(machine_id),
   "unit_of_measurement":"C",
   "value_template":"{{ value_json.temperature}}",
   "unique_id":"temperature_{}".format(machine_id),
   "device":{
      "identifiers":[
         "temperature_{}".format(machine_id)
      ],
      "name":"ESP32S3 BME280 Temperature {}".format(machine_id),
      "manufacturer":"CrogoIndustries TM",
      "model":"Temperature sensor (crogotype002)"
   },
   "name":"TemperatureSensor_{}".format(machine_id),
   "object_id":"TemperatureSensor_{}".format(machine_id)
}

humidity_config_payload = {
   "device_class":"humidity",
   "state_topic":"homeassistant/sensor/esp32_{}/humidity/state".format(machine_id),
   "unit_of_measurement":"\u0025",
   "value_template":"{{ value_json.humidity }}",
   "unique_id":"humidity_{}".format(machine_id),
   "device":{
      "identifiers":[
         "humidity_{}".format(machine_id)
      ],
      "name":"ESP32S3 BME280 Humidity {}".format(machine_id),
      "manufacturer":"CrogoIndustries TM",
      "model":"Humidity sensor (crogotype002)"
   },
   "name":"HumiditySensor_{}".format(machine_id),
   "object_id":"HumiditySensor_{}".format(machine_id)
}

led_config_payload = {
    "device_class": "light",
    "name": "LED State",
    "state_topic": "homeassistant/sensor/esp32_{}/led/state".format(machine_id),
    "unique_id": "esp32_{}_led_state".format(machine_id),
    "value_template": "{{ value_json.state }}"
    }

sdaPIN=Pin(41)
sclPIN=Pin(40)
i2c = I2C(1, scl=sclPIN, sda=sdaPIN, freq=100000)
bme = bme280.BME280(i2c=i2c)


temp = []
hum = []

def movavg(inform,intervals):
    return round(sum(inform)/len(inform),2)

def mqtt_check_and_reconnect(client, mqtt_host):
    if not client.sock:
        print("Reconnecting MQTT...")
        try:
            client.connect()
            print("Reconnected to MQTT.")
        except:
            print("Could not reconnect to MQTT.")
            raise MQTTIssue("MQTT Issue")
    return True

published_led = False
published_temp = False
published_humidity = False
mqtt_led_sub = False

client.set_callback(sub_cb)
while True:
    if wlan.isconnected():
        try:
            if not mqtt_led_sub and published_led:
                client.subscribe('homeassistant/sensor/esp32_{}/led/state'.format(machine_id))
                mqtt_led_sub = True
            t, p, h = bme.read_compensated_data()
            temperature=t/100
            p = p // 256
            pressure = p // 100
            hi = h // 1024
            hd = h * 100 // 1024 - hi * 100
            humidity = float("{}.{:02d}".format(hi, hd))
            temp.append(temperature)
            hum.append(humidity)
            inter = 0.05
            seconds = utime.localtime()[5]
            mseconds = utime.localtime()[6]
            #print(len(temp))
            #print("Seconds: ", seconds)
            #Calibrate to the
            if len(temp)*0.5>=30:
                temp.pop(0)
                hum.pop(0)
            #if len(temp)*inter<30:
            #    time.sleep(1)    
            #else:
                # Publish sensor data
                #print('published')
                
            if seconds:#==30 or seconds==0:
                try:
                    if not published_led:
                        client.publish("homeassistant/sensor/esp32_{}/led/config".format(machine_id), json.dumps(led_config_payload), retain=True)
                        if p2.value() == 1:
                            client.publish("homeassistant/sensor/esp32_{}/led/state".format(machine_id),json.dumps({"state": "ON"}))
                        if p2.value() == 0:
                            client.publish("homeassistant/sensor/esp32_{}/led/state".format(machine_id),json.dumps({"state": "OFF"}))
                        print('publed')
                        published_led=True
                    if not published_temp:
                        client.publish("homeassistant/sensor/esp32_{}/temp/config".format(machine_id), json.dumps(temp_config_payload), retain=True)
                        print('pub1')
                        published_temp=True
                    if not published_humidity:
                        client.publish("homeassistant/sensor/esp32_{}/humidity/config".format(machine_id), json.dumps(humidity_config_payload), retain=True)
                        print('pub2')
                        published_humidity=True
                    if published_temp:
                        client.publish("homeassistant/sensor/esp32_{}/temp/state".format(machine_id), json.dumps({"temperature": round(movavg(temp,inter),2)}))
                        print('pub_temp')
                    if published_humidity:
                        client.publish("homeassistant/sensor/esp32_{}/humidity/state".format(machine_id), json.dumps({"humidity": round(movavg(hum,inter),2)}))
                        print('pub_hum')
                except Exception as e:
                    np[0] = purple
                    np.write()
                    print('{}'.format(e))
                    client.connect()
                time.sleep(1)
                np[0]=green
                np.write()
                print('fine')
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as error:
            print('Issue ',error)
    else:
        np[0] = orange
        np.write()
        print("WiFi Not Connected")
        try:
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            while not wlan.isconnected():
                time.sleep(1)
            print("Connected to WiFi")
            np[0] = green
            np.write()
        except OSError:
            pass