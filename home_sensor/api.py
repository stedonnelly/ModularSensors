# api.py

import time
import uasyncio as asyncio

async def run_controller(controller, interval: int):
    controller.initialise()
    while True:
        for sensor_name, sensor in controller.sensors.items():
            controller.read_sensor_data(sensor_name)
            for data_type, reading in sensor.sensor_data.items():
                controller.client.publish_sensor_data(reading)
        await asyncio.sleep(interval)
