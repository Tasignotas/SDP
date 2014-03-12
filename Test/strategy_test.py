import unittest
from planning.models import World
from planning.strategies import AttackerScoreDynamic


class AttackerScoreDynamicTestCase(unittest.TestCase):

    def setUp(self):
        self.world_left = World('left')
        self.strategy_left = AttackerScoreDynamic(self.world_left)
        self.world_right = World('right')
        self.strategy_right = AttackerScoreDynamic(self.world_right)

    def test_strategy_initializes(self):
        self.assertFalse(None, self.strategy_left)

    def test_getting_shooting_coordinates_left(self):
        robot = self.world_left.our_attacker
        x, y = self.strategy_left._get_shooting_coordinates(robot)

        expected_x = int(max(self.world_left.pitch.zones[2][0], key=lambda a: a[0])[0])
        expected_y = self.world_left.pitch.height / 2
        self.assertEqual(expected_x - self.strategy_left.SHOOTING_X_OFFSET, x)
        self.assertEqual(expected_y, y)

    def test_getting_shooting_coordinates_right(self):
        robot = self.world_right.our_attacker
        x, y = self.strategy_right._get_shooting_coordinates(robot)

        expected_x = int(min(self.world_right.pitch.zones[1][0], key=lambda a: a[0])[0])
        expected_y = self.world_right.pitch.height / 2
        self.assertEqual(expected_x + self.strategy_right.SHOOTING_X_OFFSET, x)
        self.assertEqual(expected_y, y)
