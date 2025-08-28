# ---------- HEADER --------------------------------------------
# File : src/yield_analysid/data_standardization.py
# Author(s) : Enzo Fortin
#
# Description :
# This script standardizes agricultural production data for different regions and saves it in a specified format.
# --------------------------------------------------------------
import pandas as pd
import os
from src.config import config
import shutil


def copy_european_data():
    """
    Copies pre-standardized European agricultural production data files to the standardized data directory.
    """
    europe_data_dir = f"{config.paths.YIELD_DATA_DIR}/data/europe"
    standardized_data_dir = f"{config.paths.YIELD_DATA_DIR}/data_standardized/europe"
    if not os.path.exists(standardized_data_dir):
        os.makedirs(standardized_data_dir, exist_ok=True)
    for file in os.listdir(europe_data_dir):
        if file.endswith(".xlsx") or file.endswith(".xls"):
            src_file = os.path.join(europe_data_dir, file)
            filename, ext = os.path.splitext(file)
            dest_file = os.path.join(standardized_data_dir, f"{filename}_standardized{ext}")
            if not os.path.exists(dest_file):
                shutil.copy(src_file, dest_file)


def standardize_data(regions:list, sel_years:list=None, total_region=False):
    """
    Standardizes agricultural production data for a given region and year
    Args:
    - regions : list, a list of regions to standardize data for (e.g., ["usa", "china", "india", "canada", "argentina", "brazil"])
    - years: list, a list of years for which to standardize data (e.g., [1991, 2023])
    - total_region: bool, whether to include total data for the region (default is False)
    Returns:
    - dfs: dict, a dictionary containing standardized DataFrames for production and area data
    """
    dfs = {}

    for region in regions:
        # Ensure the region is valid
        valid_regions = ["usa", "china", "india", "canada", "argentina", "brazil"]
        if region not in valid_regions:
            raise ValueError(f"Invalid region: {region}. Valid regions are: {valid_regions}")

        ### USA Data Standardization ###
        if region == "usa":
            data = pd.read_csv(config.yield_config.DATA_PATHS["usa"], delimiter=",")
            columns_to_keep = ["Program", "Year", "State", "Commodity", "Data Item", "Value"]
            data = data[columns_to_keep]
            # We keep only the kind of data in the column "Data Item"
            data["Data Item"] = data["Data Item"].str.split(" - ").str[1].str.split(",").str[0]

            # Remove of data that come from the "Census" program
            data = data[data["Program"] != "CENSUS"]
            data = data.drop(columns=["Program"])

            # print(data.head())

            # Standardize the value column
            data["Value"] = pd.to_numeric(data["Value"].str.replace(",", ""))


            # print(data.head())
            # exit()

            # Conversion of american units to the one used in the rest of the project (european ones)
            units_conversion = {"ACRES PLANTED": 0.40469/1000, "CORN":.0254/1000, "BARLEY":.021772/1000, "SOYBEANS":.0272155/1000, "WHEAT": .0272155/1000}
            def convert_units(row):
                if row["Data Item"] in units_conversion:
                    return row["Value"]*units_conversion[row["Data Item"]]
                elif row["Commodity"] in units_conversion:
                    return row["Value"]*units_conversion[row["Commodity"]]
                else: return row["Value"]
            data["Value"] = data.apply(convert_units, axis=1)

            # Keeping only the data related to the Wheat (the part before can be used for other considerations)
            data = data[data["Commodity"] == "WHEAT"]
            data = data.drop(columns=["Commodity"])

            if sel_years is not None:
                data = data[data["Year"].between(sel_years[0], sel_years[-1])]
            
            # Creation two datasets for the wheat production and area
            df_prod_usa = data[data["Data Item"] == "PRODUCTION"].drop(columns=["Data Item"]).pivot(index="Year", columns="State", values="Value")
            df_area_usa = data[data["Data Item"] == "ACRES PLANTED"].drop(columns=["Data Item"]).pivot(index="Year", columns="State", values="Value")
            dfs["prod_usa"] = [df_prod_usa, "prod", "usa"]
            dfs["area_usa"] = [df_area_usa, "area", "usa"]
            # End of USA Data Standardization

        ### China Data Standardization ###
        elif region == "china":
            for kind_of_data in ["prod", "area"]:
                data = pd.read_excel(config.yield_config.DATA_PATHS[region].replace("xxxx", kind_of_data), sheet_name=0, header=None)  # Load the first sheet by default

                years = data.iloc[3, 1:].dropna().astype(int).tolist()  # Extract years from the third row and convert to integers
                # Extract the regions and values, be careful with the last two rows for the area data
                if kind_of_data == "area":
                    regions = data.iloc[4:-2,0].to_list()
                    values = data.iloc[4:-2, 1:]
                else:
                    regions = data.iloc[4:,0].to_list()
                    values = data.iloc[4:, 1:]
                
                values.columns, values.index = years, regions  # Set the columns and index
                
                values = values.apply(pd.to_numeric, errors="coerce").T.sort_index(axis=0) # Transpose and sort the index
                values.index.name, values.columns.name = "Year", "Region"

                if kind_of_data == "prod":
                    values = values / 10 

                if sel_years is not None:
                    values = values.loc[values.index.to_series().between(sel_years[0], sel_years[-1])]
                
                dfs[f"china_{kind_of_data}"] = [values, kind_of_data, "china"]
            # End of China Data Standardization

        ### India Data Standardization ###
        elif region == "india":
            for kind_of_data in ["prod", "area"]:   
                datapath_kind = f"{config.yield_config.DATA_PATHS["india"]}{kind_of_data}"
                dict_cereals_india = {}
                for file in os.listdir(datapath_kind):
                    if file.startswith("~$"):
                        continue
                    if not total_region and file.startswith("All-India"):
                        continue
                    subregion = file.split("-")[:-1]
                    subregion = "-".join(subregion)
                    
                    data = pd.read_excel(f"{datapath_kind}/{file}")
                    data, data.columns = data.iloc[6:-1,], data.iloc[5,:]
                    years = data.columns[2:].tolist()
                    years = [int(int(year.split("-")[0])+1) for year in years]
                    data.columns = ["Crop", "Season"] + years
                    
                    crops = data["Crop"].dropna().unique().tolist()
                    seasons = data["Season"].dropna().unique().tolist()
                    
                    data["Crop"] = data["Crop"].ffill()  # Forward fill crop names
                    dfs_crops = {}

                    for crop in crops:
                        dfs_crops[crop] = data[data["Crop"]==crop].drop(columns=["Crop"])

                    dict_cereals_india[subregion] = dfs_crops["Cereals"][dfs_crops["Cereals"]["Season"]=="Total"].drop(columns=["Season"])

                    if dict_cereals_india[subregion].empty:
                        dict_cereals_india[subregion] = pd.DataFrame([[float("nan")] * len(years)], columns=years)

                df_cereals_india = pd.concat(dict_cereals_india).droplevel(1).T
                df_cereals_india.index.name, df_cereals_india.columns.name = "Year", "Subregion"

                if sel_years is not None:
                    df_cereals_india = df_cereals_india.loc[df_cereals_india.index.to_series().between(sel_years[0], sel_years[-1])]
                
                dfs[f"{region}_{kind_of_data}"] = [df_cereals_india, kind_of_data, "india"]
            # End of India Data Standardization

        ### Canada Data Standardization ###
        elif region == "canada":
            for kind_of_data in ["prod", "area"]:
                # Load the data from the CSV files
                data = pd.read_csv(config.yield_config.DATA_PATHS[region].replace("xxxx", kind_of_data))

                # Remove unwanted regions if present, we also drop "Canada" (just for control)
                for region_name in ["Prairie provinces", "West", "East", "Maritime provinces", "Canada"]:
                    if region_name in data["GEO"].unique():
                        data = data[data["GEO"] != region_name]
                # Keep only the relevant columns
                columns_to_keep = ["REF_DATE", "GEO", "Type of crop", "VALUE", "STATUS", "SYMBOL", "TERMINATED"]
                data = data[columns_to_keep]

                data = data[data["Type of crop"] == "Wheat, all"]
                data = data.drop(columns=["Type of crop", "STATUS", "SYMBOL", "TERMINATED"])

                years = sorted(data["REF_DATE"].unique().tolist())
                regions = data["GEO"].unique().tolist()

                units_conversion = {"area": 0.001, "prod": 0.001}
                data["VALUE"] = (data["VALUE"].astype(float)*0.001).round(1)

                data = data.pivot(index="REF_DATE", columns="GEO", values="VALUE")
                data.index.name = "Year"

                if sel_years is not None:
                    data = data.loc[data.index.to_series().between(sel_years[0], sel_years[-1])]

                dfs[f"{kind_of_data}_canada"] = [data, kind_of_data, "canada"]
            # End of Canada Data Standardization

        ### Argentina Data Standardization ###
        elif region == "argentina":
            data = pd.read_csv(config.yield_config.DATA_PATHS["argentina"], encoding="latin1", sep=";")

            data["Year"] = data["Campana"].str.split("/").apply(lambda x: int(x[0]) + 1).tolist()
            
            # Columns to drop
            columns_to_drop = ["Id Cultivo", "ID Campaña", "Rendimiento (Kg/Ha)", "Sup. Sembrada (Ha)", "Campana"]
            data = data.drop(columns=columns_to_drop)    

            # Convert to thousands of tonnes and hectares
            data["Producción (Tn)"] = data["Producción (Tn)"].astype(float) / 1000
            data["Sup. Cosechada (Ha)"] = data["Sup. Cosechada (Ha)"].astype(float) / 1000

            # At the moment we just keep the wheat data
            data = data[data["Cultivo"] == "Trigo total"]    

            data_prod = data.groupby(["Year", "Provincia"])["Producción (Tn)"].sum().unstack().sort_index()
            data_area = data.groupby(["Year", "Provincia"])["Sup. Cosechada (Ha)"].sum().unstack().sort_index()

            data_prod.columns.name, data_area.columns.name = "Region", "Region"

            if sel_years is not None:
                data_prod = data_prod.loc[data_prod.index.to_series().between(sel_years[0], sel_years[-1])]
                data_area = data_area.loc[data_area.index.to_series().between(sel_years[0], sel_years[-1])]
            
            dfs["prod_argentina"] = [data_prod, "prod", "argentina"]
            dfs["area_argentina"] = [data_area, "area", "argentina"]
            # End of Argentina Data Standardization

        ### Brazil Data Standardization ###
        elif region == "brazil":
            for kind_of_data in ["prod", "area"]:
                if kind_of_data == "prod": sheet_name = "Quantidade produzida"
                elif kind_of_data == "area": sheet_name = "Área colhida"
                data = pd.read_excel(config.yield_config.DATA_PATHS["brazil"], sheet_name=sheet_name, header=None)
                
                data = data.iloc[3:-1, 2:]  # Remove the first three rows and the first two columns

                data = data.T
                data = data[[data.columns[1], data.columns[0]] + list(data.columns[2:])]   # Reorder the columns to have "Crop" and "Year" first
                data.columns = ["Crop", "Year"] + data.iloc[0,2:].tolist()  # Extract the first row as column names
                data.columns.name, data.index.name = "Region", "Year"
                data = data.iloc[1:, :]  # Remove the first row (which is now the header)

                data.index = data.iloc[:, 1].ffill().astype(int)  # Set the index to the first column (Year) and convert to int

                if sel_years is not None:
                    data = data[(data.index.astype(int) >= sel_years[0]) & (data.index.astype(int) <= sel_years[-1])]

                data = data.iloc[2::2,:]  # Keep only the rows with production values (every second row)

                crops = data.iloc[0, 1:].tolist()  # Extract crops from the first row
                sel_crops = ["Trigo (em grão)"] # Change this to the crops you want to keep

                if len(sel_crops)>=2:
                    for crop in sel_crops:
                        pass
                else:
                    data = data[data["Crop"]==sel_crops[0]].drop(columns=["Crop", "Year"])

                replace_symbol = {"-":0, "X":float("nan"), "..":float("nan"), "...":float("nan")}
                pd.set_option("future.no_silent_downcasting", True)
                data = data.replace(replace_symbol)

                data = data.apply(pd.to_numeric, errors="coerce")

                if total_region:
                    cols = [col for col in data.columns if col != "Brasil"] + ["Brasil"]
                    data = data[cols]
                else:
                    data = data.drop(columns=["Brasil"])
                
                # Convert to thousands of tonnes and hectares
                data = data.astype(float) / 1000

                dfs[f"{kind_of_data}_brazil"] = [data, kind_of_data, "brazil"]
            # End of Brazil Data Standardization

        else :
            print("The region is not a valid region")
        
    return dfs
    ##### End of Data Standardization #####


