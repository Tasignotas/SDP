from models import *
from collisions import *
from math import tan, log10
import time


DEFENDER_THRESHOLD = 25
UNALIGNED = True
SPEED_CONST = 10

HAS_BALL = False
NO_ACTION = False

WAIT = False

KICKER_SPEED_CAGE_IN = -63


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)

        self.ball_aligned = False


    def plan(self, position_dictionary, part='attacker'):
        global UNALIGNED
        global HAS_BALL
        global NO_ACTION
        global WAIT

        """
        {'their_attacker': x: 31, y: 159, angle: 0.0, velocity: 1.0
            , 'our_defender': x: 172, y: 63, angle: 4.81205763288, velocity: 1.0
            , 'our_attacker': x: 453, y: 217, angle: 2.0344439358, velocity: 0.0
            , 'ball': x: None, y: None, angle: -1.57079632679, velocity: None
            , 'their_defender': x: None, y: None, angle: None, velocity: None
            }
        """

        self._world.update_positions(position_dictionary)
        our_defender = self._world.get_our_defender()
        our_attacker = self._world.get_our_attacker()
        ball = self._world.get_ball()
        top_goal_y = (self._world._pitch._height - GOAL_WIDTH) / 2
        bottom_goal_y = top_goal_y + GOAL_WIDTH
        distance = abs(ball.get_y() - our_defender.get_y())
        if part == 'defence':
            # print 'Angle difference:', abs(our_defender.get_angle() - pi/2)
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
        else:
            x, y, displacement, theta = our_attacker.get_path_to_point(
                ball.get_x(), ball.get_y())
            print 'DISPLACEMENT', displacement
            print 'NO_ACTION', NO_ACTION
            print 'HAS_BALL', HAS_BALL
            if HAS_BALL and WAIT:
                time.sleep(0.1)
                WAIT = False
            if NO_ACTION:
                return {'attacker' : {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}}


            alignment = our_attacker.get_robot_alignment(ball)

            ALIGN_THRESH = 0.2 * log10(displacement)
            SPEED = 5
            kicker = 0

            if theta < ALIGN_THRESH or theta > 2 * pi - ALIGN_THRESH:
                self.ball_aligned = True
                left, right = -15, -15
            elif theta > ALIGN_THRESH and theta < (2 * pi - ALIGN_THRESH) / 2.0:
                left, right = SPEED, -SPEED
            else:
                left, right = -SPEED, SPEED

            if displacement < 26 and displacement > 20 and (theta < 0.07 or theta > 2 * pi - 0.07) and not HAS_BALL:
                left, right = 0, 0
                kicker = KICKER_SPEED_CAGE_IN
                HAS_BALL = True
                NO_ACTION = True
                WAIT = True

            return {'attacker' : {'left_motor' : left, 'right_motor' : right, 'kicker' : kicker}}



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