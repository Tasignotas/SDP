from utilities import *
import math
from random import randint

class Strategy(object):

    PRECISE_BALL_ANGLE_THRESHOLD = math.pi / 15.0
    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world, states):
        self.world = world
        self.states = states
        self._current_state = states[0]

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        assert new_state in self.states
        self._current_state = new_state

    def reset_current_state(self):
        self.current_state = self.states[0]

    def is_last_state(self):
        return self._current_state == self.states[-1]

    def generate(self):
        return self.NEXT_ACTION_MAP[self.current_state]()

class DefenderPenalty(Strategy):


    DEFEND_GOAL = 'DEFEND_GOAL'
    STATES = [DEFEND_GOAL]
    LEFT, RIGHT = 'left', 'right'
    SIDES = [LEFT, RIGHT]


    def __init__(self, world):
        super(DefenderPenalty, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.DEFEND_GOAL: self.defend_goal
        }

        self.their_attacker = self.world.their_attacker
        self.our_defender = self.world.our_defender
        self.ball = self.world.ball


    def defend_goal(self):
        """
        Run around, blocking shots.
        """
        # Predict where they are aiming.
        if self.ball.velocity > BALL_VELOCITY:
            predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.ball, bounce=False)

        if self.ball.velocity <= BALL_VELOCITY or predicted_y is None: 
            predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.their_attacker, bounce=False)

        if predicted_y is not None:
            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x,
                                                                           predicted_y - 7*math.sin(self.our_defender.angle))
            return calculate_motor_speed(displacement, angle, backwards_ok=True)
        else:
            y = self.ball.y
            y = max([y, 60])
            y = min([y, self.world._pitch.height - 60])
            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True)


class DefenderDefence(Strategy):

    UNALIGNED, DEFEND_GOAL = 'UNALIGNED', 'DEFEND_GOAL'
    STATES = [UNALIGNED, DEFEND_GOAL]
    LEFT, RIGHT = 'left', 'right'
    SIDES = [LEFT, RIGHT]

    GOAL_ALIGN_OFFSET = 60

    def __init__(self, world):
        super(DefenderDefence, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.UNALIGNED: self.align,
            self.DEFEND_GOAL: self.defend_goal
        }

        self.our_goal = self.world.our_goal
        # Find the point we want to align to.
        self.goal_front_x = self.get_alignment_position(self.world._our_side)
        self.their_attacker = self.world.their_attacker
        self.our_defender = self.world.our_defender
        self.ball = self.world.ball

    def align(self):
        """
        Align yourself with the center of our goal.
        """
        if has_matched(self.our_defender, x=self.goal_front_x, y=self.our_goal.y):
            # We're there. Advance the states and formulate next action.
            self.current_state = self.DEFEND_GOAL
            return do_nothing()
        else:
            displacement, angle = self.our_defender.get_direction_to_point(
                self.goal_front_x, self.our_goal.y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True)

    def defend_goal(self):
        """
        Run around, blocking shots.
        """
        # Predict where they are aiming.
        if self.ball.velocity > BALL_VELOCITY:
            predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.ball, bounce=False)

        if self.ball.velocity <= BALL_VELOCITY or predicted_y is None: 
            predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.their_attacker, bounce=False)

        if predicted_y is not None:
            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x,
                                                                           predicted_y - 7*math.sin(self.our_defender.angle))
            return calculate_motor_speed(displacement, angle, backwards_ok=True)
        else:
            y = self.ball.y
            y = max([y, 60])
            y = min([y, self.world._pitch.height - 60])
            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True)

    def get_alignment_position(self, side):
        """
        Given the side, find the x coordinate of where we need to align to initially.
        """
        assert side in self.SIDES
        if side == self.LEFT:
            return self.world.our_goal.x + self.GOAL_ALIGN_OFFSET
        else:
            return self.world.our_goal.x - self.GOAL_ALIGN_OFFSET


