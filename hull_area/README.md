GeoConvexHull
=============

## The Convex Hull Problem

Given n points on a flat Euclidean plane, draw the smallest possible polygon containing all of these points. This is the classic [Convex Hull Problem](http://en.wikipedia.org/wiki/Convex_hull). An intuitive algorithm for solving this problem can be found in [Graham Scanning](http://en.wikipedia.org/wiki/Graham_scan).

## The Spherical Case

There are several problems with extending this to the spherical case:
- All of the points must be in the same hemisphere for a definition of "polygon" to make sense. No problem, we can just require that of our input, run a test, and stop execution if this requirement is violated.
- The center of lng/lat points on a map is *not* mean(lng),mean(lat). A better definition of "center" is had by taking the average of every point's (x,y,z) coordinates and projecting that point back to the surface.
- The angle of two points relative to a third is *not* atan(dlat/dlng).
- The cross product calculation of two vectors on the sphere's surface is different.
- Data has to be normalized when adding/subtracting near the poles and the international dateline.

## The Method

First, we run a Hemisphere Test, included as a separate file because this turns out to be a non-trivial math exercise. Thus it has its uses as a standalone routine for other applications. If all the points lie in the same hemisphere, then a "pole" can be given defining that hemisphere. Geometrically, this pole is a point on the unit sphere normal to the plane defining the hemisphere and containing its Great Circle. For reference, we'll call the flat part of this hemisphere the Great Disc.

Every point on the surface of the Hemisphere (the input) lies on the same side of the plane and can therefore be projected onto this plane as points lying on the Great Disc. Now, the Graham Scanning algorithm can be run on these 2D projections. Since the resulting polygon is just an ordered subset of projected 2D points, the resulting spherical polygon is just the same ordered subset of 3D points.

## Usage

The only required files are Python scripts, although some dependencies are required to find the area:
- GEOS
- pyproj
- shapely
These dependencies can be resolved by running the script:

```
$ sudo ./gch_setup.sh
```

This requires apt-get and is tested for Ubuntu 14.04 LTS.

To use the Python scripts:

```python
>>> from GeoConvexHull import get_hull_area
>>> get_hull_area([(1.0,2.0), (1.0,3.0), (2.0, 2.0)])
6173.664940800096
```

The function `get_hull_area()` takes an input of a list of coordinates, each coordinate being a tuple (latitude, longitude). The output is the area in kilometers squared as a float. If an error occurs (an empty list, coordinates covering more than 1 hemisphere, or any other situation that prevents calculating the hull area), this function will return None.

A sample case is given. To test, run `python sample_run.py`. This should take about 2 minutes to process the 1926 coordinates in `sample_coords.txt` (with a CPU of 2.2 GHz, although only 1 thread is used).
