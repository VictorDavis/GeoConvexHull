#!/usr/bin/python

from GeoConvexHullArea import get_hull_area

if __name__ == "__main__":
    print("Starting sample...")
    coords = []
    try:
        with open("sample_coords.txt", "r") as f:
            coord_str = f.readline().strip().split(";")
            coords = map(lambda x: map(float, x.split(",")), coord_str)
    except IOError:
        print("File sample_coords.txt not found.")

    harea = get_hull_area(coords)
    if harea is None:
        print("Invalid hull: Not in a simple hemisphere.")
    else:
        print("Area = %f km^2" % harea)
