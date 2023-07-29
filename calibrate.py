#!python3

import time
ra_ratio = 86164/86400

def ra_string_to_number(str):
    global ra_ratio
    (hours,min,sec) = str.split(":")
    ra_h = 360 / 24 * ra_ratio
    ra_m = ra_h / 60
    ra_s = ra_m / 60
    return int(sec) * ra_s + int(min) * ra_m + int(hours) * ra_h

def dec_string_to_number(str):
    (deg,rest) = str.split("*")
    (min,sec) = rest.split("'")
    return int(sec) * 1/3600 + int(min) * 1/60 + int(deg)

class Calibrate:
    
    def __init__(self,client):
        self.client = client
        self.verbose = False
        
    def sendCommandAndWait(self, message, cmd):
        if message and self.verbose:
            print(message)
        return self.client.sendCommandAndWait(f":{cmd}#")[1]
    
    def waitUnitPos(self,message,match,command):
        while True:
            pos=self.sendCommandAndWait(message, command)
            if pos == match:
                return
            time.sleep(2)
            
    def waitUntilTrack(self):
        while True:
            time.sleep(2)
            pos=self.sendCommandAndWait(None, "GX").split(",")[0]
            if pos == "Tracking":
                return
    def getCurrentPosition(self):
        dec_str = self.sendCommandAndWait("Get DEC start", f"GD")[1:]
        ra_str = self.sendCommandAndWait("Get RA start", f"GR")
        return (ra_str, dec_str)
        
    def moveTo(self, ra, dec):
        print(f"Moving to RA {ra} DEC {dec}")
        self.sendCommandAndWait(f"Set DEC start to {dec}", f"Sd+{dec}")
        self.sendCommandAndWait(f"Set RA start to {ra}", f"Sr{ra}")
        self.sendCommandAndWait("Move", "MS")
        self.waitUntilTrack()
        
    def calibrate(self):
        global ra_ratio
        #self.sendCommandAndWait("Go Home", "hF")
        self.sendCommandAndWait("Unpark", "hU")
        ra_curr_steps = float(self.sendCommandAndWait("Get RA steps", "XGR"))
        dec_curr_steps = float(self.sendCommandAndWait("Get DEC steps", "XGD"))
        ra_end_steps = ra_curr_steps
        dec_end_steps = dec_curr_steps
        print(f"Current steps: RA {ra_curr_steps} DEC {dec_curr_steps}")
        (ra_start_str, dec_start_str) = self.getCurrentPosition()
        print(f"Current RA {ra_start_str} DEC {dec_start_str}")
        dec_start_str = f"70:00:00"
        if True:
            self.moveTo(ra_start_str, dec_start_str)
            print("\n>> Now plate solve and sync. Press return to continue.", end="")
            string = input()
        # this is the start position from the spreadsheet
        if False:
            # now moving DEC
            (ra_start_str, dec_start_str) = self.getCurrentPosition()
            print(f"\nStarting DEC Calibration RA: {ra_start_str}, DEC: +{dec_start_str}")
        
            dec_offset = 45
            dec_start = dec_string_to_number(dec_start_str)
            dec_deg, deg_rest = dec_start_str.split("*")
            (dec_min, dec_sec) = deg_rest.split("'")
            dec_next_str = f"{int(dec_deg)-dec_offset:02d}:{dec_min}:{dec_sec}"
            self.moveTo(ra_start_str, dec_next_str)
            
            print("\n>> Now plate solve and sync. Press return to continue.", end="")
            string = input()
            if string != "":
                dec_end_str = string
            else:
                dec_end_str = self.sendCommandAndWait("Get DEC end", f"GD")[1:]
            print(f"\nCurrent DEC {dec_end_str} vs expected {dec_next_str}")
            dec_end = dec_string_to_number(dec_end_str)
            dec_diff = dec_offset / (dec_start-dec_end)
            dec_end_steps = round(dec_curr_steps * dec_diff, 1)
            print(f">> Corrected DEC steps from {dec_curr_steps} to {dec_end_steps}")
        
        if True:
            # now moving RA
            (ra_start_str, dec_start_str) = self.getCurrentPosition()
            print(f"\nStarting RA Calibration RA: {ra_start_str}, DEC: +{dec_start_str}")
            ra_offset = 3
            (ra_start_str, dec_curr) = self.getCurrentPosition()
            ra_start = ra_string_to_number(ra_start_str)
            ra_deg, ra_rest = ra_start_str.split(":", 1)
            ra_next_hour = int(ra_deg)+ra_offset
            ra_next_str = f"{ra_next_hour:02d}:{ra_rest}"
            self.moveTo(ra_next_str, dec_curr)
            
            print("\n>> Now plate solve and sync. Press return to continue.", end="")
            string = input()
            if string != "":
                ra_end_str = string
            else:
                ra_end_str = self.sendCommandAndWait("Get RA end", f"GR")
            print(f"\nCurrent RA {ra_end_str} vs expected {ra_next_str}")
            ra_end = ra_string_to_number(ra_end_str)
            if ra_end < ra_start:
                ra_end = ra_end + 360 * ra_ratio
            ra_diff = ra_string_to_number(f"{ra_offset}:00:00") / (ra_end-ra_start)
            ra_end_steps = round(ra_curr_steps * ra_diff, 1)
            print(f">> Corrected RA steps from {ra_curr_steps} to {ra_end_steps}")
        print(f"\nXSR{ra_end_steps}\nXSD{dec_end_steps}")

if __name__ == "__main__":
    class DummyClient:
        def sendCommandAndWait(self,cmd):
            print(cmd)
            return (1,",------,")

    cal = Calibrate(DummyClient())
    # autoPA.isAdjusting()
    cal.calibrate()
