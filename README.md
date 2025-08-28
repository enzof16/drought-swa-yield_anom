# Drought and Yield Anomaly Analysis

## Project Introduction
This project aims to analyze agricultural yield data and its relationship with drought events, using a reproducible workflow developed during a summer internship at Politecnico di Milano.

The main objectives are to standardize yield datasets from multiple regions, detect agricultural droughts using Soil Water Availability (SWA) data, and investigate the correlation between drought occurrences and negative yield anomalies.

## Structure
The project is organized into several main folders and modules to support a clear and reproducible workflow:
- `src/` : Source code modules
    - `yield_analysis/` : Yield data standardization, processing, visualization
    - `swa_analysis/` : SWA drought detection and analysis
    - `correlation/` : Correlation analysis between drought and yield anomalies
    - `config.py` : Centralized configuration
- `data/` : Raw and processed input data (not versioned)
- `output/` : Generated results and figures (not versioned)
- `scripts/` : Execution scripts for batch processing
- `notebooks/` : Jupyter notebooks documenting each step of the workflow

## Workflow
The workflow in this project closely follows the chronological steps of my internship.

1. **Yield Data Standardization:** Agricultural production data is harmonized and visualized to extract meaningful information.
2. **SWA Drought Analysis:** SWA (Soil Water Availability) data is analyzed to identify agricultural drought events, using a defined threshold and a specific period (typically the growing season).
3. **Correlation Study:** The correlation between drought occurrences detected with SWA and the occurrences of negative yield anomalies is studied, aiming to assess whether yield anomalies can serve as a proxy for agricultural drought.

## Installation

To get started, you can either clone the repository using git or download the project folder manually:

- **Clone with git (recommended):**
  ```powershell
  git clone https://github.com/enzof16/drought-swa-yield_anom.git
  cd drought-swa-yield_anom
  ```
- **Or download the folder:**
  - Click 'Code' > 'Download ZIP' on the GitHub page, then extract the archive.

Next, set up your Python environment and install dependencies:

1. Make sure you have Python 3.13 (or the required version) installed.
2. (Recommended) Create and activate a virtual environment (Windows PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```



## How to Use the Package

There are several ways to use this package depending on your needs:

1. **Directly importing functions from src/**
   - You can import and call functions from the modules in the `src/` folder in your own Python scripts or notebooks.
   - This is useful for using the project as a package, or for custom and reproducible analyses.
   - See the notebooks for examples of direct function usage.

  2. **Via the command line**
   - All functionalities can be launched from the command line:
     - Either with the main `main.py` file to orchestrate the entire workflow with custom parameters:
       ```powershell
       python main.py ...
       ```
     - Or with the individual scripts in `scripts/` to run each part separately:
       ```powershell
       python scripts/yield_script.py
       python scripts/swa_script.py
       ```
      > For help with commands press `-h`/`--help` to display the commands.<br>For instance : ```python main.py --help``` or ```python scripts/yield.py -h```

3. **Via Jupyter notebooks**
   - Open the notebooks in the `notebooks/` folder to explore, document, and visualize workflow steps interactively.
   - Ideal for documentation, experimentation, and reproducibility.

Choose the method that best fits your needs: automation, interactive exploration, documentation, or custom development.


## Data Requirements
To work with this project, ensure you have the following data files/folders:
- `./corine/corine18_arable_5km.tif` : Required for identifying arable land areas using CORINE data, used in the swa part.
- `./shapefiles/*` : Contains shapefiles for defining geographic regions.
- `./swa/0-swa_anomalies/*.tif` : Includes SWA anomaly TIFF files for drought analysis.
- `./yield/data/*` : Holds yield data files necessary for yield anomaly calculations.

## Credits
Developed during a summer internship at Politecnico di Milano  
Internship supervisor: Prof. Carmelo Cammalleri  
Author: Enzo Fortin (2025)