import math
import numpy as np
import unittest
import GeoConvexHull as hull

class Test(unittest.TestCase):
	def test_graham(self):
		pt = []
		x = [-0.11, -0.15,  0.05,  0.00, -0.60, -0.86,  0.13, -0.06,  0.56,  0.19,  0.90, -0.56, -0.25, -0.55,  0.41,  0.12, -0.22,  0.36, 0.28, -0.34]
		y = [ 0.38, -0.72, -0.32, -0.67,  0.39,  0.45,  0.66, -0.19,  0.06, -0.92,  0.19, -0.78,  0.37,  0.15, -0.67,  0.35,  0.92, -0.90, 0.35, -0.38]
		for i in range(len(x)):
			pt.append(np.array([x[i], y[i]]))

		# these four points ARE all in the northern hemisphere, centered at the north pole,
		# despite their geometric center being slightly offset from the north pole
		results = [11, 9, 17, 10, 16, 5]
		self.assertEqual(hull.scan(pt), results)
