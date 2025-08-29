# ---------- HEADER --------------------------------------------
# File : src/combiantion/combination.py
# Author(s) : Enzo Fortin
#
# Description :
# This module computes the Matthews Correlation Coefficient (MCC) between
# Standardized Water Anomaly (SWA) and yield anomalies for various thresholds.
# --------------------------------------------------------------
import src.utils as utils
import os
import pandas as pd
import warnings
import xarray as xr
import numpy as np
from sklearn.metrics import matthews_corrcoef

config = None  # to be set from outside

# ---------- CONSTANTS -----------------------------------------
# swa_threshold = config.th_detection_drought
# period_agg = utils.get_period_aggregation_str(config.month_start, config.month_end)

# list_TH_SWA = config.TH_SWA_list
# list_TH_YA = config.TH_YA_list

# TH_YA = config.TH_SWA
# TH_SWA = config.TH_YA 

# FILE_YA = config.paths.CORR_YA_FILE
# FILE_SWA = config.paths.CORR_SWA_FILE
# --------------------------------------------------------------

# ---------- FUNCTIONS -----------------------------------------
def check_data_input():
    """
    Check if the data needed for the combination is available.
    """
    if not os.path.exists(config.paths.CORR_YA_FILE):
        raise FileNotFoundError(f"Yield anomaly file not found: {config.paths.CORR_YA_FILE}")
    if not os.path.exists(config.paths.CORR_SWA_FILE):
        raise FileNotFoundError(f"SWA data directory not found: {config.paths.CORR_SWA_FILE}")

def read_excel_data(file_path):
    """Read data from an Excel file in a specific format.
    Args:
        file_path (str): Path to the Excel file.
    Returns:
        ...
    """
    with pd.ExcelFile(file_path) as xls:
        df = pd.read_excel(xls, header=0, index_col=0)
    return df

def add_european_average(df):
    """Add a column with the sum of all NUTS regions in Europe for all years (index).
    Args:
        df (pd.DataFrame): DataFrame with NUTS regions as columns.
    Returns:
        pd.DataFrame: DataFrame with an additional column for the sum of all NUTS regions.
    """
    df["EUROPE_AVG"] = df.mean(axis=1)
    return df

def add_european_boolean_sum(df):
    """Add a column with the sum of all NUTS regions in Europe for all years (index), for boolean data.
    Args:
        df (pd.DataFrame): DataFrame with NUTS regions as columns.
    Returns:
        pd.DataFrame: DataFrame with an additional column for the sum of all NUTS regions.    
    """
    df["EUROPE_SUM"] = df.sum(axis=1)
    return df

def bool_data_threshold(arr, data_type, threshold):
    """Vectorized thresholding using NumPy for speed."""
    if data_type == "swa":
        mask = (arr >= threshold).astype(np.int8)
    elif data_type == "ya":
        mask = (arr <= threshold).astype(np.int8)
    else:
        raise ValueError("data_type must be either swa or ya")
    return mask


def save_to_netcdf(ds):
    """Save the MCC dataset results to a NetCDF file. With a specific construction"""
    ds = xr.Dataset({"MCC": ds})

    # Global attributes
    ds.attrs["description"]         = "Matthews Correlation Coefficient (MCC) between Standardized Water Anomaly (SWA) and Yield Anomalies for various thresholds"
    ds.attrs["author"]              = "Enzo Fortin"
    ds.attrs["institution"]         = "Politecnico di Milano"
    ds.attrs["note"]                = "Work performed during internship at Politecnico di Milano - Summer 2025"
    ds.attrs["swa_threshold"]       = config.th_detection_drought
    ds.attrs["period_aggregation"]  = utils.get_period_aggregation_str(config.month_start, config.month_end)

    ds.attrs["TH_SWA_list"]         = config.TH_SWA_list
    ds.attrs["TH_YA_list"]          = config.TH_YA_list

    # Variable attributes
    ds["MCC"].attrs["long_name"] = "Matthews Correlation Coefficient"
    ds["MCC"].attrs["units"] = "unitless"

    # Coordinate attributes
    ds["TH_SWA"].attrs["long_name"] = "Thresholds for Standardized Water Anomaly"
    ds["TH_SWA"].attrs["units"] = "unitless"
    ds["TH_YA"].attrs["long_name"] = "Thresholds for Yield Anomalies"
    ds["TH_YA"].attrs["units"] = "unitless"
    ds["region"].attrs["long_name"] = "NUTS regions"
    ds["region"].attrs["units"] = "unitless"
    
    os.makedirs(config.corr_config.CORR_RESULTS_DIR, exist_ok=True)
    try:
        ds.to_netcdf(f"{config.corr_config.CORR_RESULTS_DIR}/mcc_results.nc", format="NETCDF4", engine="h5netcdf")
    except Exception as e:
        print(f"Error saving to NetCDF: {e}")
        ds.to_netcdf(f"{config.corr_config.CORR_RESULTS_DIR}/mcc_results.nc")

