# api.py

import time
import uasyncio as asyncio
import ujson
import urequests

def download_file(url, dest):
    response = urequests.get(url)
    with open(dest, 'w') as f:
        f.write(response.text)
    response.close()

def load_config(file_path):
    with open(file_path, 'r') as f:
        return ujson.load(f)

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
                    #controller.clients.setup_single_reading(sensor)
                    controller.client.publish_sensor_data(reading)
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error while running controller: {e}")
            await asyncio.sleep(interval)
            try:
                await controller.initialise()
            except Exception as e:
                print(f"Failed to reinitialize: {e}")
