from models import *
from collisions import *
from math import tan, log10

DEFENDER_THRESHOLD = 25
UNALIGNED = True
SPEED_CONST = 10


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)


    def plan(self, position_dictionary, part='defence'):
        global UNALIGNED
        self._world.update_positions(position_dictionary)
        our_defender = self._world.get_our_defender()
        ball = self._world.get_ball()
        top_goal_y = (self._world._pitch._height - GOAL_WIDTH) / 2
        bottom_goal_y = top_goal_y + GOAL_WIDTH
        distance = abs(ball.get_y() - our_defender.get_y())
        if part == 'defence':
            print 'Angle difference:', abs(our_defender.get_angle() - pi/2)
            if UNALIGNED:
                if abs(our_defender.get_angle() - pi/2) < 0.2:
                    UNALIGNED = False
                    return {'defender' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}
                return {'defender' : {'left_motor' : 5, 'right_motor' : -5, 'kicker' : 0}}
            if (ROBOT_LENGTH/2 + top_goal_y) < ball.get_y() < (ROBOT_LENGTH/2 + bottom_goal_y) :
                if abs(ball.get_y() - our_defender.get_y()) > DEFENDER_THRESHOLD:
                    speed = log10(distance) * SPEED_CONST
                    if ball.get_y() < our_defender.get_y():
                        return {'defender' : {'left_motor' : -speed, 'right_motor' : -speed, 'kicker' : 0}}
                    else:
                        return {'defender' : {'left_motor' : speed, 'right_motor' : speed, 'kicker' : 0}}
            return {'defender' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}
            """

            return {'defender' : {'left_motor' : 10, 'right_motor' : -10, 'kicker' : 0}}
            """
        return {'attacker' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}



    '''
    def predict_y_intersection(self):
        our_zone = self._world._pitch._zones[self._world.get_our_defender().get_zone()]
        our_x = min([x for (x, y) in our_zone[0]]) if self._world.get_our_defender().get_zone() == 3 else max([x for (x, y) in our_zone[0]])
        their_angle = self._world.get_our_attacker().get_angle()
        their_x = self._world.get_our_attacker().get_x()
        their_y = self._world.get_our_attacker().get_y()
        return our_x, their_y + tan(their_angle) * (our_x - their_x)




        if our_defender.get_possession(ball):
            pass_path = our_defender.get_pass_path(our_attacker)
            avoid_plan = get_avoidance(pass_path, our_defender, their_attacker)
            if avoid_plan == None:
                return (0, 0, 0, our_defender.get_path_alignment(pass_path))
            else:
                return (avoid_plan)

        elif our_attacker.get_possession(ball):
            shoot_path = our_defender.get_shoot_path(their_goal)
            avoid_plan = get_avoidance(shoot_path, our_attacker, their_defender)
            if avoid_plan == None:
                return (0, 0, 0, our_defender.get_path_alignment(shoot_path))
            else:
                return (avoid_plan)

        elif their_defender.get_possession(ball):
            pass_path = their_defender.get_pass_path(their_attacker)
            intercept_plan = get_interception(pass_path, our_attacker)
            return (intercept_plan)

        if their_attacker.get_ball_possession(ball):
            print 'Yes!!!'
            shoot_path = their_attacker.get_shoot_path(our_goal)
            for point in shoot_path:
               print point
            raise Exception()
            intercept_plan = get_interception(shoot_path, our_defender)
            return (intercept_plan)
        else:
            print 'NO!!!'
            if our_attacker.get_ball_proximity(ball):
                our_attacker.get_robot_aligment(ball)
            elif our_defender.get_ball_proximity(ball):
                our_defender.get_robot_alignment(ball)

            if ball.get_velocity() < 5:
                print our_attacker.get_stationary_ball(ball)
                #our_defender.get_stationary_ball(ball)
            else:
                our_attacker.get_moving_ball(ball)
                our_defender.get_moving_ball(ball)
            '''