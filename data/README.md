# Data Folder

This folder is intended for all raw and processed data files used in the project.

> **Do not upload large data files to GitHub.**

## Organisation
| Folder/File      | Description                                      |
|------------------|--------------------------------------------------|
| `corine/`        | CORINE TIFF files covering arable land areas     |
| `correlation/`   | Files related to correlation analysis            |
| `shapefiles/`    | Shapefiles for relevant regions                  |
| `swa/`           | Files related to SWA analysis                    |
| `yield/`         | Files related to yield analysis                  |
| `README.md`      | Documentation for the data directory             |

## Data Requirements
To work with this project, ensure you have the following data files/folders:
- `./corine/corine18_arable_5km.tif` : Required for identifying arable land areas using CORINE data, used in the swa part.
- `./shapefiles/*` : Contains shapefiles for defining geographic regions.
- `./swa/0-swa_anomalies/*.tif` : Includes SWA anomaly TIFF files for drought analysis.
- `./yield/data/*` : Holds yield data files necessary for yield anomaly calculations.
