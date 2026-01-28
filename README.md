LiDAR LAS/LAZ to 3-ft Raster in ArcGIS Pro or ArcPy

This project automates a common GIS production workflow for raster creation based on Lidar data:
- Build an ArcGIS LAS Dataset (`.lasd`) from LAS/LAZ tiles,
- Convert the LAS dataset into a single raster at **3-ft resolution** (e.g., DTM/DSM/intensity)

Designed to be a portfolio-quality example for GIS hiring (consulting, remote GIS automation).

1 Requirements
- ArcGIS Pro (ArcPy available)
- Input LiDAR tiles: `.las` and/or `.laz`

2 What this produces
- A LAS Dataset: `*.lasd`
- A raster output (GeoTIFF by default):
  - DTM (bare-earth elevation) using ground points
  - DSM (surface) using first returns / binning
  - Intensity raster (if available)

3 Usage

3.1 Build LAS Dataset
```bash
"C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\propy.bat" scripts\build_las_dataset.py ^
  --in_folder "D:\lidar\tiles" ^
  --out_lasd "D:\lidar\project\lidar.lasd" ^
  --spatial_ref_epsg 32119
