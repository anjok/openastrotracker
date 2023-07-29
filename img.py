import time, threading, io, sys
import PyIndi

device_name = "Canon DSLR EOS 6D"
exposure_time = 1.0
host_name = "astroberry.local"
filename = "captured_image.raw"  # Provide your desired filename and extension

class CamClient(PyIndi.BaseClient):
    def __init__(self, hostname="astroberry.local", port=7624):
        super(CamClient, self).__init__()
        self.setServer(hostname,int(port))
        # self.blobEvent=threading.Event()
        self.debug = False
        if (not(self.connectServer())):
            raise Exception(f"No indiserver running on {hostname}:{port} - Run server in Ekos first.")
        self.device=self.getDevice(device_name)
        while not(self.device):
            time.sleep(0.5)
            self.log(f"Waiting for {device_name}")
            self.device=self.getDevice(device_name)
        self.setBLOBMode(1, device_name, None)

    @property
    def debug(self):
        return self._debug
    @debug.setter
    def debug(self, val):
        self._debug = val
    def getProp(self, device, propType, propName):
        func = None
        if propType.lower() == "switch":
            func = self.device.getSwitch
        elif propType.lower() == "number":
            func = self.device.getNumber
        elif propType.lower() == "text":
            func = self.device.getText
        result = None
        if func != None:
            result = func(propName)
            while not(result):
                time.sleep(0.5)
                result = func(propName)
        return result

    def send_num(self, name, val):
        prop = self.device.getNumber("CCD_EXPOSURE")
        prop[0].value = val
        self.sendNewNumber(prop)

    def get_num(self, name):
        prop = self.device.getNumber("CCD_EXPOSURE")
        return prop[0].value

    def toggle(self, switch_name, toggle):
        print(f"name: {switch_name} -> {toggle}")
        switch = self.getProp(device_name, "switch", switch_name)
        print(f"name: {switch}")
        for i in range(0,len(switch)):
            print(f"name: {switch[i].name}")
            state = PyIndi.ISS_ON if switch[i].name == toggle else PyIndi.ISS_OFF
            switch[i].setState(state)
        self.sendNewSwitch(switch) # send this new value to the device

    def log(self,msg,end="\n"):
        if self.debug:
            print(msg,end=end)
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass
    def newBLOB(self, bp):
        print(f"Image received")
        blob = bp["blobs"][0]
        blobName = bp["name"]
        with open(filename, "wb") as file:
            file.write(blob)
        print(f"Image {blobName} downloaded and saved as {filename}")
        self.disconnectServer()

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass

# Create an INDI client
indiclient = CamClient()

# Set the exposure time (in seconds)
indiclient.send_num("CCD_EXPOSURE", exposure_time)

# Start capturing
# indiclient.toggle("CCD_CAPTURE", "ON")

# Wait for the exposure to complete
while indiclient.get_num("CCD_EXPOSURE") > 0:
    print(f"{indiclient.get_num('CCD_EXPOSURE')}")
    time.sleep(0.5)

print(f"Done {indiclient.get_num('CCD_EXPOSURE')}")

# Stop capturing
# indiclient.sendNewSwitch(device, "CCD_CAPTURE", "OFF")

# Disconnect from the camera
#indiclient.disconnectDevice(device_name)

# Disconnect from the INDI server
#indiclient.disconnectServer()