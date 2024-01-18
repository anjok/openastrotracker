#!python3

import time, os, sys
from util import exec

ra_ratio = 86164/86400
ra_h = 360 / 24 * ra_ratio
dummy = False
# negative means westward
ra_offset = -3

def ra_string_to_number(str):
    global ra_ratio, ra_h
    (hours,min,sec) = str.split(":")
    ra_m = ra_h / 60
    ra_s = ra_m / 60
    return int(sec) * ra_s + int(min) * ra_m + int(hours) * ra_h

def ra_string_to_simple_number(str):
    (hours,min,sec) = str.split(":")
    return int(sec) * 1/3600 + int(min) * 1/60 + (int(hours) + 24) % 24

def dec_string_to_number(str):
    (deg,rest) = str.split("*")
    (min,sec) = rest.split("'")
    return int(sec) * 1/3600 + int(min) * 1/60 + int(deg)

class Calibrate:
    
    def __init__(self,client):
        self.client = client
        self.verbose = True
    
    def getCurrentSteps(self):
        ra_curr_steps = float(self.sendCommandAndWait("Get RA steps", "XGR"))
        dec_curr_steps = float(self.sendCommandAndWait("Get DEC steps", "XGD"))
        return (ra_curr_steps, dec_curr_steps)
        
    def sendCommandAndWait(self, message, cmd):
        if message and self.verbose:
            print(message)
        return self.client.sendCommandAndWait(f":{cmd}#")[1]
                
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
        if True:
            exec(f"indi_setprop -h {self.client.hostname} 'LX200 OpenAstroTech.ON_COORD_SET.SLEW=On'")
            exec(f"indi_setprop -h {self.client.hostname} 'LX200 OpenAstroTech.EQUATORIAL_EOD_COORD.DEC={dec_string_to_number(dec)};RA={ra_string_to_simple_number(ra)}'")
        else:
            self.sendCommandAndWait(f"Set DEC start to {dec}", f"Sd+{dec}")
            self.sendCommandAndWait(f"Set RA start to {ra}", f"Sr{ra}")
            self.sendCommandAndWait("Move", "MS")
        self.waitUntilTrack()

    def promptForSolve(self):
        print("\n>> Now plate solve and sync. Press return to continue.", end="")
        if dummy:
            # print(f"{values}, {len(values)}")
            if len(values):
                return values.pop(0)
        return input()
        
    def calibrate(self, dec=True, ra=True):
        global ra_ratio
        self.sendCommandAndWait("Go Home", "hF")
        # self.sendCommandAndWait("Unpark", "hU")
        (ra_curr_steps, dec_curr_steps) = self.getCurrentSteps()
        ra_end_steps = ra_curr_steps
        dec_end_steps = dec_curr_steps
        print(f"Current steps: RA {ra_curr_steps} DEC {dec_curr_steps}")

        (ra_start_str, dec_start_str) = self.getCurrentPosition()
        print(f"Current RA {ra_start_str} DEC {dec_start_str}")

        # this is the start position from the spreadsheet
        if dec:
            dec_start_str = f"75*00'00"
            self.moveTo(ra_start_str, dec_start_str)
            string = self.promptForSolve()

            # now moving DEC
            (ra_start_str, dec_start_str) = self.getCurrentPosition()
            print(f"\nStarting DEC Calibration (RA: {ra_start_str}, DEC: +{dec_start_str})")
        
            dec_offset = 45
            dec_start = dec_string_to_number(dec_start_str)
            dec_deg, deg_rest = dec_start_str.split("*")
            (dec_min, dec_sec) = deg_rest.split("'")
            dec_next_str = f"{int(dec_deg)-dec_offset:02d}*{dec_min}'{dec_sec}"
            self.moveTo(ra_start_str, dec_next_str)
            
            string = self.promptForSolve()
            if string != "":
                dec_end_str = string
            else:
                (_, dec_end_str)  = self.getCurrentPosition()
            print(f"\nCurrent DEC {dec_end_str} vs expected {dec_next_str}")
            dec_end = dec_string_to_number(dec_end_str)
            dec_diff = dec_offset / (dec_start-dec_end)
            dec_end_steps = round(dec_curr_steps * dec_diff, 1)
            print(f">> Corrected DEC steps from {dec_curr_steps} to {dec_end_steps} diff: {dec_diff}={dec_start}-{dec_end}")
        
        if ra:
            if not dec:
                dec_start_str = f"35*00'00"
                self.moveTo(ra_start_str, dec_start_str)
                string = self.promptForSolve()

            # now moving RA
            (ra_start_str, dec_start_str) = self.getCurrentPosition()
            print(f"\nStarting RA Calibration (RA: {ra_start_str}, DEC: +{dec_start_str})")
            (ra_start_str, dec_curr) = self.getCurrentPosition()
            ra_start = ra_string_to_simple_number(ra_start_str)
            ra_deg, ra_rest = ra_start_str.split(":", 1)
            ra_next_hour = int(ra_deg)+ra_offset
            underflow = False
            overflow = False
            if ra_next_hour < 0 and ra_offset < 0:
                underflow = True
                ra_next_hour = ra_next_hour + 24
            elif ra_next_hour > 24 and ra_offset > 0:
                overflow = True
                ra_next_hour = ra_next_hour - 24
            ra_next_str = f"{ra_next_hour:02d}:{ra_rest}"
            self.moveTo(ra_next_str, dec_curr)
            
            string = self.promptForSolve()
            if string != "":
                ra_end_str = string
            else:
                (ra_end_str, _) = self.getCurrentPosition()
            print(f"\nCurrent RA {ra_end_str} vs expected {ra_next_str}")
            ra_end = ra_string_to_simple_number(ra_end_str)
            if underflow:
                ra_start = ra_start + 24
                ra_actual_diff = ra_start-ra_end
            elif overflow:
                ra_start = ra_start - 24
                ra_actual_diff = ra_start-ra_end
            else:
                ra_actual_diff = ra_end-ra_start
            # print(f"{ra_start} {ra_end}=>{ra_actual_diff/15}")
            if abs(ra_actual_diff) > abs(ra_offset*15) * 4:
                ra_actual_diff = abs(ra_end-ra_start)
                # print(f"fixed {ra_start} {ra_end}=>{ra_actual_diff}")
            ra_diff = ra_string_to_simple_number(f"{abs(ra_offset)}:00:00") / (abs(ra_actual_diff))
            ra_end_steps = round(ra_curr_steps * ra_diff, 1)
            print(f">> Corrected RA steps from {ra_curr_steps} to {ra_end_steps}")
        print(f"\nXSR{ra_end_steps}\nXSD{dec_end_steps}")

