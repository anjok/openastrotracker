import glob
import re
from datetime import datetime, date
import json
import math
#from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os
import logging
import time
from pathlib import Path

class AutoPA:

    def __init__(self,client):
        self.client = client
        self.verbose = True
        self.autorun = False
        self.aligned = False
        self.accuracy = 0.10
        self.lastEntry = None

    def getLatestLogEntry(self, logpath, expression):
        try:
            list_of_files = glob.glob(logpath)
            latest_file = max(list_of_files, key=os.path.getctime)
            logfileModification = os.path.getmtime(latest_file)
            logging.debug(latest_file)
            inFile = open(latest_file,"r")
            result = ()
            lines = inFile.readlines()
            lines.reverse()
            for line in lines:
                result = re.findall(expression, line)
                if len(result) > 0 and len(result[0]) >= 9:
                    def to_arc_secs(values):
                        logging.debug(values)
                        #return (int(d)*60)+int(m)+int(s)/60
                        return int(((int(values[0])*60)+int(values[1])+int(values[2])/60)*100)/100
                    result = result[0]
                    result = (result[0], to_arc_secs(result[1:4]), to_arc_secs(result[4:7]), to_arc_secs(result[7:10]))
                    logging.debug(f"latestLogEntry: {result}, lastMod:{logfileModification}")
                    return (result, logfileModification)
            return (result, logfileModification)
        except FileNotFoundError:
            raise FileNotFoundError
 
    def sendCommand(self, cmd):
        res = self.client.sendCommandAndWait(f"{cmd}")
        print(res)
        return res[1]

    def move(self, command):
        logging.info(f"Sending: {command}")
        while(self.isAdjusting()):
            time.sleep(1.0)

    def isAdjusting(self):
        try:  
            logging.debug("Getting mount status...")
            result = self.sendCommand(":GX#")
            logging.debug(result)
            if not result:
                raise Exception
            logging.debug(result)
            status = re.search(",(......),", result)[1]
            if status[3]=="-" and status[4]=="-":
                return False
            else:
                return True
        except:
            logging.error("Problem determining mount status. Verify mount is connected to INDI. Stopping AutoPA.")
            raise ConnectionError

    def start(self):
        if self.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)
        if self.aligned:
            logging.info("Starting AutoPA routine")
            self.aligned = False

    def stop(self):
        self.aligned = True
        logging.info("Stopping AutoPA routine")

    def close(self):
        sys.exit(self)
           
    def align(self):
        self.start()
        done = False
        while not done:
            time.sleep(4)
            try:
                done = self.alignOnce()
            except:
                logging.exception("Error occurred")
                break
        self.stop()
        if self.autorun:
            sys.exit(0)

    def alignOnce(self):
        (line, timestamp) = self.getLatestLogEntry(softwareTypes["logpath"], softwareTypes["expression"])
        if len(line) > 0:
            #Entry date is based on file timestamp, entry time is based on log entry data
            currentEntry = datetime.strptime(datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d") + " " + line[0][:-1], '%Y-%m-%d %H:%M:%S.%f')
            if self.lastEntry == None or currentEntry > self.lastEntry:
                (alt, az, total) = line[1:]
                logging.info(f"Errors Alt {alt:.3f}\' Az: {az:.3f}\' Total: {total:.3f}\'")
                if abs(total) < self.accuracy:
                    logging.info(f"Polar aligned to within {alt*60:.0f}\" altitude and {az*60:.0f}\" azimuth.")
                    return True
                else:
                    logging.info("Correction needed.")
                    if abs(alt) > self.accuracy:
                        result = self.move(f":MAL{alt}#")
                        logging.debug(f"Adjusted altitude by {alt:.3f} arcminutes.")
                    if abs(az) > self.accuracy:
                        result = self.move(f":MAZ{az*(-1)}#")
                        logging.debug(f"Adjusted azimuth by {az:.3f} arcminutes.")
                    self.lastEntry = currentEntry
            else:
                logging.info(f"No changes after {currentEntry}")
        return False

today = date.today().strftime("%Y-%m-%d")
kstarsHome = f"{Path.home()}/Library/Application Support/kstars"
softwareTypes = {
    "expression": "(\d{2}:\d{2}:\d{2}.\d{3}).*(?:PAA Refresh).*(?:Corrected)\s+az:\s*(-?\d+).\s+(\d+).\s+(\d+)...*?\s+alt:\s*(-?\d+).\s+(\d+).\s+(\d+)...*?\s+total:\s*(-?\d+).\s+(\d+).\s+(\d+)..*",
    "logpath": f"{kstarsHome}/logs/{today}/*.txt"
}

if __name__ == "__main__":
    class DummyClient:
        def sendCommandAndWait(self,cmd):
            print(cmd)
            return (1,",------,")

    autoPA = AutoPA(DummyClient())
    # autoPA.isAdjusting()
    autoPA.align()
