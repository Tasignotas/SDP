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
        predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.their_attacker, bounce=True)

        if predicted_y is not None:
            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x,
                                                                           predicted_y - 10*math.sin(self.our_defender.angle))
            return calculate_motor_speed(displacement, angle, backwards_ok=True)
        else:
            ball = self.world.ball
            our_defender = self.world.our_defender
            displacement, angle = self.our_defender.get_direction_to_point(our_defender.x, ball.y)
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
        self.their_defender = self.world.their_defender
        self.our_defender = self.world.our_defender

    def align(self):
        """
        Align yourself with the middle of our zone.
        """
        if has_matched(self.our_attacker, x=self.center_x, y=self.center_y):
            # We're there. Advance the states and formulate next action.
            self.current_state = self.BLOCK_PASS
            return do_nothing()
        else:
            displacement, angle = self.our_defender.get_direction_to_point(
                self.center_x, self.center_y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True)

    def block_pass(self):
        predicted_y = predict_y_intersection(self.world, self.our_attacker.x, self.their_defender, full_width=True, bounce=True)
        if not (predicted_y == None):
            displacement, angle = self.our_attacker.get_direction_to_point(self.our_attacker.x, predicted_y)
            #if displacement > 30:
            return calculate_motor_speed(displacement, angle, backwards_ok=True)
        return do_nothing()


class AttackerCatch(Strategy):

    CATCH = 'CATCH'
    STATES = [CATCH]

    def __init__(self, world):
        super(AttackerCatchStrategy, self).__init__(world, STATES)

        self.NEXT_ACTION_MAP = {
            self.CATCH: self.catch
        }

        self.our_attacker = self.world.our_attacker
        self.ball = self.world.ball

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
    POSITION = 'POSITION'
    STATES = [POSITION]

    def __init__(self, world):
        super(AttackerPositionCatch, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.POSITION: self.position
        }

        self.our_attacker = self.world.our_attacker
        self.our_defender = self.world.our_defender
        zone = self.world._pitch._zones[self.our_attacker.zone]
        min_x, max_x, min_y, max_y  = zone.boundingBox()
        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2

    def position(self):
        if has_matched(self.our_attacker, x=self.center_x, y=self.center_y):
            return do_nothing()
        else:
            displacement, angle = self.our_defender.get_direction_to_point(
                self.center_x, self.center_y)
            return calculate_motor_speed(displacement, angle, backwards_ok=True)


