# ---------- HEADER --------------------------------------------
# File : src/yield_analysid/data_processing.py
# Author(s) : Enzo Fortin
#
# Description :
# This module contains functions to process yield data for various regions.
# --------------------------------------------------------------
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import geopandas as gpd
import os
from src.config import config



def get_prod_anom(region, return_data=False, return_years=False, return_meta=False, save=False)-> dict:
    """
    Prepares the data for the specified region by reading production and area data.
    Args:
        region (str): The region for which to prepare the data.
        return_years (bool): If True, also return the years array.
        return_meta (bool): If True, also return name, iso_3166_2, code arrays.
    Returns:
        np.ndarray: Array containing production anomalies.
        np.ndarray (optional): Array of years, if return_years is True.
        tuple (optional): name, iso_3166_2, code arrays, if return_meta is True.
    """
    if region not in config.yield_config.REGIONS and region != "europe":
        raise ValueError(f"Region '{region}' is not defined in config.yield_config.REGIONS.")

    file_prod = f"{config.yield_config.DATA_STANDARDIZED_DIR}/{region}/prod_{region}_standardized.xlsx"
    file_area = f"{config.yield_config.DATA_STANDARDIZED_DIR}/{region}/area_{region}_standardized.xlsx"
    
    data_prod = pd.read_excel(file_prod, header=None, index_col=0)
    data_area = pd.read_excel(file_area, header=None, index_col=0)

    name = data_prod.iloc[0,].values.astype(str)
    iso_3166_2 = data_prod.iloc[1,].values
    code = data_prod.iloc[2,].values.astype(str)
    years = data_prod.index.values[3:].astype(int)

    prod = data_prod.iloc[3:,0:].values.astype(float)
    area = data_area.iloc[3:,0:].values.astype(float)

    n_site = prod.shape[1]
    prod_anom = np.full(prod.shape, np.nan)

    data_sub_df = np.full(prod.shape, np.nan)
    filt_sub_df = np.full(prod.shape, np.nan)

    for pos in range(n_site):
        with np.errstate(divide="ignore", invalid="ignore"):
            data_sub = np.where((area[:, pos] == 0) | np.isnan(area[:, pos]), np.nan, prod[:, pos] / area[:, pos])
        nn = len(data_sub)
        pos_bad = np.where(np.isnan(data_sub))[0]

        if len(pos_bad) / nn < 0.35:
            data_sub2 = np.concatenate((data_sub[::-1], data_sub, data_sub[::-1]))

            mask_no = np.where(np.isnan(data_sub2))[0]
            mask_ok = np.where(~np.isnan(data_sub2))[0]

            data_int = interp1d(mask_ok, data_sub2[mask_ok], bounds_error=False, fill_value="extrapolate")
            data_sub3 = data_sub2.copy()
            data_sub3[mask_no] = data_int(mask_no)

            filt_data = savgol_filter(data_sub3, polyorder=2, window_length=7, deriv=0,delta=1.)   
            filt_sub = filt_data[nn:2*nn]
            filt_sub[pos_bad] = np.nan

            data_sub_df[:, pos] = data_sub
            filt_sub_df[:, pos] = filt_sub

            data_sub2 = data_sub-filt_sub

            prod_anom[:, pos] = (data_sub2-np.nanmean(data_sub2))/np.nanstd(data_sub2)

    prod_anom = pd.DataFrame(prod_anom, columns=iso_3166_2 if region!="europe" else code, index=years)
    prod_anom.index.name = "year"
    prod_anom.columns.name = "id"
    prod_anom = prod_anom.sort_index(axis=1)

    # Build the return tuple based on requested flags
    result = {"prod_anom": prod_anom}
    if return_data: result["data_sub"], result["filt_sub"] = data_sub_df, filt_sub_df
    if return_years: result["years"] = years
    if return_meta: result["name"], result["iso_3166_2"], result["code"] = name, iso_3166_2, code

    if save:
        output_file = f"{config.yield_config.OUTPUT_DIR}/{region}_prod_anom-{years[0]}_{years[-1]}.xlsx"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        prod_anom.to_excel(output_file, index=True, header=True)

    return result