class AttackerDefend(Strategy):

    UNALIGNED, BLOCK_PASS = 'UNALIGNED', 'BLOCK_PASS'
    STATES = [UNALIGNED, BLOCK_PASS]

    def __init__(self, world):
        super(AttackerDefend, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.UNALIGNED: self.align,
            self.BLOCK_PASS: self.block_pass
        }

        zone = self.world._pitch._zones[self.world.our_attacker.zone]
        min_x, max_x, min_y, max_y  = zone.boundingBox()
        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2
        self.our_attacker = self.world.our_attacker
        self.our_defender = self.world.our_defender
        self.their_attacker = self.world.their_attacker
        self.their_defender = self.world.their_defender

    def align(self):
        """
        Align yourself with the middle of our zone.
        """
        if has_matched(self.our_attacker, x=self.center_x, y=self.our_attacker.y):
            # We're there. Advance the states and formulate next action.
            self.current_state = self.BLOCK_PASS
            return do_nothing()
        else:
            displacement, angle = self.our_attacker.get_direction_to_point(
                self.center_x, self.our_attacker.y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True)

    def block_pass(self):
        predicted_y = predict_y_intersection(self.world, self.our_attacker.x, self.their_defender, full_width=True, bounce=True)
        if predicted_y is None:
            ideal_x = self.our_attacker.x
            ideal_y = (self.their_attacker.y + self.their_defender.y) / 2
        else:
            ideal_x = self.our_attacker.x
            ideal_y = predicted_y - 7  *math.sin(self.our_attacker.angle)

        displacement, angle = self.our_attacker.get_direction_to_point(ideal_x, ideal_y)
        if not has_matched(self.our_attacker, ideal_x, ideal_y):
            return calculate_motor_speed(displacement, angle, backwards_ok=True)
        else:
            return do_nothing()


class AttackerCatch(Strategy):

    PREPARE, CATCH = 'PREPARE', 'CATCH'
    STATES = [PREPARE, CATCH]

    def __init__(self, world):
        super(AttackerCatchStrategy, self).__init__(world, STATES)

        self.NEXT_ACTION_MAP = {
            self.PREPARE: self.prepare,
            self.CATCH: self.catch
        }

        self.our_attacker = self.world.our_attacker
        self.ball = self.world.ball

    def prepare(self):
        self.current_state = self.CATCH
        if self.our_attacker.catcher == 'closed':
            self.our_attacker.catcher = 'open'
            return open_catcher()
        else:
            return do_nothing()

    def catch(self):
        ideal_x = self.our_attacker.x
        ideal_y = self.ball.y

        displacement, angle = self.our_attacker.get_direction_to_point(ideal_x, ideal_y)
        return calculate_motor_speed(displacement, angle, backwards_ok=True)


class AttackerPositionCatch(Strategy):
    '''
    This catching strategy positions the robot in the middle of the zone
    so that (ideally) it does not need to do anything
    '''
    PREPARE, ALIGN, ROTATE = 'PREPARE', 'ALIGN', 'ROTATE'
    STATES = [PREPARE, ALIGN, ROTATE]

    def __init__(self, world):
        super(AttackerPositionCatch, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.PREPARE: self.prepare,
            self.ALIGN: self.align,
            self.ROTATE: self.rotate
        }

        self.our_attacker = self.world.our_attacker
        self.our_defender = self.world.our_defender
        self.ball = self.world.ball
        zone = self.world._pitch._zones[self.our_attacker.zone]
        min_x, max_x, min_y, max_y  = zone.boundingBox()
        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2

    def prepare(self):
        self.current_state = self.ALIGN
        if self.our_attacker.catcher == 'closed':
            self.our_attacker.catcher = 'open'
            return open_catcher()
        else:
            return do_nothing()

    def align(self):
        if has_matched(self.our_attacker, x=self.center_x, y=self.center_y):
            self.current_state = self.ROTATE
            return do_nothing()
        else:
            displacement, angle = self.our_attacker.get_direction_to_point(
                self.center_x, self.center_y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True)

    def rotate(self):
        '''
        Rotate in the center of the zone in order to intercept the pass of the defender.
        Tries to match the correct angle given the angle of the defender.
        '''
        defender_angle = self.our_defender.angle
        attacker_angle = None
        our_side = self.world._our_side
        if our_side == 'left':
            if defender_angle > 0 and defender_angle < pi / 2:
                attacker_angle = 3 * pi / 4
            elif defender_angle > 3 * pi / 2:
                attacker_angle = 5 * pi / 4
        else:
            if defender_angle > pi / 2 and defender_angle < pi:
                attacker_angle = pi / 4
            elif defender_angle > pi and defender_angle < 3 * pi / 2:
                attacker_angle = 7 * pi / 4

        if attacker_angle:
            # Offsets the attacker's position in the direction of the desired angled in order to calculate the
            # required rotation.
            displacement, angle = self.our_attacker.get_direction_to_point(self.our_attacker.x + 10 * math.cos(attacker_angle),
                                                                           self.our_attacker.y + 10 * math.sin(attacker_angle))
            return calculate_motor_speed(None, angle, careful=True)
        
        return do_nothing()


