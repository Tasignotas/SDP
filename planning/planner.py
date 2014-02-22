from models import *
from collisions import *
from math import tan, pi
import time


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)

    def update_world(self, position_dictionary):
        self._world.update_positions(position_dictionary)

    def plan(self, position_dictionary, robot='attacker'):
        assert robot in ['attacker', 'defender']
        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        their_defender = self._world.their_defender
        their_attacker = self._world.their_attacker
        ball = self._world.ball
        our_goal = self._world.our_goal
        if robot == 'defender':
            if 'ball is not in the defender zone':
                # If we need to defend the goal:
                return self.defend_goal(our_defender, their_attacker, ball, our_goal)



        else:
            pass


    def defend_goal(our_defender, their_attacker, ball, our_goal):
        # 1. Go to the goal line
        # 2. Align with y axis
        # 3. Predict the intersection point of the ball if the attacker shot and move to that y coordinate
        # If the robot is not on the goal line:
        if not (((our_defender.x - our_goal.x) < THRESH) and
                (our_defender.y < (our_goal.y + our_goal.width/2.0)) and
                (our_defender.y > (our_goal.y - our_goal.width/2.0))):
            displacement, angle = our_defender.get_direction_to_point(our_goal.x, our_goal.y)
            return calculate_motor_speed(displacement, angle, 'reach')
        # If we need to adjust the orientation:
        angle = our_defender.get_rotation_to_point(our_defender.x, 10000)
        if not (abs(angle) < Y_ALIGNMENT_THRESHOLD):
            return angle
        # If we need to go to the predicted point:
        y = self.predict_y_intersection(goal, robot)
        if y == None:
            return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0}
        else:
            # If the predicted point is above the goal line, we still want to defend the top of the goal line:
            if y > our_goal.y + (our_goal.width / 2):
                y = our_goal.y + (our_goal.width / 2)
            elif y < our_goal.y - (our_goal.width / 2):
                y = our_goal.y - (our_goal.width / 2)







    def predict_y_intersection(self, goal, robot):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        '''
        x = robot.x
        y = robot.y
        angle = robot.angle
        if robot.zone == 2 and (-pi/2 < angle < pi/2):
            while x < goal.x:
                if not (0 < (y + tan(angle) * (goal.x - x)) < self._world._pitch.height):
                    print 'Bounce!'
                    x += (self._world._pitch.height - y) / tan(angle) if tan(angle) > 0 else (0 - y) / tan(angle)
                    y = self._world._pitch.height if tan(angle) > 0 else 0
                    angle = (-angle) % (2*pi)
                else:
                    return (y + tan(angle) * (goal.x - x))
        elif robot.zone == 1 and (pi/2 < angle < 3*pi/2):
            while x > goal.x:
                if not (0 < (y + tan(angle) * (goal.x - x)) < self._world._pitch.height):
                    print 'Bounce!'
                    x += (self._world._pitch.height - y) / tan(angle) if tan(angle) < 0 else (0 - y) / tan(angle)
                    y = self._world._pitch.height if tan(angle) < 0 else 0
                    angle = (-angle) % (2*pi)
                else:
                    return (y + tan(angle) * (goal.x - x))
        return None

    def calculate_motor_speed(self, robot, displacement, angle, mode, careful=False):
        '''
        This method calculates the speed by which robot motors should be turned.
        There are two modes: "reach" and "match".
        Sometimes you want to make the robot's center coordinates to *match* your
        desired coordinates. In this case, use the "match" mode.
        In other cases you are ok with the robot just *reaching* some point - making
        some point of your robot very close to some other point. In this case use "reach".
        '''
        assert mode in ['match', 'reach']



    def has_matched(self, robot, x=None, y=None, angle=None):
        pass

    def has_reached(self, robot, x=None, y=None, angle=None):
        pass

    '''
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