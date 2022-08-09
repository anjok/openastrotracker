#!/usr/bin/env python3
import sys, math, time
from mpu import Sensor
from openastroclient import OpenAstroClient

#mpu9250
offsets = [-37.8, -24.2, 23.0, 19.0]
offsets = [-38.2, -24.2, 23.0, 19.0]
##mpu6050
#offsets = [-7.1, -22.5, 2.0, 2.0]

# table
targets = [-1.9, 47.1]
# front
targets = [ -2.65, 45.72]
# back

epsilon = 0.5

sensor = Sensor(offsets=offsets)

class Axis:
    def __init__(self, target, steps, meade):
        self.target = target
        self.steps = steps
        self.meade = meade
        self.speed = -1
    @property
    def is_close(self, pos):
        return math.fabs(self.target - pos) < epsilon
    @property
    def is_ra(self):
        return self.meade == 'r'
    @property
    def current_position(self):
        (a,b) = client.sendCommandAndWait(":GX#")
        array = b.split(",")[2:4]
        index = 0 if self.is_ra else 1
        return array[index]
        
    def do_home(self, pos):
        sgn = -1 if self.is_ra else 1
        steps = int(self.steps * sgn * (self.target - pos))
        if(math.fabs(steps) < 500):
            speed = 1
        elif(math.fabs(steps) < 1000):
            speed = 2
        else:
            speed = 3
        if self.speed != speed:
            self.speed = speed
            speed_char = "GCMS"[self.speed]
            client.sendCommandAndWait(f":R{speed_char}#")
        cmd = f":MX{self.meade}{steps}#"
        return cmd
    
    def home(self):
        done = False
        while not done:
             x,y = sensor.angles
             pos = x if self.is_ra else y
             diff = self.target - pos
             done = math.fabs(diff) < epsilon
             if not done:
                cmd = self.do_home(pos)
                print(f"\nTarget:{self.target:5.2f} pos:{pos:5.2f} delta:{diff:5.2f}")
                client.sendCommand(cmd)
                current_position = self.current_position
                new_position = self.current_position
                while new_position != current_position:
                    print(f"\rWaiting until target is reached, current: {current_position}, new: {new_position}", end="")
                    current_position = new_position
                    new_position = self.current_position
                    time.sleep(1)
                #print(cmd)
                #time.sleep(10)

ra = Axis(targets[0], 314.2, "r")
dec = Axis(targets[1], 314.2, "d")

if __name__ == '__main__':
    client = OpenAstroClient(hostname="localhost")
    client.debug = True
    x,y = sensor.angles
    print(f"\rX: {x:5.2f} Y: {y:5.2f} dX:{x-ra.target:5.2f} dY:{y-dec.target:5.2f}", end="")
    for i in range(0,2):
        ra.home()
        dec.home()
    client.sendCommandAndWait(":Q#")
    client.sendCommandAndWait(":SHP#")
    x,y = sensor.angles
    print(f"\rX: {x:5.2f} Y: {y:5.2f} dX:{x-ra.target:5.2f} dY:{y-dec.target:5.2f}", end="")
    time.sleep(1)
