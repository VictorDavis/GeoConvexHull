GeoConvexHull
=============

## The Convex Hull Problem

Given n points on a flat Euclidean plane, draw the smallest possible polygon containing all of these points. This is the classic [Convex Hull Problem](http://en.wikipedia.org/wiki/Convex_hull). An intuitive algorithm for solving this problem can be found in [Graham Scanning](http://en.wikipedia.org/wiki/Graham_scan).

## The Spherical Case

There are several problems with extending this to the spherical case:  
- All of the points must be in the same hemisphere for a definition of "polygon" to make sense. No problem, we can just require that of our input.  
- The center of lng/lat points on a map is *not* mean(lng),mean(lat). I've chosen to define "center" by taking the average of every point's x,y,z coordinates and projecting that point back to the surface.  
- The angle of two points relative to a third is *not* atan(dlat/dlng).  
- The cross product calculation of two vectors on the sphere's surface is different.  
- Data has to be normalized when adding/subtracting near the poles and the international dateline.  

## A first iteration

Nonetheless, by taking random points "around" the contiguous US, the Mercator Projection does not skew the data enough to make a significant difference, and Graham Scanning will work if we treat the lng,lat points as sitting inside a flat rectangle ranging from longitude x in [-124,-66], latitude y in [25,50]. Attached is a screenshot showing what you get when you apply this to 100 random points.

## A second iteration

Changed the definition of the "center" of geographic points. Rather than taking the means of longitudes and latitudes, which treats them as y,x in cartesian space respectively, I've taken each lng,lat as a point in 3D space x,y,z. I then take the center of all these points in Euclidean space, which will be some point just under the surface of the earth. Then I project that point back to the surface along a ray from the earth's center. Note that this can be interpreted whether all the points are in the same hemisphere or not; the center of n geographic points is simply some point within the earth that represents their inertial center. For "friendly" US data, the corrected longitude agrees with the uncorrected longitude to the first decimal place and the two latitudes differ by just over a degree.

## Usage

*The only required file is the Python script*. When you run it, it will check for an input.txt. This is where you should put your lng,lat data formatted like the included input.txt. If it does not find it, it will choose 100 points at random to write to an input.txt for you. The script will create an output.kml, which you can open in Google Earth. The KML will contain one marker on every point in your input file and the resulting convex polygon surrounding them.