
# bloody dependencies
import math
import random
import string
import os

## uses the Graham Scanning algorithm to find the convex hull of a list of points
## given by *rectangular* coordinates

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
mykml.write('<Placemark>\n')
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
    
## find the center of the data
n = len(lng)

# cartesian center
clng = sum(lng)/n
clat = sum(lat)/n
print('Cartesian Center is {0},{1}'.format(clng, clat))

# correction for curvature of the earth
# refer to http://mathworld.wolfram.com/SphericalCoordinates.html
x = []
y = []
z = []

# 1. convert each lng,lat point to <x,y,z> on the unit sphere
for i in range(n):
    theta = lng[i] / 180 * math.pi # [-180,180] -> [-pi, pi]
    phi = ( 90 - lat[i] ) / 180 * math.pi # [+90,-90] -> [0, pi], north pole = 0, equator = 90, south pole = 180
    sinphi = math.sin(phi)
    
    tx = math.cos(theta) * sinphi
    ty = math.sin(theta) * sinphi
    tz = math.cos(phi)
    
    x.append( tx )
    y.append( ty )
    z.append( tz )
    #print('<{0}, {1}, {2}>\n'.format(tx, ty, tz))

# 2. find the center in 3-space by <mean(x),mean(y),mean(z)>
cx = sum(x) / n
cy = sum(y) / n
cz = sum(z) / n
#print('Centered At <{0}, {1}, {2}>\n'.format(cx, cy, cz))

# 3. project that point back onto the unit sphere in lng,lat
r = math.sqrt(cx*cx + cy*cy + cz*cz)
theta = math.atan2(cy, cx)
phi = math.acos(cz / r)

# curvilinear center
clng = theta / math.pi * 180
clat = 90 - ( phi / math.pi * 180 )
print('Curvilinear Center is {0},{1}'.format(clng, clat))

# calculate the angle & quadrant of each point in polar coordinates
quad = []
angle = []
for i in range(n):
    # relative to center
    alng = lng[i] - clng
    alat = lat[i] - clat
    
    # quadrant ( x = lng, y = lat )
    if ((alng >= 0) & (alat >= 0)):
	q = 1
    if ((alng <  0) & (alat >= 0)):
	q = 2
    if ((alng <  0) & (alat <  0)):
	q = 3
    if ((alng >= 0) & (alat <  0)):
	q = 4
    quad.append(q)
    
    # angle from the origin
    th = math.atan(math.fabs(alat / alng)) # returns positive angle only
    if ((q == 2) | (q == 4)):
	th = math.pi / 2 - th # reverse direction for negative ranges
	
    th = math.pi / 2 * (q - 1) + th
    angle.append(th)
    
# put it all together in a data frame
data = zip(lng, lat, quad, angle)

# sort by 3rd column, angle [0-2pi)
def getKey(item):
    return item[3]

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
    
    dxa = forw[0] - curr[0]
    dya = forw[1] - curr[1]
    dxb = curr[0] - back[0]
    dyb = curr[1] - back[1]
    
    cross_product = dxa * dyb - dxb * dya
    if (cross_product > 0):
	data.pop(i)
	convex_runs = 0
    else:
	convex_runs += 1
    
    mod = len(data)
    i = (i+1) % mod

# KML polygon
mykml.write('<LinearRing>\n')
mykml.write('<coordinates>\n')
for datum in data:
    msg = '{0[0]},{0[1]}\n'.format(datum)
    mykml.write(msg)
    
# KML rewrite first entry so first = last will complete the loop
msg = '{0[0]},{0[1]}\n'.format(data[0])
mykml.write(msg)

# KML footer
mykml.write('</coordinates>\n')
mykml.write('</LinearRing>\n')
mykml.write('</MultiGeometry>\n')
mykml.write('</Placemark>\n')
mykml.write('</kml>\n')

# KML close
mykml.close()