from models import *
from collisions import *
from math import tan, pi, hypot, log
from collections import namedtuple

REVERSE = 1
DISTANCE_MATCH_THRESHOLD = 20
ANGLE_MATCH_THRESHOLD = pi/18
MAX_DISPLACEMENT_SPEED = 690 * REVERSE
MAX_ANGLE_SPEED = 50 * REVERSE

# Differential Normalization
DIFF_NORMALIZE_RATIO = 1000


WheelRatio = namedtuple('WheelRatio', ['left', 'right'])



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
            # If the ball is in not in our defender zone, we defend:
            if not (self._world.pitch.zones[our_defender.zone].isInside(ball.x, ball.y)):
                if not(our_defender.state in DEFENDER_DEFENCE_STATES):
                    our_defender.state = DEFENDER_DEFENCE_STATES[0]
                return self.defender_defend()
            # We have the ball in our zone, so we attack
            else:
                if not(our_defender.state in DEFENDER_ATTACK_STATES):
                    our_defender.state = DEFENDER_ATTACK_STATES[0]
                return self.defender_attack()
        else:
            pass


    def defender_defend(self):
        our_defender = self._world.our_defender
        their_attacker = self._world.their_attacker
        our_goal = self._world.our_goal
        goal_front_x = our_goal.x + 35 if self._world._our_side == 'left' else our_goal.x - 35
        # If the robot is not on the goal line:
        if our_defender.state == 'defence_somewhere':
            # Need to go to the front of the goal line
            if self.has_matched(our_defender, x=goal_front_x, y=our_goal.y):
                our_defender.state = 'defence_goal_line'
            else:
                displacement, angle = our_defender.get_direction_to_point(goal_front_x, our_goal.y)
                return self.calculate_motor_speed(our_defender, displacement, angle)
        if our_defender.state == 'defence_goal_line':
            predicted_y = self.predict_y_intersection(our_goal, their_attacker)
            print 'PREDICTED Y', predicted_y
            if not (predicted_y == None):
                displacement, angle = our_defender.get_direction_to_point(goal_front_x, predicted_y)
                return self.calculate_motor_speed(our_defender, displacement, angle, backwards_ok=True)
            return self.calculate_motor_speed(our_defender, 0, 0)

    def defender_attack(self):
        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        ball = self._world.ball
        if our_defender.state == 'attack_go_to_ball':
            # If we don't need to move or rotate, we advance to grabbing:
            displacement, angle = our_defender.get_direction_to_point(our_attacker.x, our_attacker.y)
            if self.has_matched(our_defender, x=ball.x, y=ball.y, angle=angle):
                our_defender = 'attack_grab_ball'
            else:
                return self.calculate_motor_speed(our_defender, displacement, angle)
        if our_defender.state == 'attack_grab_ball':
            our_defender.state = 'attack_rotate_to_pass'
            return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 30}
        if our_defender.state == 'attack_rotate_to_pass':
            _, angle = our_defender.get_direction_to_point(our_attacker.x, our_attacker.y)
            if self.has_matched(our_defender, angle=angle):
                our_defender.state = 'attack_pass'
            else:
                return self.calculate_motor_speed(our_defender, None, angle)
        if our_defender.state == 'attack_pass':
            return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 30, 'catcher' : -30}

    def predict_y_intersection(self, goal, robot):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        Corrects them so that it's definitely within the goal
        '''
        x = robot.x
        y = robot.y
        max_iter = 10
        angle = robot.angle

        if (robot.zone == 2 and not (pi/2 < angle < 3*pi/2)) or (robot.zone == 1 and (3*pi/2 > angle > pi/2)):
            while True and max_iter > 0:
                if not (0 <= (y + tan(angle) * (goal.x - x)) <= self._world._pitch.height):
                    bounce_pos = 'top' if (y + tan(angle) * (goal.x - x)) > self._world._pitch.height else 'bottom'
                    x += (self._world._pitch.height - y) / tan(angle) if bounce_pos == 'top' else (0 - y) / tan(angle)
                    y = self._world._pitch.height if bounce_pos == 'top' else 0
                    angle = (-angle) % (2*pi)
                    max_iter -= 1
                else:
                    predicted_y = (y + tan(angle) * (goal.x - x))
                    break
            if max_iter == 0:
                return None
            # Correcting the y coordinate to the closest y coordinate on the goal line:
            if predicted_y > goal.y + (goal.width/2):
                return goal.y + (goal.width/2)
            elif predicted_y < goal.y - (goal.width/2):
                return goal.y - (goal.width/2)
            return predicted_y
        else:
            return None

    def calculate_motor_speed(self, robot, displacement, angle, backwards_ok=False, differential=False):
        '''
        Simplistic view of calculating the speed: no modes or trying to be careful
        '''
        moving_backwards = False
        if backwards_ok and abs(angle) > pi/2:
            angle = (-pi + angle) if angle > 0 else (pi + angle)
            moving_backwards = True

        left_ratio, right_ratio = None, None
        if differential:
            left_ratio, right_ratio = self.calculate_motor_differential(angle)

        if not (displacement is None):
            if displacement < DISTANCE_MATCH_THRESHOLD:
                return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 0, 'left_ratio': left_ratio, 'right_ratio': left_ratio}
            elif abs(angle) > ANGLE_MATCH_THRESHOLD:
                speed = (angle/pi) * MAX_ANGLE_SPEED
                return {'left_motor' : -speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0, 'left_ratio': left_ratio, 'right_ratio': right_ratio}
            else:
                speed = log(displacement, 10) * MAX_DISPLACEMENT_SPEED
                speed = -speed if moving_backwards else speed
                return {'left_motor' : speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0, 'left_ratio': left_ratio, 'right_ratio': right_ratio}
        else:
            if abs(angle) > ANGLE_MATCH_THRESHOLD:
                speed = (angle/pi) * MAX_ANGLE_SPEED
                return {'left_motor' : -speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0, 'left_ratio': left_ratio, 'right_ratio': right_ratio}
            else:
                return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 0, 'left_ratio': left_ratio, 'right_ratio': right_ratio}

    def calculate_motor_differential(
            self, angle_delta, match_thresh=ANGLE_MATCH_THRESHOLD):
        """
        Take the THRESHOLD log of the angle difference to get ratio of left to right wheel.

        If we want to turn left, right motor turns faster and vice versa.
        """
        if angle_delta == 0:
            return WheelRatio(DIFF_NORMALIZE_RATIO, DIFF_NORMALIZE_RATIO)

        ratio_const = log(abs(angle_delta), match_thresh)

        print 'ratio_const', ratio_const

        if ratio_const <= 1:
            return WheelRatio(DIFF_NORMALIZE_RATIO , DIFF_NORMALIZE_RATIO)

        # Normalize
        ratio = int(1 / ratio_const * DIFF_NORMALIZE_RATIO)

        # Positive angle means turn left, negative - turn right
        if angle_delta > 0:
            return WheelRatio(DIFF_NORMALIZE_RATIO - ratio, ratio)
        else:
            return WheelRatio(ratio, DIFF_NORMALIZE_RATIO - ratio)



    def has_matched(self, robot, x=None, y=None, angle=None):
        dist_matched = True
        angle_matched = True
        if not(x == None and y == None):
            dist_matched = hypot(robot.x - x, robot.y - y) < DISTANCE_MATCH_THRESHOLD
        if not(angle == None):
            angle_matched = abs(angle) < ANGLE_MATCH_THRESHOLD
        return dist_matched and angle_matched
