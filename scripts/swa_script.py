# ---------- HEADER --------------------------------------------
# File : scripts/swa_script.py
# Author(s) : Enzo Fortin
#
# Description :
# This file contains scripts to analyze swa data for various regions.
# --------------------------------------------------------------
import argparse
import src.swa_analysis.data_processing as dp
import src.swa_analysis.visualization as vz
from src.config import config



def run(args, config):
    print("\n############ SWA ANALYSIS SCRIPT ################\n")
    if getattr(args, "run", False):
        args.data_processing = True
        args.visualization = True
        args.plot_raster = True
        args.plot_shapefile = True


    ### SWA Data Processing
    if args.data_processing:
        print("Starting data processing...")
        dp.run_swa(
            threshold=getattr(args, "threshold", config.th_detection_drought_default),
            year_start=getattr(args, "start_year", config.start_year_default),
            year_end=getattr(args, "end_year", config.end_year_default),
            month_start=getattr(args, "month_start", config.month_start_default),
            month_end=getattr(args, "month_end", config.month_end_default)
        )


    ### SWA Data Visualization
    if getattr(args, "visualization", False):
        print("Starting visualization...")
        vz.plot_time_serie(
            None,
            save=False,
            show=True,
            threshold=getattr(args, "threshold", config.th_detection_drought_default),
            month_start=getattr(args, "month_start", config.month_start_default),
            month_end=getattr(args, "month_end", config.month_end_default)
        )

    if getattr(args, "plot_raster", False):
        print("Plotting raster data...")
        # vz.plot_raster(...)  # Ajoute ta fonction ici si besoin

    if getattr(args, "plot_shapefile", False):
        print("Plotting shapefile data...")
        vz.plot_shapefile()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze SWA data for various regions.")
    parser.add_argument("--run", "--run_all", help="Run all steps: processing, visualization. Just Europe is available here", action="store_true")

    group_proc = parser.add_argument_group("Processing options")
    group_proc.add_argument("-dp", "--data_processing", help="Run data processing", action="store_true")
    group_proc.add_argument("--temporal_series_region", "--temporal_serie", help="Calculate temporal series for a region", action="store_true")
    group_proc.add_argument("--processed_swa", help="Process SWA data", action="store_true")
    group_proc.add_argument("--spatial_mean_shp", help="Calculate spatial mean for shapefile regions", action="store_true")
    group_proc.add_argument("--temporal_mean_shp", help="Calculate temporal mean for shapefile regions", action="store_true")

    group_vis = parser.add_argument_group("Visualization options")
    group_vis.add_argument("-vz", "--visualization", help="Run visualization", action="store_true")
    group_vis.add_argument("--plot_raster", action="store_true", help="Plot raster data")
    group_vis.add_argument("--plot_shapefile", action="store_true", help="Plot shapefile data")
    group_vis.add_argument("--plot_time_series", action="store_true", help="Plot time series data")

    parser.add_argument("--start_year", type=int, default=config.start_year_default, help="Start year")
    parser.add_argument("--end_year", type=int, default=config.end_year_default, help="End year")
    parser.add_argument("--month_start", type=int, default=config.month_start_default, help="Start month")
    parser.add_argument("--month_end", type=int, default=config.month_end_default, help="End month")

    args = parser.parse_args()
    run(args)






