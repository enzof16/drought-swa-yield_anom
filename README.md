# Drought and Yield Anomaly Analysis

## Description
This project analyzes the relationship between agricultural yield anomalies (mainly cereals) and drought events detected using Soil Water Availability (SWA) data.  
It provides a reproducible workflow for standardizing, processing, and visualizing yield and drought data across multiple regions.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
### Yield Data Workflow
- **Standardization:**  
  Run scripts/yield_script.py to harmonize yield data for a selected region.
- **Processing:**  
  Run scripts/yield_script.py to compute yield anomalies.
- **Visualization:**  
  Run scripts/yield_script.py to generate time series and anomaly maps.

### SWA Drought Workflow
- **Single month analysis:**  
  ```bash
  python main.py --year 2022 --month 4 --mode single
  ```
- **Period analysis (e.g., 6 months):**  
  ```bash
  python main.py --year 2022 --month 4 --period 6 --mode period
  ```
- **Time series analysis:**  
  ```bash
  python main.py --mode timeseries --years-range 1991 2023
  ```

## Project Structure
- `src/` : Source code modules
    - `yield_analysis/` : Yield data standardization, processing, visualization
    - `swa_analysis/` : SWA drought detection and analysis
    - `correlation/` : Correlation analysis between drought and yield anomalies
    - `config.py` : Centralized configuration
- `data/` : Raw and processed input data (not versioned)
- `output/` : Generated results and figures (not versioned)
- `scripts/` : Execution scripts for batch processing
- `notebooks/` : Jupyter notebooks documenting each step of the workflow

## Data Requirements
- SWA raster files (monthly)
- CORINE land cover data
- NUTS shapefiles
- Yield data (regional/country level, various formats)

## Credits
Developed during a summer internship at Politecnico di Milano  
Internship supervisor: Prof. Carmelo Cammalleri  
Author: Enzo Fortin