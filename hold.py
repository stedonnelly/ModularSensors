import time
import network
from umqtt.simple import MQTTClient
import json
from machine import Pin, I2C
import neopixel
import bme280
import utime

# Constants and Configurations
WIFI_SSID = 'Unifi-A'
WIFI_PASSWORD = "lxYWuZUcyrMj"
MQTT_HOST = "192.168.1.213"
LED_PIN = 38
NEOPIXEL_PIN = 39
NEOPIXEL_COUNT = 255
SDA_PIN = 41
SCL_PIN = 40
I2C_ID = 1
I2C_FREQ = 100000

# LED and Neopixel Setup
p2 = Pin(LED_PIN, Pin.OUT, Pin.PULL_UP)
np = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), NEOPIXEL_COUNT)
p2.value(1)
purple = (10,0,10)
orange = (10,5,0)
green = (0,10,0)
red = (10,0,0)
blue = (0,0,10)
off = (0,0,0)

# Function Definitions

def connect_to_wifi(wlan):
    try:
        if not wlan.active() or not wlan.isconnected():
            wlan.active(False)  # Deactivate to reset WiFi interface
            time.sleep(1)
            wlan.active(True)   # Reactivate WiFi interface
            print("Connecting to WiFi...")
            np[0] = orange  # Update Neopixel color if defined
            np.write()
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)

            timeout = 10  # Timeout in seconds
            start_time = time.time()
            while not wlan.isconnected():
                if time.time() - start_time > timeout:
                    raise Exception("WiFi Connection Timeout")
                np[0] = orange  # Update Neopixel color if defined
                np.write()
                time.sleep(1)

            print("Connected to WiFi")
            np[0] = green  # Update Neopixel color if defined
            np.write()
        else:
            print("Already connected to WiFi")
    except Exception as e:
        print("Error connecting to WiFi:", e)
        time.sleep(5)  # Wait before retrying
        connect_to_wifi(wlan)  # Retry connecting

def get_unique_id(wlan):
    mac = wlan.config('mac')
    return ''.join('{:02X}'.format(b) for b in mac)

def mqtt_check_and_reconnect(client):
    if not client.sock:
        np[0] = purple
        np.write()
        try:
            client.connect()
            print("Reconnected to MQTT.")
            np[0] = green
            np.write()
        except Exception as e:
            print("Could not reconnect to MQTT:", e)
            raise

def publish_sensor_data(client, machine_id, temp, hum):
    try:
        temp_payload = {"temperature": temp}
        hum_payload = {"humidity": hum}
        
        client.publish(f"homeassistant/sensor/esp32_{machine_id}/temp/state", json.dumps(temp_payload))
        client.publish(f"homeassistant/sensor/esp32_{machine_id}/humidity/state", json.dumps(hum_payload))
        
    except Exception as e:
        print("Error publishing sensor data:", e)




def publish_config_payloads(client, machine_id, temp_config_payload, humidity_config_payload, led_config_payload):
    try:
        client.publish(f"homeassistant/switch/esp32_{machine_id}/config", json.dumps(led_config_payload), retain=True)
        client.publish(f"homeassistant/sensor/esp32_{machine_id}/temp/config", json.dumps(temp_config_payload), retain=True)
        client.publish(f"homeassistant/sensor/esp32_{machine_id}/humidity/config", json.dumps(humidity_config_payload), retain=True)
    except Exception as e:
        print("Error publishing config payloads:", e)

# Main Code
def main():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    connect_to_wifi(wlan)
    np[0] = green
    np.write()
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=I2C_FREQ)
    bme = bme280.BME280(i2c=i2c)

    machine_id = get_unique_id(wlan)
    
    def sub_cb(topic, msg):
        print(f"MQTT Message: {topic} -> {msg}")
        
        # Handling LED control messages
        if topic == f"homeassistant/switch/esp32_{machine_id}/led/set".encode():
            if msg.decode() == "ON":
                p2.value(1)  # Assuming p2 controls the LED
                np.write()
                
            elif msg.decode() == "OFF":
                p2.value(0)
        led_state = "ON" if p2.value() == 1 else "OFF"
        state_topic = f"homeassistant/switch/esp32_{machine_id}/led/state"
        client.publish(state_topic, led_state)
    
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
        "name": "ESP32S3 LED Switch",
        "command_topic": f"homeassistant/switch/esp32_{machine_id}/led/set",
        "state_topic": f"homeassistant/switch/esp32_{machine_id}/led/state",
        "payload_on": "ON",
        "payload_off": "OFF",
        "value_template": "{{ value_json.state }}",
        "unique_id": f"esp32_{machine_id}_led_switch",
        "device": {
            "identifiers": [f"esp32_{machine_id}_led_switch"],
            "name": "ESP32S3 LED Switch",
            "manufacturer": "CrogoIndustries TM",
            "model": "LED Switch (crogotype003)"
        }
    }


    mqtt_client_id = "esp32s3_{}".format(machine_id)
    
    client = MQTTClient(
        client_id=mqtt_client_id,
        server=MQTT_HOST,
        keepalive=60)
    mqtt_check_and_reconnect(client)
    client.set_callback(sub_cb)
    client.subscribe(f"homeassistant/switch/esp32_{machine_id}/led/set")

    
    publish_config_payloads(client, machine_id, temp_config_payload, humidity_config_payload, led_config_payload)
    
    led_state = "ON" if p2.value() == 1 else "OFF"
    state_topic = f"homeassistant/switch/esp32_{machine_id}/led/state"
    client.publish(state_topic, led_state)
    
    # Main Loop
    while True:
        if not wlan.isconnected():
            connect_to_wifi(wlan)
        try:
            mqtt_check_and_reconnect(client)  # Check and reconnect MQTT if needed
            client.check_msg()
            t, p, h = bme.read_compensated_data()
            temperature = t / 100
            humidity = h / 1024
            publish_sensor_data(client, machine_id, temperature, humidity)
            time.sleep(1)  # Adjust the sleep time as needed
        except:
            pass

if __name__ == "__main__":
    main()
