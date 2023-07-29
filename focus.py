import sys, time, logging
import PyIndi
from io import StringIO

CAM_NAME = "Canon DSLR EOS 6D"
CAM_NAME = "Canon DSLR EOS 450D (PTP mode)"
FOCUSER_NAME = "LX200 OpenAstroTech"
 
class IndiClient(PyIndi.BaseClient):
    cam = None
    focuser = None
 
    def __init__(self):
        super(IndiClient, self).__init__()
        self.logger = logging.getLogger('PyIndi.IndiClient')
        self.logger.info('creating an instance of PyIndi.IndiClient')
        self.cam_ready = 0
        self.received_blob = False
        self.focuser_ready = 0
        self.focus_position = 50000
        self.focus_direction = 0
        self.focus_index = 0
    def connect(self):
        self.setServer("astroberry.local",7624)
        # connect to indi server
        print("Connecting and waiting 2 secs")
        if (not(self.connectServer())):
            print("No indiserver running on {self.getHost()}:{self.getPort()} - Try to run")
            print("  indiserver indi_simulator_telescope indi_simulator_ccd")
            sys.exit(1)
        time.sleep(1)
    def newDevice(self, d):
        self.logger.info(f"new device {d.getDeviceName()}")
        if d.getDeviceName() == CAM_NAME:
            self.logger.info(f"Set new cam {CAM_NAME}!")
            # save reference to the device in member variable
            self.cam = d
        elif d.getDeviceName() == FOCUSER_NAME:
            self.logger.info(f"Set new focuser {FOCUSER_NAME}!")
            # save reference to the device in member variable
            self.focuser = d
    def newProperty(self, p):
        #self.logger.info("new property "+ p.getName() + " for device "+ p.getDeviceName())
        if self.cam is not None and p.getDeviceName() == self.cam.getDeviceName():
            if p.getName() == "CONNECTION":
                self.logger.info(f"Got property {self.cam.getDeviceName()}.{p.getName()}")
                self.connectDevice(self.cam.getDeviceName())
                # set BLOB mode to BLOB_ALSO
                self.setBLOBMode(1, self.cam.getDeviceName(), None)
            if p.getName() in ["CCD_EXPOSURE", "CCD_FRAME"]:
                self.logger.info(f"Got property {self.cam.getDeviceName()}.{p.getName()}")
                self.cam_ready = self.cam_ready + 1 
        if self.focuser is not None and p.getDeviceName() == self.focuser.getDeviceName():
            if p.getName() == "CONNECTION":
                self.logger.info(f"Got property {self.focuser.getDeviceName()}.{p.getName()}")
                self.connectDevice(self.focuser.getDeviceName())
            if p.getName() in ["FOCUS_MOTION", "REL_FOCUS_POSITION", "FOCUS_BACKLASH_STEPS", "FOCUS_BACKLASH_TOGGLE"]:
                self.logger.info(f"Got property {self.focuser.getDeviceName()}.{p.getName()}")
                self.focuser_ready = self.focuser_ready + 1 
    def removeProperty(self, p):
        self.logger.info(f"remove property {p.getName()} >> {p.getDeviceName()}")
        pass
    def newBLOB(self, bp):
        self.logger.info(f"new BLOB {bp.name}")
        img = bp.getblobdata()
        with open(f"focus/frame-{self.focus_position}-{self.focus_index}.fits", "wb") as f:
            f.write(img)
        self.received_blob = True
        self.handle_image(img)
        # self.disconnectServer()
    def newSwitch(self, svp):
        self.logger.info(f"new Switch {svp.name} >> {svp.device} = {svp[0]}")
        pass
    def newNumber(self, nvp):
        self.logger.info(f"new Number {nvp.name} >> {nvp.device} = {nvp[0].value}")
        pass
    def newText(self, tvp):
        self.logger.info(f"new Text {tvp.name} >> {tvp.device} = {tvp[0].text}")
        pass
    def newLight(self, lvp):
        self.logger.info(f"new Light {lvp.name} >> {lvp.device} = {lvp[0]}")
        pass
    def newMessage(self, d, m):
        self.logger.info(f"new Message {d.messageQueue(m)}")
        pass
    def serverConnected(self):
        print("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
        self.connected = True
    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")
        # set connected to False
        self.connected = False
    def set_number(self, device, name, *values):
        prop = device.getNumber(name)
        for i in range(0, len(values)):
            prop[i].value = values[i]
        self.sendNewNumber(prop)
    def set_toggle(self, device, name, index):
        prop = device.getSwitch(name)
        for i in range(0,len(prop)):
            state = PyIndi.ISS_ON if i == index else PyIndi.ISS_OFF
            prop[i].setState(state)
        self.sendNewSwitch(prop)
    def set_frame(self, x, y, w, h):
        self.set_number(self.cam, "CCD_FRAME", x, y, w, h)
    def take_exposure(self, value, idx):
        self.logger.info(f"<<<<<<<< Exposure >>>>>>>>>")
        self.received_blob = False
        self.focus_index = idx
        self.set_number(self.cam, "CCD_EXPOSURE", value)
        while not indiclient.received_blob:
            time.sleep(0.5)
    def move_focus(self, amount):
        new_dir = 0 if amount > 0 else 1
        self.focus_position = self.focus_position + amount
        amount = amount if amount > 0 else -amount
        if self.focus_direction != new_dir:
            self.set_number(self.focuser, "FOCUS_MOTION", new_dir)
            self.focus_direction = new_dir
        self.set_number(self.focuser, "REL_FOCUS_POSITION", amount)
        time.sleep(1)
    def handle_image(self, data):
        pass
    def move_and_shoot(self, amount):
        self.move_focus(amount)
        self.take_exposure(0.01, 0)
        self.take_exposure(0.01, 1)
        self.take_exposure(0.01, 2)
        while not(self.received_blob):
            time.sleep(0.2)
        # process and log
    def wait_ready(self):
        while not(self.cam_ready == 2):
            self.logger.info(f"waiting for cam: {self.cam_ready}")
            time.sleep(0.3)
        while not(self.focuser_ready == 4):
            self.logger.info(f"waiting for focuser: {self.focuser_ready}")
            time.sleep(0.3)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
indiclient=IndiClient()
indiclient.connect()

if __name__ == '__main__':
    indiclient=IndiClient()

    while indiclient.connected:
        time.sleep(1)
        if indiclient.cam_ready == 2:
            indiclient.cam_ready == 0
            # indiclient.set_frame(10,10,200,200)
            indiclient.take_exposure(0.01)
            while not indiclient.received_blob:
                time.sleep(0.5)
            break
        #