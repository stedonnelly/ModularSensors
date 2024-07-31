from home_sensor.controllers import ESP32S2
from home_sensor.sensors import BME280Sensor
from home_sensor.clients import MQTT
from home_sensor.hosts import HomeAssistant
from home_sensor.api import run_controller

esp32s2 = ESP32S2()
esp32s2.set_wifi_parameters({"ssid": "", "password": ""})

mqtt_client = MQTT()
home_assistant = HomeAssistant()
home_assistant.host_address = ""

mqtt_parameters = {
    "client_id": esp32s2.id,
    "server": home_assistant.host_address,
    "keepalive": 60,
}
mqtt_client.set_parameters(mqtt_parameters)

esp32s2.register_client(mqtt_client)
esp32s2.register_host(home_assistant)

bme280_sensor = BME280Sensor()

esp32s2.add_sensor(bme280_sensor)

run_controller(esp32s2, 30)
