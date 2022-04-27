#!/usr/bin/env python3
import sys, math, time
import smbus

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
REG_CONFIG   = 0x1A #  5Hz bandwidth (lowest) for smoothing
REG_ACCEL_XOUT_H = 0x3B
REG_TEMP_OUT_H   = 0x41
REG_PWR_MGMT_1   = 0x6B
REG_WHO_AM_I     = 0x75

class MPU:
    def __init__(self):
        self.bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
        self.address = 0x68 # This is the address value read via the i2cdetect command
        self.bus.write_byte_data(self.address, REG_PWR_MGMT_1 , 0)  # Now wake the 6050 up as it starts in sleep mode
        self.bus.write_byte_data(self.address, REG_CONFIG , 6)      # Reduce BW to 5HZ 
    
    def read_byte(self, adr):
        return self.bus.read_byte_data(self.address, adr)
    
    def read_word(self,adr):
        high = self.read_byte(adr)
        low = self.read_byte(adr+1)
        val = (high << 8) + low
        return val
    
    def read_word_2c(self,adr):
        val = self.read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val
    
    def dist(self, a,b):
        return math.sqrt((a*a)+(b*b))
    
    def get_y_rotation(self,x,y,z):
        radians = math.atan2(x, self.dist(y,z))
        return math.degrees(radians)
    
    def get_x_rotation(self,x,y,z):
        radians = math.atan2(y, self.dist(x,z))
        return math.degrees(radians)
         
    @property
    def angles(self):
        accel_xout = self.read_word_2c(0x3b)
        accel_yout = self.read_word_2c(0x3d)
        accel_zout = self.read_word_2c(0x3f)
        accel_xout_scaled = accel_xout / 4096   # 16384.0 8192
        accel_yout_scaled = accel_yout / 4096
        accel_zout_scaled = accel_zout / 4096
        x = self.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        y = self.get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        return (x,y)

mpu = MPU()

class Axis:
    def __init__(self, target, steps, error, meade):
        self.target = target
        self.steps = steps
        self.error = error - target
        self.meade = meade
    @property
    def is_close(self, pos):
        return self.target - pos < 0.3
        
    def home(self, pos):
        steps = -int(self.steps * (self.target - (pos - self.error)))
        print(f":MX{self.meade}{steps}#")
        return steps/self.steps

ra = Axis(0, 314.2, -10.8, "r")
dec = Axis(48.1, 314.2, 65.3, "d")
ra.home(mpu.angles[0])
dec.home(mpu.angles[1])
mpu = MPU()
while True:
    (x,y) = mpu.angles
    if not(ra.is_close(x)):
        steps = ra.home(x)
    else:
        break

while True:
    (x,y) = mpu.angles
    if not(dec.is_close(y)):
        steps = dec.home(y)
    else:
        break
