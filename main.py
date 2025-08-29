# ---------- HEADER --------------------------------------------
# File : main.py
# Author(s) : Enzo Fortin
#
# Description :
# Main entry point for the drought-swa-yield_anom project.
# --------------------------------------------------------------
import argparse
from src.config import Config
import sys
from argparse import ArgumentParser
import shlex

def main():
    parser = argparse.ArgumentParser(
        description="Main entry point for drought-swa-yield_anom project."
    )
    subparsers = parser.add_subparsers(dest="module", help="Choose the analysis module to run")

    # General information
    parser.add_argument("--version", "-v", action="version", version="drought-swa-yield_anom 1.0", help="Show program version and exit")
    parser.add_argument("--about", "--description", "-a", action="store_true", help="Show information about the program and exit")
    parser.add_argument("--authors", action="store_true", help="Show authors of the program and exit")
    parser.add_argument("--title", action="store_true", help="Show the program title and exit")

    # Config options
    parser_config = parser.add_argument_group("Configuration options")
    parser_config.add_argument("--th_detection_drought", "--threshold", "-th", type=float, default=Config().th_detection_drought, help="Threshold for drought detection")
    parser_config.add_argument("--start_year", type=int, default=Config().start_year, help="Start year")
    parser_config.add_argument("--end_year", type=int, default=Config().end_year, help="End year")
    parser_config.add_argument("--month_start", type=int, default=Config().month_start, help="Start month")
    parser_config.add_argument("--month_end", type=int, default=Config().month_end, help="End month")    
    parser_config.add_argument("--regions", nargs="+", default=["all"], help="Regions to process", choices=["europe", "usa", "china", "india", "canada", "argentina", "brazil", "all"], type=str)
    parser_config.add_argument("--TH_SWA", "--th_swa", type=float, default=Config().TH_SWA, help="Threshold for SWA analysis")
    parser_config.add_argument("--TH_YA", "--th_ya", type=float, default=Config().TH_YA, help="Threshold for Yield analysis")
    parser_config.add_argument("--TH_SWA_LIST", "--th_swa_list", nargs="+", type=float, default=Config().TH_SWA_list, help="List of thresholds for SWA analysis")
    parser_config.add_argument("--TH_YA_LIST", "--th_ya_list", nargs="+", type=float, default=Config().TH_YA_list, help="List of thresholds for Yield analysis")



    
    ##### Yield analysis
    parser_yield = subparsers.add_parser("yield", help="Yield analysis")

    ## General options
    parser_yield.add_argument("--run", "--run_all", help="Run all steps: standardization, processing, visualization", action="store_true")
    ## Configuration options
    parser_yield.add_argument("-r", "--regions", nargs="+", default="all", help="Regions to standardize", choices=["europe", "usa", "china", "india", "canada", "argentina", "brazil", "all"], type=str)
    parser_yield.add_argument("--start_year", type=int, default=Config().start_year, help="Start year for analysis (default: 1991)")
    parser_yield.add_argument("--end_year", type=int, default=Config().end_year, help="End year for analysis (default: 2023)")

    ## Standardization options
    yield_group_std = parser_yield.add_argument_group("Standardization options")
    yield_group_std.add_argument("-ds", "--data_standardization", help="Run data standardization", action="store_true")

    ## Processing options
    yield_group_proc = parser_yield.add_argument_group("Processing options")
    yield_group_proc.add_argument("-dp", "--data_processing", help="Run data processing", action="store_true")
    # Processing functions
    yield_group_proc.add_argument("--get_prod_anom", "--output", help="Get production anomalies for regions. Used in the correlation part", action="store_true")

    ## Visualization options
    yield_group_vis = parser_yield.add_argument_group("Visualization options")
    yield_group_vis.add_argument("-vz", "--visualization", help="Run visualization", action="store_true")
    # Plot functions
    yield_group_vis.add_argument("--plot_anomaly_series", action="store_true", help="Plot anomaly series. If no plot option is selected, all plots will be generated")
    yield_group_vis.add_argument("--plot_anomaly_map", action="store_true", help="Plot anomaly map. If no plot option is selected, all plots will be generated")
    yield_group_vis.add_argument("--plot_area_covered", action="store_true", help="Plot area covered series. If no plot option is selected, all plots will be generated")
    # Plot options
    yield_group_vis.add_argument("--show_plot", help="Show plots after computation", action="store_true")
    yield_group_vis.add_argument("--save_plot", help="Save plots after computation", action="store_true")
    yield_group_vis.add_argument("--anomaly_type", type=str, default="normalized", choices=["standardized", "normalized"], help="Type of anomaly series to plot")
    yield_group_vis.add_argument("--anomaly_map", type=str, default="neg", choices=["neg", "pos"], help="Type of anomaly map to plot. 'neg' for negative anomalies, 'pos' for positive anomalies")
    




    ##### SWA analysis
    parser_swa = subparsers.add_parser("swa", help="SWA analysis")
    parser_swa.add_argument("--run", "--run_all", help="Run all steps: processing, visualization. Just Europe is available here", action="store_true")

    # General options
    swa_group_gen = parser_swa.add_argument_group("General options")
    swa_group_gen.add_argument("--th_detection_drought", "--threshold", "-th", default=Config().th_detection_drought, type=float, help="Threshold for drought detection")
    swa_group_gen.add_argument("--start_year", type=int, default=Config().start_year, help="Start year")
    swa_group_gen.add_argument("--end_year", type=int, default=Config().end_year, help="End year")
    swa_group_gen.add_argument("--month_start", type=int, default=Config().month_start, help="Start month")
    swa_group_gen.add_argument("--month_end", type=int, default=Config().month_end, help="End month")

    # Processing options
    swa_group_proc = parser_swa.add_argument_group("Processing options")
    swa_group_proc.add_argument("-dp", "--data_processing", help="Run data processing", action="store_true")
    swa_group_proc.add_argument("--temporal_series_region", "--temporal_serie", help="Calculate temporal series for a region", action="store_true")
    swa_group_proc.add_argument("--processed_swa", help="Process SWA data", action="store_true")
    swa_group_proc.add_argument("--spatial_mean_shp", help="Calculate spatial mean for shapefile regions", action="store_true")
    swa_group_proc.add_argument("--temporal_mean_shp", help="Calculate temporal mean for shapefile regions", action="store_true")

    # Visualization options
    swa_group_vis = parser_swa.add_argument_group("Visualization options")
    swa_group_vis.add_argument("-vz", "--visualization", help="Run visualization", action="store_true")
    swa_group_vis.add_argument("--plot_raster", action="store_true", help="Plot raster data")
    swa_group_vis.add_argument("--plot_shapefile", action="store_true", help="Plot shapefile data")
    swa_group_vis.add_argument("--plot_time_series", action="store_true", help="Plot time series data")
    swa_group_vis.add_argument("--save_plot", action="store_true", help="Save plots")
    swa_group_vis.add_argument("--show_plot", action="store_true", help="Show plots")
    swa_group_vis.add_argument("--raster_path", help="Raster data to plot. Warning be sure the data exists")




    ##### Correlation analysis
    parser_corr = subparsers.add_parser("correlation", help="Correlation analysis")
    parser_corr.add_argument("--run", "--run_all", help="Run all steps: compute correlations and visualize", action="store_true")

    # General options
    corr_group_gen = parser_corr.add_argument_group("General options")
    corr_group_gen.add_argument("--th_detection_drought", "--threshold", "-th", default=Config().th_detection_drought, type=float, help="Threshold for drought detection")
    corr_group_gen.add_argument("--start_year", type=int, default=Config().start_year, help="Start year")
    corr_group_gen.add_argument("--end_year", type=int, default=Config().end_year, help="End year")
    corr_group_gen.add_argument("--month_start", type=int, default=Config().month_start, help="Start month")
    corr_group_gen.add_argument("--month_end", type=int, default=Config().month_end, help="End month")
    corr_group_gen.add_argument("--th_swa_list", type=str, default=Config().TH_SWA_list, help="List of thresholds for SWA in MCC map (comma-separated or tuple '(start,end,step)')")
    corr_group_gen.add_argument("--th_ya_list", type=str, default=Config().TH_YA_list, help="List of thresholds for Yield Anomaly in MCC map (comma-separated or tuple '(start,end,step)')")
    corr_group_gen.add_argument("-cp", "--correlation_processing", "--corr", "--correlation", help="Run correlation processing", action="store_true")
    
    # Processing options
    corr_group_proc = parser_corr.add_argument_group("Processing options")
    corr_group_proc.add_argument("--save_data", choices=["netcdf", "excel", "both"], help="Format to save correlation data", type=str, default=None)

    # Visualization options
    corr_group_vis = parser_corr.add_argument_group("Visualization options")
    corr_group_vis.add_argument("-vz", "--visualization", help="Run visualization", action="store_true")
    corr_group_vis.add_argument("--plot_mcc_map", action="store_true", help="Plot MCC correlation map")
    corr_group_vis.add_argument("--plot_max_mcc_map", action="store_true", help="Plot max MCC correlation map")
    corr_group_vis.add_argument("--display_interactive_map_holoviz", action="store_true", help="Display interactive map using Holoviz")
    corr_group_vis.add_argument("--display_interactive_map_matplotlib", action="store_true", help="Display interactive map using Folium")
    corr_group_vis.add_argument("--show_plot", help="Show correlation maps after computation", action="store_true")
    corr_group_vis.add_argument("--save_plot", help="Save correlation maps after computation", action="store_true")
    corr_group_vis.add_argument("--mode_holoviz", type=str, default=None, help="Mode for Holoviz interactive map", choices=["notebook", "browser"])
    corr_group_vis.add_argument("--th_swa", type=float, default=Config().TH_SWA, help="Threshold for SWA in MCC map")
    corr_group_vis.add_argument("--th_ya", type=float, default=Config().TH_YA, help="Threshold for Yield Anomaly in MCC map")
    

    args = parser.parse_args()

    # Dispatch to the correct script
    if args.about:
        print("This program analyzes the relationship between drought conditions (using SWA data) and cereal yield anomalies across various regions.")
        print("Part of my 2025 summer internship at Politecnico di Milano, supervised by Prof. Carmelo Cammalleri.\n")
        sys.exit(0)
    if args.authors:
        print("Internship supervised by Prof Carmelo Cammalleri")
        print("Developed by Enzo Fortin")
        sys.exit(0)
    if args.title:
        print("Analysis and processing of cereals yield datasets as a proxy variable of impacts of drought in agriculture\n")
        sys.exit(0)

    if args.module == "yield":
        import scripts.yield_script as yield_script
        yield_script.run(args)
    elif args.module == "swa":
        import scripts.swa_script as swa_script
        swa_script.run(args)
    elif args.module == "correlation":
        import scripts.corr_script as corr_script
        corr_script.run(args)
    else:
        parser.print_help()

