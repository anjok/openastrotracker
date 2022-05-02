# from msilib.schema import Error
import time, math, sys
import board
import adafruit_mpu6050 as MPU6050

i2c = board.I2C()  # uses board.SCL and board.SDA
mpu = MPU6050.MPU6050(i2c)
mpu.accelerometer_range = MPU6050.Range.RANGE_2_G
mpu.gyro_range = MPU6050.GyroRange.RANGE_250_DPS
mpu.cycle_rate = MPU6050.Rate.CYCLE_1_25_HZ
mpu.filter_bandwidth = 6

class Sensor:
    def __init__(self, offsets=[0, 0, 0, 0.0]):
        self._offsets = offsets
        self.id = mpu._device_id

    @property 
    def raw_acceleration(self):
        (accX,accY,accZ) = mpu.acceleration
        accel = [accX,accY,accZ]
        factor = 100
        for j in range(0,3):
            accel[j] = accel[j]/MPU6050.STANDARD_GRAVITY * factor
            accel[j] = accel[j] + self._offsets[j]
        (accX,accY,accZ) = accel
        return (accX,accY,accZ)
        
    @property 
    def averaged_acceleration(self):
        sumX,sumY,sumZ = (0,0,0)
        cnt = 10
        for i in range(0,cnt):
            accX,accY,accZ = self.raw_acceleration
            sumX,sumY,sumZ = (sumX+accX,sumY+accY,sumZ+accZ)
            time.sleep(0.01)
        return (sumX/cnt,sumY/cnt,sumZ/cnt)
        
    @property
    def acceleration(self):
        (accX,accY,accZ) = self.averaged_acceleration
        return (accX,accY,accZ)

    @property
    def angles(self):
        (accX,accY,accZ) = self.acceleration
        def dist(x,y):
            return math.sqrt((x**2)+(y**2))
        def angle(x,y,z):
            return math.degrees(math.atan(x/dist(y,z)))
            return math.degrees(math.atan2(x,dist(y,z)))
        x = angle(accY,accX,accZ)
        y = angle(accX,accY,accZ)
        return (x,y)

    @property 
    def temperature(self):
        return mpu.temperature - offsets[3]

if __name__ == "__main__":
    # mpu 6050 1
    # offsets = [-7.1, -22.5, 2.0, 2.0]
    # mpu 9250 1
    # offsets = [-38.4, -23.2, 23.5, 19.0]
    offsets = [-38.4, -23.2, 23.5, 19.0]
    offsets = [-37.8, -24.2, 23.0, 19.0]
    #offsets = [0, 0, 0, 0.0]

    sensor = Sensor(offsets=offsets)
    #sensor.raw_acceleration
    #(x,y,z) = sensor.acceleration
    print("""
        Place sensor with z-axis upwards. 
        Wait a bit, press return, move the z-axis perpendicular to gravity.
        Wait a bit and then note the X/Y of the first and the Z of the second reading.
        Negate those and put it in the offsets array. 
        Use your sensor with:
          sensor = Sensor(offsets=[7.0,-7.6,25.0,13.0])
        """)
    while True:
        try:
            (x,y,z) = sensor.acceleration
            (X,Y) = sensor.angles
            print(f"""\rPos(X: {X:5.2f} Y:{Y:5.2f}) Accel(X:{x:5.2f}  Y:{y:5.2f}, Z:{z:5.2f}) Temp({sensor.temperature:.2f}) C""", end="")
            time.sleep(1)
        except KeyboardInterrupt:
            print()
            sys.exit(0)
        except Exception as e:
            print(e)
            continue
