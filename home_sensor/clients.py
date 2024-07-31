from umqtt.simple import MQTTClient
import json


class MQTT:
    def __init__(self):
        self.name = "MQTT Client"
        self.parent_id = None
        self.host = None

    def set_parameters(self, mqtt_parameters: dict):
        self.mqtt_parameters = mqtt_parameters

    def set_reciever(self, host):
        self.host = host

    def setup(self):
        self.client = MQTTClient(**self.mqtt_parameters)

    def connect(self):
        self.client.connect()

    def mqtt_config_template(
        self,
        device_class,
        measurement_type,
        unit_of_measurement,
        sensor_model,
        sensor_manufacturer,
    ):
        config_payload_template = {
            "device_class": f"{measurement_type}",
            "state_topic": f"{self.host.mqtt_state_topic}/{device_class}/{self.parent_id}/{measurement_type}/state",
            "unit_of_measurement": unit_of_measurement,
            "value_template": f"{{{{ value_json.{measurement_type} }}}}",
            "unique_id": f"{measurement_type}_{self.parent_id}",
            "device": {
                "identifiers": [f"{measurement_type}_{self.parent_id}"],
                "name": f"{self.parent_id} {sensor_model} {measurement_type}",  # "ESP32S3 BME280 Temperature {}".format(machine_id),
                "manufacturer": f"{sensor_manufacturer}",  # "CrogoIndustries TM",
                "model": f"{sensor_model}",  # "Temperature sensor (crogotype002)",
            },
            "name": f"{measurement_type}{device_class}_{self.parent_id}",
            "object_id": f"{measurement_type}{device_class}_{self.parent_id}",
        }
        return config_payload_template

    def mqtt_payload(self, reading):
        return {reading.measurement_type: reading.value}
    
    def publish_config(
        self,
        device_class,
        measurement_type,
        unit_of_measurement,
        sensor_model,
        sensor_manufacturer,
    ):
        mqtt_config_payload = self.mqtt_config_template(
            device_class,
            measurement_type,
            unit_of_measurement,
            sensor_model,
            sensor_manufacturer,
        )
        self.client.publish(
            f"{self.host.mqtt_state_topic}/{device_class}/{self.parent_id}/{measurement_type}/config",
            json.dumps(mqtt_config_payload),
            retain=True,
        )

    def setup_single_reading(self, sensor):
        self.publish_config(
            sensor.device_class,
            sensor.measurement_type,
            sensor.unit,
            sensor.model_number,
        )

    def initialise_sensor(self, sensor):
        for data_type in sensor.sensor_data:
            self.setup_single_reading(sensor.sensor_data[data_type])

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
        
    def publish_reading(self, reading):
        payload = self.mqtt_payload(reading)
        self.publish(
            f"{self.host.mqtt_state_topic}/{reading.device_class}/{self.parent_id}/{reading.measurement_type}/state",
            json.dumps(payload),
        )
