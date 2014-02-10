from models import World
from path import find_path
from math import log10, tan, radians
from collisions import *


ANGLE_THRESHOLD = 20
DEFENDER_THRESHOLD = 25
SPEED_CONST = 35

class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)


    def plan(self, position_dictionary):

        self._world.update_positions(position_dictionary)
        our_defender = self._world.get_our_defender()

        #### From Rowan's plan ####
        # our_goal = self._world.get_our_goal()
        # their_attacker = self._world.get_their_attacker()
        # their_defender = self._world.get_their_defender()
        # their_goal = self._world.get_their_goal()
        # ball = self._world.get_ball()

        y_intersection = self.predict_y_intersection()
        distance = abs(y_intersection - our_defender.get_y())
        if distance >  DEFENDER_THRESHOLD:
            speed = log10(distance) * SPEED_CONST
            if y_intersection < our_defender.get_y():
                return {'defender' : {'left_motor' : speed, 'right_motor' : speed, 'kicker' : 0}}
            else:
                return {'defender' : {'left_motor' : -speed, 'right_motor' : -speed, 'kicker' : 0}}
        return {'defender' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}

        #### From Rowan's planner ####
        # if our_defender.get_possession(ball):
        #     pass_path = our_defender.get_pass_path(our_attacker)
        #     avoid_plan = get_avoidance(pass_path, our_defender, their_attacker)
        #     if avoid_plan == None:
        #         return (0, 0, 0, our_defender.get_path_alignment(pass_path))
        #     else:
        #         return (avoid_plan)

        # elif our_attacker.get_possession(ball):
        #     shoot_path = our_defender.get_shoot_path(their_goal)
        #     avoid_plan = get_avoidance(shoot_path, our_attacker, their_defender)
        #     if avoid_plan == None:
        #         return (0, 0, 0, our_defender.get_path_alignment(shoot_path))
        #     else:
        #         return (avoid_plan)

        # elif their_defender.get_possession(ball):
        #     pass_path = their_defender.get_pass_path(their_attacker)
        #     intercept_plan = get_interception(pass_path, our_attacker)
        #     return (intercept_plan)

        # elif their_attacker.get_possession(ball):
        #     shoot_path = their_attacker.get_shoot_path(our_goal)
        #     intercept_plan = get_interception(shoot_path, our_defender)
        #     return (intercept_plan)

        # else:
        #     if our_attacker.get_ball_proximity(ball):
        #         our_attacker.get_robot_aligment(ball)
        #     elif our_defender.get_ball_proximity(ball):
        #         our_defender.get_robot_alignment(ball)
        #     elif ball.get_velocity() == 0:
        #         our_attacker.get_stationary_ball(ball)
        #         our_defender.get_stationary_ball(ball)
        #     else:
        #         our_attacker.get_moving_ball(ball)
        #         our_defender.get_moving_ball(ball)

    def predict_y_intersection(self):
        our_zone = self._world._pitch.get_zone(self._world.get_our_defender().get_zone())
        our_x = min([x for (x, y) in our_zone[0]])
        our_top_y = min([y for (x, y) in our_zone[0]])
        our_bottom_y = max([y for (x, y) in our_zone[0]])
        their_angle = self._world.get_their_defender().get_angle()
        their_x = self._world.get_their_defender().get_x()
        their_y = self._world.get_their_defender().get_y()
        print their_x, their_y, their_angle
        print our_top_y
        while their_x < our_x:
            # If the ball is going to bounce off the wall:
            if not (our_top_y < (their_y + tan(radians(their_angle)) * (our_x - their_x)) < our_bottom_y):
                print 'Bounce!'
                their_x += (our_top_y - their_y) / tan(radians(their_angle)) if tan(radians(their_angle)) < 0 else (our_bottom_y - their_y) / tan(radians(their_angle))
                their_y = our_top_y if tan(radians(their_angle)) < 0 else our_bottom_y
                their_angle = -their_angle
                print 'x: ', their_x
                print 'y: ', their_y
                print 'angle: ', their_angle
            else:
                return (their_y + tan(radians(their_angle)) * (our_x - their_x))