import os
import sys
import numpy as np
from astropy.io import fits
from glob import glob

def calibrate_light_frame(light_file, master_dark, master_flat, master_bias, output_dir):
    """
    Calibrates a single light frame using the master dark, flat, and bias frames.

    Args:
        light_file (str): Path to the light FITS file.
        master_dark (numpy.ndarray): Master dark frame.
        master_flat (numpy.ndarray): Master flat frame.
        master_bias (numpy.ndarray): Master bias frame.
        output_dir (str): Directory to save calibrated light frames.
    """
    with fits.open(light_file) as hdul:
        light_data = hdul[0].data.astype(np.float32)
        header = hdul[0].header

    # Calibration: (Light - Bias - Dark) / Flat
    calibrated_data = (light_data - master_bias - master_dark) / master_flat

    # Ensure no negative values after calibration
    calibrated_data[calibrated_data < 0] = 0

    # Save the calibrated light frame
    output_file = os.path.join(output_dir, os.path.basename(light_file))
    fits.writeto(output_file, calibrated_data, header=header, overwrite=True)
    print(f"Calibrated and saved: {output_file}")

def load_master_frame(file_path):
    """
    Loads a master calibration frame.

    Args:
        file_path (str): Path to the master frame file.

    Returns:
        numpy.ndarray: The master frame data.
    """
    with fits.open(file_path) as hdul:
        return hdul[0].data.astype(np.float32)

if __name__ == "__main__":
    # Set up directories
    #calibration_dir = "/Volumes/SSDonUSB/astro_pics/calibration"
    calibration_dir = "/Volumes/SSDonUSB/astro_pics/sv_cals_binned"
    calibration_dir = "/Volumes/SSDonUSB/astro_pics/sv_cals"
    light_dir = "/Volumes/SSDonUSB/astro_pics/WASP-12/demosaiced/green"
    output_dir = "/Volumes/SSDonUSB/astro_pics/WASP-12/calibrated_light_frames/green"
    

    # Load master calibration frames
    master_dark = load_master_frame(os.path.join(calibration_dir, "master_dark.fits"))
    master_flat = load_master_frame(os.path.join(calibration_dir, "master_flat.fits"))
    master_bias = load_master_frame(os.path.join(calibration_dir, "master_bias.fits"))
    if len(sys.argv) < 2:
        print("Usage: python calibrate_light_frames.py <demosaiced_file_path>")
        sys.exit(1)

    colors = []
    colors.append('red')
    colors.append('blue')
    colors.append('green')
    for color in colors:
        lights_file_path = sys.argv[1]
        light_dir = lights_file_path + '/' + color
        output_dir = lights_file_path.replace('demosaiced','calibrated_light_frames')
        output_dir = output_dir + '/' + color
        os.makedirs(output_dir, exist_ok=True)
        # Calibrate each light frame
        light_files = glob(os.path.join(light_dir, "*.fits"))
        for light_file in light_files:
            calibrate_light_frame(light_file, master_dark, master_flat, master_bias, output_dir)

    print("\nAll light frames have been calibrated and saved.")

