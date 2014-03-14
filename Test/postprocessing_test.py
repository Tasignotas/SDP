import unittest
from math import pi, sqrt
from postprocessing.postprocessing import *
from planning.models import *


class TestPostprocessing(unittest.TestCase):

    def setUp(self):
        self.postprocessor = Postprocessing()

    def test_analyze_ball(self):
        '''
        Tests if the ball position, angle and speed is
        analyzed correctly.
        '''
        self.postprocessor._time += 1
        info_dict = {'x': 10, 'y': 10}
        result_vector = self.postprocessor.analyze_ball(info_dict)
        self.assertEqual(result_vector, Vector(10, 10, pi/4, sqrt(200)))
        self.postprocessor._time += 1
        info_dict = {'x': None, 'y': 0}
        result_vector = self.postprocessor.analyze_ball(info_dict)
        self.assertEqual(result_vector, Vector(10, 10, pi/4, sqrt(200)))
        self.postprocessor._time += 1
        info_dict = {'x': None, 'y': None}
        result_vector = self.postprocessor.analyze_ball(info_dict)
        self.assertEqual(result_vector, Vector(10, 10, pi/4, sqrt(200)))
        self.postprocessor._time += 1
        info_dict = {'x': 20, 'y': 0}
        result_vector = self.postprocessor.analyze_ball(info_dict)
        self.assertEqual(result_vector, Vector(20, 0, (7*pi)/4, sqrt(200)/3))

    def test_analyze_robot(self):
        '''
        Tests if the robot positions, speeds and angles
        are analyzed correctly.
        '''
        self.postprocessor._time += 1
        info_dict = {'x': 10, 'y': 10, 'angle': 1}
        result_vector = self.postprocessor.analyze_robot('our_defender', info_dict)
        self.assertEqual(result_vector, Vector(10, 10, 1, sqrt(200)))
        self.postprocessor._time += 1
        info_dict = {'x': None, 'y': 0, 'angle': 2}
        result_vector = self.postprocessor.analyze_robot('our_defender', info_dict)
        self.assertEqual(result_vector, Vector(10, 10, 1, sqrt(200)))
        self.postprocessor._time += 1
        info_dict = {'x': None, 'y': None, 'angle': 2}
        result_vector = self.postprocessor.analyze_robot('our_defender', info_dict)
        self.assertEqual(result_vector, Vector(10, 10, 1, sqrt(200)))
        self.postprocessor._time += 1
        info_dict = {'x': 20, 'y': 0, 'angle': 3.14}
        result_vector = self.postprocessor.analyze_robot('our_defender', info_dict)
        self.assertEqual(result_vector, Vector(20, 0, 3.14, -sqrt(200)/3))
        self.postprocessor._time += 1
        info_dict = {'x': 20, 'y': 0, 'angle': 3.14}
        result_vector = self.postprocessor.analyze_robot('their_defender', info_dict)
        self.assertEqual(result_vector, Vector(20, 0, 3.14, -4))
