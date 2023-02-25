
import time, threading, io, sys
import PyIndi
import readline
import autopa
import calibrate

from os.path import split

cmdName = "Meade"

class OpenAstroClient(PyIndi.BaseClient):
    def __init__(self, hostname="astroberry.local", port=7624):
        super(OpenAstroClient, self).__init__()
        self.setServer(hostname,int(port))
        self.blobEvent=threading.Event()
        self.debug = False
        if (not(self.connectServer())):
            raise Exception(f"No indiserver running on {hostname}:{port} - Run server in Ekos first.")
        telescopeName = "LX200 OpenAstroTech"
        self.telescope=self.getDevice(telescopeName)
        while not(self.telescope):
            time.sleep(0.5)
            self.log(f"Waiting for {telescopeName}")
            self.telescope=self.getDevice(telescopeName)
        if True:
            self.connect()
            self.meadeProp = self.telescope.getText(cmdName)
            while not(self.meadeProp):
                self.log(f"Waiting for '{cmdName}'")
                time.sleep(0.5)
                meadeProp=self.telescope.getText(cmdName)
    @property
    def debug(self):
        return self._debug
    @debug.setter
    def debug(self, val):
        self._debug = val
    def sendCommand(self,cmd):
        self.meadeResultRead = False
        self.meadeProp[0].text = cmd
        self.log(f">> Sending: {cmd}")
        self.sendNewText(self.meadeProp)
        time.sleep(1.0)
        return ("ok", "ok")
    def sendCommandAndWait(self,cmd):
        self.meadeResultRead = False
        self.meadeProp[0].text = cmd
        self.log(f">> Sending: {cmd}")
        self.sendNewText(self.meadeProp)
        while not(self.meadeResultRead):
            self.log(f"\r<<Waiting for result: {cmd}", end="")
            time.sleep(1)
        self.log(f"<< Received: {self.meadeResult.s} {self.meadeResult.tp.text}")
        return self.meadeResult.s,self.meadeResult.tp.text
    def log(self,msg,end="\n"):
        if self.debug:
            print(msg,end=end)
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        if tvp.label == cmdName:
            self.meadeResultRead = True
            self.meadeResult = tvp
        self.log(f">> newText=>{tvp.label}={tvp.tp.text}")
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass
    def toggleSwitch(self, switch, index):
        for i in range(0,len(switch)):
            state = PyIndi.ISS_ON if i == index else PyIndi.ISS_OFF
            switch[i].setState(state)
        self.sendNewSwitch(switch) # send this new value to the device
    def getProp(self, device, propType, propName):
        func = None
        if propType.lower() == "switch":
            func = self.telescope.getSwitch
        elif propType.lower() == "number":
            func = self.telescope.getNumber
        elif propType.lower() == "text":
            func = self.telescope.getText
        result = None
        if func != None:
            result = func(propName)
            while not(result):
                time.sleep(0.5)
                result = func(propName)
        return result
    def connect(self):
        telescope_connect = self.getProp(self.telescope, "switch", "CONNECTION")
        if not(self.telescope.isConnected()):
            self.toggleSwitch(telescope_connect, 0)
    def disconnect(self):
        telescope_connect = self.getProp(self.telescope, "switch", "CONNECTION")
        # if the telescope device is not connected, we do connect it
        while self.telescope.isConnected():
            self.toggleSwitch(telescope_connect, 1)
        time.sleep(1)

class Settings: 
    def __init__(self):
        self.dec_lower = None
        self.dec_upper = None
        self.ra_steps = None
        self.dec_steps = None
        self.dec_park = None
        self.ra_offset = None
        pass
    def save(self):
        pass
    def load(self):
        pass
    def read(self):
        if(self.dec_lower):
            return
        res = sendCommandAndWait(f"XGDLL")[1]
        res = res.split("|")
        self.dec_lower = int(res[0])
        self.dec_upper = int(res[1])
        self.ra_steps = float(sendCommandAndWait(f"XGR")[1])
        self.dec_steps = float(sendCommandAndWait(f"XGD")[1])
        self.dec_park = int(sendCommandAndWait(f"XGDP")[1])
        self.ra_offset = int(sendCommandAndWait(f"XGHR")[1])
    def write(self):
        pass
    def print(self):
        print(f"""DEC Limits:
    Lower: {self.dec_lower}
    Upper: {self.dec_upper}
Steps:
    RA: {self.ra_steps}
    DEC: {self.dec_steps}
Offsets:
    DEC: {self.dec_park}
    RA: {self.ra_offset}""")
        
if __name__ == '__main__':
    c = OpenAstroClient()
    s = Settings()
    pa = autopa.AutoPA(c)
    cal = calibrate.Calibrate(c)
    def sendCommandAndWait(cmd):
        res = c.sendCommandAndWait(f":{cmd}#")
        print(f"# {cmd} -> {res}")
        return res
    def status():
        res = sendCommandAndWait(f"GX")[1].split(",")[0]
        return res
    def print_settings():
        print("# settings")
        s.read()
        s.print()
    def home():
        # stop motors
        sendCommandAndWait(f"Q")
        # get status for first display
        sendCommandAndWait(f"GX")
        # set slew speed to M
        sendCommandAndWait(f"RC")
        # set speed
        sendCommandAndWait(f"GCMS3")
        # NOTE: re-check when the sensor was bent
        # find RA home offset (just to be safe)
        sendCommandAndWait(f"XSHR-1200")
        # find RA home in 2 hours range
        if True:
            sendCommandAndWait(f"MHRR3")
            while True:
                res = status()
                print(res)
                if res == 'Tracking':
                    break
        # set slew speed to highest again
        sendCommandAndWait(f"RS")
        # move to 90 deg
        sendCommandAndWait(f"MXd12900")
        while True:
            res = status()
            print(res)
            if res == 'Tracking':
                break
        # set home pos
        sendCommandAndWait(f"SHP")
        # stop motors
        sendCommandAndWait(f"Q")
        sendCommandAndWait(f"GX")
        print("# homing done")
    sendCommandAndWait(f"Q")
    def pa():
        pa.alignOnce()
    def calibrate():
        cal.calibrate()
    while True:
        print(">> Command: ", end="")
        string = input()
        if len(string) > 1 and string[0] == '#':
            command = string.split()
            if command[0]  == '#sleep' and len(command) > 1:
                time.sleep(int(command[1]))
            if command[0]  == '#home':
                home()
            if command[0]  == '#prefs':
                print_settings()
            if command[0]  == '#cal':
                calibrate()
            if command[0]  == '#pa':
                pa()
        else:
            result = c.sendCommandAndWait(f":{string}#")
            print(f">> Result: {result}")

