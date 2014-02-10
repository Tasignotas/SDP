from models import World
from path import find_path
from math import log10, tan, radians


ANGLE_THRESHOLD = 20
DEFENDER_THRESHOLD = 25
SPEED_CONST = 35


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)


    def plan(self, position_dictionary):
        self._world.update_positions(position_dictionary)
        our_defender = self._world.get_our_defender()
        y_intersection = self.predict_y_intersection()
        distance = abs(y_intersection - our_defender.get_y())
        if distance >  DEFENDER_THRESHOLD:
            speed = log10(distance) * SPEED_CONST
            if y_intersection < our_defender.get_y():
                return {'defender' : {'left_motor' : speed, 'right_motor' : speed, 'kicker' : 0}}
            else:
                return {'defender' : {'left_motor' : -speed, 'right_motor' : -speed, 'kicker' : 0}}
        return {'defender' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}


    def predict_y_intersection(self):
        our_zone = self._world._pitch._zones[self._world.get_our_defender().get_zone()]
        our_x = min([x for (x, y) in our_zone[0]]) if self._world.get_our_defender().get_zone() == 3 else max([x for (x, y) in our_zone[0]])
        their_angle = self._world.get_their_defender().get_angle()
        their_x = self._world.get_their_defender().get_x()
        their_y = self._world.get_their_defender().get_y()
        return (their_y + tan(radians(their_angle)) * abs(our_x - their_x))




