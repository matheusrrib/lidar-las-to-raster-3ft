import os
import argparse
import arcpy

from utils import log, die, ensure_parent_dir, write_csv_row

def make_lasd_layer(in_lasd, layer_name, product):
    """
    Creates a LAS Dataset Layer and applies filters when needed.
    - dtm: filter to ground points (class 2)
    - dsm/intensity: no class filter (all points)
    """
    class_codes = None
    if product == "dtm":
        class_codes = [2]  # ASPRS Ground

    arcpy.management.MakeLasDatasetLayer(
        in_las_dataset=in_lasd,
        out_layer=layer_name,
        class_code=class_codes
    )
    return layer_name

def build_interpolation_type(product: str) -> str:
    """
    ArcPy requires full syntax:
      "BINNING {cell_assignment_type} {void_fill_method}"
    Valid cell assignments: AVERAGE, MINIMUM, MAXIMUM, IDW, NEAREST
    Valid void fill: NONE, SIMPLE, LINEAR, NATURAL_NEIGHBOR
    """
    void_fill = "LINEAR"  # good default; change to NONE if you prefer NoData voids

    if product == "dsm":
        cell_assign = "MAXIMUM"
    elif product == "dtm":
        cell_assign = "MINIMUM"
    else:  # intensity
        cell_assign = "AVERAGE"

    return f"BINNING {cell_assign} {void_fill}"

def lasd_to_raster(in_layer, out_raster, product, cellsize):
    ensure_parent_dir(out_raster)
    arcpy.env.overwriteOutput = True

    # Value field (ArcPy expects these keywords)
    if product == "intensity":
        value_field = "INTENSITY"
    else:
        value_field = "ELEVATION"

    interpolation_type = build_interpolation_type(product)

    log(f"Rasterizing product={product}")
    log(f"  value_field={value_field}")
    log(f"  interpolation_type={interpolation_type}")
    log(f"  cellsize={cellsize}")

    arcpy.conversion.LasDatasetToRaster(
        in_las_dataset=in_layer,
        out_raster=out_raster,
        value_field=value_field,
        interpolation_type=interpolation_type,
        data_type="FLOAT",
        sampling_type="CELLSIZE",
        sampling_value=cellsize,
        z_factor=1
    )

def raster_qa(raster):
    # Stats are helpful for MIN/MAX
    arcpy.management.CalculateStatistics(raster)
    desc = arcpy.Describe(raster)
    extent = desc.extent

    minv = arcpy.management.GetRasterProperties(raster, "MINIMUM")[0]
    maxv = arcpy.management.GetRasterProperties(raster, "MAXIMUM")[0]

    return {
        "path": raster,
        "cellsize_x": desc.meanCellWidth,
        "cellsize_y": desc.meanCellHeight,
        "xmin": extent.XMin,
        "ymin": extent.YMin,
        "xmax": extent.XMax,
        "ymax": extent.YMax,
        "min": minv,
        "max": maxv,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_lasd", required=True)
    parser.add_argument("--out_raster", required=True)
    parser.add_argument("--product", choices=["dtm", "dsm", "intensity"], default="dtm")
    parser.add_argument("--cellsize", type=float, default=3.0)
    parser.add_argument("--qa_csv", default=None)
    args = parser.parse_args()

    in_lasd = os.path.abspath(args.in_lasd)
    out_raster = os.path.abspath(args.out_raster)

    if not os.path.exists(in_lasd):
        die(f"LAS Dataset not found: {in_lasd}")

    layer = "las_layer_tmp"
    make_lasd_layer(in_lasd, layer, args.product)

    lasd_to_raster(layer, out_raster, args.product, args.cellsize)
    log(f"Raster created: {out_raster}")

    qa = raster_qa(out_raster)
    log(f"QA: min={qa['min']} max={qa['max']}")

    if args.qa_csv:
        header = ["path", "product", "cellsize_x", "cellsize_y", "xmin", "ymin", "xmax", "ymax", "min", "max"]
        row = {
            "path": qa["path"],
            "product": args.product,
            "cellsize_x": qa["cellsize_x"],
            "cellsize_y": qa["cellsize_y"],
            "xmin": qa["xmin"],
            "ymin": qa["ymin"],
            "xmax": qa["xmax"],
            "ymax": qa["ymax"],
            "min": qa["min"],
            "max": qa["max"],
        }
        write_csv_row(args.qa_csv, header, row)
        log(f"Wrote QA row to: {args.qa_csv}")

    log("Done.")

if __name__ == "__main__":
    main()
