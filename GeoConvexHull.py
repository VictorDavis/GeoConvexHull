
# bloody dependencies
import math
import random
import string
import os
import numpy as np
import HemisphereTest as ht

## uses the Graham Scanning algorithm to find the convex hull of a list of points
## given by *rectangular* coordinates

# convert point (x,y,z) to (lng,lat)
def toLngLat(p):
	r = np.linalg.norm(p)
	theta = math.atan2(p[1], p[0]) # y / x
	phi = math.acos(p[2] / r) # z / r
	tlng = theta / math.pi * 180
	tlat = 90 - ( phi / math.pi * 180 )
	return [tlng, tlat]

def toXYZ(lng, lat):
	theta = lng / 180 * math.pi # [-180,180] -> [-pi, pi]
	phi = ( 90 - lat ) / 180 * math.pi # [+90,-90] -> [0, pi], north pole = 0, equator = 90, south pole = 180
	sinphi = math.sin(phi)  
	tx = math.cos(theta) * sinphi
	ty = math.sin(theta) * sinphi
	tz = math.cos(phi)
	return [tx, ty, tz]

# input/output files
fin = 'input.txt'
fout = 'output.kml'

# if input file does not exist, initialize one with 100 random points
if (not os.path.isfile(fin)):
	# create blank output file
	f = open(fin, 'w')

	# counter
	cnt = 0
	cntto = 100
	while (cnt < cntto):
		## pick random point on sphere, and keep only those around contiguous U.S.
		## see Sphere Picking guidelines here: http://mathworld.wolfram.com/SpherePointPicking.html

		# pick the seed random values in [0,1)x[0,1)
		u = random.random()
		v = random.random()

		# convert to spherical coordinates
		theta = 2 * math.pi * u # range [0,2pi)
		phi = math.acos(2 * v - 1) # range (0, pi]

		# convert to lng,lat
		lng = theta / (2 * math.pi) * 360 - 180
		lat =   phi / (2 * math.pi) * 360 -  90

		# only keep points inside loosely defined "contiguous united states"
		if ((lng < -124) | (lng > -66)):
			continue
		if ((lat <   25) | (lat >  50)):
			continue

		# display result
		coord = {'lng': lng, 'lat': lat}
		msg = '{lng} {lat}\n'.format(**coord)
		f.write(msg)
		cnt = cnt + 1

	f.close()

# open input, KML file
f = open(fin, 'r')
mykml = open(fout, 'w')

# KML header
mykml.write('<kml>\n')
mykml.write('<Document>\n')
mykml.write('<Style id="ylwPlacemark">\n<IconStyle>\n<Icon>\n<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>\n</Icon>\n</IconStyle>\n</Style>\n')
mykml.write('<Style id="redPlacemark">\n<IconStyle>\n<Icon>\n<href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>\n</Icon>\n</IconStyle>\n</Style>\n')
mykml.write('<Style id="ylwLine">\n<LineStyle>\n<color>ff00ffff</color>\n<width>3</width>\n</LineStyle>\n</Style>\n')

# KML input points yellow
mykml.write('<Placemark>\n')
mykml.write('<styleUrl>#ylwPlacemark</styleUrl>\n')
mykml.write('<MultiGeometry>\n')

# extract lng/lat into arrays
lng = []
lat = []
for line in f:
	coord = string.split(line, " ")
	lng.append( float(coord[0]) )
	lat.append( float(coord[1]) )
    
	# go ahead and create placemark file while you're at it
	fmt = ["Point", "coordinates", coord[0], float(coord[1])]
	msg = '<{0[0]}><{0[1]}>{0[2]},{0[3]}</{0[1]}></{0[0]}>\n'.format(fmt)
	mykml.write(msg)
	
# KML end input points yellow
mykml.write('</MultiGeometry>\n')
mykml.write('</Placemark>\n')
    
## find the center of the data
n = len(lng)

# cartesian center
clng = sum(lng)/n
clat = sum(lat)/n
print('Cartesian Center is {0},{1}'.format(clng, clat))

# correction for curvature of the earth
# refer to http://mathworld.wolfram.com/SphericalCoordinates.html
pt = []

# 1. convert each lng,lat point to <x,y,z> on the unit sphere
for i in range(n):
	txyz = toXYZ(lng[i], lat[i])
	pt.append( np.array(txyz) )

# 2. test that they are in the same hemisphere, if so,
#    then find the pole of a viable hemisphere
ht1 = ht.HemisphereTest(pt)
print('Running same hemisphere test...')
ok = ht1.getResult()
if not ok:
	print('...Input points do not lie in the same hemisphere. No convex hull possible.\n')
	exit()
	
print('...Same hemisphere test passed.')
pole = ht1.getCentralPole()

