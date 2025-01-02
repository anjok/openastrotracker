import time, os, readline

default_delay = 0.002
has_rpi = False
steps_per_angle = 1260/90
fast = True
prefs_file = os.path.expanduser("~/.rotator")

try:
    from gpiozero import LED
except:
    class LED:
        def __init__(self,pin):
            pass
        def on(self):
            # print("Pin ON")
            pass
        def off(self):
            # print("Pin OFF")
            pass


def read_last_angle():
    if os.path.exists(prefs_file):
        try:
            with open(prefs_file, "r") as f:
                return float(f.read())
        except (ValueError, FileNotFoundError):
            pass
    return 0.0

def save_current_angle(current_angle):
    with open(prefs_file, "w") as f:
        f.write(str(current_angle))

def to_angle(s, default=None):
    try:
        angle = float(s)
        if angle > 90:
            angle = 90
        elif angle < -90:
            angle = -90
        return angle
    except (ValueError, TypeError):
        return default

class Stepper:
    # Define GPIO pins
    IN1 = 18
    IN2 = 17
    IN3 = 27
    IN4 = 22

    # Define sequence
    seq = [
        [1,0,0,1],
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1]]
    fast_seq = [
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]]

    def __init__(self):
        # Set GPIO mode
        self._delay = default_delay
        self._running = False
        self._angle = read_last_angle()
        self._position = self._angle * (steps_per_angle * len(Stepper.fast_seq) * 2)
        self.leds = []
        self.init_pins()

    def init_pins(self):
        self.leds.append(LED(Stepper.IN1))
        self.leds.append(LED(Stepper.IN2))
        self.leds.append(LED(Stepper.IN3))
        self.leds.append(LED(Stepper.IN4))

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, val):
        self._delay = val

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, val):
        self._running = val

    @property
    def position(self):
        return self._position
    @property
    def angle(self):
        return self._angle

    @position.setter
    def position(self, val):
        self._position = val

    def setStep(self, w1, w2, w3, w4):
        self.leds[0].on() if w1 else self.leds[0].off()
        self.leds[1].on() if w2 else self.leds[1].off()
        self.leds[2].on() if w3 else self.leds[2].off()
        self.leds[3].on() if w4 else self.leds[3].off()

    def move(self, steps, reverse, fast=False):
        seq = (Stepper.fast_seq if fast else Stepper.seq)
        seq = (list(reversed(seq)) if reverse else seq)
        increase = (2 if fast else 1)
        delay = self.delay * increase
        increase = (-increase if reverse else increase)
        self.running = True
        for i in range(steps):
            print(f"Pos {self.position}", end="\r")
            if not(self.running):
                print("Abort")
                break
            for step in seq:
                self.setStep(step[0], step[1], step[2], step[3])
                self._position = self._position + increase
                time.sleep(delay)
        self.setStep(0, 0, 0, 0)
        self._angle = self.position / (steps_per_angle * len(Stepper.fast_seq) * 2)
        self.running = False

    def forward(self, steps, fast=False):
        self.move(steps, False, fast)

    def backward(self, steps, fast=False):
        self.move(steps, True, fast)

    def move_to(self, to_angle):
        if to_angle != None:
            diff = to_angle - self.angle
            steps = int(diff * steps_per_angle)
            print(f">> move from {self.angle} to {to_angle} ({diff}) by {steps}")
            if steps > 0:
                stepper.forward(steps, fast)
            elif steps < 0:
                stepper.backward(-steps, fast)
            print(f"<<moved from {self.angle} to {to_angle} ({diff}) by {steps}")
            print(f"")
        
    def cleanup(self):
        save_current_angle(self.angle)
        self.setStep(0, 0, 0, 0)
        time.sleep(1)
        pass

if __name__ == '__main__':
    stepper = Stepper()
    try:
        print(f"Delay: {stepper.delay}")
        while True:
            line = input(">> ")
            target = to_angle(line)
            stepper.move_to(target)
    except KeyboardInterrupt:
        pass
    finally:
        
        stepper.cleanup()
