import network
import neopixel
import machine
from machine import Pin
from .data import NEOPIXEL_PIN, NEOPIXEL_COUNT, colors, LED_PIN


class ESP32S2:
    def __init__(self, name: str = "ESP32S2"):
        self.name = name
        self.machine_id = self.set_machine_id()
        self.id = f"{self.name}_{self.machine_id}"
        self.model_number = "CT001"
        self.Manufacturer = "CrogoIndustries TM"

        self.p2 = Pin(LED_PIN, Pin.OUT, Pin.PULL_UP)
        self.onboard_led = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), NEOPIXEL_COUNT)
        self.sensors = {}

    def set_machine_id(self):
        s = machine.unique_id()
        return "".join([hex(b)[2:] for b in s]).upper()

    def set_wifi_parameters(self, wifi_parameters: dict):
        self.ssid = wifi_parameters["ssid"]
        self.password = wifi_parameters["password"]

    def check_wifi_params(func):
        def wrapper(self, *args, **kwargs):
            if not self.ssid or not self.password:
                raise ValueError("WiFi parameters not set")
            return func(self, *args, **kwargs)

        return wrapper

    @check_wifi_params
    def connect_to_wifi(self):
        self.set_led_color("orange")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)
        print("Connecting to WiFi...")
        while not self.wlan.isconnected():
            pass
        print("Connected to WiFi.")
        self.set_led_color("purple")

    def set_led_color(self, color):
        self.onboard_led[0] = colors[color]
        self.onboard_led.write()

    def register_host(self, host):
        self.host = host

    def register_client(self, client):
        self.client = client()
        self.client.parent_id = self.id

    def initialise(self):
        self.p2.value(1)
        self.connect_to_wifi()
        #self.set_machine_id(self.wlan)
        
        self.client.register_host(self.host)
        self.client.setup()
        self.client.connect()
        
        for sensor in self.sensors:
            self.client.initialise_sensor(sensor)

    def add_sensor(self, sensor):
        sensor.parent_id = self.id
        self.sensors[sensor.name] = sensor

    def read_sensor_data(self, name):
        self.sensors[name].read_sensor_data()