class DefenderBouncePass(Strategy):
    '''
    Once the defender grabs the ball, move to the center of the zone and shoot towards
    the wall of the center of the opposite attacker zone, in order to reach our_attacker
    attacker zone.
    '''

    POSITION, ROTATE, SHOOT, FINISHED = 'POSITION', 'ROTATE', 'SHOOT', 'FINISHED'
    STATES = [POSITION, ROTATE, SHOOT, FINISHED]

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
        self.ball = self.world.ball

        # Choose a random side to bounce off
        self.point = randint(0,1)

        # Find the position to shoot from and cache it
        self.shooting_pos = self._get_shooting_coordinates(self.our_defender)

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
            return calculate_motor_speed(distance, angle)

    def rotate(self):
        """
        Once the robot is in position, rotate to one side or the other in order
        to bounce the ball into the attacker zone. If one side is blocked by their
        attacker, then rotate to the other side.
        """
        bounce_points = self._get_bounce_points(self.our_defender)
        x, y = bounce_points[self.point][0], bounce_points[self.point][1]
        angle = self.our_defender.get_rotation_to_point(x, y)

        if has_matched(self.our_defender, angle=angle, angle_threshold=pi/7):
            if not is_shot_blocked(self.world, self.our_defender, self.world.their_attacker):
                self.current_state = self.SHOOT
                return do_nothing()
            else:
                self.point = 1 - self.point
                x, y = bounce_points[self.point][0], bounce_points[self.point][1]
                angle = self.our_defender.get_rotation_to_point(x, y)
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
        if self.our_attacker.catcher == 'closed':
            self.our_attacker.catcher = 'open'
            self.current_state = self.GO_TO_BALL
            return open_catcher()
        else:
            self.current_state = self.GO_TO_BALL
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

    PREPARE, GO_TO_BALL, GRAB_BALL, GRABBED = 'PREPARE', 'GO_TO_BALL', 'GRAB_BALL', 'GRABBED'
    STATES = [PREPARE, GO_TO_BALL, GRAB_BALL, GRABBED]

    def __init__(self, world):
        super(DefenderGrab, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.PREPARE: self.prepare,
            self.GO_TO_BALL: self.position,
            self.GRAB_BALL: self.grab,
            self.GRABBED: do_nothing
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball

    def prepare(self):
        if self.our_defender.catcher == 'closed':
            self.our_defender.catcher = 'open'
            self.current_state = self.GO_TO_BALL
            return open_catcher()
        else:
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
        1) Move to a location either in the UP or DOWN section
        2) Drive backwards to a location opposite to the previous
        3) Rotate to face the goal
        4) Shoot
    """

    GRABBED, ALIGNED_CENTER = 'GRABBED', 'ALIGNED_CENTER'
    DRIVE, ALIGNED_GOAL, SHOT = 'DRIVE1', 'ALIGNED_GOAL', 'SHOT'
    STATES = [GRABBED, ALIGNED_CENTER, DRIVE, ALIGNED_GOAL, SHOT]

    X_OFFSET = 70
    Y_OFFSET = 100

    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world):
        super(AttackerDriveBy, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.GRABBED: self.align_center,
            self.ALIGNED_CENTER: self.drive_one,
            self.DRIVE: self.align_to_goal,
            self.ALIGNED_GOAL: self.shoot,
            self.SHOT: self.finish
        }

        self.drive_first_side = None

    def generate(self):
        return self.NEXT_ACTION_MAP[self.current_state]()

    def align_center(self):
        our_attacker = self.world.our_attacker
        middle_y = self.world.pitch.height / 2
        middle_x = self.get_zone_attack_x_offset()

        distance, angle = our_attacker.get_direction_to_point(middle_x, middle_y)

        if has_matched(our_attacker, x=middle_x, y=middle_y):
            self.current_state = self.ALIGNED_CENTER
            return self.drive_one()

        return calculate_motor_speed(distance, angle, backwards_ok=True)

    def drive_one(self):
        our_attacker = self.world.our_attacker
        # Assign side if not yet assigned.
        if self.drive_first_side is None:
            self.drive_first_side = self.pick_side()

        print 'PICKED SIDE:', self.drive_first_side

        x = self.get_zone_attack_x_offset()
        if self.drive_first_side == self.UP:
            y = self.world.pitch.height
        else:
            y = 0

        # offset the y
        if self.drive_first_side == self.UP:
            y -= self.Y_OFFSET
        else:
            y += self.Y_OFFSET

        print 'XY', x, y

        distance, angle = our_attacker.get_direction_to_point(x, y)

        if has_matched(our_attacker, x=x, y=y):
            self.current_state = self.DRIVE
            return self.align_to_goal()

        return calculate_motor_speed(distance, angle)

    def align_to_goal(self):
        our_attacker = self.world.our_attacker
        other_side = self.UP if self.drive_first_side == self.DOWN else self.DOWN
        goal_y = self._get_goal_corner_y(other_side)
        goal_x = self.world.their_goal.x

        angle = our_attacker.get_rotation_to_point(goal_x, goal_y)

        print angle, has_matched(our_attacker, angle=angle)

        if has_matched(our_attacker, angle=angle):
            self.current_state = self.ALIGNED_GOAL
            return self.shoot()

        return calculate_motor_speed(None, angle, careful=True)


    def shoot(self):
        self.current_state = self.SHOT
        return kick_ball()

    def finish(self):
        return calculate_motor_speed(0, 0)

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

    def pick_side(self):
        middle_y = self.world.pitch.height / 2
        if self.world.their_defender.y < middle_y:
            return self.DOWN
        return self.UP

    def _get_goal_corner_y(self, side):
        """
        Get the coordinates of where to aim / shoot.
        """
        assert side in [self.UP, self.DOWN]
        if side == self.UP:
            # y coordinate of the goal is DOWN, offset by the width
            return self.world.their_goal.y + self.world.their_goal.width / 2 - 50
        return self.world.their_goal.y - self.world.their_goal.width / 2 + 50


class AttackerTurnScore(Strategy):
    """
    Move up and down the opponent's goal line and suddenly turn 90 degrees and kick if the
    path is clear.
    """

    UNALIGNED, POSITION, KICK = 'UNALIGNED', 'POSITION', 'KICK'
    STATES = [UNALIGNED, POSITION, KICK]

    def __init__(self, world):
        super(AttackerTurnScore, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.UNALIGNED: self.align,
            self.POSITION: self.position,
            self.KICK: self.kick
        }

        self.their_goal = self.world.their_goal
        self.our_attacker = self.world.our_attacker
        self.their_defender = self.world.their_defender

        # Distance that the attacker should keep from its boundary.
        self.offset = 55

        # Opponent's goal edge where our attacker is currently heading.
        self.point = 0

    def align(self):
        '''
        Go to the boundary of the attacker's zone and align with the goal line.
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
        # Check if we have a clear shot
        if not is_attacker_shot_blocked(self.world, self.our_attacker, self.their_defender):
            self.current_state = self.KICK
            return do_nothing()

        else:
            # If our shot is blocked, continue moving up and down the goal line.
            goal_edges = [self.their_goal.y, self.their_goal.y + self.their_goal.width]
            ideal_x = self.our_attacker.x
            ideal_y = goal_edges[self.point]

            if has_matched(self.our_attacker, x=self.our_attacker.x, y=ideal_y):
                # Go to the other goal edge
                self.point = 1 - self.point
                ideal_y = goal_edges[self.point]

            distance, angle = self.our_attacker.get_direction_to_point(ideal_x, ideal_y)
            return calculate_motor_speed(distance, angle)

    def kick(self):
        # This will also include the 90 degree turn.
        return kick_ball()

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
        offset = {1: self.offset, 2: -self.offset}
        boundary_x = int(f(zone_poly, key=lambda z: z[0])[0]) + offset[zone]
        return boundary_x


class CarefulGrabAttacker(Strategy):
    """
    Carefully grabbing the ball when it is located by the wall.

    Idea:
        Approach perpendicular to the wall to avoid getting stuck by the wall.
    """

    UNALIGNED, ALIGNED, GRABBED = 'UNALIGNED', 'ALIGNED', 'GRABBED'
    STATES = [UNALIGNED, ALIGNED, GRABBED]

    BALL_Y_OFFSET = 40

    def __init__(self, world):
        super(CarefulGrabAttacker, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            self.UNALIGNED: self.align,
            self.ALIGNED: self.grab,
            self.GRABBED: self.finish
        }

        self.ball_side = self.get_ball_side()

    def align(self):
        our_attacker = self.world.our_attacker
        ball = self.world.ball

        # Find ideal x and y
        ideal_x = ball.x
        if self.ball_side == self.UP:
            ideal_y = ball.y - self.BALL_Y_OFFSET
            angle = math.pi / 2.0   # 90 degrees, pointing up
        else:
            ideal_y = ball.y + self.BALL_Y_OFFSET
            angle = 3 * math.pi / 2.0   # 270 degrees, pointing down

        if has_matched(our_attacker, x=ideal_x, y=ideal_y, angle=angle):
            self.current_state = self.ALIGNED
            return self.grab()

        return calculate_motor_speed()

        distance, angle = self.our_defender.get_direction_to_point(ideal_x, ideal_y)
        # if self.ball_side == self.UP:


    def grab(self):
        pass

    def finish(self):
        pass

    def get_ball_side(self):
        ball = self.world.ball
        middle = self.world.pitch.height / 2
        if ball.y < middle:
            return self.DOWN
        return self.UP
