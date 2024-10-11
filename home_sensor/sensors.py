from machine import I2C, Pin
from .bme.bme280 import BME280
from .containers import SensorReading
from .data import SDA_PIN, SCL_PIN, I2C_ID, I2C_FREQ
import time

class BME280Sensor:
    def __init__(self):
        i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=I2C_FREQ)
        self.sensor = BME280(i2c=i2c)
        self.name = "BME280"
        self.parent_id = None
        self.manufacturer = "CrogoIndustries TM"
        self.model_number = "CT001"

        self.temperature = SensorReading("Temperature", self.parent_id, "C", "temperature", self.manufacturer, self.model_number)
        self.humidity = SensorReading("Humidity", self.parent_id, "%", "humidity", self.manufacturer, self.model_number)
        self.sensor_data = {"temperature": self.temperature, "humidity": self.humidity}

        # Delay for sensor stability
        time.sleep(1)

    def read_compensated_data(self):
        # Add debug statement to verify communication with the sensor
        data = self.sensor.read_compensated_data()
        print(f"Raw data from BME280: {data}")
        return data

    def get_sensor_data(self):
        print("Getting sensor data...")
        t, p, h = self.read_compensated_data()
        if t is None or h is None:
            print("Error: Sensor returned None values")
            return

        temperature = t / 100
        humidity = h / 1024
        self.temperature.value = round(temperature, 2)
        self.humidity.value = round(humidity, 2)
        print(f"Temperature: {temperature} C, Humidity: {humidity} %")

    def read_sensor_data(self):
        self.get_sensor_data()
