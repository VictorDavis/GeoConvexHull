
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