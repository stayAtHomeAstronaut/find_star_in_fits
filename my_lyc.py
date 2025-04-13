import os
import glob
import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.stats import SigmaClip
from astropy.utils.exceptions import AstropyWarning
from photutils.aperture import CircularAperture, aperture_photometry
from photutils.background import Background2D, MedianBackground
from astropy import units as u
import warnings
warnings.simplefilter('ignore', category=AstropyWarning)

# === User Inputs ===
fits_folder = '/home/dan/Pictures/TIC_67646988/Light/'  # folder containing FITS files
target_ra = 147.769065  # example RA in degrees
target_dec = 35.969295  # example DEC in degrees
aperture_radius = 5.0  # in pixels

# === Convert RA/DEC to SkyCoord ===
target_coord = SkyCoord(ra=target_ra*u.deg, dec=target_dec*u.deg)

# === Collect FITS Files ===
fits_files = sorted(glob.glob(os.path.join(fits_folder, '*.fits')))

times = []
fluxes = []

# === Loop Through Each FITS Image ===
for file in fits_files:
    with fits.open(file) as hdul:
        data = hdul[0].data
        header = hdul[0].header
        wcs = WCS(header)

        # Convert sky coordinates to pixel position
        x, y = wcs.world_to_pixel(target_coord)

        # Background subtraction
        bkg_estimator = MedianBackground()
        sigma_clip = SigmaClip(sigma=3)
        bkg = Background2D(data, (50, 50), filter_size=(3, 3),
                           sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
        data_sub = data - bkg.background

        # Aperture photometry
        position = [(x, y)]
        aperture = CircularAperture(position, r=aperture_radius)
        phot_table = aperture_photometry(data_sub, aperture)
        flux = phot_table['aperture_sum'][0]

        # Get observation time
        time_obs = header.get('DATE-OBS', None)
        if time_obs is not None:
            time = Time(time_obs, format='isot', scale='utc').jd
            times.append(time)
            fluxes.append(flux)

# === Sort by time and convert to numpy arrays ===
times = np.array(times)
fluxes = np.array(fluxes)
sorted_indices = np.argsort(times)
times = times[sorted_indices]
fluxes = fluxes[sorted_indices]

# === Plot Light Curve ===
plt.figure(figsize=(10, 5))
plt.plot(times, fluxes, 'o-', color='black')
plt.xlabel('Julian Date')
plt.ylabel('Flux (ADU)')
plt.title('Light Curve')
plt.grid(True)
plt.tight_layout()
plt.show()
