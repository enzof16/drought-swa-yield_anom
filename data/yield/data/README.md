# Yield Data Folder

This folder contains input yield data (area and production) used in the project. Contains regional/country-level yield datasets in CSV or Excel format.

## Data Sources

This file provides an overview of the input yield data available in this folder, including details about data sources, formats, and usage guidelines.

### Example Entries

#### Europe Wheat Data
**Source:** [Eurostat](https://ec.europa.eu/eurostat)  
**Description:** Annual wheat yield data for European countries, harmonized for analysis.  
**Files:** [`area_europe.xlsx`](./europe/area_europe.xlsx) (original name: ` `), [`prod_europe.xlsx`](./europe/prod_europe.xlsx) (original name: ` `)

#### USA Corn Data
**Source:** [USDA National Agricultural Statistics Service](https://www.nass.usda.gov/)  
**Description:** State-level corn yield data for the United States.  
**File:** [`USDA_data_1991-2023.xlsx`](./usa/USDA_data_1991-2023.xlsx) (original file : [`USDA_data_1991-2023`](./usa/USDA_data_1991-2023.csv))


#### China Rice Data
**Source:** [FAOSTAT](https://www.fao.org/faostat/en/)  
**Description:** ?<br>
**File:** [`Cereal_area_excluding_Rice_China_1991_2022.xlsx`](./china/Cereal_area_excluding_Rice_China_1991_2022.xlsx), [`Cereal_prod_excluding_Rice_China_1991_2022.xlsx`](./china/Cereal_prod_excluding_Rice_China_1991_2022.xlsx)
(original files : the other ones in the folder)

### Canada Data
**Source:** [Statistics Canada](https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=3210035901)<br>
**Description:** Table 32-10-0359-01 | No data found for : Northwest territories, Yukon, Nunavut.<br>
**Files:** [`Canada_area-1991_2024.csv`](./canada/Canada_area-1991_2024.csv), [`Canada_prod-1991_2024.csv`](./canada/Canada_prod-1991_2024.csv)

### India Data
**Source:** [DA&FW | Department of Agriculture & Farmers Welfare](https://upag.gov.in/dashboard/apy-overview-tab)<br>
**Description:** Initial data contained duplicate years, we use the harvest year, so 2013-2014 becomes 2014.  
No distinction is made between cereal types—all cereals are included.  
Region IDs follow the ISO-3166 standard.  
No data is available for the region "The-Dadra-And-Nagar-Haveli-And-Daman-And-Diu"<br>
**Files:** `area/<region>.xlsx`, `prod/<region>.xlsx`

### Brazilian Data
**Source:** [IBGE](https://sidra.ibge.gov.br/tabela/1612)<br>
**Description:** <br>
**Files:** [`data_all_brazil.xlsx`](./brazil/data_all_brazil.xlsx)

### Argentina Data
**Source:** [Ministerio de Agrícultura, Ganaderia y Pesca](https://datosestimaciones.magyp.gob.ar/reportes.php?reporte=Estimaciones)
**Description:** For a crop season labeled 1969/70, use 1970.
For missing data:  
- Light gray background / gray hatching: No data available, but the region/crop appears in the file  
- Gray background / light gray hatching: No data at all in the file for the selected years or crops


## Usage Tips

- Update this README if you add new data requirements or change the folder structure.

---