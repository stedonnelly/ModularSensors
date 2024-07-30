# runfile.py
# Test runfile

from home_sensor.controllers import ESP32S2
from home_sensor.sensors import BME280
from home_sensor.clients import MQTT
from home_sensor.hosts import HomeAssistant

esp32s2 = ESP32S2()
mqtt_client = MQTT()
home_assistant = HomeAssistant()

mqtt_parameters = {
    "client_id": esp32s2.id,
    "server": home_assistant.host_address,
    "keepalive": 60,
}
mqtt_client.set_parameters(mqtt_parameters)

esp32s2.register_client()
esp32s2.register_host(home_assistant)

