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

    config = Config.from_args(args)
    
    dp.config = config  # update config in data_processing
    vz.config = config  # update config in visualization


    # Run arguments
    if getattr(args, "run", False):
        args.data_processing = True
        args.visualization = True
        args.plot_raster = True
        args.plot_shapefile = True


    ### SWA Data Processing
    if args.data_processing:
        print("> Processing of SWA data")
        dp.run_swa(
            threshold=config.th_detection_drought,
            year_start=config.year_start,
            year_end=config.year_end,
            month_start=config.month_start,
            month_end=config.month_end
        )
        print("Data processing completed\n")    


    ### SWA Data Visualization
    if getattr(args, "visualization", False):
        print("> Visualization of SWA data")
        if getattr(args, "plot_time_series", False):
            print("     > Plotting temporal series for Europe")
            dp.temporal_series_region(year_start=config.year_start,year_end=config.year_end, month_start=config.month_start, month_end=config.month_end, save=False, show=getattr(args, "show_plot", False), save_plot=getattr(args, "save_plot", False), threshold=config.th_detection_drought)
            print("     Temporal series plotted")
        print("Visualization completed\n")

        if getattr(args, "plot_raster", False):
            print("     > Plotting raster data")
            if getattr(args, "raster_path", None) is not None:
                vz.plot_raster(raster=dp.open_raster(getattr(args, "raster_path", None)), cmap="RdBu", save=getattr(args, "save_plot", False), show=getattr(args, "show_plot", False))
            else:
                print("     No raster path provided. Skipping raster plot.")
            print("     Raster data plotted")

        # to complete



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze SWA data for various regions.")
    parser.add_argument("--run", "--run_all", help="Run all steps: processing, visualization. Just Europe is available here", action="store_true")

    # General options
    group_gen = parser.add_argument_group("General options")
    group_gen.add_argument("--th_detection_drought", "--threshold", "-th", type=float, help="Threshold for drought detection")
    group_gen.add_argument("--year_start", type=int, help="Start year")
    group_gen.add_argument("--year_end", type=int, help="End year")
    group_gen.add_argument("--month_start", type=int, help="Start month")
    group_gen.add_argument("--month_end", type=int, help="End month")

    # Processing options
    group_proc = parser.add_argument_group("Processing options")
    group_proc.add_argument("-dp", "--data_processing", help="Run data processing", action="store_true")

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
    run(args)






