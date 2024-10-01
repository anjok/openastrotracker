import PyIndi

class MyINDIClient(PyIndi.BaseClient):
    def __init__(self):
        super(MyINDIClient, self).__init__()
        self.device = None

    def newDevice(self, d):
        if d.getDeviceName() == "CCD Simulator":
            print(f"Found device: {d.getDeviceName()}")
            self.device = d

    def newProperty(self, p):
        print(f"New property: {p.getName()} for device {p.getDeviceName()}")

    def newBLOB(self, bp):
        # Handle new BLOB properties here
        pass

    def newSwitch(self, sp):
        pass

    def newNumber(self, np):
        pass

    def newText(self, tp):
        pass

    def newLight(self, lp):
        pass

    def newMessage(self, d, m):
        print(f"Message from {d.getDeviceName()}: {m.message}")

# Create a client and connect to the server
client = MyINDIClient()
client.setServer("localhost", 7624)
if not client.connectServer():
    print("Could not connect to INDI server")
    exit(1)
