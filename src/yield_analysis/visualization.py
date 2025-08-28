# ---------- HEADER --------------------------------------------
# File : src/yield_analysis/visualization.py
# Author(s) : Enzo Fortin
#
# Description :
# This file contains functions for visualizing yield anomaly data.
# --------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch
import cartopy.crs as ccrs
import os
import geopandas as gpd
import numpy as np
import pandas as pd

import src.yield_analysis.data_processing as dp
from src.config import config
import src.utils as utils




def plot_anomaly_series(region, type, save=False, show=False):
    """Plots the yield anomaly series of the subregion of a given region.
    Args:
        region (str): The name of the region to plot.
    Returns:
        None: Shows or saves the plot.
    """
    prod_anom_df, data_sub_df, filt_sub_df, years, name, id, code = dp.get_prod_anom(region, return_data=True, return_years=True, return_meta=True).values()
    n_sites = prod_anom_df.shape[1]

    progress_bar_step = 1

    for pos in range(n_sites):
        if type == "filtered":
            data_sub = data_sub_df[:, pos]
            filt_sub = filt_sub_df[:, pos]

            print(f"Plotting anomaly series for {name[pos]} ({id[pos]}) in {region} ...")
            # Plotting the data -> à faire sur un meme graphique (ou plusieurs)
            plt.figure(figsize=(10, 5))
            plt.plot(years, data_sub, label=name[pos])
            plt.plot(years, filt_sub, label=f"{name[pos]} (filtered)")
            plt.axhline(0, color="black", linestyle="--", linewidth=0.5)
            plt.xticks(years, rotation=60)
            plt.xlabel("Year")
            plt.ylabel("Yield anomaly (t/ha)")
            plt.title(f"Yield Anomaly for {code[pos]} - {name[pos]} ({region.capitalize()})")
            plt.legend()
            plt.tight_layout()
            plt.grid()

            if save:
                if region=="europe":
                    id[pos] = code[pos]
                filepath = f"{config.yield_config.FIGURES_DIR}/{region}/anomaly_series_filtered/anomaly_series-{id[pos]}.png"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                plt.savefig(filepath, dpi=300)
            
            if show:
                plt.show()

        elif type == "normalized":
            prod_anom = prod_anom_df.iloc[:, pos]
            # Plotting the data -> à faire sur un meme graphique (ou plusieurs)
            plt.figure(figsize=(10, 5))
            plt.plot(years, prod_anom, color="black", linewidth=.8)
            plt.axhline(0, color="black", linestyle="--", linewidth=0.5)
            plt.xticks(years, rotation=60)
            plt.xlabel("Year")
            plt.ylabel("Normalized yield anomaly")
            plt.title(f"Normalized Yield Anomaly for {code[pos]} - {name[pos]} ({region.capitalize()})")
            plt.tight_layout()
            plt.grid()

            if save:
                if region=="europe":
                    id[pos] = code[pos]
                filepath = f"{config.yield_config.FIGURES_DIR}/{region}/anomaly_series_normalized/normalized_anomaly_series-{id[pos]}.png"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                plt.savefig(filepath, dpi=300)
            if show:
                plt.show()
        progress_bar_step += 1
        utils.progress_bar(progress_bar_step, n_sites, prefix=f"Progress for {region}", suffix=f"Completed for site {name[pos]} ({id[pos]})       ")
        plt.close()
        


