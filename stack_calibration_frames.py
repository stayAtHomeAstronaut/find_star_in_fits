import os
import numpy as np
from astropy.io import fits
from glob import glob

def stack_fits(directory, output_file):
    """
    Stacks all FITS images in a directory to create a master calibration frame.
    
    Args:
        directory (str): Directory containing the FITS images.
        output_file (str): Path to the output master frame.
    """
    fits_files = glob(os.path.join(directory, "*.fits"))

    if not fits_files:
        print(f"No FITS files found in {directory}")
        return
    
    # Initialize stacking
    stack = None
    header = None

    for i, fits_file in enumerate(fits_files):
        with fits.open(fits_file) as hdul:
            data = hdul[0].data.astype(np.float32)
            if stack is None:
                stack = np.zeros_like(data)
                header = hdul[0].header

            # Accumulate image data
            stack += data

    # Average the stack
    master_frame = stack / len(fits_files)

    # Save the master frame
    fits.writeto(output_file, master_frame, header=header, overwrite=True)
    print(f"Created {output_file} from {len(fits_files)} images.")

if __name__ == "__main__":
    # Input directories
    calibration_dir = "/Volumes/SSDonUSB/astro_pics/sv_cals_binned"
    dark_dir = os.path.join(calibration_dir, "Dark")
    flat_dir = os.path.join(calibration_dir, "Flat")
    bias_dir = os.path.join(calibration_dir, "Bias")

    # Output files
    master_dark = os.path.join(calibration_dir, "master_dark.fits")
    master_flat = os.path.join(calibration_dir, "master_flat.fits")
    master_bias = os.path.join(calibration_dir, "master_bias.fits")

    # Create master calibration frames
    stack_fits(dark_dir, master_dark)
    stack_fits(flat_dir, master_flat)
    stack_fits(bias_dir, master_bias)

    print("All master calibration frames have been created.")

