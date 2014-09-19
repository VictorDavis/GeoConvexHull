
import math
import numpy as np
import unittest
from hemisphericity import HemisphereTest

def lnglat(lng, lat):
	theta = lng / 180 * math.pi # [-180,180] -> [-pi, pi]
	phi = ( 90 - lat ) / 180 * math.pi # [+90,-90] -> [0, pi], north pole = 0, equator = 90, south pole = 180
	sinphi = math.sin(phi)
	tx = math.cos(theta) * sinphi
	ty = math.sin(theta) * sinphi
	tz = math.cos(phi)
	return np.array([tx, ty, tz])

class Test(unittest.TestCase):
	def test_true(self):
		pt = []
		
		# three points equally spaced along the equator
		pt.append( lnglat(0.0, 0.0) )
		pt.append( lnglat(120.0, 0.0) )
		pt.append( lnglat(-120.0, 0.0) )
		
		# iceland
		pt.append( lnglat(-19.0, 64.0) )

		# these four points ARE all in the northern hemisphere, centered at the north pole,
		# despite their geometric center being slightly offset from the north pole
		positiveTest = HemisphereTest(pt)
		self.assertEqual(positiveTest.getResult(), True)
	
	def test_false(self):
		pt = []
		
		# three points equally spaced along the equator
		pt.append( lnglat(0.0, 0.0) )
		pt.append( lnglat(120.0, 0.0) )
		pt.append( lnglat(-120.0, 0.0) )
		
		 # south pole
		pt.append( lnglat(0.0, -90.0) )
		
		# add in the south pole, and you get a negative result
		negativeTest = HemisphereTest(pt)
		self.assertEqual(negativeTest.getResult(), False)