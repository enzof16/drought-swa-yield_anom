# ---------- HEADER --------------------------------------------
# File : src/combiantion/combination.py
# Author(s) : Enzo Fortin
#
# Description :
# This module handles the visualization of correlation results between SWA and yield anomalies.
# --------------------------------------------------------------
import os
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider
import geopandas as gpd
import numpy as np
import holoviews as hv
import geoviews as gv
import panel as pn
import param
from IPython import get_ipython
hv.extension('bokeh', 'matplotlib')
# --------------------------------------------------------------

config = None  # to be set from outside


# ---------- CONSTANTS -----------------------------------------
# CORRELATION_RESULTS_FILE = f"{config.corr_config.CORR_RESULTS_DIR}/mcc_results.nc"
# OUTPUT_DIR = f"{config.corr_config.CORR_OUTPUT_DIR}"
# SHAPEFILE_PATH = config.paths.NUTS_SHAPEFILE
# --------------------------------------------------------------


# ---------- DATA TREATMENT -----------------------------------------
def load_correlation_results():
    """Load the correlation results from the NetCDF file."""
    if not os.path.exists(f"{config.corr_config.CORR_RESULTS_DIR}/mcc_results.nc"):
        raise FileNotFoundError(f"Correlation results file not found: {f"{config.corr_config.CORR_RESULTS_DIR}/mcc_results.nc"}")
    ds = xr.open_dataset(f"{config.corr_config.CORR_RESULTS_DIR}/mcc_results.nc")
    return ds


def read_shapefile():
    """ Load the NUTS shapefile for mapping."""
    if not os.path.exists(config.paths.NUTS_SHAPEFILE):
        raise FileNotFoundError(f"Shapefile not found: {config.paths.NUTS_SHAPEFILE}")
    gdf = gpd.read_file(config.paths.NUTS_SHAPEFILE)
    return gdf


def associate_shp_data(gdf, data_df, data_col, shp_id_col='NUTS_ID', data_id_col='Region'):
    """Associate data from a DataFrame to a GeoDataFrame based on region identifiers."""
    gdf = gdf.set_index(shp_id_col).join(data_df.set_index(data_id_col))
    return gdf


def get_mcc_ds(ds, th_swa, th_ya):
    """Extract MCC values for specific thresholds from the dataset.
    Args:
        ds (xarray.Dataset): Dataset containing MCC values and thresholds.
        th_swa (float): Threshold for SWA.
        th_ya (float): Threshold for Yield Anomaly.
    Returns:
        xarray.DataArray: DataArray with MCC values for the specified thresholds.
    """
    mcc_da = ds.sel(TH_SWA=th_swa, TH_YA=th_ya)['MCC']
    return mcc_da


def get_max_mcc_ds():
    """Load the correlation results and compute the maximum MCC values across thresholds.
    Returns:
        xarray.Dataset: Dataset with maximum MCC values and corresponding thresholds.
    """
    ds = load_correlation_results()
    max_mcc_ds = ds['MCC'].max(dim=["TH_SWA", "TH_YA"])
    return max_mcc_ds


def get_max_mcc_df(ds):
    """Create a DataFrame with the maximum MCC value for each region across all threshold combinations, with corresponding thresholds.
    Args:
        ds (xarray.Dataset): Dataset containing MCC values and thresholds.
    Returns:
        pd.DataFrame: DataFrame with columns 'Region', 'Max_MCC', 'TH_SWA', 'TH_YA'.
    """
    max_mcc_ds = ds['MCC'].max(dim=["TH_SWA", "TH_YA"])
    max_indices = ds['MCC'].argmax(dim=["TH_SWA", "TH_YA"])

    TH_SWA_max, TH_YA_MAX = ds['TH_SWA'].values[max_indices["TH_SWA"].values], ds['TH_YA'].values[max_indices["TH_YA"].values]

    df_max_mcc = pd.DataFrame({'Region': max_mcc_ds['region'].values, 'Max_MCC': max_mcc_ds.values})
    df_max_mcc['TH_SWA'], df_max_mcc['TH_YA'] = [ds['TH_SWA'].values[idx] for idx in max_indices["TH_SWA"]], [ds['TH_YA'].values[idx] for idx in max_indices["TH_YA"]]
    return df_max_mcc

def get_max_mcc_shapefile(ds):
    """
    Get a GeoDataFrame with maximum MCC values and corresponding thresholds for each region.
    """
    df_max_mcc = get_max_mcc_df(ds)
    gdf = read_shapefile()
    gdf = associate_shp_data(gdf, df_max_mcc, 'Max_MCC')
    return gdf