class DefenderBouncePass(Strategy):
    '''
    Once the defender grabs the ball, move to the center of the zone and shoot towards
    the wall of the center of the opposite attacker zone, in order to reach our_attacker
    attacker zone.
    '''

    POSITION, ROTATE, SHOOT, FINISHED = 'POSITION', 'ROTATE', 'SHOOT', 'FINISHED'
    STATES = [POSITION, ROTATE, SHOOT, FINISHED]

    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world):
        super(DefenderBouncePass, self).__init__(world, self.STATES)

        # Map states into functions
        self.NEXT_ACTION_MAP = {
            self.POSITION: self.position,
            self.ROTATE: self.rotate,
            self.SHOOT: self.shoot,
            self.FINISHED: do_nothing
        }

        self.our_defender = self.world.our_defender
        self.their_attacker = self.world.their_attacker
        self.ball = self.world.ball

        # Choose a random side to bounce off
        self.point = randint(0,1)

        # Find the position to shoot from and cache it
        self.shooting_pos = self._get_shooting_coordinates(self.our_defender)

        # Maximum number of turns
        self.laps_left = 4

    def position(self):
        """
        Position the robot in the middle close to the goal. Angle does not matter.
        Executed initially when we've grabbed the ball and want to move.
        """
        ideal_x, ideal_y = self.shooting_pos
        distance, angle = self.our_defender.get_direction_to_point(ideal_x, ideal_y)

        if has_matched(self.our_defender, x=ideal_x, y=ideal_y):
            self.current_state = self.ROTATE
            return do_nothing()
        else:
            return calculate_motor_speed(distance, angle, careful=True)

    def rotate(self):
        """
        Once the robot is in position, rotate to one side or the other in order
        to bounce the ball into the attacker zone. If one side is blocked by their
        attacker, turn 90 degrees and shoot to the other side.
        """
        bounce_points = self._get_bounce_points(self.our_defender)
        x, y = bounce_points[self.point][0], bounce_points[self.point][1]
        angle = self.our_defender.get_rotation_to_point(x, y)

        if has_matched(self.our_defender, angle=angle, angle_threshold=pi/20):
            # if not is_shot_blocked(self.world, self.our_defender, self.world.their_attacker) or \
            their_attacker_side = self._get_robot_side(self.their_attacker)
            if (self.point == 0 and their_attacker_side == self.UP) or \
               (self.point == 1 and their_attacker_side == self.DOWN):
                self.current_state = self.SHOOT
                return do_nothing()
            else:
                # self.point = 1 - self.point
                # self.laps_left -= 1
                # x, y = bounce_points[self.point][0], bounce_points[self.point][1]
                # angle = self.our_defender.get_rotation_to_point(x, y)
                if self.world._our_side == 'right':
                    orientation = 1 if self.point == 1 else -1
                else:
                    orientation = 1 if self.point == 0 else -1
                self.current_state = self.FINISHED
                print 'orientation', orientation
                return turn_shoot(orientation)
        else:
            return calculate_motor_speed(None, angle, careful=True)

    def shoot(self):
        """
        Kick.
        """
        self.current_state = self.FINISHED
        self.our_defender.catcher = 'open'
        return kick_ball()

    def _get_shooting_coordinates(self, robot):
        """
        Retrive the coordinates to which we need to move before we set up the pass.
        """
        zone_index = robot.zone
        zone_poly = self.world.pitch.zones[zone_index][0]

        min_x = int(min(zone_poly, key=lambda z: z[0])[0])
        max_x = int(max(zone_poly, key=lambda z: z[0])[0])

        x = min_x + (max_x - min_x) / 2
        y =  self.world.pitch.height / 2

        return (x, y)

    def _get_robot_side(self, robot):
        height = self.world.pitch.height
        print '###########', height, robot.y
        if robot.y > height/2:
            return self.UP
        else:
            return self.DOWN


    def _get_bounce_points(self, robot):
        """
        Get the points in the opponent's attacker zone where our defender needs to shoot
        in order to bounce the ball to our attacker zone.
        """
        attacker_zone = {0:1, 3:2}
        zone_index = attacker_zone[robot.zone]
        zone_poly = self.world.pitch.zones[zone_index][0]

        min_x = int(min(zone_poly, key=lambda z: z[0])[0])
        max_x = int(max(zone_poly, key=lambda z: z[0])[0])
        bounce_x = min_x + (max_x - min_x) / 2

        min_y = int(min(zone_poly, key=lambda z: z[1])[1])
        max_y = int(max(zone_poly, key=lambda z: z[1])[1])

        return [(bounce_x, min_y), (bounce_x, max_y)]


