import os
import argparse
import arcpy

from utils import log, die, ensure_parent_dir


def list_las_files(in_folder: str):
    exts = (".las", ".laz", ".zlas")
    las_files = []

    for root, _, files in os.walk(in_folder):
        for fn in files:
            if fn.lower().endswith(exts):
                las_files.append(os.path.join(root, fn))

    return las_files


def main():
    parser = argparse.ArgumentParser(
        description="Build an ArcGIS LAS Dataset (.lasd) from a folder of LAS/LAZ tiles."
    )
    parser.add_argument("--in_folder", required=True)
    parser.add_argument("--out_lasd", required=True)
    parser.add_argument("--spatial_ref_epsg", type=int, default=None)
    parser.add_argument("--compute_stats", action="store_true")
    parser.add_argument("--build_pyramids", action="store_true")
    args = parser.parse_args()

    in_folder = os.path.abspath(args.in_folder)
    out_lasd = os.path.abspath(args.out_lasd)

    if not os.path.isdir(in_folder):
        die(f"Input folder not found: {in_folder}")

    las_files = list_las_files(in_folder)
    if not las_files:
        die("No LAS/LAZ files found.")

    ensure_parent_dir(out_lasd)
    arcpy.env.overwriteOutput = True

    sr = None
    if args.spatial_ref_epsg:
        sr = arcpy.SpatialReference(args.spatial_ref_epsg)
        log(f"Using spatial reference EPSG:{args.spatial_ref_epsg}")

    log(f"Found {len(las_files)} LAS/LAZ files.")
    log("Creating LAS Dataset...")

    arcpy.management.CreateLasDataset(
        input=las_files,
        out_las_dataset=out_lasd,
        relative_paths="ABSOLUTE_PATHS",
        compute_stats="COMPUTE_STATS" if args.compute_stats else "NO_COMPUTE_STATS",
        spatial_reference=sr
    )

    log(f"LAS Dataset created: {out_lasd}")

    if args.build_pyramids:
        log("Building LAS dataset pyramids...")
        arcpy.management.BuildLasDatasetPyramid(out_lasd)

    log("Done.")


if __name__ == "__main__":
    main()
