import unittest
from math import pi, sin, cos, tan, atan, hypot, sqrt
from planning.models import *
from numpy.testing import assert_almost_equal
from Polygon.cPolygon import Polygon


class TestCoordinate(unittest.TestCase):
    '''
    Tests the Coordinate class.
    '''

    def setUp(self):
        pass

    def test_wrong_initialisation(self):
        '''
        This test checks if the Coordinate object can be initialised incorrectly
        '''
        self.assertRaises(ValueError, Coordinate, None, 5)
        self.assertRaises(ValueError, Coordinate, 5, None)
        self.assertRaises(ValueError, Coordinate, None, None)

    def test_wrong_assignment(self):
        '''
        This test checks if the Coordinate object can be assigned a wrong value
        '''
        coord = Coordinate(10, 10)
        self.assertRaises(ValueError, setattr, coord, 'x', None)
        self.assertRaises(ValueError, setattr, coord, 'y', None)


class TestVector(unittest.TestCase):
    '''
    Tests the Vector class.
    Our assumption is that Vector extends Coordinate so we do not retest
    the coordinate attribute initialisation and assignment.
    '''

    def setUp(self):
        pass

    def test_wrong_initialisation(self):
        '''
        This test checks if the Vector object can be initialised incorrectly.
        '''
        #Incorrect angle:
        self.assertRaises(ValueError, Vector, 2, 5, -0.5, 2)
        self.assertRaises(ValueError, Vector, 2, 5, 7, 2)
        self.assertRaises(ValueError, Vector, 2, 5, 2*pi, 3)

    def test_wrong_assignment(self):
        '''
        This test checks if the Vector object can be incorrectly updated.
        '''
        vec = Vector(2, 5, pi, 10)
        #Incorrect angle:
        self.assertRaises(ValueError, setattr, vec, 'angle', -0.5)
        self.assertRaises(ValueError, setattr, vec, 'angle', 10)
        #Incorrect velocity:
        self.assertRaises(ValueError, setattr, vec, 'velocity', -1)

    def test_correct_assignment(self):
        '''
        This test checks if the edge values of speed and angle can be chosen.
        There is no way of checking if something does not raise an error, so
        I'm just using a hack...
        '''
        try:
            vec = Vector(2, 5, 0, 5)
            vec.angle = 0
            vec = Vector(2, 5, 2*pi-0.1, 0)
            vec.speed = 0
        except ValueError:
            #This should raise no errors!
            self.assertTrue(False)

class TestPitchObject(unittest.TestCase):
    '''
    Tests the PitchObject class.
    The tests include the modification of the object and methods
    for getting the polygons that bound the object.
    '''

    def setUp(self):
        pass

    def test_PitchObject_initialisation(self):
        '''
        Checks if width, length and height can't be set as negative.
        Also checks if valid values are accepted.
        '''
        self.assertRaises(ValueError, PitchObject, *(2, 2, 0, 0, -1, 1, 1))
        self.assertRaises(ValueError, PitchObject, *(2, 2, 0, 0, 1, -1, 1))
        self.assertRaises(ValueError, PitchObject, *(2, 2, 0, 0, 1, 1, -1))
        try:
            p = PitchObject(2, 2, 1, 10, 20, 30, 10)
        except ValueError:
            #This should raise no errors!
            self.assertTrue(False)

    def test_PitchObject_modification(self):
        '''
        Checks if vector can't be set to None
        '''
        p = PitchObject(2, 2, 0, 0, 20, 20, 20)
        self.assertRaises(ValueError, setattr, p, 'vector', None)
        try:
            p.vector = Vector(2, 2, 1, 10)
        except ValueError:
            #This should raise no errors!
            self.assertTrue(False)

    def test_generic_polygon(self):
        '''
        Checks if the points returned by the
        generic polygon method are correct
        '''
        angles = ([0, pi/6, pi/4, pi/2, pi/2 + pi/6, pi/2 + pi/4,
                    pi/2 + pi/3, pi, pi + pi/6, pi + pi/4, pi + pi/3,
                    3*pi/2, 3*pi/2 + pi/6, 3*pi/2 + pi/4, 3*pi/2 + pi/3])
        for angle in angles:
            p_object = PitchObject(50, 50, angle, 0, 40, 20, 10)
            poly = Polygon(((60, 70), (60, 30), (40, 70), (40, 30)))
            poly.rotate(angle, 50, 50)
            assert_almost_equal(p_object.get_polygon(), poly[0])


