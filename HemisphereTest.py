
import math
import numpy as np

class HemisphereTest:
	# initialize test with list of points
	def __init__(self, points):
		self.points = points
		self.test = False
	# add pole to list if new
	def addPole(self, pole):
		new = True
		for i in range(0, len(self.poles)):
			if np.array_equal(pole, self.poles[i]):
				new = False
		if new:
			self.poles.append(pole)
	# do all the number crunching in one method
	def runTest(self):
		self.poles = []
		n = len(self.points)
		for i in range(0, n):
			for j in range(0, n):
				if (i != j):
					# for each pair of points, take the positive and negative normalized cross products
					p = np.cross(self.points[i], self.points[j])
					p = p / np.linalg.norm(p)
					ok1 = True
					ok2 = True
					for k in range(0, n):
						# if either (or both) of these are less than orthogonal to every other point, it is a pole
						dp = np.dot(self.points[k], p)
						if dp < 0:
							ok1 = False
						if -dp < 0:
							ok2 = False
					if (ok1):
						self.addPole(p)
					if (ok2):
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

class HemisphereTestDemo:
	def __init__(self):
		self.demo()
	def lnglat(self, lng, lat):
		theta = lng / 180 * math.pi # [-180,180] -> [-pi, pi]
		phi = ( 90 - lat ) / 180 * math.pi # [+90,-90] -> [0, pi], north pole = 0, equator = 90, south pole = 180
		sinphi = math.sin(phi)
		tx = math.cos(theta) * sinphi
		ty = math.sin(theta) * sinphi
		tz = math.cos(phi)
		return np.array([tx, ty, tz])
	def demo(self):
		pt = []
		
		# three points equally spaced along the equator
		pt.append( self.lnglat(0.0, 0.0) )
		pt.append( self.lnglat(120.0, 0.0) )
		pt.append( self.lnglat(-120.0, 0.0) )
		
		# iceland
		pt.append( self.lnglat(-19.0, 64.0) )

		# these four points ARE all in the northern hemisphere, centered at the north pole,
		# despite their geometric center being slightly offset from the north pole
		positiveTest = HemisphereTest(pt)
		print(positiveTest.getResult())
		print(positiveTest.getCentralPole())
		
		 # south pole
		pt.append( self.lnglat(0.0, -90.0) )
		
		# add in the south pole, and you get a negative result
		negativeTest = HemisphereTest(pt)
		print(negativeTest.getResult())
		print(negativeTest.getCentralPole())