import numpy as np
from astropy.io import fits
import cv2

def demosaic_fits_image(fits_file, output_prefix, bayer_pattern='GRBG'):
    """
    Demosaics a FITS image and saves the R, G, and B channels as separate images.

    Args:
        fits_file (str): Path to the input FITS file.
        output_prefix (str): Prefix for the output image files.
        bayer_pattern (str, optional): Bayer pattern of the image. Defaults to 'RGGB'.
    """

    with fits.open(fits_file) as hdul:
        image_data = hdul[0].data
        header = hdul[0].header

    # Demosaic the image using cv2.cvtColor
    if bayer_pattern == 'RGGB':
      demosaiced_image = cv2.cvtColor(image_data, cv2.COLOR_BAYER_RG2RGB)
    elif bayer_pattern == 'BGGR':
      demosaiced_image = cv2.cvtColor(image_data, cv2.COLOR_BAYER_BG2RGB)
    elif bayer_pattern == 'GRBG':
      demosaiced_image = cv2.cvtColor(image_data, cv2.COLOR_BAYER_GR2RGB)
    elif bayer_pattern == 'GBRG':
      demosaiced_image = cv2.cvtColor(image_data, cv2.COLOR_BAYER_GB2RGB)
    else:
        raise ValueError("Invalid Bayer pattern specified.")

    # Extract the R, G, and B channels
    red_channel = demosaiced_image[:, :, 0]
    green_channel = demosaiced_image[:, :, 1]
    blue_channel = demosaiced_image[:, :, 2]

    # Save the channels as separate FITS files
    fits.writeto(f'{output_prefix}_red.fits', red_channel, header=header, overwrite=True)
    fits.writeto(f'{output_prefix}_green.fits', green_channel,header=header, overwrite=True)
    fits.writeto(f'{output_prefix}_blue.fits', blue_channel,header=header, overwrite=True)

if __name__ == '__main__':
    # Example usage:
    fits_file_path = '/Volumes/SSDonUSB/astro_pics/XO-6/XO-6_Light_exo_default_001.fits'
    output_file_prefix = 'demosaiced_image'
    demosaic_fits_image(fits_file_path, output_file_prefix, bayer_pattern='GRBG')
    print(f"Demosaicing complete. RGB channels saved as:\n"
          f"- {output_file_prefix}_red.fits\n"
          f"- {output_file_prefix}_green.fits\n"
          f"- {output_file_prefix}_blue.fits")