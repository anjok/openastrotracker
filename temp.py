import time
import PyIndi
import RPi.GPIO as GPIO

# Pin number where the relay is connected
RELAY_PIN = 18

# Temperature threshold (in degrees Celsius) to trigger the relay
TEMP_THRESHOLD = 10.0

# Polling interval (in seconds)
POLL_INTERVAL = 5

# Setup GPIO pin for relay
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Make sure relay is off initially

class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
        self.device_name = "ZWO CCD ASI183MC"  # Your camera's INDI device name
        self.device = None

    def newDevice(self, d):
        print(f"New device {d.getDeviceName()}")
        if d.getDeviceName() == self.device_name:
            self.device = d

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
    try:
        indiclient = IndiClient()
        indiclient.setServer("localhost", 7624)  # Adjust to your INDI server IP and port
        if not indiclient.connectServer():
            print("No INDI server running at localhost:7624")
            exit(1)

        # Wait for camera device to connect
        while not indiclient.device:
            time.sleep(0.5)

        # Main polling loop
        try:
            while True:
                temp_value = indiclient.get_temperature()
                if temp_value is not None:
                    print(f"Current temperature: {temp_value}")
                    if temp_value >= TEMP_THRESHOLD:
                        print(f"Temperature {temp_value} >= {TEMP_THRESHOLD}, turning on the relay.")
                        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on relay
                    else:
                        print(f"Temperature {temp_value} < {TEMP_THRESHOLD}, turning off the relay.")
                        GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off relay
                else:
                    print("Failed to retrieve temperature.")

                time.sleep(POLL_INTERVAL)  # Wait for the next poll

        except KeyboardInterrupt:
            print("Exiting...")

    finally:
        # Cleanup GPIO on exit
        GPIO.output(RELAY_PIN, GPIO.LOW)
        GPIO.cleanup()
