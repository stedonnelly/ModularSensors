# containers.py
# In the containers.py file, we define the classes for the sensor data and configuration messages.

class SensorReading:
    def __init__(self, name, machine_id, unit, measurement_type):
        self.name = name
        self.device_class = 'sensor'
        self.machine_id = machine_id
        self.unit = unit
        self.measurement_type = measurement_type
        self.value = None