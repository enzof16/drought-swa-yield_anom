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
from src.config import Config



def run(args):
    print("\n############ SWA ANALYSIS SCRIPT ################\n")
    global config
    if any(getattr(args, k, None) is not None for k in ["start_year", "end_year", "month_start", "month_end", "th_detection_drought"]):
        config = Config(th_detection_drought=getattr(args, "th_detection_drought", Config().th_detection_drought),
                        start_year=getattr(args, "start_year", Config().start_year),
                        end_year=getattr(args, "end_year", Config().end_year),
                        month_start=getattr(args, "month_start", Config().month_start),
                        month_end=getattr(args, "month_end", Config().month_end))
    else:
        config = Config()
    
    dp.config = config  # update config in data_processing
    vz.config = config  # update config in visualization

    if getattr(args, "run", False):
        args.data_processing = True
        args.visualization = True
        args.plot_raster = True
        args.plot_shapefile = True


    ### SWA Data Processing
    if args.data_processing:
        print("Starting data processing...")
        dp.run_swa(
            threshold=config.th_detection_drought,
            year_start=config.start_year,
            year_end=config.end_year,
            month_start=config.month_start,
            month_end=config.month_end
        )


    ### SWA Data Visualization
    if getattr(args, "visualization", False):
        if getattr(args, "plot_time_series", False):
            print("Starting visualization...")
            dp.temporal_series_region(year_start=config.start_year,year_end=config.end_year, month_start=config.month_start, month_end=config.month_end, save=False, show=getattr(args, "show_plot", False), save_plot=getattr(args, "save_plot", False), threshold=config.th_detection_drought)

    # TO FIX LATER
        # if getattr(args, "plot_raster", False):
        #     print("Plotting raster data...")
        #     if not args.raster:
        #         raise ValueError("Please specify a raster to plot with --raster")
        #     raster = args.raster
        #     vz.plot_raster(dp.open_raster(raster), save=getattr(args, "save_plot", False), show=getattr(args, "show_plot", False))

        # if getattr(args, "plot_shapefile", False):
        #     print("Plotting shapefile data...")
            
        #     vz.plot_shapefile()



if __name__ == "__main__":
    from src.config import config
    parser = argparse.ArgumentParser(description="Analyze SWA data for various regions.")
    parser.add_argument("--run", "--run_all", help="Run all steps: processing, visualization. Just Europe is available here", action="store_true")

    # General options
    group_gen = parser.add_argument_group("General options")
    group_gen.add_argument("--th_detection_drought", "--threshold", "-th", default=config.th_detection_drought, type=float, help="Threshold for drought detection")
    group_gen.add_argument("--start_year", type=int, default=config.start_year, help="Start year")
    group_gen.add_argument("--end_year", type=int, default=config.end_year, help="End year")
    group_gen.add_argument("--month_start", type=int, default=config.month_start, help="Start month")
    group_gen.add_argument("--month_end", type=int, default=config.month_end, help="End month")

    # Processing options
    group_proc = parser.add_argument_group("Processing options")
    group_proc.add_argument("-dp", "--data_processing", help="Run data processing", action="store_true")
    group_proc.add_argument("--temporal_series_region", "--temporal_serie", help="Calculate temporal series for a region", action="store_true")
    group_proc.add_argument("--processed_swa", help="Process SWA data", action="store_true")
    group_proc.add_argument("--spatial_mean_shp", help="Calculate spatial mean for shapefile regions", action="store_true")
    group_proc.add_argument("--temporal_mean_shp", help="Calculate temporal mean for shapefile regions", action="store_true")

    # Visualization options
    group_vis = parser.add_argument_group("Visualization options")
    group_vis.add_argument("-vz", "--visualization", help="Run visualization", action="store_true")
    group_vis.add_argument("--plot_raster", action="store_true", help="Plot raster data")
    group_vis.add_argument("--plot_shapefile", action="store_true", help="Plot shapefile data")
    group_vis.add_argument("--plot_time_series", action="store_true", help="Plot time series data")
    group_vis.add_argument("--save_plot", action="store_true", help="Save plots")
    group_vis.add_argument("--show_plot", action="store_true", help="Show plots")
    group_vis.add_argument("--raster_path", help="Raster data to plot. Warning be sure the data exists")


    args = parser.parse_args()
    # for arg in vars(args):
    #     print(f"{arg} : {getattr(args, arg)}")
    run(args)






