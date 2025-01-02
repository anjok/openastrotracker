import time
import PyIndi
import time, threading, io, sys

host_name = "localhost"
device_name = "ZWO CCD ASI183MC"
port = 7624
try:
    from gpiozero import LED
except:
    class LED:
        def __init__(pin):
            pass
        def on():
            print("Pin ON")
        def off():
            print("Pin OFF")
# Pin number where the relay is connected
RELAY_PIN = 2

# Temperature threshold (in degrees Celsius) to trigger the relay
TEMP_THRESHOLD = 10.0
TEMP_RANGE = 1.0

# Polling interval (in seconds)
POLL_INTERVAL = 5

class IndiClient(PyIndi.BaseClient):
    def __init__(self, hostname=host_name, port=port):
        super(IndiClient, self).__init__()
        self.device = None
        self.setServer(hostname,int(port))
        self.blobEvent=threading.Event()
        self.debug = True
        if (not(self.connectServer())):
            raise Exception(f"No indiserver running on {hostname}:{port} - Run server in Ekos first.")
        self.device=self.getDevice(device_name)
        while not(self.device):
            time.sleep(0.5)
            self.device=self.getDevice(device_name)
            self.log(f"Waiting for {device_name}")

    def newDevice(self, d):
        print(f"New device {d.getDeviceName()}")
        if d.getDeviceName() == self.device_name:
            self.device = self.getDevice(self.device_name)
    
    def log(self, message):
        print(message)
        
    def newText(self, tvp):
        print(f"New text {tvp}")
        if tvp.label == 'Nickname':
            self.meadeResultRead = True
            self.meadeResult = tvp
        self.log(f">> newText=>{tvp.label}={tvp.tp.text}")

    def get_temperature(self):
        """Poll the temperature from the camera until we get a valid response."""
        if not self.device:
            print("Device not connected yet.")
            return None

        print("Requesting temperature...")
        temp_property = None

        # Poll until the property is returned
        while temp_property is None:
            temp_property = self.device.getNumber("CCD_TEMPERATURE")
            if temp_property is None:
                time.sleep(0.5)  # Small wait before retrying

        # Access the temperature value after a successful response
        for element in temp_property:
            if element.name == "CCD_TEMPERATURE_VALUE":  # Check the actual field name in the device
                return element.value

        return None

    def serverConnected(self):
        print("Server connected")

    def serverDisconnected(self, code):
        print(f"Server disconnected (code {code})")

# Main program
if __name__ == "__main__":
    led = Led(RELAY_PIN)
    indiclient = IndiClient(hostname=host_name, port=port)
    try:
        # Main polling loop
        try:
            while True:
                temp_value = indiclient.get_temperature()
                # exit(1)
                if temp_value is not None:
                    print(f"Current temperature: {temp_value}, target: {TEMP_THRESHOLD} +/- {TEMP_RANGE}")
                    elif temp_value >= TEMP_MAX:
                        print(f"Temperature {temp_value} >= {TEMP_MAX}, turning relay OFF and exiting.")
                        led.off()  # Turn on relay
                        exit(10)
                    elif temp_value >= TEMP_THRESHOLD + TEMP_RANGE and not led.is_lit:
                        print(f"Temperature {temp_value} >= {TEMP_THRESHOLD}, turning relay ON.")
                        led.on()  # Turn on relay
                    elif temp_value <= TEMP_THRESHOLD - TEMP_RANGE and led.is_lit:
                        print(f"Temperature {temp_value} < {TEMP_THRESHOLD}, turning relay OFF.")
                        led.off()  # Turn off relay
                else:
                    print("Failed to retrieve temperature.")
                time.sleep(POLL_INTERVAL)  # Wait for the next poll
        except KeyboardInterrupt:
            print("Exiting...")
    finally:
        led.off()