def plot_anomaly_map(region, anomaly="neg", sel_years=None, save=False, show=False):
    """Plots the yield anomaly map of the subregion of a given region.
    Args:
        region (str): The name of the region to plot.
        ...: Additional parameters for the map.
    Returns:
        None: Shows or saves the plot.
    """
    if region != "europe":
        gdf = gpd.read_file(f"{config.paths.SHAPEFILES_DIR}/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp")
    elif region == "europe":
        gdf = gpd.read_file(f"{config.paths.SHAPEFILES_DIR}/NUTS_RG_10M_2021_4326/NUTS_RG_10M_2021_4326.shp")
    else:
        raise ValueError("Region not recognized.")
    
    if isinstance(region, str):
        anom_df_long, years = dp.get_anom_df(region, sel_years=sel_years, return_years=True).values()
    elif isinstance(region, list):
        years = sel_years
    
    progress_bar_step = 0

    for year in years:
        if region == "europe":
            gdf_year = gdf.merge(anom_df_long[anom_df_long["year"]==year], left_on="NUTS_ID", right_on="code", how="right")
        else:
            if isinstance(region, list):
                anom_df_long = dp.mult_regions(region)
            anom_df_year = anom_df_long[anom_df_long["year"]==year]["anom"]
            gdf_year = gdf.merge(anom_df_year, left_on="iso_3166_2", right_on="id")
        
        fig, ax = plt.subplots(figsize=(10,8), subplot_kw={"projection": ccrs.PlateCarree()})
        # ax.set_aspect("equal")

        # TO DO:  UNIFORMIZE THE REGIONS LIMITS
        region_limits = {"europe": {"xlim": (-10, 30), "ylim": (35, 65)}, "usa": {"xlim": (-130, -60), "ylim": (20, 50)}, "china": {"xlim": (70, 140), "ylim": (15, 55)}, "india": {"xlim": (68, 98), "ylim": (6, 38)}, "canada": {"xlim": (-140, -50), "ylim": (40, 70)}, "argentina": {"xlim": (-75, -50), "ylim": (-60, -20)}, "brazil": {"xlim": (-75, -30), "ylim": (-35, 5)}}
        if isinstance(region, list):
            region_name = "-".join(region)
            # Compute the min/mmax limits across all regions
            xlims, ylims = [region_limits[r]["xlim"] for r in region if r in region_limits], [region_limits[r]["ylim"] for r in region if r in region_limits]
            ax.set_xlim(min(x[0] for x in xlims), max(x[1] for x in xlims)) ; ax.set_ylim(min(y[0] for y in ylims), max(y[1] for y in ylims))
        elif region in region_limits:
            ax.set_xlim(region_limits[region]["xlim"]) ; ax.set_ylim(region_limits[region]["ylim"])

        # Load the countries shapefule and plot it
        countries = gpd.read_file(f"{config.paths.SHAPEFILES_DIR}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
        countries.plot(ax=ax, color="lightgrey", edgecolor="grey", linewidth=0.5, zorder=0)

        # No Data
        if isinstance(region, list):
            for r in region:
                if config.yield_config.CODE_REGIONS[r] is not None:
                    gdf[gdf["iso_a2"] == config.yield_config.CODE_REGIONS[r]].plot(ax=ax, color="grey", hatch="/////", edgecolor="lightgrey", linewidth=0.5, label="No Data")
        if isinstance(region, str):
            if config.yield_config.CODE_REGIONS[region] is not None:
                gdf[gdf["iso_a2"] == config.yield_config.CODE_REGIONS[region]].plot(ax=ax, color="grey", hatch="/////", edgecolor="lightgrey", linewidth=0.5, label="No Data")

        if anomaly == "neg":
            cmap = "afmhot"
            vmax = 0
        elif anomaly == "all":
            cmap = "RdBu"
            vmax = 2.5

        if gdf_year.empty or gdf_year.geometry.isnull().all():
            print(f"Warning: No geometry data to plot for {region} in year {year}. Skipping plot.")
            plt.close()
            continue
        map = gdf_year.plot(column="anom", ax=ax, cmap=cmap, vmin=-2.5, vmax=vmax, missing_kwds={"facecolor":"lightgrey", "label":"No Data", "hatch":"/////", "edgecolor":"grey"})

        if isinstance(region, str):
            map.set_title(f"Normalized Yield Anomaly Map - {region.upper()} - {year}", fontsize=16, loc="center")
        elif isinstance(region, list):
            map.set_title(f"Normalized Yield Anomaly Map - {region_name.upper()} - {year}", fontsize=16, loc="center")

        # Add country borders
        countries.plot(ax=ax, facecolor="none", edgecolor="grey", linewidth=1)

        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=-2.5, vmax=vmax))
        sm.set_array([])
        if anomaly == "neg":
            extend = "min"
            ticks = [i for i in np.arange(-2.5, 0, 0.5)]
        elif anomaly == "all":
            extend = "both"
            ticks = [i for i in np.arange(-2.5, 2.5, 0.5)]
        cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", pad=0.08, aspect=100, extend=extend)
        cbar.set_label("Normalized Yield Anomaly", fontsize=12)
        cbar.ax.tick_params(labelsize=10)
        cbar.set_ticks(ticks)
        cbar.set_ticklabels(ticks)
        # Add a legend with custom patches
        custom_handles = [
            Patch(facecolor="grey", hatch="/////", edgecolor="lightgrey", label="No Data"),
            Patch(facecolor="lightgrey", hatch="/////", edgecolor="grey", label="#N/A")]
        # Place the legend outside the map, below the plot
        ax.legend(handles=custom_handles, loc="upper center", bbox_to_anchor=(0.5, 0.), fontsize=10, ncol=2, frameon=False)
       
        # Remove axis
        ax.axis("off")
        ax.set_aspect("equal", adjustable="box")

        if save:
            if isinstance(region, str):
                filepath = f"{config.yield_config.FIGURES_DIR}/{region}/anomaly_map/{anomaly}_anomaly_map-{year}.png"
            elif isinstance(region, list):
                region_name = "-".join(region)
                filepath = f"{config.yield_config.FIGURES_DIR}/mult_regions/anomaly_map/{region_name}-{anomaly}_anomaly_map-{year}.png"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            plt.savefig(filepath, dpi=300)
        if show:
            plt.show()

        progress_bar_step += 1
        utils.progress_bar(progress_bar_step, len(years), prefix=f"Progress for {region}", suffix=f"| Completed for year {year}       ")

        plt.close()
 



