import unittest
from planning.models import World, Robot
from planning.strategies import *
import math
from planning import utilities


class StrategyTestCase(unittest.TestCase):

    def place_robot(self, world, position, robot):
        world._robots[position] = robot

    def get_aimed_robot(self, x, y, angle_x, angle_y, zone):
        """
        Return a new Robot object pointing to x, y
        """
        robot = Robot(zone, x, y, 0, 0)
        theta = robot.get_rotation_to_point(angle_x, angle_y)
        theta = theta if theta > 0 else 2 * math.pi + theta
        return Robot(zone, robot.x, robot.y, theta, robot.velocity)



class AttackerScoreDynamicTestCase(StrategyTestCase):

    def setUp(self):
        self.world_left = World('left')
        self.strategy_left = AttackerScoreDynamic(self.world_left)
        self.world_right = World('right')
        self.strategy_right = AttackerScoreDynamic(self.world_right)

    def test_strategy_initializes(self):
        self.assertFalse(None, self.strategy_left)

    # Test getting the position to which we need to move before we start confusing them

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

    # Test finding corners of the goal.

    def test_get_goal_corner_y_UP(self):
        y = self.strategy_left._get_goal_corner_y(self.strategy_left.UP)
        expected_y = self.world_left.their_goal.y + self.world_left.their_goal.width
        self.assertEqual(expected_y, y)

    def test_get_goal_corner_y_DOWN(self):
        y = self.strategy_left._get_goal_corner_y(self.strategy_left.DOWN)
        expected_y = self.world_left.their_goal.y
        self.assertEqual(expected_y, y)

    # Test selecting which side to confuse to

    def test_get_fake_shoot_side_DOWN(self):
        robot = Robot(3, self.world_left.pitch.width, 50, 0, 0)
        side = self.strategy_left._get_fake_shoot_side(robot)
        expected_side = self.strategy_left.DOWN
        self.assertEqual(expected_side, side)

    def test_get_fake_shoot_side_UP(self):
        robot = Robot(3, self.world_left.pitch.width, self.world_left.pitch.height, 0, 0)
        side = self.strategy_left._get_fake_shoot_side(robot)
        expected_side = self.strategy_left.UP
        self.assertEqual(expected_side, side)

    def test_get_fake_shoot_side_middle(self):
        middle = self.world_left.pitch.width / 2
        robot = Robot(3, self.world_left.pitch.width, middle, 0, 0)
        side = self.strategy_left._get_fake_shoot_side(robot)
        expected_side = self.strategy_left.UP
        self.assertEqual(expected_side, side)

    # Test getting the other side to aim to in CONFUSE 2

    def test_getting_other_side_up(self):
        side = self.strategy_left._get_other_side(self.strategy_left.UP)
        expected_side = self.strategy_left.DOWN
        self.assertEqual(expected_side, side)

    def test_getting_other_side_down(self):
        side = self.strategy_left._get_other_side(self.strategy_left.DOWN)
        expected_side = self.strategy_left.UP
        self.assertEqual(expected_side, side)

    # Test states

    def test_initially_moving_to_middle(self):
        zone = self.world_left.pitch.zones[2][0]

        target_x, target_y = self.strategy_left._get_shooting_coordinates(
            self.world_left.our_attacker)

        for x, y in zone:
            robot = self.get_aimed_robot(
                x, y, target_x, target_y, self.world_left.our_attacker.zone)
            world = World('left')
            self.place_robot(world, world.our_attacker.zone, robot)

            strategy = AttackerScoreDynamic(world)

            actions = strategy.generate()
            left_motor = actions['left_motor']
            right_motor = actions['right_motor']

            # Both left motor and right motor should be positive or negative.
            self.assertEqual(True, left_motor * right_motor > 0)

    def test_reach_middle(self):
        target_x, target_y = self.strategy_left._get_shooting_coordinates(
            self.world_left.our_attacker)

        robot = self.get_aimed_robot(
            target_x, target_y, target_x - 1, target_y - 1, self.world_left.our_attacker.zone)

        self.place_robot(self.world_left, self.world_left.our_attacker.zone, robot)

        strategy = AttackerScoreDynamic(self.world_left)

        actions = strategy.generate()

        self.assertEqual(strategy.POSITION, strategy.current_state)

    def test_reach_middle_within_threshold(self):
        target_x, target_y = self.strategy_left._get_shooting_coordinates(
            self.world_left.our_attacker)

        robot = self.get_aimed_robot(
            target_x - utilities.DISTANCE_MATCH_THRESHOLD + 1, target_y, 0, 0,
            self.world_left.our_attacker.zone)

        self.place_robot(self.world_left, self.world_left.our_attacker.zone, robot)

        strategy = AttackerScoreDynamic(self.world_left)
        actions = strategy.generate()
        self.assertEqual(strategy.POSITION, strategy.current_state)

    def test_progress_to_target(self):
        """
        Approach the target in steps of 10 and verify that the state changes.
        """
        target_x, target_y = self.strategy_left._get_shooting_coordinates(
            self.world_left.our_attacker)

        expected_iterations = math.ceil(target_x / 10.0)
        max_iterations = 60

        for x in range(max_iterations):
            robot = self.get_aimed_robot(
                x * 10, target_y + 1, target_x, target_y, self.world_left.our_attacker.zone)

            self.place_robot(self.world_left, self.world_left.our_attacker.zone, robot)

            strategy = AttackerScoreDynamic(self.world_left)
            actions = strategy.generate()

            if strategy.current_state == strategy.POSITION:
                break

        self.assertEqual(expected_iterations, x)

    def test_confuse1_rotation_up(self):
        target_x, target_y = self.strategy_left.shooting_pos

        aim_x = self.world_left.their_goal.x
        aim_y = self.world_left.their_goal.y + self.world_left.their_goal.height / 2 + self.strategy_left.GOAL_CORNER_OFFSET

        attacker = self.get_aimed_robot(
            target_x, target_y, aim_x, aim_y,
            self.world_left.our_attacker.zone)

        defender = self.get_aimed_robot(
            self.world_left.their_goal.x, self.world_left.their_goal.y,
            aim_x, aim_y, self.world_left.their_defender.zone)

        world = World('left')
        self.place_robot(world, attacker.zone, attacker)
        self.place_robot(world, defender.zone, defender)

        strategy = AttackerScoreDynamic(world)

        actions = strategy.generate()
        self.assertTrue(actions['left_motor'] < 0)
        self.assertTrue(actions['right_motor'] > 0)


class DefaultDefenderDefenceTestCase(StrategyTestCase):

    def setUp(self):
        self.world_left = World('left')
        self.strategy_left = DefaultDefenderDefence(self.world_left)

    def test_initializes_properly(self):
        self.assertFalse(self.strategy_left is None)

    def test_default_action_generated(self):
        actions = self.strategy_left.generate()
        self.assertFalse(actions is None)

    def test_defend_goal_action_generated(self):
        strategy = DefaultDefenderDefence(self.world_left)
        strategy.current_state = strategy.ALIGNED

        actions = strategy.generate()
        self.assertFalse(actions is None)