class DummyCalibrate(Calibrate):
    def __init__(self, client):
        super().__init__(client)
        self.pos = start
        self.steps = (418.1,419)
    def moveTo(self, ra, dec):
        print(f"Moving to RA {ra} DEC {dec}")
        self.pos = (ra, dec)
        return self.pos
    def getCurrentPosition(self):
        return self.pos
    def getCurrentSteps(self):
        return self.steps
    def promptForSolve(self):
        print("\n>> Now plate solve and sync. Press return to continue.", end="")
        if len(values):
            return values.pop(0)

if __name__ == "__main__":
    dummy = True
    dec = True
    ra = True
    if dummy:
        start_ra = 1
        start = (f"{start_ra:0d}:30:00", "90*00'00")
        start = (f"01:27:12", "90*00'00")
        values = [""]
        if dec:
            values.append("29*00'00")
        if ra:
            end_ra = (start_ra+ra_offset+24) % 24
            #values.append(f"{end_ra:0d}:35:00")
            values.append(f"22:28:46")
    class DummyClient:
        def sendCommandAndWait(self,cmd):
            print(f"command {cmd}")
            return (1,",------,")

    cal = DummyCalibrate(DummyClient())
    # autoPA.isAdjusting()
    cal.calibrate(ra=ra,dec=dec)
