#pip install astropy astroquery
#python find_star_in_fits.py my_image.fits "Betelgeuse"

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
import astropy.units as u
import sys

def get_star_pixel_coordinates(fits_file, star_name):
    #search Simbad for star name and get RA DEC
    #shaq did not play Simbad
    shaq = Simbad()
    shaq.TIMEOUT = 10
    shaq.remove_votable_fields('coordinates')
    shaq.add_votable_fields('ra(d)', 'dec(d)')
    result = shaq.query_object(star_name)

    if result is None:
        raise ValueError(f"Could not find star name '{star_name}'")

    ra = result['RA_d'][0]
    dec = result['DEC_d'][0]
    sky_coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')

    #Get the WCS from the FITS header
    with fits.open(fits_file) as hdul:
        w = WCS(hdul[0].header)
    
    #Convert sky coordinates to pixel coordinates
    x, y = w.world_to_pixel(sky_coord)
    return x, y, ra, dec

# Example usage:
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python find_star_in_fits.py <fits_file> <star_name>")
        print("Put star name in double quotes")
        sys.exit(1)
    
    fits_path = sys.argv[1]
    star = sys.argv[2]
    x, y, ra, dec = get_star_pixel_coordinates(fits_path, star)
    print(f"{star} coordinates: ra = {ra:.4f}, dec = {dec:.4f}")
    print(f"{star} is at FITS pixel coordinates: x = {x:.2f}, y = {y:.2f}")
