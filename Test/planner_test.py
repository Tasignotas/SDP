import unittest
from planning.models import Vector
from planning.planner import *
from numpy.testing import assert_almost_equal
from math import *


class TestYPredictionLeft(unittest.TestCase):

    def setUp(self):
        self.planner = Planner('left')
        self.our_goal = self.planner._world.our_goal
        self.their_attacker = self.planner._world.their_attacker
        self.pitch = self.planner._world._pitch

    def test_straight_shot(self):
        # Shot to the center:
        self.their_attacker.vector = Vector(200, self.our_goal.y, pi, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.our_goal.y)
        # Shot to the bottom:
        goal_top = self.our_goal.y - (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(200, goal_top, pi, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_top)

    def test_straight_corrected_shot(self):
        # Shot above the top:
        goal_top = self.our_goal.y + (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(200, goal_top + 20, pi, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_top)
        # Shot below the bottom:
        goal_bottom = self.our_goal.y - (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(200, goal_bottom - 20, pi, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_bottom)

    def test_angle_shot(self):
        # Shot above the center:
        self.their_attacker.vector = Vector(50, self.our_goal.y, (3*pi)/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.our_goal.y + 50)
        # Shot below the center:
        self.their_attacker.vector = Vector(50, self.our_goal.y, (5*pi)/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.our_goal.y - 50)

    def test_bounce_shot(self):
        # Shot bounced of the top:
        self.their_attacker.vector = Vector(self.pitch.height, self.pitch.height/2.0, (3*pi)/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.pitch.height/2.0)
        # Shot bounced of the bottom:
        self.their_attacker.vector = Vector(self.pitch.height, self.pitch.height/2.0, (5*pi)/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.pitch.height/2.0)
        # Shot bounced of the top that needs to be corrected:
        goal_top = self.our_goal.y + (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(self.pitch.height/2.0, self.pitch.height/2.0, (13*pi)/16, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_top)

    def test_no_intersection(self):
        self.their_attacker.vector = Vector(self.pitch.height, self.pitch.height/2.0, pi/4, 0)
        self.assertEqual(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), None)


class TestYPredictionRight(unittest.TestCase):

    def setUp(self):
        self.planner = Planner('right')
        self.our_goal = self.planner._world.our_goal
        self.their_attacker = self.planner._world.their_attacker
        self.pitch = self.planner._world._pitch

    def test_straight_shot(self):
        # Shot to the center:
        self.their_attacker.vector = Vector(400, self.our_goal.y, 0, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.our_goal.y)
        # Shot to the bottom:
        goal_top = self.our_goal.y - (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(400, goal_top, 0, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_top)

    def test_straight_corrected_shot(self):
        # Shot above the top:
        goal_top = self.our_goal.y + (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(200, goal_top + 20, 0, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_top)
        # Shot below the bottom:
        goal_bottom = self.our_goal.y - (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(200, goal_bottom - 20, 0, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_bottom)

    def test_angle_shot(self):
        # Shot above the center:
        self.their_attacker.vector = Vector(self.pitch.width - 50, self.our_goal.y, pi/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.our_goal.y + 50)
        # Shot below the center:
        self.their_attacker.vector = Vector(self.pitch.width - 50, self.our_goal.y, (7*pi)/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.our_goal.y - 50)

    def test_bounce_shot(self):
        # Shot bounced of the top:
        self.their_attacker.vector = Vector(self.pitch.width - self.pitch.height, self.pitch.height/2.0, pi/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.pitch.height/2.0)
        # Shot bounced of the bottom:
        self.their_attacker.vector = Vector(self.pitch.width - self.pitch.height, self.pitch.height/2.0, (7*pi)/4, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), self.pitch.height/2.0)
        # Shot bounced of the top that needs to be corrected:
        goal_top = self.our_goal.y + (self.our_goal.width/2.0)
        self.their_attacker.vector = Vector(self.pitch.width - (self.pitch.height/2.0), self.pitch.height/2.0, (3*pi)/16, 0)
        assert_almost_equal(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), goal_top)

    def test_no_intersection(self):
        self.their_attacker.vector = Vector(self.pitch.height, self.pitch.height/2.0, (3*pi)/4, 0)
        self.assertEqual(self.planner.predict_y_intersection(self.our_goal, self.their_attacker), None)


class MotorDifferentialTest(unittest.TestCase):

    def setUp(self):
        self.planner = Planner('right')
        self.motor_diff = self.planner.calculate_motor_differential

    def test_angle_zero(self):
        angle = 0
        self.assertEqual((DIFF_NORMALIZE_RATIO, DIFF_NORMALIZE_RATIO), self.motor_diff(angle))

    def test_angle_positive(self):
        angle = pi / 2
        ratio = self.motor_diff(angle, pi / 4)
        right_motor_ratio = ratio[1]
        self.assertTrue(right_motor_ratio > 1)

    def test_angle_negative(self):
        angle = -pi / 2
        ratio = self.motor_diff(angle, pi / 4)
        right_motor_ratio = ratio[0]
        self.assertTrue(right_motor_ratio > 1)

    def test_ratio_complete(self):
        angle = -pi / 16
        ratio = self.motor_diff(angle, pi / 8)
        total = ratio[0] + ratio[1]
        self.assertEqual(DIFF_NORMALIZE_RATIO, total)

    def test_ratio_is_one_when_angle_matched(self):
        angle = pi / 4
        ratio = self.motor_diff(angle, pi / 4)
        self.assertEqual(DIFF_NORMALIZE_RATIO , ratio[1])
        self.assertEqual(DIFF_NORMALIZE_RATIO, ratio[0])

    def test_ratio_actual_value(self):
        angle = pi / 18
        ratio = self.motor_diff(angle, pi / 16)
        expected_ratio = int(1 / log(angle, pi / 16) * DIFF_NORMALIZE_RATIO)
        self.assertEqual(DIFF_NORMALIZE_RATIO - expected_ratio, ratio[0])
        self.assertEqual(expected_ratio, ratio[1])