def get_anom_df(region, sel_years=None, return_years=False, return_meta=False):
    """
    Args:
        region (str): Region to retrieve anomaly data for.
        sel_years (tuple or list, optional): Year range (start, end) to filter. If None, all years are included.
        return_years (bool, optional): If True, includes the list of years.
        return_meta (bool, optional): If True, includes metadata (name, iso_3166_2, code).
    ----------------
    Returns:
        anom_df_long (pd.DataFrame): DataFrame containing the anomalies in long format.
        years (list, optional): List of years if return_years is True.
        name (np.ndarray, optional): Array of names if return_meta is True.
        iso_3166_2 (np.ndarray, optional): Array of ISO 3166-2 codes if return_meta is True.
        code (np.ndarray, optional): Array of codes if return_meta is True.
    """
    code_mapping = config.yield_config.get_code_mapping(region)
    prod_anom, years, name, id, code = get_prod_anom(region, return_years=True, return_meta=True).values()

    gdf = gpd.read_file(f"{config.paths.SHAPEFILES_DIR}/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp" if region!="europe" else f"{config.paths.SHAPEFILES_DIR}/NUTS_shapefile/NUTS_aggregated.shp")

    anom_df = pd.DataFrame(prod_anom, columns=id if region!="europe" else code, index=years)
    anom_df.index.name = "year"
    id_df = pd.DataFrame({"code":code, "id":id, "name":name})
    anom_df_long = anom_df.reset_index().melt(id_vars="year", var_name="id" if region!="europe" else "code", value_name="anom")
    anom_df_long = anom_df_long.merge(id_df, on="id" if region!="europe" else "code", how="left")

    rows = []
    for _, row in anom_df_long.iterrows():
        code = row["code"]
        if code in code_mapping:
            for subcode in code_mapping[code]:
                new_row = row.copy()
                new_row["code"] = subcode
                rows.append(new_row)
        else:
            rows.append(row)
    anom_df_long = pd.DataFrame(rows)

    if sel_years is not None:
        years = [year for year in range(sel_years[0], sel_years[1] + 1)]
    else:
        years = sorted(anom_df_long["year"].unique())

    anom_df_long.index, anom_df_long.index.name = anom_df_long["id"], "id"

    # Build the return tuple based on requested flags
    result = {"anom_df_long": anom_df_long}
    if return_years: result["years"] = years
    if return_meta: result["name"], result["iso_3166_2"], result["code"] = name, id, code
    return result



def mult_regions(regions:list, sel_years=None):
    """Aggregates multiple regions into a single DataFrame.
    """
    if not isinstance(regions, list):
        raise ValueError("regions must be a list of region names.")
    
    anom_df_list = []
    for region in regions:
        if region not in config.yield_config.REGIONS:
            raise ValueError(f"Region '{region}' is not defined in the path dictionary.")
        anom_df, years, name, id, code = get_anom_df(region, return_years=True, return_meta=True).values()
        anom_df_list.append(anom_df)

    combined_anom_df = pd.concat(anom_df_list, ignore_index=True)
    combined_anom_df = combined_anom_df.sort_values(by=["year", "id"]).reset_index(drop=True)
    return combined_anom_df



