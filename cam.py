from picamera import PiCamera
from time import sleep
from fractions import Fraction

# Force sensor mode 3 (the long exposure mode), set
# the framerate to 1/6fps, the shutter speed to 6s,
# and ISO to 800 (for maximum gain)
camera = PiCamera(
    resolution=(2592, 1944),
    #resolution=(1024, 768),
    framerate=Fraction(1, 16),
    sensor_mode=1)
camera.shutter_speed = int(0.5 * 100000)
camera.iso = 400
camera.exposure_mode = 'off' # PiCamera.EXPOSURE_MODES['off']
camera.awb_mode = 'off' # PiCamera.AWB_MODES.off
camera.drc_strength = 'off' # PiCamera.DRC_STRENGTHS.off
camera.image_effect = 'none' # PiCamera.IMAGE_EFFECTS.none
camera.still_stats = True
camera.awb_gains = (Fraction(185, 128), Fraction(327, 256))
if False:
    camera.start_preview()
    #camera.preview.alpha = 128
    sleep(1200)
camera.rotation = 180
# Finally, capture an image with a 6s exposure. Due
# to mode switching on the still port, this will take
# longer than 6 seconds
print(f"awb:{camera.awb_gains}, analog:{camera.analog_gain}")
camera.capture('dark.jpg',use_video_port=False)