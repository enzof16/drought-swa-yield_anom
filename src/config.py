# ---------- HEADER --------------------------------------------
# File : src/config.py
# Author(s) : Enzo Fortin
#
# Description :
# Configuration file for the project.
# --------------------------------------------------------------
from pathlib import Path
import src.utils as utils
import numpy as np

class Config:
    # Default configuration
    DEFAULT_TH_DETECTION_DROUGHT = -0.67
    DEFAULT_MONTH_START = 4
    DEFAULT_MONTH_END = 9
    DEFAULT_YEAR_START = 1991
    DEFAULT_YEAR_END = 2023
    DEFAULT_TH_SWA_LIST = (0, 1, 0.05)
    DEFAULT_TH_YA_LIST = [0., -0.3, -0.5, -0.67, -1.0, -1.5]
    DEFAULT_TH_SWA = 0.1
    DEFAULT_TH_YA = -0.67
    DEFAULT_REGIONS_LIST = ["europe", "usa", "china", "india", "canada", "argentina", "brazil"]
    DEFAULT_REGIONS_TO_STANDARDIZE = ["usa", "china", "india", "canada", "argentina", "brazil"]

    def __init__(
        self,
        th_detection_drought: float = DEFAULT_TH_DETECTION_DROUGHT,
        month_start: int = DEFAULT_MONTH_START,
        month_end: int = DEFAULT_MONTH_END,
        year_start: int = DEFAULT_YEAR_START,
        year_end: int = DEFAULT_YEAR_END,
        TH_SWA_list = DEFAULT_TH_SWA_LIST,
        TH_YA_list = DEFAULT_TH_YA_LIST,
        TH_SWA: float = DEFAULT_TH_SWA,
        TH_YA: float = DEFAULT_TH_YA,
        regions_list = DEFAULT_REGIONS_LIST,
        regions_to_standardize = DEFAULT_REGIONS_TO_STANDARDIZE,
    ):
        self.regions_list = regions_list,
        self.th_detection_drought = th_detection_drought
        self.month_start = month_start
        self.month_end = month_end
        self.year_start = year_start
        self.year_end = year_end
        self.TH_SWA = TH_SWA
        self.TH_YA = TH_YA
        if isinstance(TH_YA_list, list):
            self.TH_YA_list = TH_YA_list
        elif isinstance(TH_YA_list, tuple) and len(TH_YA_list) == 3:
            self.TH_YA_list = list(np.arange(TH_YA_list[0], TH_YA_list[1]+TH_YA_list[2], TH_YA_list[2]))
        else:
            raise ValueError("TH_YA_list must be a list or a tuple of (start, end, step)")
        if isinstance(TH_SWA_list, list):
            self.TH_SWA_list = TH_SWA_list
        elif isinstance(TH_SWA_list, tuple) and len(TH_SWA_list) == 3:
            self.TH_SWA_list = list(np.arange(TH_SWA_list[0], TH_SWA_list[1]+TH_SWA_list[2], TH_SWA_list[2]))
        else:
            raise ValueError("TH_SWA_list must be a list or a tuple of (start, end, step)")
        
        # "Calculated" options
        self.sel_years = [self.year_start, self.year_end]
        self.regions_to_standardize = regions_to_standardize
        
        # Initialize sub-configurations
        self.paths = self.Paths(self)
        self.yield_config = self.YieldConfig(data_dir_yield=self.paths.YIELD_DATA_DIR)
        self.swa_config = self.SwaConfig(data_dir_swa=self.paths.SWA_DATA_DIR, th_detection_drought=self.th_detection_drought, month_start=self.month_start, month_end=self.month_end)
        self.nuts_config = self.NUTSConfig()
        self.plot_config = self.PlotConfig()
        self.corr_config = self.CorrelationConfig(data_dir_corr=self.paths.CORR_DIR, th_detection_drought=self.th_detection_drought, month_start=self.month_start, month_end=self.month_end)
    

    
    @classmethod
    def from_args(cls, args):
        """Build a Config object from argparse arguments.
        Args:
            args (argparse.Namespace): The parsed command-line arguments containing
                configuration options.
        Returns:
            Config: An instance of the Config class with attributes set according to
                the provided arguments or their default values.
        Example:
            >>> import argparse
            >>> parser = argparse.ArgumentParser()
            >>> parser.add_argument('--start_year', type=int, default=2000)
            >>> args = parser.parse_args(['--start_year', '2020'])
            >>> config = build_config_from_args(args)
            >>> print(config.start_year)
            2020
        """
        return Config(
            th_detection_drought=getattr(args, "th_detection_drought", None) or cls.DEFAULT_TH_DETECTION_DROUGHT,
            year_start=getattr(args, "year_start", None) or cls.DEFAULT_YEAR_START,
            year_end=getattr(args, "year_end", None) or cls.DEFAULT_YEAR_END,
            month_start=getattr(args, "month_start", None) or cls.DEFAULT_MONTH_START,
            month_end=getattr(args, "month_end", None) or cls.DEFAULT_MONTH_END,
            TH_SWA=getattr(args, "th_swa", None) or cls.DEFAULT_TH_SWA,
            TH_YA=getattr(args, "th_ya", None) or cls.DEFAULT_TH_YA,
            TH_SWA_list=getattr(args, "th_swa_list", None) or cls.DEFAULT_TH_SWA_LIST,
            TH_YA_list=getattr(args, "th_ya_list", None) or cls.DEFAULT_TH_YA_LIST
        )

    class Paths:
        def __init__(self, config):
            self.config = config

            """Configuration class for project paths and constants.
            The paths are set relative to the project root directory.
            Here, the values can be modified if needed."""
            self.PROJECT_ROOT = Path(__file__).resolve().parent.parent.as_posix()
            self.DATA_DIR = f"{self.PROJECT_ROOT}/data"
            self.SRC_DIR = f"{self.PROJECT_ROOT}/src"
            self.SCRIPTS_DIR = f"{self.SRC_DIR}/scripts"

            self.YIELD_DATA_DIR = f"{self.DATA_DIR}/yield"
            self.SWA_DATA_DIR = f"{self.DATA_DIR}/swa"
            self.CORR_DIR = f"{self.DATA_DIR}/correlation"
            self.SHAPEFILES_DIR = f"{self.DATA_DIR}/shapefiles"
            self.CORINE_DIR = f"{self.DATA_DIR}/corine"

            # Specific filepaths for yield analysis
            self.CORINE_TIF = f"{self.CORINE_DIR}/corine18_arable_5km.tif"
            self.NUTS_SHAPEFILE = f"{self.SHAPEFILES_DIR}/NUTS_shapefile/NUTS_aggregated.shp"

            # Specific paths for correlation analysis
            self.CORR_DIR = f"{self.DATA_DIR}/correlation"
            self.CORR_SWA_FILE = f"{self.SWA_DATA_DIR}/th_{self.config.th_detection_drought}/{utils.get_period_aggregation_str(self.config.month_start, self.config.month_end)}/4-temporal_series/temporal_series_swa-{self.config.year_start}_{self.config.year_end}-{utils.get_month_str(self.config.month_start)}_{utils.get_month_str(self.config.month_end)}.xlsx"
            self.CORR_YA_FILE = f"{self.YIELD_DATA_DIR}/output/europe_prod_anom-{self.config.year_start}_{self.config.year_end}.xlsx"
            
    class YieldConfig:
            def __init__(self, data_dir_yield:Path=None):
                self.REGIONS = ["europe", "usa", "china", "india", "canada", "argentina", "brazil"]
                self.DATA_DIR = f"{data_dir_yield}/data"
                self.DATA_STANDARDIZED_DIR = f"{data_dir_yield}/data_standardized"
                self.DATA_PROCESSED_DIR = f"{data_dir_yield}/data_processed"
                self.FIGURES_DIR = f"{data_dir_yield}/figures"
                self.OUTPUT_DIR = f"{data_dir_yield}/output"

                self.DATA_PATHS = {
                    "usa": f"{self.DATA_DIR}/usa/USDA_data_1991-2023.csv",
                    "china": f"{self.DATA_DIR}/china/Cereal_xxxx_excluding_Rice_China_1991_2022.xlsx",
                    "india": f"{self.DATA_DIR}/india/",
                    "canada": f"{self.DATA_DIR}/canada/Canada_xxxx-1991_2024.csv",
                    "argentina": f"{self.DATA_DIR}/argentina/data_all_argentina.csv",
                    "brazil": f"{self.DATA_DIR}/brazil/data_all_brazil.xlsx"
                }
                self.CODE_REGIONS = {"europe":None, "usa":"US", "canada":"CA", "china":"CN", "india":"IN", "argentina":"AR", "brazil":"BR"}

                # self.SEL_YEARS = 
                


            def get_region_mapping(self, region):
                """
                Returns a mapping of region names to their ISO 3166-2 codes or other identifiers.
                Args:
                - region: str, the region for which to get the mapping (e.g., "usa", "china", "india", "canada", "argentina", "brazil")
                Returns:
                - ID : dict, a dictionary mapping region names to their ISO 3166-2 codes or other identifiers
                - CODE : dict or None, a dictionary mapping region names to a specific code (e.g., FIPS for USA) or None if not applicable
                """
                if region == "usa":
                    id_to_iso3166 = {"ALABAMA": "US-AL", "ARIZONA": "US-AZ", "ARKANSAS": "US-AR", "CALIFORNIA": "US-CA", "COLORADO": "US-CO", "CONNECTICUT": "US-CT", "DELAWARE": "US-DE", "FLORIDA": "US-FL", "GEORGIA": "US-GA", "HAWAII": "US-HI", "IDAHO": "US-ID", "ILLINOIS": "US-IL", "INDIANA": "US-IN", "IOWA": "US-IA", "KANSAS": "US-KS", "KENTUCKY": "US-KY", "LOUISIANA": "US-LA", "MAINE": "US-ME", "MARYLAND": "US-MD", "US-MASSACHUSETTS": "US-MA", "MICHIGAN": "US-MI", "MINNESOTA": "US-MN", "MISSISSIPPI": "US-MS", "MISSOURI": "US-MO", "MONTANA": "US-MT", "NEBRASKA": "US-NE", "NEVADA": "US-NV", "NEW HAMPSHIRE": "US-NH", "NEW JERSEY": "US-NJ", "NEW MEXICO": "US-NM", "NEW YORK": "US-NY", "NORTH CAROLINA": "US-NC", "NORTH DAKOTA": "US-ND", "OHIO": "US-OH", "OKLAHOMA": "US-OK", "OREGON": "US-OR", "PENNSYLVANIA": "US-PA", "RHODE ISLAND": "US-RI", "SOUTH CAROLINA": "US-SC", "SOUTH DAKOTA": "US-SD", "TENNESSEE": "US-TN", "TEXAS": "US-TX", "UTAH": "US-UT", "VERMONT": "US-VT", "VIRGINIA": "US-VA", "WASHINGTON": "US-WA", "WEST VIRGINIA": "US-WV", "WISCONSIN": "US-WI", "WYOMING": "US-WY", "DISTRICT OF COLUMBIA": "US-DC"}
                    states_to_fips = {"ALABAMA": "01", "ALASKA": "02", "ARIZONA": "04", "ARKANSAS": "05", "CALIFORNIA": "06", "COLORADO": "08", "CONNECTICUT": "09", "DELAWARE": "10", "FLORIDA": "12", "GEORGIA": "13", "HAWAII": "15", "IDAHO": "16", "ILLINOIS": "17", "INDIANA": "18", "IOWA": "19", "KANSAS": "20", "KENTUCKY": "21", "LOUISIANA": "22", "MAINE": "23", "MARYLAND": "24", "MASSACHUSETTS": "25", "MICHIGAN": "26", "MINNESOTA": "27", "MISSISSIPPI": "28", "MISSOURI": "29", "MONTANA": "30", "NEBRASKA": "31", "NEVADA": "32", "NEW HAMPSHIRE": "33", "NEW JERSEY": "34", "NEW MEXICO": "35", "NEW YORK": "36", "NORTH CAROLINA": "37", "NORTH DAKOTA": "38", "OHIO": "39", "OKLAHOMA": "40", "OREGON": "41", "PENNSYLVANIA": "42", "RHODE ISLAND": "44", "SOUTH CAROLINA": "45", "SOUTH DAKOTA": "46", "TENNESSEE": "47", "TEXAS": "48", "UTAH": "49", "VERMONT": "50", "VIRGINIA": "51", "WASHINGTON": "53", "WEST VIRGINIA": "54", "WISCONSIN": "55", "WYOMING": "56", "DISTRICT OF COLUMBIA": "11"}
                    return {"ID":id_to_iso3166, "CODE":states_to_fips}
                elif region == "china":
                    id_to_iso3166 = {"Anhui":"CN-AH", "Beijing":"CN-BJ", "Chongqing":"CN-CQ", "Fujian":"CN-FJ", "Gansu":"CN-GS", "Guangdong":"CN-GD", "Guangxi":"CN-GX", "Guizhou":"CN-GZ", "Hainan":"CN-HI", "Hebei":"CN-HE", "Heilongjiang":"CN-HL", "Henan":"CN-HA", "Hong Kong":"CN-HK", "Hubei":"CN-HB", "Hunan":"CN-HN", "Inner Mongolia":"CN-NM", "Jiangsu":"CN-JS", "Jiangxi":"CN-JX", "Jilin":"CN-JL", "Liaoning":"CN-LN", "Macau":"CN-MO", "Ningxia":"CN-NX", "Qinghai":"CN-QH", "Shaanxi":"CN-SN", "Shandong":"CN-SD", "Shanghai":"CN-SH", "Shanxi":"CN-SX", "Sichuan":"CN-SC", "Tianjin":"CN-TJ", "Tibet":"CN-TI", "Xinjiang":"CN-XJ", "Yunnan":"CN-YN", "Zhejiang":"CN-ZJ", "Taiwan":"CN-TW"}
                    return {"ID":id_to_iso3166, "CODE":None}
                elif region == "india":
                    id_to_iso3166 = {"Andaman-And-Nicobar-Islands":"IN-AN","Andhra-Pradesh":"IN-AP","Arunachal-Pradesh":"IN-AR","Assam":"IN-AS","Bihar":"IN-BR","Chandigarh":"IN-CH","Chhattisgarh":"IN-CT", "Daman-And-Diu":"IN-DH","Delhi":"IN-DL","Goa":"IN-GA","Gujarat":"IN-GJ","Haryana":"IN-HR","Himachal-Pradesh":"IN-HP","Jammu-And-Kashmir":"IN-JK", "Jharkhand":"IN-JH", "Karnataka":"IN-KA", "Kerala":"IN-KL", "Ladakh":"IN-LA", "Lakshadweep":"IN-LD", "Madhya-Pradesh":"IN-MP", "Maharashtra":"IN-MH", "Manipur":"IN-MN", "Meghalaya":"IN-ML", "Mizoram":"IN-MZ", "Nagaland":"IN-NL", "Odisha":"IN-OR", "Puducherry":"IN-PY", "Punjab":"IN-PB", "Rajasthan":"IN-RJ", "Sikkim":"IN-SK", "Tamil-Nadu":"IN-TN", "Telangana":"IN-TG", "Tripura":"IN-TR", "Uttar-Pradesh":"IN-UP", "Uttarakhand":"IN-UT", "West-Bengal":"IN-WB"}
                    return {"ID":id_to_iso3166, "CODE":None}
                elif region == "canada":
                    id_to_iso3166 = {"Alberta": "CA-AB", "British Columbia": "CA-BC", "Manitoba": "CA-MB", "New Brunswick": "CA-NB", "Newfoundland and Labrador": "CA-NL", "Nova Scotia": "CA-NS", "Ontario": "CA-ON", "Prince Edward Island": "CA-PE", "Quebec": "CA-QC", "Saskatchewan": "CA-SK", "Yukon": "CA-YT", "Northwest Territories": "CA-NT", "Nunavut": "CA-NU"}
                    return {"ID":id_to_iso3166, "CODE":None}
                elif region == "argentina":
                    id_to_iso3166 = {"BUENOS AIRES":"AR-B", "CATAMARCA":"AR-K", "CHACO":"AR-H", "CHUBUT":"AR-U", "CORDOBA":"AR-X", "CORRIENTES":"AR-W", "ENTRE RIOS":"AR-E", "FORMOSA":"AR-P", "JUJUY":"AR-Y", "LA PAMPA":"AR-L", "LA RIOJA":"AR-F", "MENDOZA":"AR-M", "MISIONES":"AR-N", "NEUQUEN":"AR-Q", "RIO NEGRO":"AR-R","SALTA":"AR-A", "SAN JUAN":"AR-J","SAN LUIS":"AR-D", "SANTA CRUZ":"AR-Z", "SANTA FE":"AR-S", "SANTIAGO DEL ESTERO":"AR-G", "TUCUMAN":"AR-T", "TIERRA DEL FUEGO":"AR-V"}
                    return {"ID":id_to_iso3166, "CODE":None}
                elif region == "brazil":
                    id_to_iso3166 = {"Acre":"BR-AC", "Alagoas":"BR-AL", "Amapá":"BR-AP", "Amazonas":"BR-AM", "Bahia":"BR-BA", "Ceará":"BR-CE", "Distrito Federal":"BR-DF", "Espírito Santo":"BR-ES", "Goiás":"BR-GO", "Maranhão":"BR-MA", "Mato Grosso":"BR-MT", "Mato Grosso do Sul":"BR-MS", "Minas Gerais":"BR-MG", "Pará":"BR-PA", "Paraíba":"BR-PB", "Paraná":"BR-PR", "Pernambuco":"BR-PE", "Piauí":"BR-PI", "Rio de Janeiro":"BR-RJ", "Rio Grande do Norte":"BR-RN", "Rio Grande do Sul":"BR-RS", "Rondônia":"BR-RO", "Roraima":"BR-RR", "Santa Catarina":"BR-SC", "São Paulo":"BR-SP", "Sergipe":"BR-SE", "Tocantins":"BR-TO"}
                    return {"ID":id_to_iso3166, "CODE":None}
                else:
                    raise ValueError(f"Invalid region: {region}. Valid regions are: usa, china, india, canada, argentina, brazil")

            def get_code_mapping(self, region):
                """Returns a mapping of region codes to their corresponding subcodes.
                Args:
                    region (str): The region for which to get the code mapping.
                Returns:
                    dict: A dictionary mapping region codes to lists of subcodes.
                """
                if region == "europe":
                    return config.nuts_config.CODE_MAPPING
                elif region == "china":
                    return {"Inner Mongolia": ["Inner Mongol"], "Tibet": ["Xizang"]}
                else:
                    return {}
                
    
    class SwaConfig:
        def __init__(self, data_dir_swa:Path, th_detection_drought, month_start, month_end):
            self.th_detection_drought = th_detection_drought
            self.month_start = month_start
            self.month_end = month_end

            self.SWA_ANOM_DIR = f"{data_dir_swa}/0-swa_anomalies"
            self.CUSTOM_DATA_DIR = f"{data_dir_swa}/th_{th_detection_drought}/{self.month_end-self.month_start+1}_months-{utils.get_month_str(month_start)}_{utils.get_month_str(month_end)}"   # Directory dependent on the threshold and months
            self.SWA_PROCESSED_DIR = f"{self.CUSTOM_DATA_DIR}/1-processed"
            self.SWA_SPATIAL_MEAN_DIR = f"{self.CUSTOM_DATA_DIR}/2-spatial_mean_shp"
            self.SWA_TEMPORAL_MEAN_DIR = f"{self.CUSTOM_DATA_DIR}/3-temporal_mean_shp"
            self.SWA_TEMPORAL_MEAN_MAP_DIR = f"{self.CUSTOM_DATA_DIR}/3.1-temporal_mean_map"
            self.SWA_TEMPORAL_SERIES_DIR = f"{self.CUSTOM_DATA_DIR}/4-temporal_series"
            self.SWA_TEMPORAL_SERIES_PLOT_DIR = f"{self.CUSTOM_DATA_DIR}/4.1-temporal_series_region_plot"

    
    class CorrelationConfig:
        def __init__(self, data_dir_corr:Path, th_detection_drought, month_start, month_end):
            self.th_detection_drought = th_detection_drought
            self.month_start = month_start
            self.month_end = month_end

            self.CORR_DIR = f"{data_dir_corr}/th_{th_detection_drought}/{utils.get_period_aggregation_str(month_start, month_end)}"
            self.CORR_OUTPUT_DIR = f"{self.CORR_DIR}/visualizations"
            self.CORR_RESULTS_DIR = f"{self.CORR_DIR}/results"          

    
    class NUTSConfig:
        def __init__(self):
            # NUTS Constants
            self.CODE_MAPPING = {
            "FR1": ["FR10"],    # Ile-de-France
            "FR2": ["FRB0", "FRC1", "FRD1", "FRD2", "FRE2", "FRF2"],    # Centre-Val de Loire, Bourgogne, Basse-Normandie, Haute-Normandie, Picardie, Champagne-Ardenne
            "FR3": ["FRE1"],    # Nord-Pas-de-Calais
            "FR4": ["FRC2", "FRF1", "FRF3"],    # Franche-Comté, Alsace, Lorraine
            "FR5": ["FRG0", "FRH0", "FRI3"], # Pays de la Loire, Bretagne, Poitou-Charentes
            "FR6": ["FRI1", "FRI2", "FRJ2"],  # Aquitaine, Limousin, Midi-Pyrénées
            "FR7": ["FRK1", "FRK2"],    # Auvergne, Rhône-Alpes
            "FR8": ["FRJ1", "FRL0", "FRM0"],   # Languedoc-Roussillon, Provence-Alpes-Côte d'Azur, Corse
            "ES3+4": ["ES3", "ES4"],  # Comunidad de Madrid, Centro (ES)
            "PTother": ["PT15", "PT16", "PT17", "PT18", "PT20", "PT30"], # Other regions in Portugal
            "UKI+J": ["UKI", "UKJ"],  # London, South East (UK)
            "DE3+4": ["DE3", "DE4"],  # Berlin, Brandenburg (DE)
            "DE9+5": ["DE9", "DE5"],  # Niedersachsen, Bremen (DE)
            "DEF+6": ["DEF", "DE6"],  # Schlewig-Holstein, Hamburg (DE)
            "DEB+C": ["DEB", "DEC"],  # Rheinland-Pfalz, Saarland (DE)
            "FI1B+C": ["FI1B", "FI1C"],  # Helsinki-Uusimaa, Etelä-Suomi (FI)
            "EL3+EL6": ["EL3", "EL6"],  # Attiki, Kentriki Ellada (EL)
            "TR1+2": ["TR1", "TR2"],  # Istanbul, Batı Marmara (TR)
            }

            # NUTS Regions
            self.NUTS_REGIONS = [
            "ITC", "ITF", "ITG1", "ITG2", "ITH", "ITI", "FR1", "FR2", "FR3", "FR4", "FR5", "FR6", "FR7", "FR8",
            "DE1", "DE2", "DE3+4", "DE7", "DE8", "DE9+5", "DEA", "DEB+C", "DED", "DEE", "DEF+6", "DEG",
            "ES1", "ES2", "ES3+4", "ES5", "ES6",
            "TR1+2", "TR3", "TR4", "TR5", "TR6", "TR7", "TR8", "TR9", "TRA", "TRB", "TRC",
            "PL7", "PL2", "PL8", "PL4", "PL5", "PL6", "PL9",
            "RO1", "RO2", "RO3", "RO4",
            "SE1", "SE2", "SE3",
            "AT1", "AT2", "AT3",
            "EL3+EL6", "EL4", "EL5",
            "FI19", "FI1B+C", "FI1D",
            "PT11", "PTother",
            "UKC", "UKD", "UKE", "UKF", "UKG", "UKL", "UKH", "UKI+J", "UKK", "UKN", "UKM",
            "HU", "DK", "CZ", "BG", "RS", "LT", "AL", "BA", "BE", "CY", "EE", "IE", "LV", "MK", "MT", "NL", "NO", "SI", "SK", "CH", "HR", "ME", "XK"
            ]
        
    
    class PlotConfig:
        def __init__(self):
            self.BOUNDARIES = {
            "world": [-180, -90, 180, 90],
            "global": [-180, -90, 180, 90],
            "globe": [-180, -90, 180, 90],
            "europe": [-12, 35, 35, 72],
            "eu": [-12, 35, 35, 72],
            "eur": [-12, 35, 35, 72],
            "france": [-5, 41, 41, 51],
            "fr": [-5, 41, 41, 51]
            }



config = Config()
