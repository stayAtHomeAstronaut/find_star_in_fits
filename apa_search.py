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
            if(float({row['tmid']}.pop()) > 0):
                tmid=float({row['tmid']}.pop()) 
            else:
                tmid = 0
        else:
            print(f"Index: {index} is comp")
            print(f" {row['star_name']}")
            comp_name = {row['star_name']}.pop()
            comp_ra = float({row['ra_degrees']}.pop())  # RA in degrees
            comp_dec = float({row['dec_degrees']}.pop())  # DEC in degrees
    
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

    print (fits_folder)
    # === Collect FITS Files ===
    fits_files = sorted(glob.glob(os.path.join(fits_folder, '*.fits')))

    # === Loop Through Each FITS Image to determine best apature ===
    best_aperture_radius = 1.0  # in pixels
    aperture_radius = 1.0  # in pixels
    most_snr = 0
    brightest_fits = ""
    for aperture_radius in range(4,20):
        print(f"trying aptature {aperture_radius:.1f}")
        for file in fits_files[::20]:
            #print(file)
            with fits.open(file) as hdul:
                data = hdul[0].data
                header = hdul[0].header
                wcs = WCS(header)
        
                # Convert sky coordinates to pixel position
                x, y = wcs.world_to_pixel(target_coord)

                # Background subtraction
                bkg_estimator = MedianBackground()
                sigma_clip = SigmaClip(sigma=3)
                bkg = Background2D(data, (50, 50), filter_size=(3, 3),sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
                data_sub = data - bkg.background
                background_rms = bkg.background_rms
                avg_bkg_rms=np.average(background_rms)
        
                # Aperture photometry
                position = [(x, y)]
                aperture = CircularAperture(position, r=aperture_radius)
                phot_table = aperture_photometry(data_sub, aperture)
                flux = phot_table['aperture_sum'][0]

                snr=flux/avg_bkg_rms

                print(f"avg_background_rms = {avg_bkg_rms} flux = {flux:5f} snr={snr:5}")
                if snr > most_snr:
                    most_snr=snr
                    best_aperture_radius = aperture_radius
                    brightest_fits = file
        print(f"So far, {best_aperture_radius:.1f} is best_aperture_radius: most_snr = {most_snr:.4f}, brightest_fits = {brightest_fits} ")
        aperture_radius+=2
    print(f"{best_aperture_radius:.1f} is best_aperture_radius: most_snr = {most_snr:.4f}, brightest_fits = {brightest_fits} ")
    aperture_radius=best_aperture_radius



    
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
                


    # === Sort by time and convert to numpy arrays ===
    times = np.array(times)
    fluxes = np.array(fluxes)
    sorted_indices = np.argsort(times)
    times = times[sorted_indices]
    fluxes = fluxes[sorted_indices]
    rows = len(times)
    obs_time_list = []
    for i in range(rows):
        obs_time = Time(times[i], format='jd')
        obs_time_list.append(obs_time.iso)

    cols = 6
    #always append to a list, then concatinate into a dataframe
    row_list = []
    for i in range(rows):
        row_list.append({"obs_date_time":obs_time_list[i],"JD":times[i],"airmass":airmass[i],"target_name":target_name,"tmid":tmid,"target_flux":fluxes[i]})

    df = pd.concat([pd.DataFrame([row]) for row in row_list], ignore_index=True)

    print(df)
    outfile = target_name.replace(" ","_") + '_' + comp_name.replace(" ","_") + '_apa_search_output.csv'
    df.to_csv(outfile, index=False)






if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python apa_search.py <json_file_name> <fits_folder>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    fits_folder = sys.argv[2]

    suess(json_file_path)