class AttackerGrab(Strategy):

    PREPARE, GO_TO_BALL, GRAB_BALL, GRABBED = 'PREPARE', 'GO_TO_BALL', 'GRAB_BALL', 'GRABBED'
    STATES = [PREPARE, GO_TO_BALL, GRAB_BALL, GRABBED]

    def __init__(self, world):
        super(AttackerGrab, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.PREPARE: self.prepare,
            self.GO_TO_BALL: self.position,
            self.GRAB_BALL: self.grab,
            self.GRABBED: do_nothing
        }

        self.our_attacker = self.world.our_attacker
        self.ball = self.world.ball

    def prepare(self):
        self.current_state = self.GO_TO_BALL
        if self.our_attacker.catcher == 'closed':
            self.our_attacker.catcher = 'open'
            return open_catcher()
        else:
            return do_nothing()

    def position(self):
        displacement, angle = self.our_attacker.get_direction_to_point(self.ball.x, self.ball.y)
        if self.our_attacker.can_catch_ball(self.ball):
            self.current_state = self.GRAB_BALL
            return do_nothing()
        else:
            return calculate_motor_speed(displacement, angle, careful=True)

    def grab(self):
        if self.our_attacker.has_ball(self.ball):
            self.current_state = self.GRABBED
            return do_nothing()
        else:
            self.our_attacker.catcher = 'closed'
            return grab_ball()


class DefenderGrab(Strategy):

    DEFEND, GO_TO_BALL, GRAB_BALL, GRABBED = 'DEFEND', 'GO_TO_BALL', 'GRAB_BALL', 'GRABBED'
    STATES = [DEFEND, GO_TO_BALL, GRAB_BALL, GRABBED]

    def __init__(self, world):
        super(DefenderGrab, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.DEFEND: self.defend,
            self.GO_TO_BALL: self.position,
            self.GRAB_BALL: self.grab,
            self.GRABBED: do_nothing
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball

    def defend(self):
        '''
        If the ball is heading towards our goal at high velocity then don't go directly into
        grabbing mode once the ball enters our zone. Try to match it's y-coordinate as fast as possible.
        '''
        if self.ball.velocity > BALL_VELOCITY:
            predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.ball, bounce=True)

            if predicted_y is not None:
                displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x,
                                                                               predicted_y - 7*math.sin(self.our_defender.angle))
                return calculate_motor_speed(displacement, angle, backwards_ok=True)
        
        self.current_state = self.GO_TO_BALL
        return do_nothing()

    def position(self):
        displacement, angle = self.our_defender.get_direction_to_point(self.ball.x, self.ball.y)
        if self.our_defender.can_catch_ball(self.ball):
            self.current_state = self.GRAB_BALL
            return do_nothing()
        else:
            return calculate_motor_speed(displacement, angle, careful=True)

    def grab(self):
        if self.our_defender.has_ball(self.ball):
            self.current_state = self.GRABBED
            return do_nothing()
        else:
            self.our_defender.catcher = 'closed'
            return grab_ball()


