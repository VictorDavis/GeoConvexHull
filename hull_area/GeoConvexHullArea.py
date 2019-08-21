
# bloody dependencies
import sys
import math
import random
import string
import os
import numpy as np
#import hemisphericity as ht


from pyproj import Proj
from shapely.geometry import shape










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



















class HemisphereTest:
	# initialize test with list of points
	def __init__(self, points):
		self.points = np.array(points)
		self.test = False
		self.poles = []
	# add pole to list if new
	def addPole(self, pole):
		new = True
		if len(self.poles) > 0:
			new = np.any(np.all(np.array(self.poles) == pole, axis=1))
		"""
		new = True
		for i in xrange(0, len(self.poles)):
			if np.array_equal(pole, self.poles[i]):
				new = False
		"""
		if new:
			self.poles.append(pole)
	# do all the number crunching in one method
	def runTest(self):
		n = len(self.points)
		for i in xrange(0, n):
			#print(i)
			#sys.stdout.flush()
			for j in xrange(0, n):
				#print(i,j)
				#sys.stdout.flush()
				if (i != j):
					# for each pair of points, take the positive and negative normalized cross products
					p = np.cross(self.points[i], self.points[j])
					p = p / np.linalg.norm(p)
					ok1 = True
					ok2 = True
					"""
					for k in range(0, n):
						# if either (or both) of these are less than orthogonal to every other point, it is a pole
						dp = np.dot(self.points[k], p)
						if dp < 0:
							ok1 = False
						if -dp < 0:
							ok2 = False
					"""
					dotres = self.points.dot(p)
					if np.all(dotres > 0): #(ok1):
						self.addPole(p)
					if np.all(dotres < 0): #(ok2):
						self.addPole(-p)
		self.test = True
	def getResult(self):
		if (not self.test): self.runTest()
		if len(self.poles) > 0:
			return True
		else:
			return False
	def getPoles(self):
		if (not self.test): self.runTest()
		return self.poles
	def getCentralPole(self):
		if (self.getResult()):
			p = np.mean(self.poles, axis = 0)
			p = p / np.linalg.norm(p)
			return p
		else:
			return np.array([0,0,0])


def test_Hemisphere(pt):
	# Test that they are in the same hemisphere, if so, give the pole
	ht1 = HemisphereTest(pt)
	#print('Running same hemisphere test...')
	ok = ht1.getResult()
	if not ok:
		#print('...Input points do not lie in the same hemisphere. No convex hull possible.\n')
		#exit()
		return None

	#print('...Same hemisphere test passed.')
	pole = ht1.getCentralPole()
	return pole













DEBUG_FLAG = False
#import datetime

# Input: List of tuples (latitude, longitude)
# Output: Area of convex hull (km^2)
#
def get_hull_area(all_coords):
	"""
	n = 0
	lng = []
	lat = []
	with open(sys.argv[1], 'r') as f:
		for line in f:
			coord = string.split(line, " ")
			lng.append( float(coord[0]) )
			lat.append( float(coord[1]) )
			n += 1
	"""
	#print(datetime.datetime.now().time())
	if DEBUG_FLAG:  #Colorado Test
		all_coords = [
		 (41.0, -102.05),
		 (37.0, -102.05),
		 (40.0, -105.05),
		 (37.0, -109.05),
		 (41.0, -109.05)]
	n = len(all_coords)
	if n == 0: return None
	lat, lng = map(list, zip(*all_coords))

	# Convert each lng,lat point to <x,y,z> on the unit sphere
	pt = []
	for i in range(n):
		txyz = toXYZ(lng[i], lat[i])
		pt.append( np.array(txyz) )
	pole = test_Hemisphere(pt)
	if pole is None: return None
	#print(datetime.datetime.now().time())
	#sys.stdout.flush()


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
	#print(datetime.datetime.now().time())
	#sys.stdout.flush()
	idx = scan(proj)
	#print(datetime.datetime.now().time())
	#sys.stdout.flush()
	hull = []
	hull_lat = []
	hull_lng = []
	for i in idx:
		hull.append([lng[i], lat[i]])
		hull_lat.append(lat[i])
		hull_lng.append(lng[i])
	#for x in hull: print(x)

	"""
	with open("output.txt", 'w') as f:
		for x in hull:
			f.write(str(x)+"\n")
	"""





	# Getting the area
	# http://stackoverflow.com/questions/4681737/
	pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
	x, y = pa(hull_lng, hull_lat)
	cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
	convex_area = shape(cop).area
	#print(datetime.datetime.now().time())

	#print(convex_area)  # 268952044107.43506
	#print(str(int(convex_area/(1000**2))) + " km^2")
	return convex_area/(1000.0**2)









	#
