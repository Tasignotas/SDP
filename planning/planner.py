from models import World
from path import find_path
from math import log10


ANGLE_THRESHOLD = 20
DEFENDER_THRESHOLD = 25
SPEED_CONST = 35


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)


    def plan(self, position_dictionary):
        self._world.update_positions(position_dictionary)
        our_defender = self._world.get_our_defender()
        ball = self._world.get_ball()
        distance = abs(ball.get_y() - our_defender.get_y())
        if distance >  DEFENDER_THRESHOLD:
            speed = log10(distance) * SPEED_CONST
            if ball.get_y() < our_defender.get_y(): 
                return {'defender' : {'left_motor' : speed, 'right_motor' : speed, 'kicker' : 0}}
            else:
                return {'defender' : {'left_motor' : -speed, 'right_motor' : -speed, 'kicker' : 0}}
        return {'defender' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}


    def predict_y_intersection(self):
        our_zone = self._world.get_our_defender().get_zone()
        our_x = min([x for (x, y) in our_zone[0]])
        our_top_y = min([y for (x, y) in our_zone[0]])
        our_bottom_y = max([y for (x, y) in our_zone[0]])
        their_angle = self._world.get_their_defender().get_angle()
        their_x = self._world.get_their_defender().get_x()
        their_y = self._world.get_their_defender().get_y()
        while their_x < our_x:
            # If the ball is going to bounce off the wall:
            if not (our_top_y < (their_y + tan(their_angle) * our_x) < our_bottom_y):
                their_x = (our_top_y - their_x) / tan(their_angle) if tan(their_angle) < 0 else (our_bottom_y - their_x) / tan(their_angle)
                their_y = our_top_y if tan(their_angle) < 0 else our_bottom_y
                their_angle = -their_angle
            else:
                return (their_y + tan(their_angle) * our_x)                




