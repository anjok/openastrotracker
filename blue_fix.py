import numpy as np
from astropy.io import fits
import os

# Load the FITS file
base_dir = "/Volumes/Images/images/ZWO/Iris"

# Function to adjust blue channel to match red channel brightness
def adjust_blue_to_red(fits_file, output_dir):
    # Load the FITS file
    hdul = fits.open(fits_file)
    image_data = hdul[0].data

    # Ensure the file has a 2D image (Bayer pattern assumed)
    if image_data.ndim == 2:
        # Extract the red and blue pixels in the RGGB pattern
        red_pixels = image_data[0::2, 0::2]  # Red pixels in Bayer RGGB pattern
        blue_pixels = image_data[1::2, 1::2]  # Blue pixels in Bayer RGGB pattern

        # Calculate the average or median brightness of red and blue pixels
        avg_red = np.median(red_pixels)
        avg_blue = np.median(blue_pixels)

        # Calculate the scaling factor to match blue brightness to red brightness
        scale_factor = avg_red / avg_blue

        # Adjust the blue pixels by multiplying them by the scaling factor
        image_data[1::2, 1::2] = blue_pixels * scale_factor
        print(f"Scale {scale_factor}")

        # Save the modified FITS file to the output directory
        output_file = os.path.join(output_dir, os.path.basename(fits_file))
        hdul.writeto(output_file, overwrite=True)

    # Close the FITS file
    hdul.close()

# Main function to process all FITS files in the directory
def process_fits_files(input_dir, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop over all files in the input directory
    for filename in os.listdir(input_dir):
        if filename[0] != '.' and filename.endswith(".fits"):
            print(f"Processing {filename}")
            fits_file = os.path.join(input_dir, filename)
            adjust_blue_to_red(fits_file, output_dir)

def process_type(base_dir, type):
    input_directory = f"{base_dir}/Blue/{type}"
    print(f"{input_directory}")
    if os.path.exists(input_directory):
        output_directory = f"{base_dir}/{type}"
        process_fits_files(input_directory, output_directory)

for type in ["Dark", "Flat", "Light"]:
    process_type(base_dir, type)
