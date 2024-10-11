from umqtt.robust import MQTTClient
import uasyncio as asyncio
import json

class MQTT:
    def __init__(self, name: str = "MQTT Client"):
        self.name = name
        self.parent_id = None
        self.host = None
        self.connected = False  # Track the connection status
        self.sensors = []

    def set_parameters(self, mqtt_parameters: dict):
        self.mqtt_parameters = mqtt_parameters

    def register_host(self, host):
        self.host = host

    def setup(self):
        self.client = MQTTClient(**self.mqtt_parameters)

    async def connect(self):
        asyncio.create_task(self.monitor_mqtt())  # Start the monitor task
        while not self.connected:
            try:
                self.client.connect()  # Connect to the MQTT broker
                self.connected = True  # Set connected status to True if successful
                print("Connected to MQTT broker.")
            except Exception as e:
                self.connected = False  # Set connected status to False if connection fails
                print(f"Failed to connect to MQTT broker: {e}")
            await asyncio.sleep(5)


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
            sensor.manufacturer,
        )

    async def initialise_sensor(self, sensor):
        for data_type in sensor.sensor_data:
            print('Setup: '+data_type)
            self.setup_single_reading(sensor.sensor_data[data_type])

    def publish(self, topic, payload):
        try:
            self.client.publish(topic, payload)
        except Exception as e:
            self.connected = False  # If publish fails, set connected to False
            print(f"Failed to publish message: {e}")

    def publish_sensor_data(self, reading):
        payload = self.mqtt_payload(reading)
        topic = f"{self.host.mqtt_state_topic}/{reading.device_class}/{self.parent_id}/{reading.measurement_type}/state"
        print(f'Publishing {reading.measurement_type} to topic {topic}')
        print(payload)
        self.publish(
            f"{self.host.mqtt_state_topic}/{reading.device_class}/{self.parent_id}/{reading.measurement_type}/state",
            json.dumps(payload),
        )
        # Enqueue the message instead of direct publish

    async def publish_sensor_data1(self, reading):
        payload = self.mqtt_payload(reading)
        print(f'Publishing {reading.measurement_type} to topic {self.host.mqtt_state_topic}/{reading.device_class}/{self.parent_id}/{reading.measurement_type}/state')
        print(payload)
        self.publish(
            f"{self.host.mqtt_state_topic}/{reading.device_class}/{self.parent_id}/{reading.measurement_type}/state",
            json.dumps(payload),
        )

    async def monitor_mqtt(self):
        print("Starting MQTT monitor task")
        while True:
            print("Checking MQTT Status")
            try:
                # Try pinging the broker to check if we're still connected
                self.client.ping()
                print("MQTT client is connected")
            except Exception as e:
                print(f"MQTT client disconnected, attempting to reconnect... Reason: {e}")
                try:
                    # Attempt to reconnect
                    self.client.connect()
                    print("Reconnected to MQTT broker successfully.")
                    
                    # Wait for stability
                    await asyncio.sleep(15)
                    
                    # Reinitialize sensors after reconnecting
                    for sensor in self.sensors:
                        print(f"Reinitializing sensor: {sensor}")
                        await self.initialise_sensor(self.sensors[sensor])
                    print("Reinitialized sensors after reconnection.")
                except Exception as e:
                    print(f"Failed to reconnect MQTT client: {e}")

            await asyncio.sleep(10)  # Check every 10 seconds
