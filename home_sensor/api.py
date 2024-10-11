# api.py

import time
import uasyncio as asyncio

async def run_controller(controller, interval: int):
    INITIALISED = False
    while not INITIALISED:
        try:
            await controller.initialise()
            INITIALISED = True
            print("Controller initialized successfully.")
        except Exception as e:
            print(f"Initialization error: {e}")
            await asyncio.sleep(1)

    while True:
        try:
            for sensor_name, sensor in controller.sensors.items():
                print(f"Attempting to read data from sensor: {sensor_name}")
                controller.read_sensor_data(sensor_name)  # Add print statements
                for data_type, reading in sensor.sensor_data.items():
                    await controller.client.publish_sensor_data(reading)
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error while running controller: {e}")
            await asyncio.sleep(5)
            try:
                await controller.initialise()
            except Exception as e:
                print(f"Failed to reinitialize: {e}")
