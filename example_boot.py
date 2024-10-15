# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import uasyncio as asyncio
from home_sensor.controllers import ESP32S2
from home_sensor.sensors import BME280Sensor
from home_sensor.clients import MQTT
from home_sensor.hosts import HomeAssistant
from home_sensor.api import run_controller, load_config
import file_server  # Import the new file server module

# Load configuration
config = load_config("config.json")

# Initialize ESP32S2
esp32s2 = ESP32S2(machine_id=config['esp32']['machine_id'], final_light=config['esp32']['final_light'])
esp32s2.set_wifi_parameters(config['wifi'])

# Initialize MQTT and Home Assistant
mqtt_client = MQTT()
home_assistant = HomeAssistant()
home_assistant.host_address = config['home_assistant']['host_address']

mqtt_parameters = {
    "client_id": esp32s2.id,
    "server": home_assistant.host_address,
    "keepalive": 60,
}
mqtt_client.set_parameters(mqtt_parameters)

esp32s2.register_client(mqtt_client)
esp32s2.register_host(home_assistant)

# Initialize sensor
bme280_sensor = BME280Sensor()
esp32s2.add_sensor(bme280_sensor)

# Start the file server in a separate asynchronous task
asyncio.create_task(file_server.launch_file_server())

# Start the controller
asyncio.run(run_controller(esp32s2, 30))