def process_area_covered(region, sel_years=None, save=False, thresh_min=-2.5, thresh_max=0, step=0.5, inf=True, **kwargs):
    """Plots the time series of the area covered by the yield anomaly data for a given region.
    Args:
        region (str): The region for which to plot the area covered.
        sel_years (tuple or list, optional): Year range (star, end) to filter. If None, all years are included.
    Returns:
        None: 
    """
    if sel_years is not None:
        if not isinstance(sel_years, (tuple, list)):
            raise ValueError("sel_years must be a tuple or list.")
        sel_years = [int(year) for year in sel_years]

    file_prod, file_area = f"{config.yield_config.DATA_STANDARDIZED_DIR}/{region}/prod_{region}_standardized.xlsx", f"{config.yield_config.DATA_STANDARDIZED_DIR}/{region}/area_{region}_standardized.xlsx"

    if isinstance(region, str):
        data_prod = pd.read_excel(file_prod, index_col=0)
        data_area = pd.read_excel(file_area, index_col=0)
        anom_df, years, name, id, code = get_anom_df(region, return_years=True, return_meta=True).values()
        if sel_years is not None:
            years = [year for year in range(sel_years[0], sel_years[1] + 1) if year in years]

    elif isinstance(region, list):   
        anom_df = mult_regions(region, sel_years=sel_years)
        data_prod = pd.concat([pd.read_excel( f"{config.yield_config.DATA_STANDARDIZED_DIR}/{r}/prod_{r}_standardized.xlsx", index_col=0) for r in region], axis=1)
        data_area = pd.concat([pd.read_excel( f"{config.yield_config.DATA_STANDARDIZED_DIR}/{r}/prod_{r}_standardized.xlsx", index_col=0) for r in region], axis=1)
        id = data_area.columns.values.astype(str)
        years = anom_df["year"].unique()
        if sel_years is not None:
            years = [year for year in range(sel_years[0], sel_years[1] + 1) if year in years]  
        region = " & ".join(region) 
    
    area = data_area[2:].loc[years]
    prod = data_prod[2:].loc[years]

    prod_all = prod.values.astype(float)
    area_all = area.values.astype(float)
    columns = id
    index = years

    data_area_df = pd.DataFrame(area_all, columns=columns, index=index); data_area_df.index.name, data_area_df.columns.name = "year", "region"
    data_prod_df = pd.DataFrame(prod_all, columns=columns, index=index); data_prod_df.index.name, data_prod_df.columns.name = "year", "region"
    
    anom_df_years = anom_df.groupby("year")

    
    thresholds = np.concatenate([[-np.inf], np.linspace(thresh_min, thresh_max, int(np.abs((thresh_max-thresh_min)/step+1)), endpoint=True)])
    if not inf:
        thresholds = thresholds[1:]
    anom_area_covered = {thresh: pd.DataFrame(np.nan, index=years, columns=["area_covered_percentage"]) for thresh in thresholds}

    for year in years:
        anom_df_year = anom_df_years.get_group(year); anom_df_year = anom_df_year.set_index("id").drop(columns=["year", "name", "code"])
        data_area_year = data_area_df.loc[year].rename("area")

        anom_area_covered_year = pd.merge(anom_df_year, data_area_year, left_index=True, right_index=True, how="left")
        total_area_year = anom_area_covered_year["area"].sum()
        anom_area_covered_year = anom_area_covered_year[anom_area_covered_year["anom"]<=0].sort_values("anom", ascending=True)
        
        anom_area_covered_year["area_covered_percentage"] = anom_area_covered_year["area"] / total_area_year * 100    

        if anom_area_covered_year.empty:
            anom_area_covered_year["area_covered_percentage"] = 0

        def calculate_area_covered(thresh_min, thresh_max):
            return anom_area_covered_year[(anom_area_covered_year["anom"] >= thresh_min) & (anom_area_covered_year["anom"] <= thresh_max)]["area_covered_percentage"].sum()
        
        for thresh in thresholds:
            anom_area_covered[thresh].loc[year, "area_covered_percentage"] = calculate_area_covered(thresh_min=thresh, thresh_max=thresh_max)


    if save:
        anom_area_covered_df = pd.concat(anom_area_covered, axis=1)
        anom_area_covered_df.index.name = "year"
        filename = f"{config.yield_config.DATA_PROCESSED_DIR}/{region}/area_covered_{region}_anom_{thresh_min}_{thresh_max}_step_{step}.csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        anom_area_covered_df.to_csv(filename, index=True, header=True)


    return {
        "thresholds": thresholds,
        "anom_area_covered": anom_area_covered,
        "data_area_df": data_area_df,
        "data_prod_df": data_prod_df,
        "region": region,
        "years": years,
    }