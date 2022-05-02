#!/usr/bin/env python3
import sys, math, time
from mpu import Sensor
from openastroclient import OpenAstroClient

#mpu9250
offsets = [-37.8, -24.2, 23.0, 19.0]

sensor = Sensor(offsets=offsets)

class Axis:
    def __init__(self, target, steps, meade):
        self.target = target
        self.steps = steps
        self.meade = meade
    @property
    def is_close(self, pos):
        return self.target - pos < 2
        
    def do_home(self, pos):
        sgn = -1 if self.meade == 'r' else 1
        steps = int(self.steps * sgn * (self.target - pos))
        cmd = f":MX{self.meade}{steps}#"
        return cmd
    
    def home(self):
        done = False
        while not done:
             x,y = sensor.angles
             pos = x if self.meade == 'r' else y
             diff = math.fabs(pos-self.target)
             done = diff < .5
             if not done:
                cmd = self.do_home(pos)
                print(f"\r{self.meade} pos:{pos:5.2f} delta:{diff:5.2f}", end="")
                client.sendCommand(cmd)

if __name__ == '__main__':
    client = OpenAstroClient(hostname="localhost")
    client.sendCommand(":Q#")
    ra = Axis(11.2, 314.2, "r")
    dec = Axis(52.7, 314.2, "d")
    x,y = sensor.angles
    print(f"\rX: {x:5.2f} Y: {y:5.2f} dX:{x-ra.target:5.2f} dY:{y-dec.target:5.2f}", end="")
    for i in range(0,2):
        ra.home()
        dec.home()
    client.sendCommand(":Q#")
    x,y = sensor.angles
    print(f"\rX: {x:5.2f} Y: {y:5.2f} dX:{x-ra.target:5.2f} dY:{y-dec.target:5.2f}", end="")
    time.sleep(1)