def save_to_excel(df):
    """Save the MCC DataArray results to an Excel file with one sheet per region and a summary sheet."""
    excel_df = df.to_dataframe().reset_index()
    output_path = f"{config.corr_config.CORR_RESULTS_DIR}/mcc_results.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        excel_df.to_excel(writer, sheet_name="All regions", index=False)
        for region in df.region.values:
            region_df = excel_df[excel_df["region"] == region].drop(columns=["region"])
            region_df.to_excel(writer, sheet_name=str(region), index=False)

def compute_mcc_xarray(ds_swa, ds_ya, th_swa_list, th_ya_list):
    """
    Compute MCC for all regions and all threshold combinations using xarray.
    Args:
        ds_swa (xr.DataArray): dims ("time", "region")
        ds_ya (xr.DataArray): dims ("time", "region")
        th_swa_list (list): thresholds for SWA
        th_ya_list (list): thresholds for YA
    Returns:
        xr.DataArray: dims ("TH_SWA", "TH_YA", "region"), MCC values
    """
    regions = ds_swa.region.values
    mcc_array = np.zeros((len(th_swa_list), len(th_ya_list), len(regions)))
    total = len(th_swa_list) * len(th_ya_list)
    step = 0
    for i, th_swa in enumerate(th_swa_list):
        swa_bin = bool_data_threshold(ds_swa.values, "swa", th_swa)
        for j, th_ya in enumerate(th_ya_list):
            ya_bin = bool_data_threshold(ds_ya.values, "ya", th_ya)
            for k, region in enumerate(regions):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=UserWarning)
                    mcc = matthews_corrcoef(swa_bin[:, k], ya_bin[:, k])
                mcc_array[i, j, k] = mcc
            step += 1
            utils.progress_bar(step, total, prefix="Computing MCC:", suffix="Complete", bar_length=40)
    return xr.DataArray(
        mcc_array,
        coords={
            "TH_SWA": th_swa_list,
            "TH_YA": th_ya_list,
            "region": regions
        },
        dims=["TH_SWA", "TH_YA", "region"]
    )
# --------------------------------------------------------------

# ---------- MAIN PROGRAM ---------------------------------------
def main(netcdf=False, excel=False):
    check_data_input()

    df_ya, df_swa = read_excel_data(config.paths.CORR_YA_FILE), read_excel_data(config.paths.CORR_SWA_FILE)

    df_ya.columns.name, df_swa.columns.name = "region", "region"
    df_ya.index.name, df_swa.index.name = "time", "time"

    ds_ya = xr.DataArray(df_ya.values, dims=["time", "region"], coords={"time": df_ya.index, "region": df_ya.columns})
    ds_swa = xr.DataArray(df_swa.values, dims=["time", "region"], coords={"time": df_swa.index, "region": df_swa.columns})

    mcc_ds = compute_mcc_xarray(ds_swa, ds_ya, config.TH_SWA_list, config.TH_YA_list)
    mcc_ds.name = "MCC"

    if netcdf: save_to_netcdf(mcc_ds)
    if excel: save_to_excel(mcc_ds)


if __name__ == "__main__":
    from src.config import config
    config = config
    main(netcdf=False, excel=True)
# --------------------------------------------------------------