def plot_area_covered_old(region, sel_years=None, save=False, show=False, thresh_min=-2.5, thresh_max=0, step=0.5, inf=True, **kwargs):
    """Plots the time series of the area covered by the yield anomaly data for a given region.
    Args:
        region (str): The region for which to plot the area covered.
        sel_years (tuple or list, optional): Year range (star, end) to filter. If None, all years are included.
    Returns:
        None: Shows or saves the plot.
    """
    ### AMELIORER LE DEBUT DU CODE JUSQU"AUX PLOTS !!! ###
    if sel_years is not None:
        if not isinstance(sel_years, (tuple, list)):
            raise ValueError("sel_years must be a tuple or list.")
        sel_years = [int(year) for year in sel_years]

    if isinstance(region, str):
        data_prod = pd.read_excel(dp.path[region]["file_in_prod"], index_col=0)
        data_area = pd.read_excel(dp.path[region]["file_in_area"], index_col=0)
        anom_df, years, name, id, code = dp.get_anom_df(region, return_years=True, return_meta=True).values()
        if sel_years is not None:
            years = [year for year in range(sel_years[0], sel_years[1] + 1)]

    elif isinstance(region, list):   
        anom_df = dp.mult_regions(region, sel_years=sel_years)
        data_prod = pd.concat([pd.read_excel(dp.path[r]["file_in_prod"], index_col=0) for r in region], axis=1)
        data_area = pd.concat([pd.read_excel(dp.path[r]["file_in_area"], index_col=0) for r in region], axis=1)
        id = data_area.columns.values.astype(str)
        years = anom_df["year"].unique()
        if sel_years is not None:
            years = [year for year in range(sel_years[0], sel_years[1] + 1)]     
        region = " & ".join(region) 

    area = data_area.loc[years]
    prod = data_prod.loc[years]

    prod_all = prod.values.astype(float)
    area_all = area.values.astype(float)
    columns = id
    index = years

    data_area_df = pd.DataFrame(area_all, columns=columns, index=index); data_area_df.index.name, data_area_df.columns.name = "year", "region"
    data_prod_df = pd.DataFrame(prod_all, columns=columns, index=index); data_prod_df.index.name, data_prod_df.columns.name = "year", "region"
    
    anom_df_years = anom_df.groupby("year")

    
    thresholds = np.concatenate([[-np.inf], np.linspace(thresh_min, thresh_max, int(np.abs((thresh_max-thresh_min)/step+1)), endpoint=True)])
    thresholds_0_5 = np.concatenate([[-np.inf], np.linspace(-2.5, 0.0, 6, endpoint=True)])
    if not inf:
        thresholds = thresholds[1:]
    anom_area_covered = {thresh: pd.DataFrame(np.nan, index=years, columns=["area_covered_percentage"]) for thresh in thresholds}
    anom_area_covered_intervals = {thresh: pd.DataFrame(np.nan, index=years, columns=["area_covered_percentage"]) for thresh in thresholds}
    anom_area_covered_intervals_0_5 = {thresh: pd.DataFrame(np.nan, index=years, columns=["area_covered_percentage"]) for thresh in thresholds_0_5}

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
        for i, thresh in enumerate(thresholds_0_5):
            next_thresh = thresholds_0_5[i+1] if i+1 < len(thresholds_0_5) else thresh_max
            anom_area_covered_intervals_0_5[thresh].loc[year, "area_covered_percentage"] = calculate_area_covered(thresh_min=thresh, thresh_max=next_thresh)
        for i, thresh in enumerate(thresholds):
            next_thresh = thresholds[i+1] if i+1 < len(thresholds) else thresh_max
            anom_area_covered_intervals[thresh].loc[year, "area_covered_percentage"] = calculate_area_covered(thresh_min=thresh, thresh_max=next_thresh)
    


    ##############################################
    ### Plotting the area covered by anomalies ###
    ##############################################

    fig, ax = plt.subplots(figsize=(16, 10))
    cmap = mpl.cm.afmhot
    norm = mpl.colors.BoundaryNorm(boundaries=np.linspace(-2.5, 0, 26), ncolors=cmap.N, extend="min")
    extend = "min" if inf else "neither"
    cbar = plt.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, orientation="horizontal", extend=extend, pad=0.1, aspect=100)

    # Moddifable parameters
    cbar.set_ticks(np.linspace(-2.5,0,26))
    title = "Area covered by anomalies"
    full_title = f"{title} - {region.upper()} - [{thresh_min}, {thresh_max}]"
    dir_fig = f"{config.yield_config.FIGURES_DIR}/{region}/anomaly_covered_area"
    figname = f"{dir_fig}/{region.upper()} - {title} - [{thresh_min}, {thresh_max}].png"
    if not inf:
        figname = f"{dir_fig}/{region.upper()} - {title} - [{thresh_min}, {thresh_max}] (no inf {thresh_min}).png"
        full_title += f" (no inf {thresh_min})"
    #

    # Fill between using the same colormap and norm as the colorbar
    for thresh in thresholds:
        df = anom_area_covered[thresh]
        color = cmap(norm(thresh))
        ax.fill_between(df.index, df["area_covered_percentage"], color=color)

    ax.plot(df.index, anom_area_covered[thresholds[0]]["area_covered_percentage"], color="black", alpha=0.5, linestyle="--", linewidth=0.5)

    ax.axhline(0, color="black", linestyle="--", linewidth=0.5)
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=60)
    ax.set_xlabel("Year")
    ax.set_xlim(min(years), max(years))
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_ylabel("Area covered by anomalies (%)")
    ax.set_ylim(0, 100)
    
    ax.grid()
    # ax.legend()
    ax.set_title(full_title, fontsize=16, loc="center")
    
    if save:
        os.makedirs(dir_fig, exist_ok=True)
        plt.savefig(figname, dpi=300, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        print(f"Figure saved as: {figname}")
    
    if show:
        plt.show()
    
    plt.close(fig)
    ### ###
    



def plot_area_covered(region, data, save=False, show=False, thresh_min=-2.5, thresh_max=0., step=0.5, inf=True):
    """Plots the time series of the area covered by the yield anomaly data for a given region.
    Args:
        region (str): The region for which to plot the area covered.
        data (dict): Dictionary containing the data to plot, from process_area_covered.
        thresh_min (float): Minimum threshold for the area covered.
        thresh_max (float): Maximum threshold for the area covered.
        step (float): Step size for the thresholds.
    Returns:
        None: Shows or saves the plot.
    """
    if data:
        thresholds = data["thresholds"]
        anom_area_covered = data["anom_area_covered"]
        years = data["years"]
    
    fig, ax = plt.subplots(figsize=(16, 10))
    cmap = mpl.cm.afmhot
    norm = mpl.colors.BoundaryNorm(boundaries=np.linspace(-2.5, 0, 26), ncolors=cmap.N, extend="min")
    extend = "min" if inf else "neither"
    cbar = plt.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, orientation="horizontal", extend=extend, pad=0.1, aspect=100)

    # Moddifable parameters
    cbar.set_ticks(np.linspace(-2.5,0,26))
    title = "Area covered by anomalies"
    full_title = f"{title} - {region.upper()} - [{thresh_min}, {thresh_max}]"
    dir_fig = f"{config.yield_config.FIGURES_DIR}/{region}/anomaly_covered_area"
    figname = f"{dir_fig}/{region.upper()} - {title} - [{thresh_min}, {thresh_max}].png"
    if not inf:
        figname = f"{dir_fig}/{region.upper()} - {title} - [{thresh_min}, {thresh_max}] (no inf {thresh_min}).png"
        full_title += f" (no inf {thresh_min})"
    #

    # Fill between using the same colormap and norm as the colorbar
    for thresh in thresholds:
        df = anom_area_covered[thresh]
        color = cmap(norm(thresh))
        ax.fill_between(df.index, df["area_covered_percentage"], color=color)

    ax.plot(df.index, anom_area_covered[thresholds[0]]["area_covered_percentage"], color="black", alpha=0.5, linestyle="--", linewidth=0.5)

    ax.axhline(0, color="black", linestyle="--", linewidth=0.5)
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=60)
    ax.set_xlabel("Year")
    ax.set_xlim(min(years), max(years))
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_ylabel("Area covered by anomalies (%)")
    ax.set_ylim(0, 100)
    
    ax.grid()
    ax.set_title(full_title, fontsize=16, loc="center")
    
    if save:
        os.makedirs(dir_fig, exist_ok=True)
        plt.savefig(figname, dpi=300, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
    
    if show:
        plt.show()
    
    plt.close(fig)