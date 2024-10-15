# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

# runfile.py
# Test runfile

import uasyncio as asyncio

from home_sensor.controllers import ESP32S2
from home_sensor.sensors import BME280Sensor
from home_sensor.clients import MQTT
from home_sensor.hosts import HomeAssistant
from home_sensor.api import run_controller, load_config


config = load_config('config.json')


esp32s2 = ESP32S2()
esp32s2.set_wifi_parameters(config['wifi'])

mqtt_client = MQTT()
home_assistant = HomeAssistant()
home_assistant.host_address = config['home_assistant']['host_address']

mqtt_parameters = {
    "client_id": esp32s2.id, # Client ID for your MQTT server, can be anything you choose
    "server": home_assistant.host_address, # Since we're using the home assistant data host with MQTT then we use the MQTT address supplied in host
    "keepalive": 60,
}
mqtt_client.set_parameters(mqtt_parameters) # Initialising the MQTT paramets

esp32s2.register_client(mqtt_client) # Register the client with the controller
esp32s2.register_host(home_assistant) # Register the data host with the controller

########### SENSORS ############

bme280_sensor = BME280Sensor() # Create the sensor object

esp32s2.add_sensor(bme280_sensor)

########## Run Commands ###########

asyncio.run(run_controller(esp32s2, interval = 30)) # Uses the api.run_controller to get things rolling setting the sensor interval to 30 s
