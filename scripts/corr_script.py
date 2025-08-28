# ---------- HEADER --------------------------------------------
# File : scripts/corr_script.py
# Author(s) : Enzo Fortin
#
# Description :
# This file contains scripts to compute and visualize correlation maps.
# --------------------------------------------------------------
import src.correlation.correlation as cr
import src.correlation.visualization as vz
from src.config import config

import argparse

def run(args, config):
    if getattr(args, "run", False):
        args.correlation_processing = True
        args.visualization = True
        args.plot_mcc_map = True
        args.plot_max_mcc_map = True
        args.display_interactive_map_holoviz = True
        args.display_interactive_map_matplotlib = True

    if getattr(args, "correlation_processing", False):
        print("Computing correlation maps...")
        cr.compute_and_save_correlation_maps()
        if getattr(args, "save_data", False):
            print("Correlation data saved.")

    if getattr(args, "visualization", False):
        print("Visualizing correlation maps...")
        ds = vz.load_correlation_results()
        if getattr(args, "plot_mcc_map", False):
            vz.plot_mcc_map(ds, th_swa=0.2, th_ya=-0.5)
        if getattr(args, "plot_max_mcc_map", False):
            vz.plot_max_mcc_map(ds, save=getattr(args, "save_plot", False), show=getattr(args, "show_plot", False))
        if getattr(args, "display_interactive_map_holoviz", False):
            vz.holoviz_interactive_mcc(ds, mode=getattr(args, "mode_holoviz", None))
        if getattr(args, "display_interactive_map_matplotlib", False):
            vz.interactive_mcc_map(ds)
        print("Visualization done.")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute and visualize correlation maps.")
    parser.add_argument("--run", "--run_all", help="Run all steps: compute correlations and visualize", action="store_true")

    # Correlation processing options
    group_corr = parser.add_argument_group("Correlation processing options")
    group_corr.add_argument("-cp", "--correlation_processing", "--corr", "--correlation", help="Run correlation processing", action="store_true")
    group_corr.add_argument("--save_data", help="Save correlation data after computation", action="store_true")

    # Visualization options
    group_vis = parser.add_argument_group("Visualization options")
    group_vis.add_argument("-vz", "--visualization", help="Run visualization", action="store_true")
    group_vis.add_argument("--plot_mcc_map", action="store_true", help="Plot MCC correlation map")
    group_vis.add_argument("--plot_max_mcc_map", action="store_true", help="Plot max MCC correlation map")
    group_vis.add_argument("--display_interactive_map_holoviz", action="store_true", help="Display interactive map using Holoviz")
    group_vis.add_argument("--display_interactive_map_matplotlib", action="store_true", help="Display interactive map using Folium")
    group_vis.add_argument("--show_plot", help="Show correlation maps after computation", action="store_true")
    group_vis.add_argument("--save_plot", help="Save correlation maps after computation", action="store_true")
    group_vis.add_argument("--mode_holoviz", type=str, default=None, help="Mode for Holoviz interactive map", choices=["notebook", "browser"])

    args = parser.parse_args()

    run(args, config)