# --------------------------------------------------------------

# ---------- VISUALIZATION ---------------------------------------
def plot_mcc_map(ds, th_swa, th_ya, save=False, show=False):
    """Plot a static MCC map for given thresholds TH_SWA and TH_YA."""
    mcc_da = ds.sel(TH_SWA=th_swa, TH_YA=th_ya)['MCC']
    df_mcc = pd.DataFrame({'Region': mcc_da['region'].values, 'MCC': mcc_da.values})
    gdf = read_shapefile()
    gdf = associate_shp_data(gdf, df_mcc, 'MCC')

    fig, ax = plt.subplots(figsize=(10, 8))
    gdf.plot(column='MCC', ax=ax, legend=True, cmap='coolwarm', vmin=-1, vmax=1)
    ax.set_title(f'MCC Map | TH_SWA:{th_swa} - TH_YA:{th_ya})')
    ax.axis('off')

    if save:
        os.makedirs(f"{config.corr_config.CORR_OUTPUT_DIR}", exist_ok=True)
        plt.savefig(f"{f"{config.corr_config.CORR_OUTPUT_DIR}"}/mcc_map_thswa_{th_swa}_thya_{th_ya}.png", dpi=300)
    
    if show:
        plt.show()


def plot_max_mcc_map(ds, save=False, show=False):
    """
    Plot a map showing the maximum MCC value for each region across all threshold combinations.
    """
    gdf = get_max_mcc_shapefile(ds)
    max_mcc_ds = get_max_mcc_ds()

    # Map of maximum MCC values
    fig, ax = plt.subplots(2, 2, figsize=(15, 12))

    europe_bounds = {"minx": -25, "maxx": 45, "miny": 34, "maxy": 72}
    for (i, j) in [(0, 0), (0, 1), (1, 1)]:
        ax[i, j].set_xlim(europe_bounds["minx"], europe_bounds["maxx"])
        ax[i, j].set_ylim(europe_bounds["miny"], europe_bounds["maxy"])

    gdf.boundary.plot(ax=ax[0,0], color='black', linewidth=0.2, zorder=2)
    gdf.plot(column='Max_MCC', ax=ax[0,0], cmap="Blues", vmin=0, vmax=1)
    
    ax[0,0].set_title('Maximum MCC Map')
    ax[0,0].axis('off')

    gdf.boundary.plot(ax=ax[0,1], color='black', linewidth=0.2, zorder=2)
    gdf.plot(column='TH_SWA', ax=ax[0,1], cmap="jet", vmin=0)
    ax[0,1].set_title('TH_SWA at Max MCC')
    ax[0,1].axis('off')

    gdf.boundary.plot(ax=ax[1,1], color='black', linewidth=0.2, zorder=2)
    gdf.plot(column='TH_YA', ax=ax[1,1], cmap="plasma", vmin=-1.5, vmax=0)
    ax[1,1].set_title('TH_YA at Max MCC')
    ax[1,1].axis('off')

    # Annotate the bottom-left subplot with the maximum MCC value
    max_mcc_value = np.nanmax(max_mcc_ds.values)
    region_idx = np.nanargmax(max_mcc_ds.values)
    region_name = max_mcc_ds['region'].values[region_idx]
    mean_mcc_value = np.nanmean(max_mcc_ds.values)
    ax[1,0].annotate(
        f"Max MCC: {max_mcc_value:.2f}\nRegion: {region_name} \n\nMean MCC: {mean_mcc_value:.2f}",
        xy=(0.5, 0.5), xycoords='axes fraction', ha='center', va='center',
        fontsize=12, fontweight='bold'
    )
    ax[1,0].axis('off')

    for (i,j) in [(0,0), (0,1), (1,1)]:
        ax[i,j].set_aspect('equal')
        if (i,j) == (0,0):
            cbar = plt.cm.ScalarMappable(cmap="Blues", norm=plt.Normalize(vmin=0, vmax=1))
            cbar._A = []
            fig.colorbar(cbar, ax=ax[i,j], orientation='horizontal', fraction=0.05, pad=0.05, aspect=50, shrink=0.7)
        elif (i,j) == (0,1):
            cbar = plt.cm.ScalarMappable(cmap="jet", norm=plt.Normalize(vmin=0, vmax=ds['TH_SWA'].values.max()))
            cbar._A = []
            fig.colorbar(cbar, ax=ax[i,j], orientation='horizontal', fraction=0.05, pad=0.05, aspect=50, shrink=0.7,
                         extend="max", ticks=ds['TH_SWA'].values.round(1).tolist())
        elif (i,j) == (1,1):
            cbar = plt.cm.ScalarMappable(cmap="plasma", norm=plt.Normalize(vmin=-1.5, vmax=0))
            cbar._A = []
            fig.colorbar(cbar, ax=ax[i,j], orientation='horizontal', fraction=0.05, pad=0.05, aspect=50, shrink=0.7,
                         extend="min", ticks=ds['TH_YA'].values)

        for idx, row in gdf.iterrows():
            if row['geometry'] is not None and not np.isnan(row['Max_MCC']):
                centroid = row['geometry'].centroid
                if (i,j) == (0,0):
                    ax[i,j].annotate(f"{row['Max_MCC']:.2f}", xy=(centroid.x, centroid.y),
                                ha='center', va='center', fontsize=4, color="black", bbox={"boxstyle": "round, pad=0.2, rounding_size=0.5", "facecolor":"white", "ec":"black", "lw":0.2, "alpha":0.7}, zorder=5)
                if (i,j) == (0,1):
                    ax[i,j].annotate(f"{row['TH_SWA']:.2f}", xy=(centroid.x, centroid.y),
                                    ha='center', va='center', fontsize=4, color="black", bbox={"boxstyle": "round, pad=0.2, rounding_size=0.5", "facecolor":"white", "ec":"black", "lw":0.2, "alpha":0.7}, zorder=5)
                elif (i,j) == (1,1):
                    ax[i,j].annotate(f"{row['TH_YA']:.2f}", xy=(centroid.x, centroid.y),
                                    ha='center', va='center', fontsize=4, color="black", bbox={"boxstyle": "round, pad=0.2, rounding_size=0.5", "facecolor":"white", "ec":"black", "lw":0.2, "alpha":0.7}, zorder=5)

    plt.tight_layout()

    if save:
        os.makedirs(f"{config.corr_config.CORR_OUTPUT_DIR}", exist_ok=True)
        plt.savefig(f"{f"{config.corr_config.CORR_OUTPUT_DIR}"}/max_mcc_map.png", dpi=300)
        plt.close()
    
    if show:
        plt.show()  
    