class AttackerScoreDynamic(Strategy):
    """
    Goal scoring tactic. Assumes it will be executed when the robot has grabbed the ball.

    Outline:
        1) Position the robot closer to the border line.
        2) Move to aim into one corner of the goal.
        3) Re-rotate and aim into the other corner
        4) Shoot

    Effectivness:
        * Only effective if their attacker is not standing on the white line
          close to us. They need to be at least 40px (the side facing us) from
          the division line between defender and attacker.
        * If opponent's grabber is extended we may not get any leavway for scoring.
          This assumes that they effectively predict direction and optimize for
          maximum blocking area.

    Maths:
        * When the opponent is defending ideally, we have about 15 degrees leaveway to
          score
        * Each ~5 pixels away from the ideal position we lose 2 degrees
            - Imprecision of 15px results in highly unprobable score in CONFUSE1.
            - Probability of scoring increases in CONFUSE2
        * Size of their grabber in extended position is not factored in

    TODO:
        * Finish implementing
        * After CONFUSE1, check if we have a clear shot at the goal and shoot
            - Defender's velocity should be taken into consideration
                - if velocity high, we are better off pulling off the CONFUSE2 part
                - if low, best to try to shoot as opponent's vision/delay may not pickup the trick
        * Attempt to pick sides based on their robot velocity as well
        * Contigency
            - If both CONFUSE1 and CONFUSE2 fail, we may switch strategies or resort to a shot
              either UP or DOWN, based on their position.
    """
    GRABBED, POSITION = 'GRABBED', 'POSITION'
    CONFUSE1, CONFUSE2, SHOOT = 'CONFUSE1', 'CONFUSE2', 'SHOOT'
    STATES = [GRABBED, POSITION, CONFUSE1, CONFUSE2, SHOOT]

    UP, DOWN = 'UP', 'DOWN'
    GOAL_SIDES = [UP, DOWN]

    SHOOTING_X_OFFSET = 85
    GOAL_CORNER_OFFSET = 55

    def __init__(self, world):
        super(AttackerScoreDynamic, self).__init__(world, self.STATES)
        # Map states into functions
        self.NEXT_ACTION_MAP = {
            self.GRABBED: self.position,
            self.POSITION: self.confuse_one,
            self.CONFUSE1: self.confuse_two,
            self.CONFUSE2: self.shoot,
            self.SHOOT: self.shoot
        }

        self.our_attacker = self.world.our_attacker
        self.their_defender = self.world.their_defender

        # Find the position to shoot from and cache it
        self.shooting_pos = self._get_shooting_coordinates(self.our_attacker)

        # Remember which side we picked first
        self.fake_shoot_side = None

    def generate(self):
        """
        Pick an action based on current state.
        """
        print 'BALL', self.world.ball
        return self.NEXT_ACTION_MAP[self.current_state]()

    def position(self):
        """
        Position the robot in the middle close to the goal. Angle does not matter.
        Executed initially when we've grabbed the ball and want to move.
        """
        ideal_x, ideal_y = self.shooting_pos
        distance, angle = self.our_attacker.get_direction_to_point(ideal_x, ideal_y)

        if has_matched(self.our_attacker, x=ideal_x, y=ideal_y):
            # We've reached the POSITION state.
            self.current_state = self.POSITION
            return self.confuse_one()

        # We still need to drive
        return calculate_motor_speed(distance, angle)

    def confuse_one(self):
        """
        Pick a side and aim at it. Executed when we've reached the POSITION state.
        """
        # Initialize fake shoot side if not available
        if self.fake_shoot_side is None:
            self.fake_shoot_side = self._get_fake_shoot_side(self.their_defender)

        target_x = self.world.their_goal.x
        target_y = self._get_goal_corner_y(self.fake_shoot_side)

        print 'SIDE:', self.fake_shoot_side

        print 'TARGET_Y', target_y
        print 'STATE:', self.current_state

        distance, angle = self.our_attacker.get_direction_to_point(target_x, target_y)

        print 'DIRECTION TO POINT', distance, angle

        if has_matched(self.our_attacker, angle=angle):
            # TODO: Shoot if we have a clear shot and the oppononet's velocity is favourable for us
            y = self.their_defender.y
            middle = self.world.pitch.height / 2

            opp_robot_side = self._get_fake_shoot_side(self.their_defender)
            if opp_robot_side != self.fake_shoot_side:
                # We've finished CONFUSE1
                self.current_state = self.CONFUSE1
                return self.confuse_two()
            else:
                return calculate_motor_speed(0, 0)

        # Rotate on the spot
        return calculate_motor_speed(None, angle)

    def confuse_two(self):
        """
        Rotate to the other side and make them go 'Wow, much rotate'.
        """
        other_side = self._get_other_side(self.fake_shoot_side)
        print 'OTHER SIDE:', other_side
        # Determine targets
        target_x = self.world.their_goal.x
        target_y = self._get_goal_corner_y(other_side)

        print 'OTHER SIDE TARGET Y', target_y

        angle = self.our_attacker.get_rotation_to_point(target_x, target_y)

        print 'OTHER SIDE ANGLE:', angle

        if has_matched(self.our_attacker, angle=angle, angle_threshold=self.PRECISE_BALL_ANGLE_THRESHOLD):
            # We've finished CONFUSE2
            self.current_state = self.SHOOT
            return self.shoot()
            # pass
            pass

        # Rotate on the spot
        return calculate_motor_speed(None, angle, careful=True)

    def shoot(self):
        """
        Kick.
        """
        self.current_state = self.SHOOT
        return kick_ball()

    def _get_shooting_coordinates(self, robot):
        """
        Retrive the coordinates to which we need to move before we set up the confuse shot.
        """
        zone_index = robot.zone
        zone_poly = self.world.pitch.zones[zone_index][0]

        # Find the x coordinate of where we need to go
        # Find which function to use, min for us on the right, max otherwise
        f = max if zone_index == 2 else min
        x = int(f(zone_poly, key=lambda z: z[0])[0])

        # Offset x to be a wee bit inside our zone
        x = x - self.SHOOTING_X_OFFSET if zone_index == 2 else x + self.SHOOTING_X_OFFSET

        # y is simply middle of the pitch
        y = self.world.pitch.height / 2

        return (x, y)

    def _get_fake_shoot_side(self, robot):
        """
        Compare the location of their robot with the middle to pick the first side
        """
        y = robot.y
        middle = self.world.pitch.height / 2
        return self.UP if y < middle else self.DOWN

    def _get_other_side(self, side):
        """
        Determine the other side to rotate to based on the CONFUSE1 side.
        """
        assert side in self.GOAL_SIDES
        return self.UP if side == self.DOWN else self.DOWN

    def _get_goal_corner_y(self, side):
        """
        Get the coordinates of where to aim / shoot.
        """
        assert side in self.GOAL_SIDES
        if side == self.UP:
            # y coordinate of the goal is DOWN, offset by the width
            return self.world.their_goal.y + self.world.their_goal.width / 2 - int(self.GOAL_CORNER_OFFSET * 1.5)
        return self.world.their_goal.y - self.world.their_goal.width / 2 + self.GOAL_CORNER_OFFSET + 20


