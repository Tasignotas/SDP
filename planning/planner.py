from models import *
from collisions import *
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
                if not(our_defender.state in DEFENDER_DEFENCE_STATES):
                    our_defender.state = DEFENDER_DEFENCE_STATES[0]
                return self.defender_defend()
            # We have the ball in our zone, so we attack:
            else:
                if not(our_defender.state in DEFENDER_ATTACK_STATES):
                    our_defender.state = DEFENDER_ATTACK_STATES[0]
                return self.defender_attack()
        else:
            print robot
            print "attackers state", our_attacker.state
            # If ball is not in our defender or attacker zones, defend:
            if self._world.pitch.zones[their_defender.zone].isInside(ball.x, ball.y):
                if not(our_attacker.state in ATTACKER_DEFENCE_STATES):
                    our_attacker.state = ATTACKER_DEFENCE_STATES[0]
                return self.attacker_defend()
            # If it's in the attacker zone, then go grab it:
            elif self._world.pitch.zones[our_attacker.zone].isInside(ball.x, ball.y):
                if not(our_attacker.state in ATTACKER_ATTACK_STATES):
                    our_attacker.state = ATTACKER_ATTACK_STATES[0]
                return self.attacker_attack()
            # 
            else:
                our_attacker.state = ATTACKER_DEFENCE_STATES[0]
                return self.calculate_motor_speed(0, 0)

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
                return self.calculate_motor_speed(displacement, angle)
        if our_defender.state == 'defence_goal_line':
            predicted_y = self.predict_y_intersection(goal_front_x, their_attacker)
            if not (predicted_y == None):
                displacement, angle = our_defender.get_direction_to_point(goal_front_x, predicted_y)
                return self.calculate_motor_speed(displacement, angle, backwards_ok=True)
            return self.calculate_motor_speed(0, 0)

    def defender_attack(self):
        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        ball = self._world.ball
        if our_defender.state == 'attack_go_to_ball':
            # We open our catcher:
            if our_defender.catcher == 'closed':
                our_defender.catcher = 'open'
                return self.open_catcher()
            # If we don't need to move or rotate, we advance to grabbing:
            displacement, angle = our_defender.get_direction_to_point(ball.x, ball.y)
            if our_defender.is_near_ball(ball):
                our_defender.state = 'attack_grab_ball'
            else:
                return self.calculate_motor_speed(displacement, angle, careful=True)
        if our_defender.state == 'attack_grab_ball':
            if our_defender.has_ball(ball):
                our_defender.state = 'attack_rotate_to_pass'
            else:
                our_defender.catcher = 'closed'
                return self.grab_ball()
        if our_defender.state == 'attack_rotate_to_pass':
            if not(our_defender.has_ball(ball)):
                our_defender.state = 'attack_go_to_ball'
                our_defender.catcher = 'open'
                return self.open_catcher()
            else:
                _, angle = our_defender.get_direction_to_point(our_attacker.x, our_attacker.y)
                if self.has_matched(our_defender, angle=angle):
                    our_defender.state = 'attack_pass'
                else:
                    return self.calculate_motor_speed(None, angle, careful=True)
        if our_defender.state == 'attack_pass':
            our_defender.state = 'defence_somewhere'
            our_defender.catcher = 'open'
            return self.kick_ball()
    
    def attacker_defend(self):
        '''
        This function will make our attacker block the path between
        the opposition's defender and our goal
        '''
        their_defender = self._world.their_defender
        our_attacker = self._world.our_attacker
        zone = self._world._pitch._zones[our_attacker.zone]
        min_x,max_x,_,_ = zone.boundingBox()
        border = (min_x + max_x)/2
        predicted_y = self.predict_y_intersection(our_attacker.x, their_defender, True)
        if not (predicted_y == None):
            displacement, angle = our_attacker.get_direction_to_point(border, predicted_y)
            if displacement > 30:
                return self.calculate_motor_speed(displacement, angle, backwards_ok=True)
        return self.calculate_motor_speed(0, 0)

    def attacker_attack(self):
        our_attacker = self._world.our_attacker
        their_goal = self._world.their_goal
        ball = self._world.ball
        if our_attacker.state == 'attack_go_to_ball':
            # We open our catcher:
            if our_attacker.catcher == 'closed':
                our_attacker.catcher = 'open'
                return self.open_catcher()
            # If we don't need to move or rotate, we advance to grabbing:
            displacement, angle = our_attacker.get_direction_to_point(ball.x, ball.y)
            if our_attacker.is_near_ball(ball):
                our_attacker.state = 'attack_grab_ball'
            else:
                return self.calculate_motor_speed(displacement, angle, careful=True)
        if our_attacker.state == 'attack_grab_ball':
            if our_attacker.has_ball(ball):
                our_attacker.state = 'attack_rotate_to_goal'
            else:
                our_attacker.catcher = 'closed'
                return self.grab_ball()
        if our_attacker.state == 'attack_rotate_to_goal':
            if not(our_attacker.has_ball(ball)):
                our_attacker.state = 'attack_go_to_ball'
                our_attacker.catcher = 'open'
                return self.open_catcher()
            else:
                _, angle = our_attacker.get_direction_to_point(their_goal.x, their_goal.y)
                if self.has_matched(our_attacker, angle=angle):
                    our_attacker.state = 'attack_shoot'
                else:
                    return self.calculate_motor_speed(None, angle)
        if our_attacker.state == 'attack_shoot':
            our_attacker.state = 'defence_block'
            our_attacker.catcher = 'open'
            return self.kick_ball()

    def predict_y_intersection(self, predict_for_x, robot, full_width=False):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        Corrects them if it's out of the bottom_y - top_y range.
        Returns None if the robot is facing the wrong direction.
        '''
        x = robot.x
        y = robot.y
        top_y = self._world._pitch.height if full_width else self._world.our_goal.y + (self._world.our_goal.width/2)
        bottom_y = 0 if full_width else self._world.our_goal.y - (self._world.our_goal.width/2)
        angle = robot.angle
        if (robot.x < predict_for_x and not (pi/2 < angle < 3*pi/2)) or (robot.x > predict_for_x and (3*pi/2 > angle > pi/2)):
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

    def predict_pass_intersection(self, robot1, robot2, ourRobot):
        '''
        Predicts the y coordinate required to intercept a pass from robot1 to robot2
        '''
        delta_x = robot2.x - robot1.x
        delta_y = robot2.y - robot1.y
        k = (delta_y * 1.0 / delta_x) if delta_x else 0
        c = robot1.y - k * robot1.x
        return k * ourRobot.x + c

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
        return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : -1, 'speed' : 1000} 

    def kick_ball(self):
        return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 1, 'catcher' : 0, 'speed' : 1000}

    def open_catcher(self):
        return {'left_motor' : 0, 'right_motor' : 0, 'kicker' : 0, 'catcher' : 1, 'speed' : 1000}

    def has_matched(self, robot, x=None, y=None, angle=None):
        dist_matched = True
        angle_matched = True
        if not(x == None and y == None):
            dist_matched = hypot(robot.x - x, robot.y - y) < DISTANCE_MATCH_THRESHOLD
        if not(angle == None):
            angle_matched = abs(angle) < ANGLE_MATCH_THRESHOLD
        return dist_matched and angle_matched 