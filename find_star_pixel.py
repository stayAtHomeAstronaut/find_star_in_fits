#find and display
#python find_star_pixel.py my_image.fits "Polaris"

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.visualization.wcsaxes import WCSAxes
from astroquery.simbad import Simbad
import astropy.units as u
import matplotlib.pyplot as plt
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
        raise ValueError(f"Could not resolve star name '{star_name}'")

    ra = result['RA_d'][0]
    dec = result['DEC_d'][0]
    sky_coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')

    with fits.open(fits_file) as hdul:
        fitsdata= hdul[0].data
        w = WCS(hdul[0].header)
        x, y = w.world_to_pixel(sky_coord)

    return x, y, w, fitsdata

def plot_star_on_image(data, wcs, x, y, star_name):
    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(projection=wcs)
    ax.imshow(data, origin='lower', cmap='gray', vmin=data.min(), vmax=data.max()*0.8)
    ax.plot(x, y, 'ro', markersize=4, label=f"{star_name}")
    ax.set_xlabel('RA')
    ax.set_ylabel('Dec')
    ax.legend()
    ax.set_title(f"{star_name} on FITS Image")
    plt.grid(color='white', ls='dotted')
    plt.show()

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python find_star_pixel.py <fits_file> <star_name>")
        print("Put star name in double quotes")
        sys.exit(1)

    fits_path = sys.argv[1]
    star = sys.argv[2]

    x, y, wcs, data = get_star_pixel_coordinates(fits_path, star)
    print(f"{star} is at pixel coordinates: x = {x:.2f}, y = {y:.2f}")
    plot_star_on_image(data, wcs, x, y, star)