# 2. find the center in 3-space by <mean(x),mean(y),mean(z)>
ctr = np.mean(pt, axis = 0)
print('Centered At {0}'.format(ctr))

# 3. project that point back onto the unit sphere in lng,lat

# curvilinear center
ctrll = toLngLat(ctr)
clng = ctrll[0]
clat = ctrll[1]
print('Curvilinear Center is {0},{1}'.format(clng, clat))

# hemisphere center
hemictr = toLngLat(pole)
clng = hemictr[0]
clat = hemictr[1]
print('Hemispheric Center is {0},{1}'.format(clng, clat))

# 4. project every starting point onto the plane defining the common hemisphere
#    (test) x,y values should be in the unit circle, all z >= 0

# the hemisphere's pole (the plane's normal) measures z
zhat = pole

# this is where the plane intersects the equator, let it be x
r = np.linalg.norm(np.array([zhat[0], zhat[1]]))
xhat = np.array([+zhat[1] / r, -zhat[0]/r, 0]) # where

# y = z cross x
yhat = np.cross(zhat, xhat)

# the above gives mutually perpendicular axes for a coord system
m = np.matrix([xhat, yhat, zhat]) # create coord system as row matrix
m = m.getT() # transpose to get column matrix
m = m.getI() # invert to get transformation matrix (invertible by constr)

# expressing each point in the new coords is equiv to projecting them
# onto the plane (as xy) and ignoring z
proj = []
for p in pt:
	mp = np.matrix([p]).getT()
	newp = (m * mp).getT() # |(x,y)| <= 1, z > 0
	tproj = np.array([newp[0,0], newp[0,1]])
	proj.append(tproj)
	print(tproj)

# 5. calculate the angle & quadrant of each projection in polar coordinates

# center of the points (should be close to 0,0)
cproj = np.mean(proj, axis = 0)
print('Projections centered at {0}.'.format(cproj))

quad = []
angle = []
for i in range(n):
	# relative to center
	dx = proj[i][0] - cproj[0]
	dy = proj[i][1] - cproj[1]
    
	## quadrant
	#if ((dx >= 0) & (dy >= 0)): q = 1
	#if ((dx <  0) & (dy >= 0)): q = 2
	#if ((dx <  0) & (dy <  0)): q = 3
	#if ((dx >= 0) & (dy <  0)): q = 4
	#quad.append(q)
    
	# angle from the center
	th = math.atan2(dy, dx)
	angle.append(th)
    
# put it all together in a data frame
# 0 = projected point
# 1 = projected angle relative to projected center
# 2 = original point in 3d
# 3 = original longitude
# 4 = original latitude
data = zip(proj, angle, pt, lng, lat)

# sort by 3rd column, angle [0-2pi)
def getKey(item):
	return item[1] # angle

# sort data by quadrant, angle to sort counterclockwise
data = sorted(data, key = getKey)

# remove interior points
i = 1
convex_runs = 0
while (convex_runs < n):
	mod = len(data)

	curr = data[i]
	forw = data[(i+1) % mod]
	back = data[(i-1) % mod]

	a = forw[0] - curr[0] # a = next - this (projected)
	b = curr[0] - back[0] # b = this - last (projected)

	cp = np.cross(a,b)
	if (cp > 0):
		data.pop(i)
		convex_runs = 0
	else:
		convex_runs += 1

	mod = len(data)
	i = (i+1) % mod

# KML polygon convex hull
mykml.write('<Placemark>\n')
mykml.write('<styleUrl>#ylwLine</styleUrl>\n')
mykml.write('<LineString>\n')
mykml.write('<tessellate>1</tessellate>\n')
mykml.write('<altitudeMode>clampToGround</altitudeMode>\n')
mykml.write('<coordinates>\n')
for datum in data:
	msg = '{0[3]},{0[4]}\n'.format(datum)
	mykml.write(msg)
    
# KML rewrite first entry so first = last will complete the loop
msg = '{0[3]},{0[4]}\n'.format(data[0])
mykml.write(msg)

# KML footer
mykml.write('</coordinates>\n')
mykml.write('</LineString>\n')
mykml.write('</Placemark>\n')

## KML write hemispheric poles as red pins
#mykml.write('<Placemark>\n')
#mykml.write('<styleUrl>#redPlacemark</styleUrl>\n')
#mykml.write('<MultiGeometry>\n')
#poles = ht1.getPoles()
#for p in poles:
#	ll = toLngLat(p)
#	fmt = ["Point", "coordinates", ll[0], float(ll[1])]
#	msg = '<{0[0]}><{0[1]}>{0[2]},{0[3]}</{0[1]}></{0[0]}>\n'.format(fmt)
#	mykml.write(msg)
#mykml.write('</MultiGeometry>\n')
#mykml.write('</Placemark>\n')

mykml.write('</Document>\n')
mykml.write('</kml>\n')

# KML close
mykml.close()