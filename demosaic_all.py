import os
import numpy as np
from astropy.io import fits
import cv2
from glob import glob

def demosaic_fits_image(fits_file, output_name, output_dir, bayer_pattern='RGGB'):
    """
    Demosaics a FITS image and saves the R, G, and B channels as separate images.

    Args:
        fits_file (str): Path to the input FITS file.
        output_name (str): Base name for the output image files.
        output_dir (str): Root directory where red, green, blue folders are created.
        bayer_pattern (str, optional): Bayer pattern of the image. Defaults to 'GRBG'.
    """
    with fits.open(fits_file) as hdul:
        image_data = hdul[0].data.astype(np.uint16)  # Ensure proper type for OpenCV
        header = hdul[0].header

    # Demosaic using OpenCV
    pattern_map = {
        'RGGB': cv2.COLOR_BAYER_RG2RGB,
        'BGGR': cv2.COLOR_BAYER_BG2RGB,
        'GRBG': cv2.COLOR_BAYER_GR2RGB,
        'GBRG': cv2.COLOR_BAYER_GB2RGB
    }

    if bayer_pattern not in pattern_map:
        raise ValueError("Invalid Bayer pattern specified.")

    demosaiced_image = cv2.cvtColor(image_data, pattern_map[bayer_pattern])

    # Extract channels
    red_channel = demosaiced_image[:, :, 0]
    green_channel = demosaiced_image[:, :, 1]
    blue_channel = demosaiced_image[:, :, 2]

    # Create output directories if they don't exist
    os.makedirs(os.path.join(output_dir, 'red'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'green'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'blue'), exist_ok=True)

    # Save each channel
    fits.writeto(os.path.join(output_dir, 'red', f'{output_name}_red.fits'), red_channel, header=header, overwrite=True)
    fits.writeto(os.path.join(output_dir, 'green', f'{output_name}_green.fits'), green_channel, header=header, overwrite=True)
    fits.writeto(os.path.join(output_dir, 'blue', f'{output_name}_blue.fits'), blue_channel, header=header, overwrite=True)

def process_fits_directory(input_dir, output_dir, bayer_pattern='GRBG'):
    fits_files = glob(os.path.join(input_dir, '*.fits'))

    for fits_file in fits_files:
        base_name = os.path.splitext(os.path.basename(fits_file))[0]
        print(f"Processing {base_name}...")
        demosaic_fits_image(fits_file, base_name, output_dir, bayer_pattern)

if __name__ == '__main__':
    # Define your input and output directories
    input_directory = '/Volumes/SSDonUSB/astro_pics/WASP-12/Light'
    output_directory = '/Volumes/SSDonUSB/astro_pics/WASP-12/demosaiced'

    process_fits_directory(input_directory, output_directory, bayer_pattern='GRBG')
    print("All FITS files have been demosaiced and saved.")
