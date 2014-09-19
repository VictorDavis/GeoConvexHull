
# bloody dependencies
import math
import random
import string
import os
import numpy as np
import hemisphericity as ht

## uses the Graham Scanning algorithm to find the convex hull of a list of points
## given by *rectangular* coordinates
	
# raw 2D graham scanning algorithm
def scan(points):
	
	n = len(points)
	
	# use the centroid as the origin to calculate angle
	ctr = np.mean(points, axis = 0)

	# calculate the angle from the origin of every point
	angle = []
	for i in range(n):
		# relative to center
		dx = points[i][0] - ctr[0]
		dy = points[i][1] - ctr[1]

		# angle from the center
		th = math.atan2(dy, dx) #[-pi, pi)
		angle.append(th)
	
	# put it all together in a data frame
	# 0 = index
	# 1 = point (x,y)
	# 2 = angle relative to centroid [-pi,pi)
	idx = range(len(points))
	data = zip(idx, points, angle)

	# sort data by angle (counterclockwise, quadrant order)
	data = sorted(data, key = lambda item: item[2])

	# remove interior points
	i = 1
	convex_runs = 0
	while (convex_runs < n):
		mod = len(data)

		curr = data[i]
		forw = data[(i+1) % mod]
		back = data[(i-1) % mod]

		a = forw[1] - curr[1] # a = next - this
		b = curr[1] - back[1] # b = this - last

		cp = np.cross(a,b)
		if (cp > 0):
			data.pop(i)
			convex_runs = 0
		else:
			convex_runs += 1

		mod = len(data)
		i = (i+1) % mod
	
	# return tuple of reordered indices
	return list(zip(*data)[0])
	
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

# pick 100 random points in US
def createInput(n):
	# create blank output file
	f = open(fin, 'w')

	# counter
	cnt = 0
	while (cnt < n):
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

# if input file does not exist, initialize one with 100 random points
if (not os.path.isfile(fin)):
	createInput(100)

def writeKML():
	# open input, KML file
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
	
	# create one yellow pin per input record
	for i in range(n):
		fmt = ["Point", "coordinates", float(lng[i]), float(lat[i])]
		msg = '<{0[0]}><{0[1]}>{0[2]},{0[3]}</{0[1]}></{0[0]}>\n'.format(fmt)
		mykml.write(msg)
	
	# KML end input points yellow
	mykml.write('</MultiGeometry>\n')
	mykml.write('</Placemark>\n')

	# KML polygon convex hull
	mykml.write('<Placemark>\n')
	mykml.write('<styleUrl>#ylwLine</styleUrl>\n')
	mykml.write('<LineString>\n')
	mykml.write('<tessellate>1</tessellate>\n')
	mykml.write('<altitudeMode>clampToGround</altitudeMode>\n')
	mykml.write('<coordinates>\n')
	for pt in hull:
		msg = '{0[0]},{0[1]}\n'.format(pt)
		mykml.write(msg)
			
	# KML rewrite first entry so first = last will complete the loop
	msg = '{0[0]},{0[1]}\n'.format(hull[0])
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

# extract lng/lat into arrays
f = open(fin, 'r')
n = 0
lng = []
lat = []
for line in f:
	coord = string.split(line, " ")
	lng.append( float(coord[0]) )
	lat.append( float(coord[1]) )
	n += 1

# Convert each lng,lat point to <x,y,z> on the unit sphere
pt = []
for i in range(n):
	txyz = toXYZ(lng[i], lat[i])
	pt.append( np.array(txyz) )

# Test that they are in the same hemisphere, if so, give the pole
ht1 = ht.HemisphereTest(pt)
print('Running same hemisphere test...')
ok = ht1.getResult()
if not ok:
	print('...Input points do not lie in the same hemisphere. No convex hull possible.\n')
	exit()
	
print('...Same hemisphere test passed.')
pole = ht1.getCentralPole()

# Project every starting point onto the plane defining the common hemisphere
#    (test) x,y values should be in the unit circle, all z >= 0

# the hemisphere's pole (the plane's normal) measures z
# Call xhat the point where zhat's Great Circle intersects the equator
# y = z cross x
zhat = pole
r = np.linalg.norm(np.array([zhat[0], zhat[1]]))
xhat = np.array([+zhat[1] / r, -zhat[0]/r, 0]) # where
yhat = np.cross(zhat, xhat)

# the above gives mutually perpendicular axes for a coord system
m = np.matrix([xhat, yhat, zhat]) # create coord system as row matrix
m = m.getT() # transpose to get column matrix
m = m.getI() # invert to get transformation matrix (invertible by constr)

# Projecting each point onto the unit disk perpendicular to zhat is equivalent
# to re-expressing each point in the new coordinate system and dropping z
proj = []
for p in pt:
	mp = np.matrix([p]).getT()
	newp = (m * mp).getT() # |(x,y)| <= 1, z > 0
	tproj = np.array([newp[0,0], newp[0,1]])
	proj.append(tproj)
	#print(tproj)

# Run 2D graham scanning algorithm on 2D points projected onto unit disk
idx = scan(proj)
hull = []
for i in idx:
	hull.append([lng[i], lat[i]])

# Create output kml
writeKML()