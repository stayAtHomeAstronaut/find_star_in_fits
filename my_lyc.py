import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.stats import SigmaClip
from astropy.utils.exceptions import AstropyWarning
from photutils.aperture import CircularAperture, aperture_photometry
from photutils.background import Background2D, MedianBackground
from astropy import units as u
from scipy import stats
import warnings
warnings.simplefilter('ignore', category=AstropyWarning)

# === User Inputs ===
fits_folder = '/Volumes/SSDonUSB/astro_pics/TIC_67646988/Light4Split_d/'  # folder containing FITS files
target_name = "TIC 67646988"
target_ra = 147.769065  # example RA in degrees
target_dec = 35.969295  # example DEC in degrees


#fits_folder = '/Volumes/SSDonUSB/astro_pics/XO-6/demosaiced/'
fits_folder = '/Volumes/SSDonUSB/astro_pics/XO-6/Light_d_a/'
target_name = 'XO-6'
target_ra = 94.793212  # RA in degrees
target_dec = 73.827663  # DEC in degrees
aperture_radius = 5.0  # in pixels

# === Convert RA/DEC to SkyCoord ===
target_coord = SkyCoord(ra=target_ra*u.deg, dec=target_dec*u.deg)

times = []
times_red = []
times_blue = []
times_green = []
fluxes = []
fluxes_red = []
fluxes_blue = []
fluxes_green =[]
ratio_array = []

colors = []
colors.append('red')
colors.append('blue')
colors.append('green')
for color in colors:
    print (fits_folder)
    # === Collect FITS Files ===
    fits_files = sorted(glob.glob(os.path.join(fits_folder,color, '*.fits')))    
    
    # === Loop Through Each FITS Image ===
    for file in fits_files:
        print(file)
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
                if color == 'red':
                	times_red.append(time)
                	fluxes_red.append(flux)
                if color == 'blue':
                	times_blue.append(time)
                	fluxes_blue.append(flux)
                if color == 'green':
                	times_green.append(time)
                	fluxes_green.append(flux)
    
# === Sort by time and convert to numpy arrays ===
times = np.array(times)
fluxes = np.array(fluxes)
sorted_indices = np.argsort(times)
times = times[sorted_indices]
fluxes = fluxes[sorted_indices]

times_red = np.array(times_red)
fluxes_red = np.array(fluxes_red)
sorted_indices = np.argsort(times_red)
times_red = times_red[sorted_indices]
fluxes_red = fluxes_red[sorted_indices]

times_blue = np.array(times_blue)
fluxes_blue = np.array(fluxes_blue)
sorted_indices = np.argsort(times_blue)
times_blue = times_blue[sorted_indices]
fluxes_blue = fluxes_blue[sorted_indices]

times_green = np.array(times_green)
fluxes_green = np.array(fluxes_green)
sorted_indices = np.argsort(times_green)
times_green = times_green[sorted_indices]
fluxes_green = fluxes_green[sorted_indices]


rows = len(times_red)
obs_time_list = []
for i in range(rows):
    obs_time = Time(times_red[i], format='jd')
    obs_time_list.append(obs_time.iso)
    if (times_red[i] == times_blue[i]):
        ratio_array.append(10000*(fluxes_blue[i]/fluxes_red[i]))
	
cols = 6
#always append to a list, then concatinate into a dataframe
row_list = []
for i in range(rows):
    row_list.append({"obs_date":obs_time_list[i],"JD":times_red[i],"flux_red":fluxes_red[i],"flux_green":fluxes_green[i],"flux_blue":fluxes_blue[i],"blue_over_red":fluxes_blue[i]/fluxes_red[i]})

df = pd.concat([pd.DataFrame([row]) for row in row_list], ignore_index=True)

print(df)
outfile = target_name + '_rgb_output.csv'
df.to_csv(outfile, index=False)


q_low = df["blue_over_red"].quantile(0.01)
q_hi  = df["blue_over_red"].quantile(0.99)
df_filtered = df[(df["blue_over_red"] < q_hi) & (df["blue_over_red"] > q_low)]
outfile = outfile = target_name + '_quantile_filtered_output.csv'
df_filtered.to_csv(outfile, index=False)

# === Plot Light Curve ===
plt.figure(figsize=(10, 5))
plt.plot(times, fluxes, 'o-', color='black')
plt.plot(times_red, fluxes_red, 'o-', color='red')
plt.plot(times_blue, fluxes_blue, 'o-', color='blue')
plt.plot(times_green, fluxes_green, 'o-', color='green')
plt.plot(times_red, ratio_array, 'o-', color='grey')

plt.xlabel('Julian Date')
plt.ylabel('Flux (ADU)')
plt.title(target_name)
plt.grid(True)
plt.tight_layout()
plt.show()