class AttackerDriveBy(Strategy):
    """
    Strategy where we drive forward and backwards, rotate and shoot.

    Idea:
        1) Move to a location either in the UP or DOWN section, opposite to
           the location of the opposite defender
        2) If path is clear, proceed. Otherwise, switch sides.
        3) Rotate to face the goal
        4) Shoot
    """

    DRIVE, ALIGN_GOAL, SHOOT, FINISHED = 'DRIVE', 'ALIGN_GOAL', 'SHOOT', 'FINISHED'
    STATES = [DRIVE, ALIGN_GOAL, SHOOT, FINISHED]

    X_OFFSET = 70
    Y_OFFSET = 100

    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world):
        super(AttackerDriveBy, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.DRIVE: self.drive,
            self.ALIGN_GOAL: self.align_to_goal,
            self.SHOOT: self.shoot,
            self.FINISHED: do_nothing
        }

        self.our_attacker = self.world.our_attacker
        self.their_defender = self.world.their_defender
        self.drive_side = None
        self._get_goal_points()
        self.pick_side()

    def pick_side(self):
        '''
        At first, choose side opposite to their defender.
        '''
        middle_y = self.world.pitch.height / 2
        if self.world.their_defender.y < middle_y:
            self.drive_side = self.UP
        self.drive_side = self.DOWN

    def drive(self):
        x = self.get_zone_attack_x_offset()
        if self.drive_side == self.UP:
            y = self.world.pitch.height
        else:
            y = 0

        # offset the y
        if self.drive_side == self.UP:
            y -= self.Y_OFFSET
        else:
            y += self.Y_OFFSET

        distance, angle = self.our_attacker.get_direction_to_point(x, y)
        if has_matched(self.our_attacker, x=x, y=y):
            self.current_state = self.ALIGN_GOAL
            return do_nothing()

        return calculate_motor_speed(distance, angle)

    def align_to_goal(self):
        other_side = self.UP if self.drive_side == self.DOWN else self.DOWN
        goal_x = self.world.their_goal.x
        goal_y = self.goal_points[self.drive_side]

        angle = self.our_attacker.get_rotation_to_point(goal_x, goal_y)

        if has_matched(self.our_attacker, angle=angle, angle_threshold=math.pi/30):
            if is_shot_blocked(self.world, self.our_attacker, self.their_defender):
                # Drive to the other side.
                self.drive_side = other_side
                self.current_state = self.DRIVE
            else:
                self.current_state = self.SHOOT
            return do_nothing()

        return calculate_motor_speed(None, angle)

    def shoot(self):
        self.current_state = self.FINISHED
        return kick_ball()

    def get_zone_attack_x(self):
        """
        Find the border coordinate for our attacker zone and their defender.
        """
        attacker = self.world.our_attacker
        zone_poly = self.world.pitch.zones[attacker.zone][0]

        f = max if attacker.zone == 2 else min
        return f(zone_poly, key=lambda x: x[0])[0]

    def get_zone_attack_x_offset(self):
        """
        Get the x coordinate already offset
        """
        our_attacker = self.world.our_attacker
        middle_x = self.get_zone_attack_x()
        if our_attacker.zone == 2:
            middle_x -= self.X_OFFSET
        else:
            middle_x += self.X_OFFSET
        return middle_x

    def _get_goal_corner_y(self, side):
        """
        Get the coordinates of where to aim / shoot.
        """
        assert side in [self.UP, self.DOWN]
        if side == self.UP:
            # y coordinate of the goal is DOWN, offset by the width
            return self.world.their_goal.y + self.world.their_goal.width / 2
        return self.world.their_goal.y - self.world.their_goal.width / 2

    def _get_goal_points(self):
        # Get the polygon of their defender's zone.
        zone_poly = self.world.pitch.zones[self.their_defender.zone][0]
        goal_points = sorted(zone_poly, key=lambda z: z[0], reverse=(self.world._our_side=='left'))[:2]
        goal_points = sorted(goal_points, key=lambda z: z[1])
        self.goal_points = {self.DOWN: goal_points[0][1]+30, self.UP: goal_points[1][1]-30}


