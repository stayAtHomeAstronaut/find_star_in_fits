import fitsio
import numpy as np

file_path = '/Volumes/SSDonUSB/astro_pics/TIC_67646988/Light4Split/TIC_67646988_Light_exo_default_093.fits'

# Open the FITS file
with fitsio.FITS(file_path, 'r') as f:
    # Assuming your RGB data is in a single extension (e.g., extension 0)
    # You might need to adjust this if your RGB data is in multiple extensions
    img_data = f[0].read()

    # Check the shape of the data to determine if it's a single image or multiple channels
    if img_data.ndim == 2:
        # If it's a 2D array, assume it's grayscale (or a single channel)
        print("Warning: The FITS file appears to contain only a single channel image.")
        # You'd typically need to convert this to a 3-channel RGB image if you want RGB values
        # For demonstration, let's create a dummy RGB array with the same grayscale data
        rgb_data = np.stack((img_data, img_data, img_data), axis=-1)

    elif img_data.ndim == 3:
        # If it's a 3D array, assume it's RGB (or a 3-channel image)
        rgb_data = img_data
    else:
        print("Error: The FITS file does not contain a standard image structure.")
        rgb_data = None

    # If we have RGB data
    if rgb_data is not None:
        # Define the aperture (example: a rectangular area)
        aperture_x_start = 10
        aperture_x_end = 20
        aperture_y_start = 15
        aperture_y_end = 25

        # Extract the aperture pixels
        aperture_pixels = rgb_data[aperture_y_start:aperture_y_end, aperture_x_start:aperture_x_end, :]

        # Print the RGB values of the pixels within the aperture
        print("RGB values within the aperture:")
        for y in range(aperture_pixels.shape[0]):
            for x in range(aperture_pixels.shape[1]):
                r, g, b = aperture_pixels[y, x, :]
                print(f"Pixel ({y}, {x}): R={r}, G={g}, B={b}")

# Example usage:
# 1. Replace 'your_file.fits' with your FITS file path
# 2. Adjust the aperture coordinates (aperture_x_start, aperture_x_end, aperture_y_start, aperture_y_end) to match your desired area
# 3. The code will print the RGB values for each pixel within the defined aperture.