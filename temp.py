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
TEMP_MAX = 30.0
TEMP_THRESHOLD = 10.0
TEMP_RANGE = 0.5

# Polling interval (in seconds)
POLL_INTERVAL = 5

class IndiClient(PyIndi.BaseClient):
    def __init__(self, hostname=host_name, port=port):
        super(IndiClient, self).__init__()
        self.led = LED(RELAY_PIN)
        self.device = None
        self.setServer(hostname,int(port))
        self.blobEvent=threading.Event()
        self.debug = True
        self.target_temperature = TEMP_THRESHOLD
        if (not(self.connectServer())):
            raise Exception(f"No indiserver running on {hostname}:{port} - Run server in Ekos first.")
        self.device=self.getDevice(device_name)
        while not(self.device):
            time.sleep(0.5)
            self.device=self.getDevice(device_name)
            self.log(f"Waiting for {device_name}")

    def log(self, message):
        print(message)

    def newDevice(self, d):
        self.log(f"New device {d.getDeviceName()}")
        if d.getDeviceName() == device_name:
            self.device = self.getDevice(device_name)

    def newText(self, tvp):
        #if tvp.label == 'Nickname':
        #    self.meadeResultRead = True
        #    self.meadeResult = tvp
        if tvp.label == 'Nickname':
            try:
                self.log(f"Setting target to {tvp.tp.text}")
                self.target_temperature = int(tvp.tp.text)
                self.log(f"Target temperature now {tvp.tp.text}")
            except:
                pass

    def get_temperature(self):
        """Poll the temperature from the camera until we get a valid response."""
        if not self.device:
            self.log("Device not connected yet.")
            return None

        # print("Requesting temperature...")
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

    def get_target_temperature(self):
        nickname_prop = self.device.getText("NICKNAME")
        while nickname_prop is None:
            time.sleep(0.5)
        for elem in nickname_prop:
            if elem.name == "nickname":
                return int(elem.text)
        self.log("returning default")
        return TEMP_THRESHOLD
    def handle(self):
        try:
            self.target_temperature = self.get_target_temperature()
            self.log(f"target {self.target_temperature}")
            while True:
                temp_value = self.get_temperature()
                # exit(1)
                if temp_value is not None:
                    status = "ON " if self.led.is_lit else "OFF"
                    self.log(f"{status} current: {temp_value}, target: {self.target_temperature} +/-{TEMP_RANGE}")
                    if temp_value >= TEMP_MAX:
                        print(f"Temperature {temp_value} >= {TEMP_MAX}, turning relay OFF and exiting.")
                        break
                    elif temp_value >= self.target_temperature + TEMP_RANGE and not self.led.is_lit:
                        print(f"Temperature {temp_value} >= {self.target_temperature}, turning relay ON.")
                        self.led.on()
                    elif temp_value <= self.target_temperature - TEMP_RANGE and self.led.is_lit:
                        print(f"Temperature {temp_value} < {self.target_temperature}, turning relay OFF.")
                        self.led.off()
                else:
                    print("Failed to retrieve temperature.")
                time.sleep(POLL_INTERVAL)  # Wait for the next poll
        finally:
            self.led.off()
            self.log(f"ended {self.led.is_lit}")
            time.sleep(1)  # Wait for the next poll

    def serverConnected(self):
        self.log("Server connected")

    def serverDisconnected(self, code):
        self.log(f"Server disconnected (code {code})")

# Main program
if __name__ == "__main__":
    indiclient = IndiClient(hostname=host_name, port=port)
    try:
        indiclient.handle()
    except KeyboardInterrupt:
        print("Exiting...")