class AttackerDriveByTurn(Strategy):

    CENTER, ROTATE, DRIVE, SHOOT, FINISHED = 'CENTER', 'ROTATE', 'DRIVE', 'SHOOT', 'FINISHED'
    STATES = [CENTER, ROTATE, DRIVE, SHOOT, FINISHED]

    Y_OFFSET = 0

    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world):
        super(AttackerDriveByTurn, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.CENTER: self.center,
            self.ROTATE: self.rotate,
            self.DRIVE: self.drive,
            self.SHOOT: self.shoot,
            self.FINISHED: do_nothing
        }

        self.our_attacker = self.world.our_attacker
        self.our_defender = self.world.our_defender
        self.their_defender = self.world.their_defender
        self.drive_side = None
        self.align_y = None
        self._get_goal_points()
        self.pick_side()
        self.laps_left = 5

    def pick_side(self):
        '''
        At first, choose side opposite to their defender.
        '''
        middle_y = self.world.pitch.height / 2
        if self.world.their_defender.y < middle_y:
            self.drive_side = self.UP
        self.drive_side = self.DOWN

    def center(self):
        if has_matched(self.our_attacker, x=self._get_zone_center_x(), y=self.our_attacker.y):
            # We're there. Advance the states and formulate next action.
            if self.our_attacker.angle < math.pi:
                self.align_y = self.world.pitch.height
            else:
                self.align_y = 0
            self.current_state = self.ROTATE
            return do_nothing()
        else:
            displacement, angle = self.our_attacker.get_direction_to_point(
                self._get_zone_center_x(), self.our_attacker.y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True, careful=True)

    def rotate(self):
        displacement, angle = self.our_attacker.get_direction_to_point(self.our_attacker.x, self.align_y)
        if has_matched(self.our_attacker, angle=angle, angle_threshold=math.pi/30):
            self.current_state = self.DRIVE
            return do_nothing()
        else:
            return calculate_motor_speed(None, angle, careful=True)

    def drive(self):
        y = self.goal_points[self.drive_side] - 10 * math.sin(self.our_attacker.angle)

        distance, angle = self.our_attacker.get_direction_to_point(self.our_attacker.x, y)
        if has_matched(self.our_attacker, x=self.our_attacker.x, y=y):
            print abs(self.our_attacker.y - self.their_defender.y)
            if abs(self.our_attacker.y - self.their_defender.y) > 30 or self.laps_left == 0:
                self.current_state = self.SHOOT
            else:
                self.drive_side = self.UP if self.drive_side == self.DOWN else self.DOWN
                self.laps_left -= 1
                self.current_state = self.ROTATE
            return do_nothing()
        else:
            return calculate_motor_speed(distance, angle, backwards_ok=True)

    def shoot(self):
        # Decide the direction of the right angle turn, based on our position and
        # side on the pitch.
        if self.world._our_side == 'right':
            if self.our_attacker.angle < math.pi:
                orientation = 1
            else:
                orientation = -1
        else:
            if self.our_attacker.angle < math.pi:
                orientation = -1
            else:
                orientation = 1
        self.current_state = self.FINISHED
        self.our_attacker.catcher = 'open'
        return turn_shoot(orientation)

    def _get_zone_center_x(self):
        """
        Find the border coordinate for our attacker zone and their defender.
        """
        attacker = self.world.our_attacker
        zone_poly = self.world.pitch.zones[attacker.zone][0]

        min_x = int(min(zone_poly, key=lambda z: z[0])[0])
        max_x = int(max(zone_poly, key=lambda z: z[0])[0])

        return (min_x + max_x) / 2

    def _get_goal_points(self):
        # Get the polygon of their defender's zone.
        zone_poly = self.world.pitch.zones[self.their_defender.zone][0]
        goal_points = sorted(zone_poly, key=lambda z: z[0], reverse=(self.world._our_side=='left'))[:2]
        goal_points = sorted(goal_points, key=lambda z: z[1])
        self.goal_points = {self.DOWN: goal_points[0][1]+40, self.UP: goal_points[1][1]-40}


