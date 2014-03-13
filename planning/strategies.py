from utilities import *

class Strategy(object):

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


class DefaultDefenderDefence(Strategy):

    def __init__(self, world):
        super(DefaultDefenderDefence, self).__init__(world, ['somewhere', 'goal_line'])

    def generate(self):
        our_defender = self.world.our_defender
        their_attacker = self.world.their_attacker
        our_goal = self.world.our_goal
        goal_front_x = our_goal.x + 35 if self.world._our_side == 'left' else our_goal.x - 35
        # If the robot is not on the goal line:
        if self.current_state == 'somewhere':
            # Need to go to the front of the goal line
            if has_matched(our_defender, x=goal_front_x, y=our_goal.y):
                self.current_state = 'goal_line'
            else:
                displacement, angle = our_defender.get_direction_to_point(goal_front_x, our_goal.y)
                return calculate_motor_speed(displacement, angle)
        if self.current_state == 'goal_line':
            predicted_y = predict_y_intersection(self.world, goal_front_x, their_attacker)
            if not (predicted_y == None):
                displacement, angle = our_defender.get_direction_to_point(goal_front_x, predicted_y)
                return calculate_motor_speed(displacement, angle, backwards_ok=True)
            return calculate_motor_speed(0, 0)

class DefaultDefenderAttack(Strategy):

    def __init__(self, world):
        super(DefaultDefenderAttack, self).__init__(world, ['go_to_ball', 'grab_ball', 'rotate_to_pass', 'pass'])

    def generate(self):
        our_defender = self.world.our_defender
        our_attacker = self.world.our_attacker
        ball = self.world.ball
        if self.current_state == 'go_to_ball':
            # We open our catcher:
            if our_defender.catcher == 'closed':
                our_defender.catcher = 'open'
                return open_catcher()
            # If we don't need to move or rotate, we advance to grabbing:
            displacement, angle = our_defender.get_direction_to_point(ball.x, ball.y)
            if our_defender.can_catch_ball(ball):
                self.current_state = 'grab_ball'
            else:
                return calculate_motor_speed(displacement, angle, careful=True)
        if self.current_state == 'grab_ball':
            if our_defender.has_ball(ball):
                self.current_state = 'rotate_to_pass'
            else:
                our_defender.catcher = 'closed'
                return grab_ball()
        if self.current_state == 'rotate_to_pass':
            if not(our_defender.has_ball(ball)):
                self.current_state = 'go_to_ball'
                our_defender.catcher = 'open'
                return open_catcher()
            else:
                _, angle = our_defender.get_direction_to_point(our_attacker.x, our_attacker.y)
                if has_matched(our_defender, angle=angle):
                    self.current_state = 'pass'
                else:
                    return calculate_motor_speed(None, angle, careful=True)
        if our_defender.state == 'pass':
            self.reset_current_state()
            our_defender.catcher = 'open'
            return kick_ball()


class DefaultAttackerDefend(Strategy):

    def __init__(self, world):
        super(DefaultAttackerDefend, self).__init__(world, ['defence_block'])

    def generate(self):
        '''
        This function will make our attacker block the path between
        the opposition's defender and our goal
        '''
        their_defender = self.world.their_defender
        our_attacker = self.world.our_attacker
        zone = self.world._pitch._zones[our_attacker.zone]
        min_x,max_x,_,_ = zone.boundingBox()
        border = (min_x + max_x)/2
        predicted_y = predict_y_intersection(self.world, our_attacker.x, their_defender, True)
        if not (predicted_y == None):
            displacement, angle = our_attacker.get_direction_to_point(border, predicted_y)
            if displacement > 30:
                return calculate_motor_speed(displacement, angle, backwards_ok=True)
        return calculate_motor_speed(0, 0)


class DefaultAttackerAttack(Strategy):

    def __init__(self, world):
        super(DefaultAttackerAttack, self).__init__(world, ['go_to_ball', 'grab_ball', 'rotate_to_goal', 'shoot'])

    def generate(self):
        our_attacker = self.world.our_attacker
        their_goal = self.world.their_goal
        ball = self.world.ball
        if self.current_state == 'go_to_ball':
            # We open our catcher:
            if our_attacker.catcher == 'closed':
                our_attacker.catcher = 'open'
                return open_catcher()
            # If we don't need to move or rotate, we advance to grabbing:
            displacement, angle = our_attacker.get_direction_to_point(ball.x, ball.y)
            if our_attacker.can_catch_ball(ball):
                self.current_state = 'grab_ball'
            else:
                return calculate_motor_speed(displacement, angle, careful=True)
        if self.current_state == 'grab_ball':
            if our_attacker.has_ball(ball):
                self.current_state = 'rotate_to_goal'
            else:
                our_attacker.catcher = 'closed'
                return grab_ball()
        if self.current_state == 'rotate_to_goal':
            if not(our_attacker.has_ball(ball)):
                self.current_state = 'go_to_ball'
                our_attacker.catcher = 'open'
                return open_catcher()
            else:
                _, angle = our_attacker.get_direction_to_point(their_goal.x, their_goal.y)
                if has_matched(our_attacker, angle=angle):
                    self.current_state = 'shoot'
                else:
                    return calculate_motor_speed(None, angle)
        if self.current_state == 'shoot':
            self.current_state = 'defence_block'
            our_attacker.catcher = 'open'
            return kick_ball()


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
    """
    GRABBED, POSITION = 'GRABBED', 'POSITION'
    CONFUSE1, CONFUSE2, SHOOT = 'CONFUSE1', 'CONFUSE2', 'SHOOT'
    STATES = [GRABBED, POSITION, CONFUSE1, CONFUSE2, SHOOT]

    UP, DOWN = 'UP', 'DOWN'

    SHOOTING_X_OFFSET = 30

    def __init__(self, world):
        super(AttackerScoreDynamic, self).__init__(world, self.STATES)
        # Map states into functions
        self.NEXT_ACTION_MAP = {
            self.GRABBED: self.position,
            self.POSITION: self.confuse_one,
            self.CONFUSE1: self.confuse_two,
            self.CONFUSE2: self.shoot
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
        return self.NEXT_ACTION_MAP[self.current_state]()

    def position(self):
        """
        Position the robot in the middle close to the goal. Angle does not matter.
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
        Pick a side and aim at it.
        """
        # Initialize fake shoot side if not available
        if self.fake_shoot_side is None:
            self.fake_shoot_side = self._get_fake_shoot_side(self.their_defender)

        target_x = self.world.their_goal.x
        target_y = self._get_goal_corner_y(self.fake_shoot_side)

        angle = self.our_attacker.get_rotation_to_point(target_x, target_y)

        if has_matched(self.our_attacker, angle=angle):
            # We've finished CONFUSE1
            self.current_state = self.CONFUSE1
            return self.confuse_two()

        # Rotate on the spot
        return calculate_motor_speed(None, angle)

    def confuse_two(self):
        """
        Rotate to the other side and make them go 'Wow, much rotate'.
        """
        pass

    def shoot(self):
        pass

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
        return self.DOWN if y < middle else self.UP

    def _get_goal_corner_y(self, side):
        """
        Get the coordinates of where to aim / shoot.
        """
        assert side in [self.UP, self.DOWN]
        if side == self.UP:
            # y coordinate of the goal is DOWN, offset by the width
            return self.world.their_goal.y + self.world.their_goal.width
        return self.world.their_goal.y
