#!/usr/bin/python3
import os
import rawpy
import glob
import io
import sys
import subprocess
from gooey import Gooey, GooeyParser
from PIL import Image
from pathlib import Path
from argparse import ArgumentParser

'''
Generates 3x3 images from fits and cr2 files for easier evaluation.
pip3 install gooey rawpy numpy opencv-python
'''

def read_raw_image(path):
    with rawpy.imread(path) as raw:
        thumb = raw.extract_thumb()
        image = Image.open(io.BytesIO(thumb.data))
        return image

def read_fits_image(path):
    from astropy.io import fits
    import cv2
    import numpy as np
    from astropy.visualization import ZScaleInterval

    with fits.open(path) as hdul:
        data = hdul[0].data
    zscale = ZScaleInterval()
    data = (zscale(data)*255).astype(np.uint8)
    rgb = cv2.cvtColor(data, cv2.COLOR_BAYER_RGGB2RGB)
    cv2.imwrite('/tmp/fits.jpg', rgb)
    return Image.open('/tmp/fits.jpg')

def create_crop(path):
    if path.endswith('.fits'):
        image = read_fits_image(path)
    else:
        image = read_raw_image(path)
    w,h=image.size
    cw,ch = int(w/9), int(h/9)
    dest = Image.new('RGB', (cw*3, ch*3))
    for i in range(0, 3): 
        for j in range(0, 3): 
            bx, by = cw*i*3+cw, ch*j*3+ch
            box = (bx, by, bx+cw, by+ch)
            # print(box)
            crop = image.crop(box)
            dest.paste(crop, (cw*i,ch*j))
    out = os.path.basename(path)
    dest.save(f"{os.path.dirname(path)}/crops/{out}.jpg")
    dest.close()
    image.close()

def read_source_files(dir):
    files = glob.glob(f"{dir}/*.cr2") +  glob.glob(f"{dir}/*.fits")
    print(files)
    return files

def clean(dir):
    print(f"cleaning up previous run")
    Path(f"{dir}/crops").mkdir(parents=True, exist_ok=True)
    crops = glob.glob(f"{dir}/crops/*.jpg")
    for file in crops:
        print(f"Deleting: {file}")
        os.remove(file)

def create_crops(dir):
    # creating crops
    print(f"creating crops")
    files = read_source_files(dir)
    files.sort()
    for file in files:
        print(f"Creating crop: {file}")
        create_crop(file)

def main(args):
    dir = args.path
    if args.create:
        clean(dir)
        create_crops(dir)
        subprocess.run(["open", f"{dir}/crops"]) 
    else:
    # wait here
        crops = glob.glob(f"{dir}/crops/*.jpg")
        files = read_source_files(dir)
        deletes = []
        for file in files:
            crop_name = os.path.basename(file)
            crop_file = f"{dir}/crops/{crop_name}.jpg"
            if not crop_file in crops:
                deletes.append(crop_name)
        if len(deletes) and len(files) != len(deletes):
            Path(f"{dir}/crap").mkdir(parents=True, exist_ok=True)
            for file in deletes:
                # print(f"mv {dir}/{file} {dir}/crap/{file}")
                subprocess.run(["mv", f"{dir}/{file}", f"{dir}/crap/{file}"])
                subprocess.run(["open", f"{dir}/crap"]) 


@Gooey()
def run_ui():
    parser = GooeyParser(description='Process thumbnails for astrophotography')
    parser.add_argument("path", help="Path to raw images", widget="DirChooser")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-c', '--create', action='store_true', help='Creates a 3x3 jpg for each input image')
    mode.add_argument('-s', '--sort', action='store_true', help='Sort images by moving those not present anymore')
    args = parser.parse_args()
    main(args)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-x", "--no-gui", action='store_true')
    if '-x' not in sys.argv:
        # parser.add_argument("-x", "--no-gui", action='store_true')
        run_ui()
    else:
        parser.add_argument("path", help="Path to raw images")
        parser.add_argument('-c', '--create', action='store_true', help='Creates a 3x3 jpg for each input image')
        parser.add_argument('-s', '--sort', action='store_true', help='Sort images by moving those not present anymore')
        args = parser.parse_args()
        main(args)

