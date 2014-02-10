from models import *
from path import find_path


ANGLE_THRESHOLD = 20
DEFENDER_THRESHOLD = 25


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)


    def plan(self, position_dictionary):
        self._world.update_positions(position_dictionary)
        our_defender = self._world.get_our_defender()
        ball = self._world.get_ball()
        top_goal_y = (self._world._pitch._height - GOAL_WIDTH) / 2
        bottom_goal_y = top_goal_y + GOAL_WIDTH
        if (ROBOT_LENGTH/2 + top_goal_y) < ball.get_y() < (ROBOT_LENGTH/2 + bottom_goal_y) : 
            if abs(ball.get_y() - our_defender.get_y()) > DEFENDER_THRESHOLD:
                if ball.get_y() < our_defender.get_y():
                    return {'defender' : {'left_motor' : 60, 'right_motor' : 60, 'kicker' : 0}}
                else:
                    return {'defender' : {'left_motor' : -60, 'right_motor' : -60, 'kicker' : 0}}
        return {'defender' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}

