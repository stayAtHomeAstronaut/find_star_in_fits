#pip install astropy astroquery
#python find_star_in_fits.py my_image.fits "Betelgeuse"

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
import astropy.units as u
import sys
import json
import pandas as pd

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_star_pixel_coordinates(fits_file, star_name):
    #search Simbad for star name and get RA DEC
    #shaq did not play Simbad
    shaq = Simbad()
    shaq.TIMEOUT = 20
    if shaq is not None:
        shaq.reset_votable_fields()
    else:
        print("shaq is None")
    shaq.add_votable_fields('ra', 'dec')
    result = shaq.query_object(star_name)

    if result is None:
        raise ValueError(f"Could not find star name '{star_name}'")

    ra = result['ra'][0]
    dec = result['dec'][0]
    sky_coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')

    #Get the WCS from the FITS header
    with fits.open(fits_file) as hdul:
        w = WCS(hdul[0].header)
    
    #Convert sky coordinates to pixel coordinates
    x, y = w.world_to_pixel(sky_coord)
    return x, y, ra, dec

# Example usage:
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python find_star_in_fits.py <fits_file> <star_name>")
        print("Put star name in double quotes")
        sys.exit(1)
    
    fits_path = sys.argv[1]
    star = sys.argv[2]
    tmid = 0


    x, y, ra, dec = get_star_pixel_coordinates(fits_path, star)
    print(f"{star} coordinates: ra = {ra:.4f}, dec = {dec:.4f}")
    print(f"{star} is at FITS pixel coordinates: x = {x:.2f}, y = {y:.2f}")
    star_data = {
        'target_comp': 'target',
        'star_name': [star],
        'ra_degrees': [ra],
        'dec_degrees': [dec]
    }
        
         
    df = pd.DataFrame(star_data)
    i = 3
    while i < len(sys.argv):
        if is_float(sys.argv[i]) == True:
            tmid = float(sys.argv[i])
            star_data = {
                'target_comp': 'target',
                'star_name': [star],
                'ra_degrees': [ra],
                'dec_degrees': [dec],
                'tmid':  [tmid]
            }
            df = pd.DataFrame(star_data)
            i += 1
        else:
            comp_star = sys.argv[i]
            x, y, ra, dec = get_star_pixel_coordinates(fits_path, comp_star)
            print(f"{comp_star} coordinates: ra = {ra:.4f}, dec = {dec:.4f} and is at FITS pixel coordinates: x = {x:.2f}, y = {y:.2f}")
            comp_star_data = {
                'target_comp': 'comp',
                'star_name': [comp_star],
                'ra_degrees': [ra],
                'dec_degrees': [dec]
            }
            comp_df = pd.DataFrame(comp_star_data)
            i += 1
    
    df = pd.concat([df, comp_df], ignore_index=True)
    json_records = df.to_json(orient='records')
    #print(json_records)
    filename = star.replace(' ','_') + '.json'
    with open(filename, 'w') as f:
        json.dump(json.loads(json_records), f, indent=4)
