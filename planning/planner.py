from models import *
from collisions import *
from math import tan, pi, hypot, log

REVERSE = 1
DISTANCE_MATCH_THRESHOLD = 20
ANGLE_MATCH_THRESHOLD = pi/18
MAX_DISPLACEMENT_SPEED = 690 * REVERSE
MAX_ANGLE_SPEED = 50 * REVERSE



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
        their_defender = self._world.their_defender
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

    def calculate_motor_speed(self, robot, displacement, angle, backwards_ok=False):
        '''
        Simplistic view of calculating the speed: no modes or trying to be careful
        '''
        moving_backwards = False
        if backwards_ok and abs(angle) > pi/2:
            angle = (-pi + angle) if angle > 0 else (pi + angle)
            moving_backwards = True
        if displacement < DISTANCE_MATCH_THRESHOLD:
            return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 0}
        elif abs(angle) > ANGLE_MATCH_THRESHOLD:
            speed = (angle/pi) * MAX_ANGLE_SPEED
            return {'left_motor' : -speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0}
        else:
            speed = log(displacement, 10) * MAX_DISPLACEMENT_SPEED
            speed = -speed if moving_backwards else speed
            return {'left_motor' : speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0}

    def has_matched(self, robot, x, y):
        return hypot(robot.x - x, robot.y - y) < DISTANCE_MATCH_THRESHOLD