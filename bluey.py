import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import json
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



def suess(json_file_path):
    star_data_df = pd.read_json(json_file_path)


    #star_data_df['dec_degrees'] = pd.to_numeric(star_data_df['dec_degrees'], errors='coerce')
    print(star_data_df)
    for index, row in star_data_df.iterrows():
        if index == 0:
            print(f"Index: {index} is target")
            print(f" {row['star_name']} ra {row['ra_degrees']} dec  {row['dec_degrees']} ")
            target_name = {row['star_name']}.pop()
            target_ra = float({row['ra_degrees']}.pop())
            target_dec = float({row['dec_degrees']}.pop())  # DEC in degrees
        else:
            print(f"Index: {index} is comp")
            print(f" {row['star_name']}")
            comp_name = {row['star_name']}.pop()
            comp_ra = float({row['ra_degrees']}.pop())  # RA in degrees
            comp_dec = float({row['dec_degrees']}.pop())  # DEC in degrees
    
    aperture_radius = 5.0  # in pixels

    # === Convert RA/DEC to SkyCoord ===
    target_coord = SkyCoord(ra=target_ra*u.deg, dec=target_dec*u.deg)
    comp_coord = SkyCoord(ra=comp_ra*u.deg, dec=comp_dec*u.deg)



    times = []
    airmass = []
    times_red = []
    times_blue = []
    times_green = []
    fluxes = []
    fluxes_red = []
    fluxes_blue = []
    fluxes_green =[]
    ratio_array = []

    comp_fluxes_red = []
    comp_fluxes_blue = []
    comp_fluxes_green =[]
    comp_ratio_array = []

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
                comp_x, comp_y = wcs.world_to_pixel(comp_coord)

                # Background subtraction
                bkg_estimator = MedianBackground()
                sigma_clip = SigmaClip(sigma=3)
                bkg = Background2D(data, (50, 50), filter_size=(3, 3),sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
                data_sub = data - bkg.background
        
                # Aperture photometry
                position = [(x, y)]
                aperture = CircularAperture(position, r=aperture_radius)
                phot_table = aperture_photometry(data_sub, aperture)
                flux = phot_table['aperture_sum'][0]
                comp_position = [(comp_x, comp_y)]
                comp_aperture = CircularAperture(comp_position, r=aperture_radius)
                comp_phot_table = aperture_photometry(data_sub, comp_aperture)
                comp_flux = comp_phot_table['aperture_sum'][0]

                # Get observation time
                time_obs = header.get('DATE-OBS', None)
                if time_obs is not None:
                    time = Time(time_obs, format='isot', scale='utc').jd
                    times.append(time)
                    airmass_obs = header.get('AIRMASS',None)
                    if airmass_obs is not None:
                        airmass.append(airmass_obs)
                    fluxes.append(flux)
                    if color == 'red':
                        times_red.append(time)
                        fluxes_red.append(flux)
                        comp_fluxes_red.append(comp_flux)
                    if color == 'blue':
                        times_blue.append(time)
                        fluxes_blue.append(flux)
                        comp_fluxes_blue.append(comp_flux)
                    if color == 'green':
                        times_green.append(time)
                        fluxes_green.append(flux)
                        comp_fluxes_green.append(comp_flux)



    # === Sort by time and convert to numpy arrays ===
    times = np.array(times)
    fluxes = np.array(fluxes)
    sorted_indices = np.argsort(times)
    times = times[sorted_indices]
    fluxes = fluxes[sorted_indices]

    times_red = np.array(times_red)
    fluxes_red = np.array(fluxes_red)
    comp_fluxes_red = np.array(comp_fluxes_red)
    sorted_indices = np.argsort(times_red)
    times_red = times_red[sorted_indices]
    fluxes_red = fluxes_red[sorted_indices]
    comp_fluxes_red = comp_fluxes_red[sorted_indices]

    times_blue = np.array(times_blue)
    fluxes_blue = np.array(fluxes_blue)
    comp_fluxes_blue = np.array(comp_fluxes_blue)
    sorted_indices = np.argsort(times_blue)
    times_blue = times_blue[sorted_indices]
    fluxes_blue = fluxes_blue[sorted_indices]
    comp_fluxes_blue = comp_fluxes_blue[sorted_indices]

    times_green = np.array(times_green)
    fluxes_green = np.array(fluxes_green)
    comp_fluxes_green = np.array(comp_fluxes_green)
    sorted_indices = np.argsort(times_green)
    times_green = times_green[sorted_indices]
    fluxes_green = fluxes_green[sorted_indices]
    comp_fluxes_green = comp_fluxes_green[sorted_indices]

    rows = len(times_red)
    obs_time_list = []
    for i in range(rows):
        obs_time = Time(times_red[i], format='jd')
        obs_time_list.append(obs_time.iso)
        if (times_red[i] == times_blue[i]):
            ratio_array.append(10000*(fluxes_blue[i]/fluxes_red[i]))
            comp_ratio_array.append(10000*(comp_fluxes_blue[i]/comp_fluxes_red[i]))

    cols = 6
    #always append to a list, then concatinate into a dataframe
    row_list = []
    for i in range(rows):
        row_list.append({"obs_date_time":obs_time_list[i],"JD":times_red[i],"airmass":airmass[i],"target_name":target_name,"target_flux_red":fluxes_red[i],"flux_green":fluxes_green[i],"flux_blue":fluxes_blue[i],"blue_over_red":fluxes_blue[i]/fluxes_red[i],"comp_name":comp_name,"comp_flux_red":comp_fluxes_red[i],"comp_flux_green":comp_fluxes_green[i],"comp_flux_blue":comp_fluxes_blue[i],"comp_blue_over_red":comp_fluxes_blue[i]/comp_fluxes_red[i]})

    df = pd.concat([pd.DataFrame([row]) for row in row_list], ignore_index=True)

    print(df)
    outfile = target_name.replace(" ","_") + '_' + comp_name.replace(" ","_") + '_rgb_output.csv'
    df.to_csv(outfile, index=False)


    # === Plot Light Curve ===
    plt.figure(figsize=(10, 5))
    #plt.plot(times, fluxes, 'o-', color='black')
    plt.plot(times, airmass, '-', color='black')
    plt.plot(times_red, fluxes_red, 'o-', color='red')
    plt.plot(times_blue, fluxes_blue, 'o-', color='blue')
    plt.plot(times_green, fluxes_green, 'o-', color='green')
    plt.plot(times_red, ratio_array, 'o-', color='grey')

    plt.plot(times_red, comp_fluxes_red, '.--', color='red')
    plt.plot(times_blue, comp_fluxes_blue, '.--', color='blue')
    plt.plot(times_green, comp_fluxes_green, '.--', color='green')
    plt.plot(times_red, comp_ratio_array, '.--', color='grey')


    plt.xlabel('Julian Date')
    plt.ylabel('Flux (ADU)')
    plt.title(target_name)
    plt.grid(True)
    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python bluey.py <json_file_name> <demosaiced_fits_folder")
        print("Put star name in double quotes")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    fits_folder = sys.argv[2]

    suess(json_file_path)