def interactive_mcc_map(ds):
    """
    Interactive MCC map with sliders for TH_SWA and TH_YA.
    """
    th_swa_vals = ds['TH_SWA'].values
    th_ya_vals = ds['TH_YA'].values

    th_swa_init = th_swa_vals[0]
    th_ya_init = th_ya_vals[0]

    mcc_da = ds.sel(TH_SWA=th_swa_init, TH_YA=th_ya_init)['MCC']
    df_mcc = pd.DataFrame({'Region': mcc_da['region'].values, 'MCC': mcc_da.values})
    gdf = read_shapefile()
    mcc_gdf = associate_shp_data(gdf, df_mcc, 'MCC')

    fig, ax = plt.subplots(figsize=(10, 8))
    plt.subplots_adjust(left=0.25)

    mcc_gdf.plot(column='MCC', ax=ax, legend=False, cmap='coolwarm', vmin=-1, vmax=1)
    ax.set_title(f'MCC Map (TH_SWA={th_swa_init:.2f}, TH_YA={th_ya_init:.2f})')
    ax.axis('off')

    # Ajoute la colorbar une seule fois et garde la référence
    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(vmin=-1, vmax=1))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical', fraction=0.03, pad=0.04)

    # Sliders
    ax_swa = plt.axes([0.05, 0.2, 0.03, 0.6])
    ax_ya = plt.axes([0.10, 0.2, 0.03, 0.6])
    slider_swa = Slider(ax_swa, 'TH_SWA', th_swa_vals.min(), th_swa_vals.max(), valinit=th_swa_init, valstep=th_swa_vals, orientation="vertical")
    slider_ya = Slider(ax_ya, 'TH_YA', th_ya_vals.min(), th_ya_vals.max(), valinit=th_ya_init, valstep=th_ya_vals, orientation="vertical")

    def update(val):
        th_swa = slider_swa.val
        th_ya = slider_ya.val
        mcc_da = ds.sel(TH_SWA=th_swa, TH_YA=th_ya)['MCC']
        df_mcc = pd.DataFrame({'Region': mcc_da['region'].values, 'MCC': mcc_da.values})
        mcc_gdf_updated = associate_shp_data(gdf, df_mcc, 'MCC', shp_id_col="NUTS_ID", data_id_col="Region")
        ax.clear()
        mcc_gdf_updated.plot(column='MCC', ax=ax, legend=False, cmap='coolwarm', vmin=-1, vmax=1)
        ax.set_title(f'MCC Map (TH_SWA={th_swa:.2f}, TH_YA={th_ya:.2f})')
        ax.axis('off')
        fig.canvas.draw_idle()

    slider_swa.on_changed(update)
    slider_ya.on_changed(update)

    print("===> Interactive MCC map with Matplotlib:")

    plt.show()



