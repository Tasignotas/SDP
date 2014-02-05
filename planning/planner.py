from models import World
from path import find_path


ANGLE_THRESHOLD = 20
DISTANCE_THRESHOLD = 10


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)


    def plan(self, position_dictionary):
        self._world.update_positions(position_dictionary)
        our_attacker = self._world.get_our_attacker()
        our_defender = self._world.get_our_defender()
        their_attacker = self._world.get_their_attacker()
        their_defender = self._world.get_their_defender()
        ball = self._world.get_ball()
        if our_defender.get_possession(ball):
            # Match orientation with h_attack
            # Check for clear kick path
            # Kick ball or get MTV
            # Follow path to MTV point
            # If kick path clear then kick else repeat
            pass
        elif our_attacker.get_possession(ball):
            # Match orientation with a_goal
            # Check for clear kick path
            # Kick ball or get MTV
            # Follow path to MTV point
            # If kick path clear then kick else repeat
            pass
        elif their_defender.get_possession(ball):
            # Check for clear kick path
            # If clear calc MTV to block
            # Follow path to MTV point
            pass
        elif their_attacker.get_possession(ball):
            # Check for clear kick path
            # If clear calc MTV to block
            # Follow path to MTV point
            pass
        else:
            # For now, we just ask the defender to fetch the ball:
            path = find_path(our_defender, ball)
            # If we're at (more or less) correct angle and we still need to go straight:
            if  ((-ANGLE_THRESHOLD) < path[1] < ANGLE_THRESHOLD) and (DISTANCE_THRESHOLD < path[0]):
                return ((50, 50, 0), (0, 0, 0))
            # If we need to turn right:
            elif (-ANGLE_THRESHOLD) < path[1]:
                return ((50, -50, 0), (0, 0, 0))
            elif ANGLE_THRESHOLD < path[1]:
                return ((-50, 50, 0), (0, 0, 0))
        return ((0, 0, 0), (0, 0, 0))
