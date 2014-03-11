from models import *
from collisions import *
from strategies import *
from math import tan, pi, hypot, log

REVERSE = 1
DISTANCE_MATCH_THRESHOLD = 15
ANGLE_MATCH_THRESHOLD = pi/10
BALL_ANGLE_THRESHOLD = pi/20
MAX_DISPLACEMENT_SPEED = 690 * REVERSE
MAX_ANGLE_SPEED = 50 * REVERSE


class Planner:

    def __init__(self, our_side):
        self._world = World(our_side)
        self._world.our_defender.catcher_area = {'width' : 30, 'height' : 10, 'front_offset' : 50}
        self._world.our_attacker.catcher_area = {'width' : 30, 'height' : 10, 'front_offset' : 50}
        self._defender_defence_strat = DefaultDefenderDefence(self._world)
        self._defender_attack_strat = DefaultDefenderAttack(self._world)
        self._attacker_defence_strat = DefaultAttackerDefend(self._world)
        self._attacker_attack_strat = DefaultAttackerAttack(self._world)
        self._defender_state = 'defence'
        self._attacker_state = 'defence'

    @property
    def attacker_state(self):
        return self._attacker_state

    @attacker_state.setter
    def attacker_state(self, new_state):
        assert new_state in ['defence', 'attack']
        self._attacker_state = new_state

    @property
    def defender_state(self):
        return self._defender_state

    @defender_state.setter
    def defender_state(self, new_state):
        assert new_state in ['defence', 'attack']
        self._defender_state = new_state

    def update_world(self, position_dictionary):
        self._world.update_positions(position_dictionary)

    def plan(self, robot='attacker'):
        assert robot in ['attacker', 'defender']
        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        their_defender = self._world.their_defender
        ball = self._world.ball
        if robot == 'defender':
            # If the ball is in not in our defender zone, we defend:
            if not (self._world.pitch.zones[our_defender.zone].isInside(ball.x, ball.y)):
                # If we need to switch from defending to attacking:
                if not self._defender_state == 'defence':
                    self._defender_defence_strat.reset_current_state()
                    self._defender_state = 'defence'
                return self._defender_defence_strat.generate()
            # We have the ball in our zone, so we attack:
            else:
                if not self._defender_state == 'attack':
                    self._defender_attack_strat.reset_current_state()
                    self._defender_state = 'attack'
                return self._defender_attack_strat.generate()
        else:
            # If ball is not in our defender or attacker zones, defend:
            if self._world.pitch.zones[their_defender.zone].isInside(ball.x, ball.y):
                if not self._attacker_state == 'defence':
                    self._attacker_defence_strat.reset_current_state()
                    self._attacker_state = 'defence'
                return self._attacker_defence_strat.generate()
            # If it's in the attacker zone, then go grab it:
            elif self._world.pitch.zones[our_attacker.zone].isInside(ball.x, ball.y):
                if not self._attacker_state == 'attack':
                    self._attacker_attack_strat.reset_current_state()
                    self._attacker_state = 'attack'
                return self._attacker_attack_strat.generate()
            else:
                return self.calculate_motor_speed(0, 0)


    def predict_y_intersection(self, predict_for_x, robot, full_width=False, bounce=False):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        Corrects them if it's out of the bottom_y - top_y range.
        If bounce is set to True, predicts for a bounced shot
        Returns None if the robot is facing the wrong direction.
        '''
        x = robot.x
        y = robot.y
        top_y = self._world._pitch.height if full_width else self._world.our_goal.y + (self._world.our_goal.width/2)
        bottom_y = 0 if full_width else self._world.our_goal.y - (self._world.our_goal.width/2)
        angle = robot.angle
        if (robot.x < predict_for_x and not (pi/2 < angle < 3*pi/2)) or (robot.x > predict_for_x and (3*pi/2 > angle > pi/2)):
            if bounce:
                if not (0 <= (y + tan(angle) * (predict_for_x - x)) <= self._world._pitch.height):
                    bounce_pos = 'top' if (y + tan(angle) * (predict_for_x - x)) > self._world._pitch.height else 'bottom'
                    x += (self._world._pitch.height - y) / tan(angle) if bounce_pos == 'top' else (0 - y) / tan(angle)
                    y = self._world._pitch.height if bounce_pos == 'top' else 0
                    angle = (-angle) % (2*pi)
            predicted_y = (y + tan(angle) * (predict_for_x - x))
            # Correcting the y coordinate to the closest y coordinate on the goal line:
            if predicted_y > top_y:
                return top_y
            elif predicted_y < bottom_y:
                return bottom_y
            return predicted_y
        else:
            return None

    def calculate_motor_speed(self, displacement, angle, backwards_ok=False, careful=False):
        '''
        Simplistic view of calculating the speed: no modes or trying to be careful
        '''
        moving_backwards = False
        general_speed = 95 if careful else 300
        angle_thresh = BALL_ANGLE_THRESHOLD if careful else ANGLE_MATCH_THRESHOLD
        if backwards_ok and abs(angle) > pi/2:
            angle = (-pi + angle) if angle > 0 else (pi + angle)
            moving_backwards = True
        if not (displacement is None):
            if displacement < DISTANCE_MATCH_THRESHOLD:
                return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 0, 'speed' : general_speed}
            elif abs(angle) > angle_thresh:
                speed = (angle/pi) * MAX_ANGLE_SPEED
                return {'left_motor' : -speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0, 'speed' : general_speed}
            else:
                speed = log(displacement, 10) * MAX_DISPLACEMENT_SPEED
                speed = -speed if moving_backwards else speed
                return {'left_motor' : speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0, 'speed' : general_speed}
        else:
            if abs(angle) > angle_thresh:
                speed = (angle/pi) * MAX_ANGLE_SPEED
                return {'left_motor' : -speed, 'right_motor' : speed, 'kicker' : 0, 'catcher' : 0, 'speed' : general_speed}
            else:
                return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 0, 'speed' : general_speed}

    def grab_ball(self):
        return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 1, 'speed' : 1000}

    def kick_ball(self):
        return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 1, 'catcher' : 0, 'speed' : 1000}

    def open_catcher(self):
        return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 1, 'catcher' : 0, 'speed' : 1000}

    def has_matched(self, robot, x=None, y=None, angle=None):
        dist_matched = True
        angle_matched = True
        if not(x == None and y == None):
            dist_matched = hypot(robot.x - x, robot.y - y) < DISTANCE_MATCH_THRESHOLD
        if not(angle == None):
            angle_matched = abs(angle) < ANGLE_MATCH_THRESHOLD
        return dist_matched and angle_matched
