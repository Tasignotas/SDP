from models import *


class Planner:

    def __init__(self, our_color, our_side):
        self.world = World(our_color, our_side)

    def update_and_plan(self, position_dict):
        self.world.update_positions(position_dict)
        return self.plan()

    def plan(self):
        """
        Given the robots and the ball, find the most appropriate action.

        Returns:
            [2-tuple of 3-tuples] defense robot action, attack robot action consisting of values to execute on robot motors
        """
        return ((0,0,0), (0,0,0))
