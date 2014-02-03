from models import World


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
        if our_defender.get_possession():
            # Match orientation with h_attack
            # Check for clear kick path
            # Kick ball or get MTV
            # Follow path to MTV point
            # If kick path clear then kick else repeat
            pass
        elif our_attacker.get_possession():
            # Match orientation with a_goal
            # Check for clear kick path
            # Kick ball or get MTV
            # Follow path to MTV point
            # If kick path clear then kick else repeat
            pass
        elif their_defender.get_possession():
            # Check for clear kick path
            # If clear calc MTV to block
            # Follow path to MTV point
            pass
        elif their_attacker.get_possession():
            # Check for clear kick path
            # If clear calc MTV to block
            # Follow path to MTV point
            pass
        else:
            # Try to follow path to ball
            pass
        return ((0,0,0), (0,0,0))
