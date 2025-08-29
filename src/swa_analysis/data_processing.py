# ---------- HEADER --------------------------------------------
# File : src/swa_analysis/data_processing.py
# Author(s) : Enzo Fortin
#
# Description :
# This file aims to process the SWA data for their analysis. During the internship we only focused on SWA data over Europe.
# So the region here corresponds to Europe and subregion to NUTS.
# --------------------------------------------------------------
import numpy as np
import os
import rioxarray as rxr
import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
import src.swa_analysis.visualization as visualization
import src.utils as utils

config = None  # Have to be set from outside before using the functions


# ---------- FUNCTIONS -----------------------------------------
def open_raster(path, masked=True):
    """Open a raster file using rioxarray.
    Args:
        path (str, required): Path to the raster file.
        masked (bool, optional): If True, mask the raster data. Defaults to True.
    Returns:
        raster (xarray.DataArray): The opened raster data.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raster file not found at {path}")
    raster = rxr.open_rasterio(path, masked=masked).squeeze()
    return raster

def process_swa(swa, corine, threshold, save=False, show=False, date=False):
    """Process SWA data with Corine Land Cover data.
    Here the SWA raster is filtered by a threshold and weighted by the Corine raster.
    Args:
        swa(..., required): SWA raster data.
        corine (..., required): Corine Land Cover raster data.
        threshold (float, required): Threshold value to filter the SWA data. Coresponds to the value for drought occurence.
        save (bool, optional): If True, save the processed data. Defaults to False.
        show (bool, optional): If True, display the processed data. Defaults to False.
        date (bool, optional): If True, include date in the output. Defaults to False.
    Returns:
        swa_drought_corine (xarray.DataArray): Processed SWA data weighted by Corine Land Cover data.
    """
    swa = swa.rio.clip_box(minx=corine.rio.bounds()[0],miny=corine.rio.bounds()[1],maxx=corine.rio.bounds()[2],maxy=corine.rio.bounds()[3]).drop_vars(["band"])
    corine = corine.rio.reproject_match(swa).sel(band=1).drop_vars(["band", "spatial_ref"])/255.0

    swa_filtered = swa.where(swa < threshold, other=np.nan)
    swa_binary = swa_filtered.notnull().astype(int)
    swa_drought_corine = swa_binary * corine

    if save:
        output_path = f"{config.swa_config.SWA_PROCESSED_DIR}/swa_processed_corine_{date}.tif" if date else f"{config.swa_config.SWA_PROCESSED_DIR}/swa_processed_corine.tif"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not os.path.exists(output_path):
            swa_drought_corine.rio.to_raster(output_path)

    if show:
        visualization.plot_raster(swa_drought_corine, title="SWA Drought X Corine Land Cover", date=date)

    return swa_drought_corine



def spatial_mean_shp(raster_path, shapefile, date="", save=False, show=False, **kwargs):
    """Transform a raster file into a shapefile with the mean values of the raster for each regions in the shapefile.
    Args:
        raster_path (strn required): Path to the raster file containing SWA data.
        nuts_shapefile (str, required): Path to the NUTS shapefile to use for aggregation.
        save (bool, optional): If True, save the aggregated raster. Defaults to False.
    Returns:
        NUTS_swa (GeoDataFrame): A GeoDataFrame containing the aggregated SWA mean values for each NUTS region.
    """
    # Open the NUTS shapefile if it's a path, otherwise use the GeoDataFrame directly
    if isinstance(shapefile, str):
        spatial_mean_shp = gpd.read_file(shapefile)
    else:
        spatial_mean_shp = shapefile.copy()

    # Perform zonal statistics to calculate the mean SWA for each NUTS region
    stats = zonal_stats(spatial_mean_shp, raster_path, stats="mean", nodata=np.nan, geojson_out=True)

    # Convert the zonal statistics results to a GeoDataFrame
    spatial_mean_shp["mean"] = [feature["properties"]["mean"] for feature in stats]
    spatial_mean_shp = spatial_mean_shp.drop(columns=["NAME_LATN", "NUTS_NAME", "MOUNT_TYPE", "URBN_TYPE", "COAST_TYPE"], errors="ignore")

    # Save the aggregated raster if requested
    if save:
        output_path = f"{config.swa_config.SWA_SPATIAL_MEAN_DIR}/spatial_mean_swa_{date}.shp"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not os.path.exists(output_path):
            spatial_mean_shp.to_file(output_path, driver="ESRI Shapefile")

    if show:
        visualization.plot_shapefile(spatial_mean_shp, column="mean", title="Spatial Mean SWA by NUTS Regions", date=date, show=True, boundaries="europe" ,threshold=kwargs.get("threshold", "#N/A"))

    return spatial_mean_shp



def temporal_mean_shp(list_dates, save=False, show=False, save_plot=False, **kwargs):
    """Calculate the temporal mean of the processed shapefile for a given period.
    Args:
        list_dates (list, required): List of dates to process. Formatted as 'YYYY-MM'
        period (str, required): Period to calculate the mean for.
        nuts_shapefile (str, optional): Path to the NUTS shapefile to use for processing spatial_mean.
                                        Have to be provided if at least one of the spatial_mean_shp is not found. Defaults to None.
        save (bool, optional): If True, save the aggregated raster. Defaults to False.
    Returns:
        ...
    """
    spatial_mean_shp_list = []
    for date in list_dates:
        shapefile_path = f"{config.swa_config.SWA_SPATIAL_MEAN_DIR}/spatial_mean_swa_{date}.shp"
        if os.path.exists(shapefile_path):
            spatial_mean_gdf = gpd.read_file(shapefile_path)
            spatial_mean_shp_list.append(spatial_mean_gdf)
        else:
            raise FileNotFoundError(f"Shapefile for date {date} not found at {shapefile_path}. Please ensure the shapefile exists or create it using spatial_mean_shp function.")

    # Concatenate the GeoDataFrames
    NUTS_period = pd.concat([gdf[["NUTS_ID", "mean"]].assign(date=date) for gdf, date in zip(spatial_mean_shp_list, list_dates)], ignore_index=True)
    # Calculate the temporal mean for each NUTS over the period
    NUTS_mean = NUTS_period.groupby("NUTS_ID")["mean"].mean().reset_index()
    # Merge the mean values back to the NUTS shapefile
    NUTS_swa_period = spatial_mean_shp_list[0][["NUTS_ID", "geometry"]].merge(NUTS_mean, on="NUTS_ID")

    year = list_dates[0].split("-")[0]
    month_start = int(list_dates[0].split("-")[1])
    month_end = int(list_dates[-1].split("-")[1])


    if save:
        output_path = f"{config.swa_config.SWA_TEMPORAL_MEAN_DIR}/temporal_mean_swa-{year}-{utils.get_month_str(month_start)}_{utils.get_month_str(month_end)}.shp"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        NUTS_swa_period.to_file(output_path, driver="ESRI Shapefile")

    if show:
        visualization.plot_shapefile(NUTS_swa_period, column="mean", title="Temporal Mean SWA by NUTS Regions", date=f"{list_dates[0]} - {list_dates[-1]}", show=True, boundaries="europe", threshold=kwargs.get("threshold", "#N/A"))

    if save_plot:
        output_path = f"{config.swa_config.SWA_TEMPORAL_MEAN_MAP_DIR}/temporal_mean_swa_-{year}-{utils.get_month_str(month_start)}_{utils.get_month_str(month_end)}.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not os.path.exists(output_path):
            visualization.plot_shapefile(NUTS_swa_period, column="mean", save=True, show=False, date=f"{list_dates[0]} - {list_dates[-1]}", boundaries="europe", threshold=kwargs.get("threshold", "#N/A"), save_path=output_path)

    return NUTS_swa_period


def temporal_series_region(year_start=None, year_end=None, month_start=None, month_end=None, save=False, show_plot=False, save_plot=False, threshold=None, **kwargs):
    """Calculate the temporal series of the Mean SWA for a given region over a period.
    """
    list_years = list(range(year_start, year_end + 1)) if year_start and year_end else [year_start]
    list_months = list(range(month_start, month_end + 1)) if month_start and month_end else [month_start]

    month_start_str, month_end_str = utils.get_month_str(month_start), utils.get_month_str(month_end)

    def check_temporal_mean_shp_available(list_years):
        """Check if the temporal mean shapefile for a year already exist, if not, it creates the shapefile"""
        for year in list_years:
            if not os.path.exists(f"{config.swa_config.SWA_TEMPORAL_MEAN_DIR}/temporal_mean_swa-{year}-{month_start_str}_{month_end_str}.shp"):
                raise FileNotFoundError(f"Temporal mean shapefile for year {year} not found. Please create it using temporal_mean_shp function.")

    check_temporal_mean_shp_available(list_years)

    list_shapefiles = {year : f"{config.swa_config.SWA_TEMPORAL_MEAN_DIR}/temporal_mean_swa-{year}-{month_start_str}_{month_end_str}.shp" for year in list_years}
    
    merged_gdf = pd.concat([gpd.read_file(list_shapefiles[year]).assign(year=year)[["NUTS_ID", "year", "mean"]] for year in list_years], ignore_index=True)

    temporal_series = merged_gdf.pivot(index="year", columns="NUTS_ID", values="mean")

    if save:
        output_path = f"{config.swa_config.SWA_TEMPORAL_SERIES_DIR}/temporal_series_swa-{year_start}_{year_end}-{month_start_str}_{month_end_str}.xlsx"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        temporal_series.to_excel(output_path, index=True, header=True)

    visualization.plot_time_serie(temporal_series, save=save_plot, show=show_plot, save_dir=f"{config.swa_config.SWA_TEMPORAL_SERIES_PLOT_DIR}/temporal_series_swa-{year_start}_{year_end}-{month_start_str}_{month_end_str}", threshold=threshold, year_start=year_start, year_end=year_end, month_start=month_start_str, month_end=month_end_str)

    return temporal_series
# --------------------------------------------------------------


# ---------- SCRIPTS -------------------------------------------
def run_swa(threshold, year_start=None, year_end=None, month_start=None, month_end=None):
    """Run SWA drought analysis for a given date or period.
    Args:
        threshold (float, required): Threshold value to filter the SWA data.
        date (str, optional): Date in 'YYYY-MM' format to process. Defaults to None.
        date_start (str, optional): Start date in 'YYYY-MM' format for a period. Defaults to None.
        date_end (str, optional): End date in 'YYYY-MM' format for a period. Defaults to None.
        period (str, optional): Period to process. Defaults to None.
    Returns:
        None: Runs the analysis and saves the results. 
    """
    list_years = list(range(year_start, year_end + 1)) if year_start and year_end else [year_start]
    list_months = list(range(month_start, month_end + 1)) if month_start and month_end else [month_start]

    print(f"Custom data directory: {config.swa_config.CUSTOM_DATA_DIR}")

    progress_total = len(list_years) * len(list_months)
    progress_count = 0

    for year in list_years:
        for month in list_months:
            date = utils.date(year, month)

            swa_path = f"{config.swa_config.SWA_ANOM_DIR}/swa_{utils.date(year, month, multplier_month=3)}.tif"
            swa = rxr.open_rasterio(swa_path, masked=True).squeeze()

            corine = rxr.open_rasterio(config.paths.CORINE_TIF, masked=True).squeeze()

            processed_swa = process_swa(swa, corine, threshold, date=date, save=True)

            spatial_mean = spatial_mean_shp(f"{config.swa_config.SWA_PROCESSED_DIR}/swa_processed_corine_{date}.tif", config.paths.NUTS_SHAPEFILE, date=date, save=True, threshold=threshold)

            # Remove the processed raster to save space
            remove_processed_path = f"{config.swa_config.SWA_PROCESSED_DIR}/swa_processed_corine_{date}.tif"
            if os.path.exists(remove_processed_path):
                os.remove(remove_processed_path)      

            progress_count += 1/(len(list_years)*len(list_months))*100
            utils.progress_bar(progress_count, 100, prefix=f"Processing date {year}-{month} | Overall Progress:", suffix="Complete", bar_length=50)

        list_dates_year = [utils.date(year, month) for month in list_months]
        temporal_mean_shp(list_dates_year, save=True, save_plot=True, threshold=threshold)

    temporal_series_region(year_start, year_end, month_start, month_end, save=True, show_plot=False, save_plot=True, threshold=threshold)
# --------------------------------------------------------------

# --------------------------------------------------------------
if __name__ == "__main__":
    from src.config import Config
    config = Config()
    run_swa(config.th_detection_drought, year_start=config.start_year, year_end=config.end_year, month_start=config.month_start, month_end=config.month_end
    )
