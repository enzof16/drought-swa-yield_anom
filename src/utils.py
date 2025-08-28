# ---------- HEADER --------------------------------------------
# File : src/utils.py
# Author(s) : Enzo Fortin
#
# Description :
# Utility functions, more or less utile.
# --------------------------------------------------------------
import datetime as dt


def aggregate_regions_shp():
    """Create a new shapefile with aggregated regions based on the provided mapping.
    Args :
    Returns :
    """
    pass

def date(year, month, multplier_month=1):
    """Format the date as "YYYY-MM".
    Args:
        year (int): The year.
        month (int): The month.
    Returns:
        str: The formatted date string.
    """
    return f"{year}-{multplier_month*month:02d}"

def get_month_str(month):
    """Get the abbreviated month name (e.g., "JAN", "FEB").
    Args:
        month (int): The month number (1-12).
    Returns:
        str: The abbreviated month name in uppercase.
    """
    return dt.date(1900, month, 1).strftime("%b").upper()

def get_period_aggregation_str(month_start, month_end):
    """Get a string representing the period aggregation (e.g. "6_months-APR_SEP").
    Used for naming files and directories.
    Args:
        month_start (int): The starting month (1-12).
        month_end (int): The ending month (1-12).
    Returns:
        str: The period aggregation string.
    """
    return f"{month_end-month_start+1}_months-{get_month_str(month_start)}_{get_month_str(month_end)}"



def progress_bar(current, total, prefix="", suffix="", bar_length=40):
    """Display a progress bar in the console.
    Args:
        current (int): Current progress.
        total (int): Total value for completion.
        bar_length (int): Length of the progress bar.
    """
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * "=" + ">"
    if current == total:
        print("\r" + " " * (bar_length + len(prefix) + len(suffix) + 10), end="\r")
        return # Clear the line on completion
    padding = int(bar_length - len(arrow)) * " "
    ending = "\n" if current == total else "\r"
    print(f"{prefix} [{arrow}{padding}] {int(fraction*100)}% {suffix}", end=ending)