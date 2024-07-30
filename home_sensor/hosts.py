class HomeAssistant:
    """Reciever class for Home Assistant."""

    def __init__(self):
        self.name = "Home Assistant"
        self.mqtt_state_topic = "homeassistant"
    
    def set_host_address(self, host_address: str):
        self.host_address = host_address
