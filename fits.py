import argparse
from astropy.io import fits

def extract_fits_tag(fits_files, tags):
    """
    Extract and display specific header tag from multiple FITS files.

    :param fits_files: List of paths to FITS files
    :param tags: Specific tag to extract from the FITS file headers
    """
    for fits_file in fits_files:
        try:
            print(f"{fits_file}:")
            # Open the FITS file
            with fits.open(fits_file) as hdul:
                # Loop through each header unit in the FITS file
                for idx, hdu in enumerate(hdul):
                    header = hdu.header
                    for key, value in header.items():
                        if tags == None or key in tags:
                            print(f"   {key}: {value}")
        except Exception as e:
            print(f"Error opening FITS file {fits_file}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract FITS header tags from multiple files.")
    parser.add_argument('files', nargs='+', help="Paths to the FITS files")
    parser.add_argument('-t', '--tags', required=False, help="Header tag to extract")

    # Parse the arguments
    args = parser.parse_args()
    tags = args.tags.split(",") if args.tags else args.tags
    print(tags)

    # Extract the tag from the FITS files
    extract_fits_tag(args.files, tags)

if __name__ == "__main__":
    main()
