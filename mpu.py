import time
import board
import adafruit_mpu6050 as MPU
import math

radToDeg = 57.2957786

i2c = board.I2C()  # uses board.SCL and board.SDA
mpu = MPU.MPU6050(i2c)
mpu.accelerometer_range = MPU.Range.RANGE_2_G
mpu.gyro_range = MPU.GyroRange.RANGE_250_DPS
mpu.cycle_rate = MPU.Rate.CYCLE_1_25_HZ
mpu.filter_bandwidth = 6
restrictPitch = True

class Pos:
    @property
    def pos(self):
        (accX,accY,accZ) = mpu.acceleration
        (r1,r2,p1,p2) = (0,0,0,0)
        
        r1 = math.atan2(accY,accZ) * radToDeg
        p1 = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * radToDeg
        
        r2 = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * radToDeg
        p2 = math.atan2(-accX,accZ) * radToDeg
        
        return ((r1, r2),(p1, p2))

pos = Pos()
pos.pos

while True:
    (x,y,z) = mpu.acceleration
    print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2"%(x,y,z))
    print("Gyro X:%.2f, Y: %.2f, Z: %.2f degrees/s"%(mpu.gyro))
    print("Temperature: %.2f C"%mpu.temperature)
    print("")
    time.sleep(1)
