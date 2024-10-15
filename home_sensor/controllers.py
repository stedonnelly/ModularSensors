import network
import neopixel
import machine
from machine import Pin
from .data import NEOPIXEL_PIN, NEOPIXEL_COUNT, colors, LED_PIN
import uasyncio as asyncio


class ESP32S2:
    def __init__(self, name: str = "ESP32S2"):
        self.name = name
        self.machine_id = self.set_machine_id()
        self.id = f"{self.name}_{self.machine_id}"
        self.model_number = "ESP32S"
        self.Manufacturer = "Espressif Systems"

        self.p2 = Pin(LED_PIN, Pin.OUT, Pin.PULL_UP)
        self.onboard_led = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), NEOPIXEL_COUNT)
        self.sensors = {}

    def set_machine_id(self):
        s = machine.unique_id()
        return "".join([hex(b)[2:] for b in s]).upper()

    def set_wifi_parameters(self, wifi_parameters: dict):
        self.ssid = wifi_parameters["ssid"]
        self.password = wifi_parameters["password"]
        self.hostname = wifi_parameters["hostname"]

    def check_wifi_params(func):
        def wrapper(self, *args, **kwargs):
            if not self.ssid or not self.password:
                raise ValueError("WiFi parameters not set")
            return func(self, *args, **kwargs)

        return wrapper

    @check_wifi_params
    async def connect_to_wifi(self):
        self.set_led_color("orange")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)
        self.wlan.config(dhcp_hostname=self.hostname, pm=0)
        print("Connecting to WiFi...")
        while not self.wlan.isconnected():
            await asyncio.sleep(1)  # Use await to yield control
        print("Connected to WiFi.")
        ip = self.wlan.ifconfig()[0]
        print(f"Device IP Address: {ip}")
        self.set_led_color("purple")
    

    def set_led_color(self, color):
        self.onboard_led[0] = colors[color]
        self.onboard_led.write()

    def register_host(self, host):
        self.host = host

    def register_client(self, client):
        self.client = client
        self.client.parent_id = self.id

    async def monitor_wifi(self):
        print("MONITORING WIFI TASK GO")
        while True:
            print("CHECKING WIFI")
            if not self.wlan.isconnected():
                print("WiFi disconnected, attempting to reconnect...")
                self.set_led_color("red")
                self.wlan.connect(self.ssid, self.password)
                while not self.wlan.isconnected():
                    await asyncio.sleep(1)
                print("Reconnected to WiFi.")
                self.set_led_color("purple")
                if self.client:
                    self.client.connect()
                await asyncio.sleep(1)  # Ensure connection stability before resuming
                self.set_led_color("green")
                self.set_led_color("off")
                ip = self.wlan.ifconfig()[0]
                print(f"Device IP Address: {ip}")
            await asyncio.sleep(10)

    async def initialise(self):
        self.p2.value(1)
        print(f"Initialising {self.id}")
        await self.connect_to_wifi()
        self.client.register_host(self.host)
        self.client.setup()
        print(f"Connecting to {self.client.name}...")
        await self.client.connect()
        await asyncio.sleep(1)  # Wait to ensure MQTT connection is stable
        print(f"Connected to {self.client.name}!")
        self.set_led_color("green")
        for sensor in self.sensors:
            await self.client.initialise_sensor(self.sensors[sensor])  # Await the async method
            self.client.sensors = self.sensors

        # Start a separate task to process MQTT messages from the queue

        asyncio.create_task(self.monitor_wifi())
        

    def add_sensor(self, sensor):
        sensor.parent_id = self.id
        self.sensors[sensor.name] = sensor
        print(f"Added sensor: {sensor.name}")

    def read_sensor_data(self, name):
        self.sensors[name].read_sensor_data()