class TestRobot(unittest.TestCase):
    '''
    Tests the Robot class.
    The tests cover the initialisation and gets paths to the ball,
    checks for possession etc.
    '''

    def setUp(self):
        pass

    def test_displacement_and_angle(self):
        '''
        Checks if the displacement and angle by which the robot
        needs to turn to be facing the given point
        '''
        for offset in [0, -pi/2, pi/2]:
            # When robot is at angle 0:
            robot = Robot(0, 50, 50, 0, 0, angle_offset=offset)
            # When there is no displacement and angle:
            assert_almost_equal(robot.get_direction_to_point(50, 50), (0, 0))
            # Only displacement:
            assert_almost_equal(robot.get_direction_to_point(60, 50), (10, 0))
            # Various kinds displacement and positive/negative angles:
            assert_almost_equal(robot.get_direction_to_point(60, 60), (sqrt(200), pi/4))
            assert_almost_equal(robot.get_direction_to_point(60, 40), (sqrt(200), -pi/4))
            assert_almost_equal(robot.get_direction_to_point(50, 60), (10, pi/2))
            assert_almost_equal(robot.get_direction_to_point(50, 40), (10, -pi/2))
            assert_almost_equal(robot.get_direction_to_point(40, 60), (sqrt(200), 3*pi/4))
            assert_almost_equal(robot.get_direction_to_point(40, 40), (sqrt(200), -3*pi/4))
            # When robot is at angle pi/4:
            robot = Robot(0, 50, 50, pi/4, 0, angle_offset=offset)
            assert_almost_equal(robot.get_direction_to_point(50, 50), (0, 0))
            # Only displacement:
            assert_almost_equal(robot.get_direction_to_point(60, 60), (sqrt(200), 0))
            # Various kinds displacement and positive/negative angles:
            assert_almost_equal(robot.get_direction_to_point(50, 60), (10, pi/4))
            assert_almost_equal(robot.get_direction_to_point(60, 50), (10, -pi/4))
            assert_almost_equal(robot.get_direction_to_point(40, 60), (sqrt(200), pi/2))
            assert_almost_equal(robot.get_direction_to_point(60, 40), (sqrt(200), -pi/2))
            assert_almost_equal(robot.get_direction_to_point(40, 50), (10, 3*pi/4))
            assert_almost_equal(robot.get_direction_to_point(50, 40), (10, -3*pi/4))
            # When robot is at angle 3*pi/4:
            robot = Robot(0, 50, 50, 3*pi/4, 0, angle_offset=offset)
            assert_almost_equal(robot.get_direction_to_point(50, 50), (0, 0))
            # Only displacement:
            assert_almost_equal(robot.get_direction_to_point(40, 60), (sqrt(200), 0))
            # Various kinds displacement and positive/negative angles:
            assert_almost_equal(robot.get_direction_to_point(40, 50), (10, pi/4))
            assert_almost_equal(robot.get_direction_to_point(50, 60), (10, -pi/4))
            assert_almost_equal(robot.get_direction_to_point(40, 40), (sqrt(200), pi/2))
            assert_almost_equal(robot.get_direction_to_point(60, 60), (sqrt(200), -pi/2))
            assert_almost_equal(robot.get_direction_to_point(50, 40), (10, 3*pi/4))
            assert_almost_equal(robot.get_direction_to_point(60, 50), (10, -3*pi/4))
            # When robot is at angle 5*pi/4:
            robot = Robot(0, 50, 50, 5*pi/4, 0, angle_offset=offset)
            assert_almost_equal(robot.get_direction_to_point(50, 50), (0, 0))
            # Only displacement:
            assert_almost_equal(robot.get_direction_to_point(40, 40), (sqrt(200), 0))
            # Various kinds displacement and positive/negative angles:
            assert_almost_equal(robot.get_direction_to_point(50, 40), (10, pi/4))
            assert_almost_equal(robot.get_direction_to_point(40, 50), (10, -pi/4))
            assert_almost_equal(robot.get_direction_to_point(60, 40), (sqrt(200), pi/2))
            assert_almost_equal(robot.get_direction_to_point(40, 60), (sqrt(200), -pi/2))
            assert_almost_equal(robot.get_direction_to_point(60, 50), (10, 3*pi/4))
            assert_almost_equal(robot.get_direction_to_point(50, 60), (10, -3*pi/4))
            # When robot is at angle 7*pi/4:
            robot = Robot(0, 50, 50, 7*pi/4, 0, angle_offset=offset)
            assert_almost_equal(robot.get_direction_to_point(50, 50), (0, 0))
            # Only displacement:
            assert_almost_equal(robot.get_direction_to_point(60, 40), (sqrt(200), 0))
            # Various kinds displacement and positive/negative angles:
            assert_almost_equal(robot.get_direction_to_point(60, 50), (10, pi/4))
            assert_almost_equal(robot.get_direction_to_point(50, 40), (10, -pi/4))
            assert_almost_equal(robot.get_direction_to_point(60, 60), (sqrt(200), pi/2))
            assert_almost_equal(robot.get_direction_to_point(40, 40), (sqrt(200), -pi/2))
            assert_almost_equal(robot.get_direction_to_point(50, 60), (10, 3*pi/4))
            assert_almost_equal(robot.get_direction_to_point(40, 50), (10, -3*pi/4))


class TestPitch(unittest.TestCase):
    '''
    Tests the Pitch class
    '''

    def test_Pitch_initialisation(self):
        '''
        Tests if the zones don't overlap
        '''
        pitch = Pitch()
        for zone1 in pitch.zones:
            for zone2 in pitch.zones:
                if not zone1 == zone2:
                    self.assertFalse(zone1.overlaps(zone2))


if __name__ == '__main__':
    unittest.main()
