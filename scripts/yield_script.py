# ---------- HEADER --------------------------------------------
# File : scripts/yield_script.py
# Author(s) : Enzo Fortin
#
# Description :
# This file contains scripts to standardize and analyze yield data for various regions.
# --------------------------------------------------------------
import argparse
import src.yield_analysis.data_standardization as ds
import src.yield_analysis.data_processing as dp
import src.yield_analysis.visualization as vz
from src.config import Config


def run(args):
    print("\n############ YIELD ANALYSIS SCRIPT ################\n")

    config = Config.from_args(args)

    ds.config = config  # update config in data_standardization
    dp.config = config  # update config in data_processing
    vz.config = config  # update config in visualization

    # Run arguments
    if getattr(args, "run", False):
        args.data_standardization = True
        args.data_processing = True
        args.get_prod_anom = True
        args.visualization = True
        args.plot_anomaly_series = True
        args.plot_anomaly_map = True
        args.plot_area_covered = True
        args.regions = "all"
        args.save_plot = True
        args.show_plot = False

    if args.regions == ["all"]:
        config.regions_list = ["europe", "usa", "china", "india", "canada", "argentina", "brazil"]

    ### Yield Data Standardization
    if getattr(args, "data_standardization", False):
        print("> Standardization of yield data")
        ds.copy_european_data()
        config.regions_to_standardize = [r for r in args.regions if r != "europe"]
        ds.save_data(ds.standardize_data())
        print("Data standardization completed\n")


    ### Yield Data Processing
    if getattr(args, "data_processing", False):
        print("> Processing of yield data")
        if getattr(args, "get_prod_anom", False):
            print("     > Getting production anomalies for regions")
            for region in args.regions:
                dp.get_prod_anom(region, save=True)
            print("     Production anomalies saved")
        print("Data processing completed\n")


    ### Yield Data Visualization
    if getattr(args, "visualization", False):
        print("> Visualization of yield data")
        if not getattr(args, "save_plot"):
            print("! WARNING : Plots will not be saved unless --save_plot is specified !")

        all_plots = not (getattr(args, "plot_anomaly_series", False) or getattr(args, "plot_anomaly_map", False) or getattr(args, "plot_area_covered", False))
        for region in args.regions:
            print(f"     > Region: {region}")
            if getattr(args, "plot_anomaly_series", False) or all_plots:
                print("         > Plotting Anomaly Series")
                vz.plot_anomaly_series(region, type=getattr(args, "anomaly_type", "normalized"), save=getattr(args, "save_plot"), show=getattr(args, "show_plot"))
                print("         Anomaly series saved")
            if getattr(args, "plot_anomaly_map", False) or all_plots:
                print("         > Plotting Anomaly Map")
                vz.plot_anomaly_map(region, anomaly=getattr(args, "anomaly_map", "neg"), sel_years=[args.year_start, args.year_end], save=getattr(args, "save_plot"), show=getattr(args, "show_plot"))
                print("         Anomaly map saved")
            if getattr(args, "plot_area_covered", False) or all_plots:
                print("         > Plotting Area Covered Series")
                vz.plot_area_covered(
                    region,
                    dp.process_area_covered(region, sel_years=[args.year_start, args.year_end], thresh_min=-2.5, thresh_max=0, step=0.5, inf=True),
                    save=getattr(args, "save_plot", False),
                    show=getattr(args, "show_plot", False),
                    thresh_min=-2.5,
                    thresh_max=0,
                    step=0.5,
                    inf=True
                )
                print("         Area covered series saved")
            print(f"     Region {region} completed")
        print("Visualization completed\n")



if __name__ == "__main__":
    from src.config import config


    ### General options
    parser = argparse.ArgumentParser(description="Standardize and analyze yield data for various regions.")
    parser.add_argument("-r", "--run", "--run_all", help="Run all steps: standardization, processing, visualization", action="store_true")
    

    ### Configuration options
    parser.add_argument("--regions", nargs="+", default=["europe", "usa", "china", "india", "canada", "argentina", "brazil"], help="Regions to standardize", choices=["europe", "usa", "china", "india", "canada", "argentina", "brazil", "all"], type=str)
    parser.add_argument("--year_start", type=int, default=config.year_start, help="Start year for analysis (default: 1991)")
    parser.add_argument("--year_end", type=int, default=config.year_end, help="End year for analysis (default: 2023)")


    ### Standardization options
    group_std = parser.add_argument_group("Standardization options")
    group_std.add_argument("-ds", "--data_standardization", help="Run data standardization", action="store_true")


    ### Processing options
    group_proc = parser.add_argument_group("Processing options")
    group_proc.add_argument("-dp", "--data_processing", help="Run data processing", action="store_true")
    # Processing functions
    group_proc.add_argument("--get_prod_anom", "--output", help="Get production anomalies for regions. Used in the correlation part", action="store_true")


    ### Visualization options
    group_vis = parser.add_argument_group("Visualization options")
    group_vis.add_argument("-vz", "--visualization", help="Run visualization", action="store_true")
    # Plot functions
    group_vis.add_argument("--plot_anomaly_series", action="store_true", help="Plot anomaly series. If no plot option is selected, all plots will be generated")
    group_vis.add_argument("--plot_anomaly_map", action="store_true", help="Plot anomaly map. If no plot option is selected, all plots will be generated")
    group_vis.add_argument("--plot_area_covered", action="store_true", help="Plot area covered series. If no plot option is selected, all plots will be generated")
    # Plot options
    group_vis.add_argument("--show_plot", help="Show plots after computation", action="store_true")
    group_vis.add_argument("--save_plot", help="Save plots after computation", action="store_true")
    group_vis.add_argument("--anomaly_type", type=str, default="normalized", choices=["standardized", "normalized"], help="Type of anomaly series to plot")
    group_vis.add_argument("--anomaly_map", type=str, default="neg", choices=["neg", "pos"], help="Type of anomaly map to plot. 'neg' for negative anomalies, 'pos' for positive anomalies")
    
    
    args = parser.parse_args()
    run(args)


