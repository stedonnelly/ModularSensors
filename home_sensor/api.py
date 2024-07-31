# api.py
# In the api.py file, we define the API endpoints for the
# sensor data and configuration messages.

import time


def run_controller(controller, interval: int):
    """_summary_

    Args:
        controller (Controller type): _description_
        interval (int): _description_
    """
    controller.initialise()

    while True:
        for sensor in controller.sensors:
            controller.read_sensor_data(sensor)
            for data_type in sensor.sensor_data:
                controller.client.publish_sensor_data(sensor.sensor_data[data_type])
        time.sleep(interval)
