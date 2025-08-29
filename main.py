# ---------- HEADER --------------------------------------------
# File : main.py
# Author(s) : Enzo Fortin
#
# Description :
# Main entry point for the drought-swa-yield_anom project.
# --------------------------------------------------------------

import argparse
from src.config import config
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
    parser.add_argument_group("Configuration options")
    parser.add_argument("--config_file", type=str, default=None, help="Path to a custom configuration file")
    parser.add_argument("--reset_config", action="store_true", help="Reset configuration to default values")
    parser.add_argument("--th_detection_drought", "--threshold", "-th", type=float, default=config.th_detection_drought, help="Threshold for drought detection")
    parser.add_argument("--start_year", type=int, default=config.start_year, help="Start year")
    parser.add_argument("--end_year", type=int, default=config.end_year, help="End year")
    parser.add_argument("--month_start", type=int, default=config.month_start, help="Start month")
    parser.add_argument("--month_end", type=int, default=config.month_end, help="End month")    
    parser.add_argument("--regions", nargs="+", default=["all"], help="Regions to process", choices=["europe", "usa", "china", "india", "canada", "argentina", "brazil", "all"], type=str)
    parser.add_argument("--TH_SWA", "--th_swa", type=float, default=config.TH_SWA, help="Threshold for SWA analysis")
    parser.add_argument("--TH_YA", "--th_ya", type=float, default=config.TH_YA, help="Threshold for Yield analysis")
    parser.add_argument("--TH_SWA_LIST", "--th_swa_list", nargs="+", type=float, default=config.TH_SWA_list, help="List of thresholds for SWA analysis")
    parser.add_argument("--TH_YA_LIST", "--th_ya_list", nargs="+", type=float, default=config.TH_YA_list, help="List of thresholds for Yield analysis")

    # Subparsers for different modules
    # Yield analysis
    parser_yield = subparsers.add_parser("yield", help="Yield analysis")
    parser_yield.add_argument("-ds", "--data_standardization", action="store_true", help="Run data standardization")
    parser_yield.add_argument("-dp", "--data_processing", action="store_true", help="Run data processing")
    parser_yield.add_argument("-vz", "--visualization", action="store_true", help="Run visualization")
    parser_yield.add_argument("-r", "--regions", nargs="+", default=["all"], help="Regions to process")
    parser_yield.add_argument("--start_year", type=int, default=1991, help="Start year")
    parser_yield.add_argument("--end_year", type=int, default=2023, help="End year")

    # SWA analysis
    parser_swa = subparsers.add_parser("swa", help="SWA analysis")
    parser_swa.add_argument("--run", action="store_true", help="Run all SWA steps (processing, visualization)")

    # Correlation analysis
    parser_corr = subparsers.add_parser("correlation", help="Correlation analysis")
    parser_corr.add_argument("--run", action="store_true", help="Run correlation analysis")

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
        corr_script.main(args)
    else:
        parser.print_help()

if __name__ == "__main__":
        print(" "*10, "--------------------------------------------------------------------------------")
        print(" "*10, "|   Welcome in the main script for launching the SWA x Yield Anomaly package   |")
        print(" "*10, "--------------------------------------------------------------------------------\n")

        parser = ArgumentParser(
            description="Main entry point for drought-swa-yield_anom project."
        )
        parser.description += "\n\nTo quit the interactive mode, type 'exit' or 'quit' at any prompt."
        subparsers = parser.add_subparsers(dest="module", help="Choose the analysis module to run")
        subparsers.add_parser("yield", help="Yield analysis")
        subparsers.add_parser("swa", help="SWA analysis")
        subparsers.add_parser("correlation", help="Correlation analysis")

        print(parser.format_help())

        while True:
            user_input = input("\n===> Please enter your command OR 'exit'/'quit' to leave OR --help to display the options : \n")
            if user_input in ['exit', 'quit']:
                print("Exiting the program. Goodbye!")
                sys.exit(0)
            else:
                sys.argv = [sys.argv[0]] + shlex.split(user_input)
                try:
                    main()
                except SystemExit as e:
                    if e.code != 0:
                        print("An error occurred while processing your command. Please check your input and try again")
                        continue
                    else:
                        continue
