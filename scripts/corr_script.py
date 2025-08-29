# ---------- HEADER --------------------------------------------
# File : scripts/corr_script.py
# Author(s) : Enzo Fortin
#
# Description :
# This file contains scripts to compute and visualize correlation maps.
# --------------------------------------------------------------
import argparse

from src.config import Config
import src.correlation.correlation as cr
import src.correlation.visualization as vz




def run(args):
    print("\n############ CORRELATION SCRIPT ################\n")

    global config
    if any(getattr(args, k, None) is not None for k in ["start_year", "end_year", "month_start", "month_end", "th_detection_drought", "th_swa", "th_ya", "th_swa_list", "th_ya_list"]):
        # Parse list arguments if provided as comma-separated strings
        def parse_list(val):
            if val is None:
                return None
            if isinstance(val, (list, tuple)):
                return val
            try:
                # Try to parse as tuple (start, end, step)
                if isinstance(val, str) and val.startswith("(") and val.endswith(")"):
                    return tuple(float(x.strip()) for x in val[1:-1].split(","))
                # Otherwise, parse as comma-separated list
                return [float(x.strip()) for x in val.split(",")]
            except Exception:
                return val

        config = Config(
            th_detection_drought=getattr(args, "th_detection_drought", Config().th_detection_drought),
            start_year=getattr(args, "start_year", Config().start_year),
            end_year=getattr(args, "end_year", Config().end_year),
            month_start=getattr(args, "month_start", Config().month_start),
            month_end=getattr(args, "month_end", Config().month_end),
            TH_SWA=getattr(args, "th_swa", Config().TH_SWA),
            TH_YA=getattr(args, "th_ya", Config().TH_YA),
            TH_SWA_list=parse_list(getattr(args, "th_swa_list", Config().TH_SWA_list)),
            TH_YA_list=parse_list(getattr(args, "th_ya_list", Config().TH_YA_list))
        )
    else:
        config = Config()

    
    cr.config = config  # update config in correlation
    vz.config = config  # update config in visualization

    if getattr(args, "run", False):
        args.correlation_processing = True
        args.visualization = True
        args.plot_mcc_map = True
        args.plot_max_mcc_map = True
        args.display_interactive_map_holoviz = True
        args.display_interactive_map_matplotlib = True
        args.save_data = "both"

    if getattr(args, "correlation_processing", False):
        print("Computing correlation maps...")
        cr.main(netcdf=getattr(args, "save_data", None) in ["netcdf", "both"], excel=getattr(args, "save_data", None) in ["excel", "both"])
        

    if getattr(args, "visualization", False):
        print("Visualizing correlation maps...")
        ds = vz.load_correlation_results()
        if getattr(args, "plot_mcc_map", False):
            vz.plot_mcc_map(ds, th_swa=config.TH_SWA, th_ya=config.TH_YA, save=getattr(args, "save_plot", False), show=getattr(args, "show_plot", False))
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

    # General options
    group_gen = parser.add_argument_group("General options")
    group_gen.add_argument("--th_detection_drought", "--threshold", "-th", default=Config().th_detection_drought, type=float, help="Threshold for drought detection")
    group_gen.add_argument("--start_year", type=int, default=Config().start_year, help="Start year")
    group_gen.add_argument("--end_year", type=int, default=Config().end_year, help="End year")
    group_gen.add_argument("--month_start", type=int, default=Config().month_start, help="Start month")
    group_gen.add_argument("--month_end", type=int, default=Config().month_end, help="End month")
    group_gen.add_argument("--th_swa_list", type=str, default=Config().TH_SWA_list, help="List of thresholds for SWA in MCC map (comma-separated or tuple '(start,end,step)')")
    group_gen.add_argument("--th_ya_list", type=str, default=Config().TH_YA_list, help="List of thresholds for Yield Anomaly in MCC map (comma-separated or tuple '(start,end,step)')")
    group_gen.add_argument("-cp", "--correlation_processing", "--corr", "--correlation", help="Run correlation processing", action="store_true")
    
    # Processing options
    group_proc = parser.add_argument_group("Processing options")
    group_proc.add_argument("--save_data", choices=["netcdf", "excel", "both"], help="Format to save correlation data", type=str, default=None)

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
    group_vis.add_argument("--th_swa", type=float, default=Config().TH_SWA, help="Threshold for SWA in MCC map")
    group_vis.add_argument("--th_ya", type=float, default=Config().TH_YA, help="Threshold for Yield Anomaly in MCC map")
    args = parser.parse_args()

    run(args)