def holoviz_interactive_mcc(ds, mode=None):
    """
    Interactive MCC map using Holoviz and Panel.
    Args:
        ds (xarray.Dataset): Dataset containing MCC values and thresholds.
        mode (str, optional): 'notebook' or 'browser' for Panel display mode. If None, auto-detects the environment.
    Returns:
        None: Displays the interactive map.
    If mode is 'notebook', it will display in the Jupyter notebook.
    If mode is 'browser', it will open in a new browser tab.
    """
    th_swa_vals = [round(v, 2) for v in ds["TH_SWA"].values]
    th_ya_vals = list(ds["TH_YA"].values)

    class MCCMap(param.Parameterized):
        th_swa  = param.Selector(label="TH_SWA", objects=th_swa_vals, default=th_swa_vals[0])
        th_ya   = param.Selector(label="TH_YA", objects=th_ya_vals, default=th_ya_vals[0])
        cmap    = param.Selector(label="cmap", objects=["coolwarm", "coolwarm_r", "RdBu", "RdBu_r", "PiYG", "PiYG_r"], default="coolwarm")
        clim    = param.Range(label="Colorbar Range", default=(-1, 1), bounds=(-1, 1))

        @param.depends('th_swa', 'th_ya', 'cmap', 'clim')
        def view(self):
            idx_swa = th_swa_vals.index(self.th_swa)
            th_swa_raw = ds["TH_SWA"].values[idx_swa]
            th_ya_raw = self.th_ya

            # Extraire MCC pour ce seuil
            mcc_da = ds.sel(TH_SWA=th_swa_raw, TH_YA=th_ya_raw)['MCC']
            df_mcc = pd.DataFrame({'NUTS_ID': mcc_da['region'].values, 'MCC': mcc_da.values})

            # Lire shapefile + fusion
            gdf = read_shapefile()  # doit contenir une colonne 'NUTS_ID'
            gdf = associate_shp_data(gdf, df_mcc, 'MCC', shp_id_col="NUTS_ID", data_id_col="NUTS_ID")

            # S'assurer que NUTS_ID existe bien
            if 'NUTS_ID' not in gdf.columns:
                gdf['NUTS_ID'] = gdf.index

            # Palette
            import matplotlib.colors as mcolors
            base_cmap = plt.get_cmap(self.cmap)
            clim_min, clim_max = self.clim
            if (clim_min, clim_max) != (-1, 1):
                left = (clim_min + 1) / 2
                right = (clim_max + 1) / 2
                truncated_cmap = mcolors.LinearSegmentedColormap.from_list(
                    f"trunc({self.cmap},{clim_min},{clim_max})",
                    base_cmap(np.linspace(left, right, 256))
                )
            else:
                truncated_cmap = base_cmap

            # Plot interactif avec hover MCC + NUTS_ID
            gdf_hv = gv.Polygons(
                gdf, vdims=['MCC', 'NUTS_ID']
            ).opts(
                cmap=truncated_cmap, color='MCC', tools=['hover', 'wheel_zoom'],
                width=800, height=600, colorbar=True, clim=self.clim,
                title=f'MCC Map | TH_SWA:{self.th_swa} - TH_YA:{th_ya_raw}',
                xlim=(-12, 42), ylim=(35, 72),
            )
            return gdf_hv

    mcc_map = MCCMap()
    pn.extension()

    print("===> Interactive MCC map:")
    print("Please do not change the parameters too quickly to avoid an Error message")
    print("The error does not affect the functionality of the interactive plot")    

    if mode is None:
        ipython = get_ipython()
        if ipython is not None and 'IPKernelApp' in ipython.config:
            mode = 'notebook'
        else:
            mode = 'browser'

    if mode == 'notebook':
        display = pn.Row(mcc_map.param, mcc_map.view)
        display.servable()
        return display
    elif mode == 'browser':
        pn.serve(pn.Row(mcc_map.param, mcc_map.view), show=True)
    else:
        raise ValueError("Invalid mode. Choose 'notebook' or 'browser'.")