class AttackerTurnScore(Strategy):
    """
    Move up and down the opponent's goal line and suddenly turn 90 degrees and kick if the
    path is clear.
    """

    UNALIGNED, POSITION, KICK, FINISHED = 'UNALIGNED', 'POSITION', 'KICK', 'FINISHED'
    STATES = [UNALIGNED, POSITION, KICK, FINISHED]

    def __init__(self, world):
        super(AttackerTurnScore, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.UNALIGNED: self.align,
            self.POSITION: self.position,
            self.KICK: self.kick,
            self.FINISHED: do_nothing
        }

        self.their_goal = self.world.their_goal
        self.our_attacker = self.world.our_attacker
        self.their_defender = self.world.their_defender

        # Distance that the attacker should keep from its boundary.
        self.offset = 60

        # Opponent's goal edge where our attacker is currently heading.
        self.point = 0

    def align(self):
        '''
        Go to the boundary of the attacker's zone and align with the center
        of the goal line.
        '''
        ideal_x = self._get_alignment_x()
        ideal_y = self.their_goal.y

        if has_matched(self.our_attacker, x=ideal_x, y=ideal_y):
            self.current_state = self.POSITION
            return do_nothing()
        else:
            distance, angle = self.our_attacker.get_direction_to_point(ideal_x, ideal_y)
            return calculate_motor_speed(distance, angle)

    def position(self):
        '''
        Go up an down the goal line waiting for the first opportunity to shoot.
        '''
        our_attacker = self.our_attacker
        # Check if we have a clear shot
        if not is_attacker_shot_blocked(self.world, self.our_attacker, self.their_defender) and \
               (abs(our_attacker.angle - math.pi / 2) < math.pi / 20 or \
               abs(our_attacker.angle - 3*math.pi/2) < math.pi / 20):
            self.current_state = self.KICK
            return self.kick()

        else:
            # If our shot is blocked, continue moving up and down the goal line.
            # We want the center of the robot to be inside the goal line.
            goal_width = self.their_goal.width/2
            goal_edges = [self.their_goal.y - goal_width + 10,
                          self.their_goal.y + goal_width - 10]
            ideal_x = self.our_attacker.x
            ideal_y = goal_edges[self.point]

            if has_matched(self.our_attacker, x=self.our_attacker.x, y=ideal_y):
                # Go to the other goal edge
                self.point = 1 - self.point
                ideal_y = goal_edges[self.point]

            distance, angle = self.our_attacker.get_direction_to_point(ideal_x, ideal_y)
            return calculate_motor_speed(distance, angle, backwards_ok=True)

    def kick(self):
        # Decide the direction of the right angle turn, based on our position and
        # side on the pitch.
        if self.world._our_side == 'left':
            if self.our_attacker.angle > 0 and self.our_attacker.angle < math.pi:
                orientation = -1
            else:
                orientation = 1
        else:
            if self.our_attacker.angle > 0 and self.our_attacker.angle < math.pi:
                orientation = 1
            else:
                orientation = -1

        self.current_state = self.FINISHED
        return turn_shoot(orientation)

    def _get_alignment_x(self):
        # Get the polygon of our attacker's zone.
        zone = self.our_attacker.zone
        assert zone in [1,2]
        zone_poly = self.world.pitch.zones[zone][0]

        # Choose the appropriate function to determine the borderline of our
        # attacker's zone facing the opponent's goal.
        side = {1: min, 2: max}
        f = side[zone]

        # Get the x coordinate that our attacker needs to match.
        sign = {1: 1, 2: -1}
        boundary_x = int(f(zone_poly, key=lambda z: z[0])[0]) + sign[zone]*self.offset
        return boundary_x


class AttackerGrabCareful(Strategy):
    """
    Carefully grabbing the ball when it is located by the wall.

    Idea:
        Approach perpendicular to the wall to avoid getting stuck by the wall.
    """

    UNALIGNED, POSITIONED, ALIGNED, GRABBED = 'UNALIGNED', 'POSITIONED', 'ALIGNED', 'GRABBED'
    STATES = [UNALIGNED, POSITIONED, ALIGNED, GRABBED]

    BALL_Y_OFFSET = 80

    def __init__(self, world):
        super(AttackerGrabCareful, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.UNALIGNED: self.position,
            self.POSITIONED: self.align,
            self.ALIGNED: self.grab,
            self.GRABBED: self.finish
        }

        self.ball_side = self.get_ball_side()

    def position(self):
        our_attacker = self.world.our_attacker
        ball = self.world.ball

        # Find ideal x and y
        ideal_x = ball.x
        if self.ball_side == self.UP:
            ideal_y = ball.y - self.BALL_Y_OFFSET
        else:
            ideal_y = ball.y + self.BALL_Y_OFFSET

        if has_matched(our_attacker, x=ideal_x, y=ideal_y):
            self.current_state = self.POSITIONED
            return self.align()

        distance, angle = our_attacker.get_direction_to_point(ideal_x, ideal_y)
        return calculate_motor_speed(distance, angle, careful=True)

    def align(self):
        our_attacker = self.world.our_attacker
        ball = self.world.ball

        print 'BALL SIDE', self.ball_side

        distance, angle = our_attacker.get_direction_to_point(ball.x, ball.y)

        if has_matched(our_attacker, angle=angle):
            self.current_state = self.ALIGNED
            return self.grab()

        motors = calculate_motor_speed(None, angle, careful=True)
        print 'MOTORS', motors
        return motors


    def grab(self):
        our_attacker = self.world.our_attacker
        ball = self.world.ball

        if our_attacker.can_catch_ball(ball):
            self.current_state = self.GRABBED
            return grab_ball()

        distance, angle = our_attacker.get_direction_to_point(ball.x, ball.y)
        return calculate_motor_speed(distance, angle, careful=True)

    def finish(self):
        return do_nothing()

    def get_ball_side(self):
        ball = self.world.ball
        middle = self.world.pitch.height / 2
        if ball.y < middle:
            return self.DOWN
        return self.UP
