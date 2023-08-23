from dom import DOM
import numpy as np
from PIL import Image
import sys
sharpness = 0
for filename in sys.argv[1:]:
    im = Image.open(filename).convert('L') # to grayscale
    array = np.asarray(im, dtype=np.int32)
    gy, gx = np.gradient(array)
    gnorm = np.sqrt(gx**2 + gy**2)
    sharpness = sharpness + np.average(gnorm)
    print(f"{filename}\t{sharpness}")

# initialize
#iqa = DOM()

# using image path
#score = iqa.get_sharpness(filename)
#print("Sharpness IPA:", score)

## using numpy array
#img = np.random.randint(50, size=(10,10,3), dtype=np.uint8)
#score = iqa.get_sharpness(img)
#print("Sharpness:", score)