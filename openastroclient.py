
import time, threading, io, sys
import PyIndi

log = print
cmdName = "Meade"

class OpenAstroClient(PyIndi.BaseClient):
    def __init__(self, hostname="localhost", port=7624):
        super(OpenAstroClient, self).__init__()
        self.setServer(hostname,int(port))
        self.blobEvent=threading.Event()
        if (not(self.connectServer())):
            raise f"No indiserver running on {hostname}:{port} - Run server in Ekos first."
        telescopeName = "LX200 OpenAstroTech"
        self.telescope=self.getDevice(telescopeName)
        while not(self.telescope):
            time.sleep(0.5)
            log(f"Waiting for {telescopeName}")
            self.telescope=self.getDevice(telescopeName)
        self.meadeProp = self.telescope.getText(cmdName)
        while not(self.meadeProp):
            log(f"Waiting for '{cmdName}'")
            time.sleep(0.5)
            meadeProp=self.telescope.getText(cmdName)
    def sendCommand(self,cmd):
        self.meadeResultRead = False
        self.meadeProp[0].text = cmd
        self.sendNewText(self.meadeProp)
        while not(self.meadeResultRead):
            log(f"Waiting for result: {cmd}")
            time.sleep(1)
        return self.meadeResult.s,self.meadeResult.tp.text
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
        log(f">> newText=>{tvp.label}={tvp.tp.text}")
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass

if __name__ == '__main__':
    c=OpenAstroClient()
    while True:
        string = input()
        c.sendCommand(f":{string}#")