def save_data(dfs):
    """
    Saves the standardized data to Excel files in the specified format.
    Args:
    - dfs: dict, a dictionary containing standardized DataFrames for production and area data
    - years: list, the years for which the data is standardized
    Returns:
    - None : The function saves the DataFrames to Excel files in the specified format.
    """
    ##### Creation of xlsx files for the standardized data #####
    for df in dfs:
        df, kind_of_data, region = dfs[df]
        dict_region_mapping = config.yield_config.get_region_mapping(region)
        num_columns = len(df.columns)
        years = df.index.tolist()

        row_1 = ["Name"] + list(df.columns)  # First row with empty values
        row_2 = ["ID"] + [dict_region_mapping["ID"].get(col, "") for col in df.columns]
        if dict_region_mapping["CODE"]:
            row_3 = ["CODE"] + [dict_region_mapping["CODE"].get(col, "") for col in df.columns]
        else:
            row_3 = ["Code"] + ["" for _ in df.columns]


        df_final = pd.concat([
            pd.DataFrame([row_1], columns=["Year"] + list(df.columns)),
            pd.DataFrame([row_2], columns=["Year"] + list(df.columns)),
            pd.DataFrame([row_3], columns=["Year"] + list(df.columns)),
            df.reset_index()
        ], ignore_index=True)        

        # Fill NaN values with "#N/A"
        df_final = df_final.fillna("#N/A")        

        # Saving the DataFrame to an Excel file
        output_file = f"{config.paths.DATA_DIR}/yield/data_standardized/{region}/{kind_of_data}_{region}_standardized.xlsx"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_final.to_excel(output_file, index=False, header=False)
# --------------------------------------------------------------


# ---------- RUNS ----------------------------------------------
def run_standardization():
    """
    """
    region = input("Enter the region (usa, china, india, canada, argentina, brazil)\nOr enter all for executing standardizing and saving for all countries: ").strip().lower()
    if region == "all":
        regions = ["usa", "china", "india", "canada", "argentina", "brazil"]
    else:
        regions = [region]
    dfs = standardize_data(regions=regions, sel_years=None, total_region=False)
    save_data(dfs)

if __name__ == "__main__":
    run_standardization()
# # --------------------------------------------------------------