if __name__ == "__main__":
        # print(" "*10, "--------------------------------------------------------------------------------")
        # print(" "*10, "|   Welcome in the main script for launching the SWA x Yield Anomaly package   |")
        # print(" "*10, "--------------------------------------------------------------------------------\n")

        # parser = ArgumentParser(
        #     description="Main entry point for drought-swa-yield_anom project."
        # )
        # parser.description += "\n\nTo quit the interactive mode, type 'exit' or 'quit' at any prompt."
        # subparsers = parser.add_subparsers(dest="module", help="Choose the analysis module to run")
        # subparsers.add_parser("yield", help="Yield analysis")
        # subparsers.add_parser("swa", help="SWA analysis")
        # subparsers.add_parser("correlation", help="Correlation analysis")

        # print(parser.format_help())

        # while True:
        #     user_input = input("\n===> Please enter your command OR 'exit'/'quit' to leave OR --help to display the options : \n")
        #     if user_input in ['exit', 'quit']:
        #         print("Exiting the program. Goodbye!")
        #         sys.exit(0)
        #     else:
        #         sys.argv = [sys.argv[0]] + shlex.split(user_input)
        #         try:
        #             main()
        #         except SystemExit as e:
        #             if e.code != 0:
        #                 print("An error occurred while processing your command. Please check your input and try again")
        #                 continue
        #             else:
        #                 continue
    main()