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
    if args.module == "yield":
        import scripts.yield_script as yield_script
        yield_script.main(args, config)
    elif args.module == "swa":
        import scripts.swa_script as swa_script
        swa_script.run(args, config)
    elif args.module == "correlation":
        import scripts.corr_script as corr_script
        corr_script.main(args, config)
    else:
        parser.print_help()

if __name__ == "__main__":
    print(" "*30, "--------------------------------------------------------------------------------")
    print(" "*30, "|   Welcome in the main script for launching the SWA x Yield Anomaly package   |")
    print(" "*30, "--------------------------------------------------------------------------------\n")

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
                    # sys.exit(0)

                    # Continue the loop after successful execution
                    continue


