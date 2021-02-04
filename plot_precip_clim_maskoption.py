# code for doing lots of stuff, has functions (w def), cartopy map plotter, a debug statement, assertions, 

import argparse

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import cmocean
import pdb  #debugger import statement

def apply_mask(darray, sftlf_file, realm):
    """Mask ocean or land using a sftlf (land surface fraction) file.
   
    Args:
     darray (xarray.DataArray): Data to mask
     sftlf_file (str): Land surface fraction file
     realm (str): Realm to mask
   
    """
  
    dset = xr.open_dataset(sftlf_file)
  
    # running debugging, Les 8 (commenting out below line bc don't normally want to go line-by-line
    #pdb.set_trace()  
    # will run line-by-line from here on, with ability to change variables, e.g. realm = 'land'
    # to continue to next line, type "n", to quit, type "c"

    # adding an assertion, that realm be only one of the following list: (Les 8)
    assert realm in ['land', 'ocean'], """Valid realms are 'land' or 'ocean'"""
    
    if realm == 'land':
        masked_darray = darray.where(dset['sftlf'].data < 50)
    else:
        masked_darray = darray.where(dset['sftlf'].data > 50)   
  
    return masked_darray



def convert_pr_units(darray):
    """Convert kg m-2 s-1 to mm day-1.
    
    Args:
      darray (xarray.DataArray): Precipitation data
    
    """
    
    darray.data = darray.data * 86400
    darray.attrs['units'] = 'mm/day'
    
    return darray


def create_plot(clim, model_name, season, gridlines=False):
    """Plot the precipitation climatology.
    
    Args:
      clim (xarray.DataArray): Precipitation climatology data
      model_name (str): Name of the climate model
      season (str): Season
      
    Kwargs:
      gridlines (bool): Select whether to plot gridlines    
    
    """
        
    fig = plt.figure(figsize=[12,5])
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree(central_longitude=180))
    #FOR SOME REASON OTHER PROJECTIONS (Robinson, Mollweide) DON'T WORK ?!?!? BELOW:
    #ax = fig.add_subplot(111, projection=ccrs.Mollweide(central_longitude=180))
    clim.sel(season=season).plot.contourf(ax=ax,
                                          levels=np.arange(0, 13.5, 1.5),
                                          extend='max',
                                          transform=ccrs.PlateCarree(),
                                          #transform=ccrs.Mollweide(),
                                          cbar_kwargs={'label': clim.units},
                                          cmap=cmocean.cm.haline_r)
    ax.coastlines()
    if gridlines:
        plt.gca().gridlines()
    
    title = '%s precipitation climatology (%s)' %(model_name, season)
    plt.title(title)


def main(inargs):
    """Run the program."""

    dset = xr.open_dataset(inargs.pr_file)
    
    clim = dset['pr'].groupby('time.season').mean('time', keep_attrs=True)
    clim = convert_pr_units(clim)

    if inargs.mask:
        sftlf_file, realm = inargs.mask
        clim = apply_mask(clim, sftlf_file, realm)

    create_plot(clim, dset.attrs['source_id'], inargs.season)
    plt.savefig(inargs.output_file, dpi=200)


if __name__ == '__main__':
    description='Plot the precipitation climatology for a given season.'
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument("pr_file", type=str, help="Precipitation data file")

    #adding les7 land or sea mask parser arg:
    parser.add_argument("--mask", type=str, nargs=2, metavar=('SFTLF_FILE', 'REALM'), default=None,
                           help="""Provide sftlf file and realm to mask ('land' or 'ocean')""")

    #older version:(adding specific constraining choices to season arg, les4?)
    #parser.add_argument("season", type=str, help="Season to plot")
    parser.add_argument("season", type=str, 
            choices=['DJF', 'MAM', 'JJA', 'SON'], 
            help="Season to plot")
    
    parser.add_argument("output_file", type=str, help="Output file name")

    args = parser.parse_args()
    
    main(args)
    
