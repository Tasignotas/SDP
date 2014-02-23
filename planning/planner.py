from models import *
from collisions import *
from math import tan, pi

DISTANCE_REACH_THRESHOLD = 0
ANGLE_REACH_THRESHOLD = 0
DISTANCE_MATCH_THRESHOLD = 0
ANGLE_MATCH_THRESHOLD = 0
MAX_DISPLACEMENT_SPEED = 0
MAX_ANGLE_SPEED = 0



class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)

    def update_world(self, position_dictionary):
        self._world.update_positions(position_dictionary)

    def plan(self, robot='attacker'):
        assert robot in ['attacker', 'defender']
        our_defender = self._world.our_defender
        ball = self._world.ball
        if robot == 'defender':
            # If the ball is in not in our defender zone:
            if not (self._world.pitch.zones[our_defender.zone].isInside(ball.x, ball.y)):
                return self.defend_goal()



        else:
            pass


    def defend_goal(self):
        our_defender = self._world.our_defender
        their_attacker = self._world.their_attacker
        our_goal = self._world.our_goal
        # If the robot is not on the goal line:
        if our_defender.state == 'defence_somewhere':
            # Need to go to the front of the goal line
            goal_front_x = our_goal.x + 30 if self._world._our_side == 'left' else our_goal.x - 30
            if self.has_matched(our_defender, x=goal_front_x, y=our_goal.y):
                our_defender.state = 'defence_goal_line'
            else:
                displacement, angle = our_defender.get_direction_to_point(goal_front_x, our_goal.y)
                return self.calculate_motor_speed(our_defender, displacement, angle, 'reach')
        if our_defender.state == 'defence_goal_line':
            if self.has_reached(our_defender, angle=pi/2):
                our_defender.state = 'defence_aligned'
            else:
                angle = our_defender.get_rotation_to_point(our_defender.x, self._world._pitch.height)
                return self.calculate_motor_speed(our_defender, 0, angle, 'reach')
        if our_defender.state == 'defence_aligned':
            predicted_y = self.predict_y_intersection(our_goal, their_attacker)
            if not (predicted_y == None):
                displacement, angle = our_defender.get_direction_to_point(our_defender.x, predicted_y)
                return self.calculate_motor_speed(our_defender, displacement, 0, 'reach')
            return self.calculate_motor_speed(our_defender, 0, 0, 'reach')
        raise

    def predict_y_intersection(self, goal, robot):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        Corrects them so that it's definitely within the goal
        '''
        x = robot.x
        y = robot.y
        angle = robot.angle
        if robot.zone == 2 and (-pi/2 < angle < pi/2):
            while x < goal.x:
                if not (0 < (y + tan(angle) * (goal.x - x)) < self._world._pitch.height):
                    print 'Bounce!'
                    x += (self.world.pitch.height - y) / tan(angle) if tan(angle) > 0 else (0 - y) / tan(angle)
                    y = self.world.pitch.height if tan(angle) > 0 else 0
                    angle = (-angle) % (2*pi)
                else:
                    predicted_y = (y + tan(angle) * (goal.x - x))
                    break
        elif robot.zone == 1 and (pi/2 < angle < 3*pi/2):
            while x > goal.x:
                if not (0 < (y + tan(angle) * (goal.x - x)) < self.world.pitch.height):
                    print 'Bounce!'
                    x += (self.world.pitch.height - y) / tan(angle) if tan(angle) < 0 else (0 - y) / tan(angle)
                    y = self.world.pitch.height if tan(angle) < 0 else 0
                    angle = (-angle) % (2*pi)
                else:
                    predicted_y = (y + tan(angle) * (goal.x - x))
                    break
        else:
            return None
        if predicted_y > goal.y + (goal.width/2):
            return goal.y + (goal.width/2)
        elif predicted_y < goal.y - (goal.width/2):
            return goal.y - (goal.width/2)
        return predicted_y

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
        if careful:
            pass
        else:
            if angle > ANGLE_MATCH_THRESHOLD:
                speed = (angle/pi) * MAX_ANGLE_SPEED
                return {'left_motor' : -speed, 'right_motor' : speed, 'kicker' : 0}



    def has_matched(self, robot, x=None, y=None, angle=None):
        if not (x == None):
            if abs(robot.x - x) > DISTANCE_MATCH_THRESHOLD:
                return False
        if not (y == None):
            if abs(robot.y - y) > DISTANCE_MATCH_THRESHOLD:
                return False
        if not (angle == None):
            if abs(robot.angle - angle) > ANGLE_MATCH_THRESHOLD:
                return False
        return True

    def has_reached(self, robot, x=None, y=None, angle=None):
        if not (x == None):
            if abs(robot.x - x) > DISTANCE_REACH_THRESHOLD:
                return False
        if not (y == None):
            if abs(robot.y - y) > DISTANCE_REACH_THRESHOLD:
                return False
        if not (angle == None):
            if abs(robot.angle - angle) > ANGLE_REACH_THRESHOLD:
                return False
        return True