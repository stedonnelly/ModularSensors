from .bme.bme280 import BME280
from machine import I2C, Pin
from .data import SDA_PIN, SCL_PIN, I2C_ID, I2C_FREQ
from .containers import SensorReading


class BME280Sensor:
    def __init__(self):
        i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=I2C_FREQ)
        self.sensor = BME280(i2c=i2c)
        self.name = "BME280"
        self.parent_id = None
    
    def setup(self):
        self.temperature = SensorReading(
            "Temperature", self.parent_machine_id, "C", "temperature"
        )
        self.humidity = SensorReading(
            "Temperature", self.parent_machine_id, "%", "humidity"
        )
        self.sensor_data = {"temperature": self.temperature,
                            "humidity": self.humidity}

    def get_sensor_data(self):
        t, p, h = self.read_compensated_data()
        temperature = t / 100
        humidity = h / 1024
        self.temperature.value = temperature
        self.humidity.value = humidity

    def read_sensor_data(self):
        self.get_sensor_data()
        return self.sensor_data
