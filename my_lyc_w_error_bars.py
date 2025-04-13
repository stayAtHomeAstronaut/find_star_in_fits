#my_lyc_w_error_bars.py

import os
import glob
import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.stats import SigmaClip
from photutils.aperture import CircularAperture, aperture_photometry
from photutils.background import Background2D, MedianBackground
from astropy import units as u

# === User Inputs ===
fits_folder = '/home/dan/Pictures/HAT-P-3/Light/'  # folder containing FITS files
target_ra = 206.094141 # example RA in degrees
target_dec = 48.028668  # example DEC in degrees
aperture_radius = 5.0  # in pixels

comparison_coords = [
    (205.808333, 47.615000),
    (206.049380, 47.918879),
    (206.569083, 48.071794)
]

target_coord = SkyCoord(ra=target_ra*u.deg, dec=target_dec*u.deg)
comparison_skycoords = [SkyCoord(ra=ra*u.deg, dec=dec*u.deg) for ra, dec in comparison_coords]

# === Output Lists ===
times = []
raw_fluxes = []
diff_fluxes = []
error_raw_fluxes = []
error_diff_fluxes = []

# === Processing FITS Files ===
fits_files = sorted(glob.glob(os.path.join(fits_folder, '*.fits')))

for file in fits_files:
    with fits.open(file) as hdul:
        data = hdul[0].data
        header = hdul[0].header
        wcs = WCS(header)

        # Convert sky coords to pixel coords
        target_xy = wcs.world_to_pixel(target_coord)
        comp_pixels = [wcs.world_to_pixel(coord) for coord in comparison_skycoords]

        # Background estimation
        bkg = Background2D(data, (50, 50), filter_size=(3, 3),
                           sigma_clip=SigmaClip(sigma=3), bkg_estimator=MedianBackground())
        data_sub = data - bkg.background
        sky_std = np.std(bkg.background)

        # Photometry
        all_positions = [target_xy] + comp_pixels
        aperture = CircularAperture(all_positions, r=aperture_radius)
        phot_table = aperture_photometry(data_sub, aperture)

        area = aperture.area
        flux_target = phot_table['aperture_sum'][0]
        flux_comps = phot_table['aperture_sum'][1:]

        # === Error Estimation ===
        err_target = np.sqrt(flux_target + area * sky_std**2)
        err_comps = np.sqrt(flux_comps + area * sky_std**2)
        mean_flux_comps = np.mean(flux_comps)
        mean_err_comps = np.sqrt(np.sum(err_comps**2)) / len(err_comps)

        # Propagate error for differential flux = A / B:
        # σ_rel = rel_flux * sqrt((σ_A/A)^2 + (σ_B/B)^2)
        diff_flux = flux_target / mean_flux_comps
        err_diff_flux = diff_flux * np.sqrt((err_target / flux_target)**2 +
                                            (mean_err_comps / mean_flux_comps)**2)

        # Time
        time_obs = header.get('DATE-OBS', None)
        if time_obs:
            jd = Time(time_obs, format='isot', scale='utc').jd
            times.append(jd)
            raw_fluxes.append(flux_target)
            diff_fluxes.append(diff_flux)
            error_raw_fluxes.append(err_target)
            error_diff_fluxes.append(err_diff_flux)

# === Convert to numpy and sort by time ===
times = np.array(times)
raw_fluxes = np.array(raw_fluxes)
diff_fluxes = np.array(diff_fluxes)
error_raw_fluxes = np.array(error_raw_fluxes)
error_diff_fluxes = np.array(error_diff_fluxes)

sorted_idx = np.argsort(times)
times = times[sorted_idx]
raw_fluxes = raw_fluxes[sorted_idx]
diff_fluxes = diff_fluxes[sorted_idx]
error_raw_fluxes = error_raw_fluxes[sorted_idx]
error_diff_fluxes = error_diff_fluxes[sorted_idx]

# === Plot with Error Bars ===
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.errorbar(times, raw_fluxes, yerr=error_raw_fluxes, fmt='o-', label='Raw Flux')
plt.ylabel('Raw Flux (ADU)')
plt.title('Light Curve of Variable Star')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.errorbar(times, diff_fluxes, yerr=error_diff_fluxes, fmt='o-', color='red', label='Differential Flux')
plt.xlabel('Julian Date')
plt.ylabel('Relative Flux')
plt.grid(True)

plt.tight_layout()
plt.show()
