# ---------- HEADER --------------------------------------------
# File : src/swa_analysis/visualization.py
# Author(s) : Enzo Fortin
#
# Description :
# Visualization functions for SWA data analysis.
# --------------------------------------------------------------
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from src.config import config
import geopandas as gpd
import numpy as np
import os


# ----- MAPS -----
def plot_raster(raster, save=False, show= False, **kwargs):
    """Plot a raster data using Cartopy.
    Args:
        raster (xarray.DataArray): Raster data to plot.
        **kwargs: Optional keyword arguments (type, title, cmap, etc.).
    Returns:
        None: Displays the plot.
    """
    # Extract optional parameters
    cmap = kwargs.get("cmap", None)
    type = kwargs.get("type", None)
    boundaries = kwargs.get("boundaries", None).lower() if kwargs.get("boundaries") else None
    if boundaries in config.plot_config.BOUNDARIES:
        boundaries = config.plot_config.BOUNDARIES[boundaries]
    crs = kwargs.get("crs", ccrs.PlateCarree())
    title = kwargs.get("title", f"Raster Plot - {type.upper()} Data" if type else "Raster Plot")

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': crs})

    raster.plot(ax=ax, cmap=cmap, add_colorbar=True, cbar_kwargs={'label': 'Value'}, transform=ccrs.PlateCarree())

    plt.title(title, fontsize=16)
    plt.xlabel("Longitude", fontsize=12) ; plt.ylabel("Latitude", fontsize=12)
    plt.tight_layout()

    if save:
        output_path = f"{config.OUTPUT_DIR}/{title.replace(' ', '_').lower()}.png"
        plt.savefig(output_path, bbox_inches='tight')
    if show:
        plt.show()    



def plot_shapefile(shapefile, column, save=False, show=False, date=None, save_path=None, **kwargs):
    """Plot the specified column of a shapefile using Cartopy. Maybe possible to add othe columns to the plot (for instance with hatching).
    Args:
        shapefile (.shp, required) : The shapefile to plot.
        column (str, required) : The column to plot.
        save (bool, optional): If True, save the plot. Defaults to False.
        show (bool, optional): If True, display the plot. Defaults to False.
    Returns:
        None: Displays the plot or saves it to a file.
    """
    # Extract optional parameters
    boundaries = kwargs.get("boundaries", None).lower() if kwargs.get("boundaries") else None
    if boundaries in config.plot_config.BOUNDARIES:
        boundaries = config.plot_config.BOUNDARIES[boundaries]
    crs = kwargs.get("crs", ccrs.PlateCarree())
    
    # Set the map
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': crs})
    if boundaries:
        ax.set_extent(boundaries, crs=crs)

    # Plot the countries, in lightgrey
    countries = gpd.read_file(f"{config.paths.SHAPEFILES_DIR}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
    countries.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.5, zorder=0)
    # Plot the missing NUTS regions, in grey with hatching
    missing_nuts = gpd.read_file(f"{config.paths.SHAPEFILES_DIR}/NUTS_RG_10M_2021_4326/NUTS_RG_10M_2021_4326.shp")
    missing_nuts.plot(ax=ax, color="grey", edgecolor="black", linewidth=0.2, zorder=1 ,hatch='/////', alpha=0.5)

    # Plot the shapefile with the specified column
    shapefile.plot(ax=ax, column=column,  cmap='YlOrBr', edgecolor='black', linewidth=0.5, zorder=2)

    # Set the colorbar
    sm = plt.cm.ScalarMappable(cmap="YlOrBr")
    sm._A = []
    cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", pad=0.05, aspect=50, shrink=0.8)
    cbar.set_label("Mean fraction of arable land affected by drought", fontsize=10)
    cbar.set_ticks(np.arange(0, 1.1, 0.1))

    ax.gridlines(draw_labels=True, linewidth=0.5, color='black', alpha=0.5, zorder=-1)

    plt.gca().set_aspect("auto", adjustable="box")

    plt.suptitle(f"Mean fraction of arable land affected by drought by NUTS regions", fontsize=14)
    plt.title(f"for {date} and threshold {kwargs.get('threshold', 'N/A'):.2f}" if date else f"for all dates and threshold {kwargs.get('threshold', 'N/A'):.2f}", fontsize=12)

    plt.xlabel("Longitude") ; plt.ylabel("Latitude")
    plt.tight_layout()

    if save and save_path is not None:
        plt.savefig(save_path, bbox_inches='tight')
    else:
        raise ValueError("Please provide a valid save path if save is True.")

    if show:
        plt.show()

    plt.close()
# -----------------------

# ----- TIME SERIES -----
def plot_time_serie(data, save=False, show=False, save_dir=None, **kwargs):
    """
    Create a time series plot of the SWA data.
    Requires the computed shapefile with the mean over a period.
    Args:
        ...
    Returns:
        ...
    """
    # Extract optional parameters
    year_start = kwargs.get("year_start", None)
    year_end = kwargs.get("year_end", None)
    month_start = kwargs.get("month_start", None)
    month_end = kwargs.get("month_end", None)
    threshold = kwargs.get("threshold", None)
    
    for subregion in data.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(data[subregion].index, data[subregion].values, label=subregion, marker='none', linestyle='-', color="black", linewidth=0.5)
        plt.suptitle(f"Time Series of SWA for {subregion}", fontsize=14)
        plt.title(f"from {month_start} to {month_end} with threshold {threshold:.2f}" if month_start and month_end else f"with threshold {threshold:.2f}", fontsize=12)
        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Mean SWA", fontsize=12)
        plt.xticks(data.index, rotation=45)
        plt.grid(True)
        plt.tight_layout()
        if save:
            os.makedirs(save_dir, exist_ok=True)
            plt.savefig(f"{save_dir}/temporal_series_swa-{year_start}_{year_end}-{month_start}_{month_end}_{subregion}.png", bbox_inches='tight')
        if show:
            plt.show()
        plt.close()
# -----------------------
