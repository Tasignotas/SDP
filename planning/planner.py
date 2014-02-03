from objects import *


class Planner:


    def __init__(self, home_pitch):
        self.pitch = Pitch('../vision/calibrate.json')
        zones = [0, 1, 2, 3]
        goals = [Goal('goal_0', 0, 0, 20, 90), Goal('goal_3', 3, 0, 20, 270)]
        self.ball = Ball('ball')
        if not home_pitch:
            zones.reverse()
            goals.reverse()
        self.h_defend = HomeRobot('home_defender', zones[0])
        self.a_attack = AwayRobot('away_attacker', zones[1])
        self.h_attack = HomeRobot('home_attacker', zones[2])
        self.a_defend = AwayRobot('away_defender', zones[3])
        self.h_goal = goals[0]
        self.a_goal = goals[1]


    def plan(self, h_defend, h_attack, a_defend, a_attack, ball):
        self.update([h_defend, h_attack, a_defend, a_attack, ball])

        if self.h_defend.get_possession(self.ball):
            # Match orientation with h_attack
            # Check for clear kick path
            # Kick ball or get MTV
            # Follow path to MTV point
            # If kick path clear then kick else repeat
            pass
        elif self.h_attack.get_possession(self.ball):
            # Match orientation with a_goal
            # Check for clear kick path
            # Kick ball or get MTV
            # Follow path to MTV point
            # If kick path clear then kick else repeat
            pass
        elif self.a_defend.get_possession(self.ball):
            # Check for clear kick path
            # If clear calc MTV to block
            # Follow path to MTV point
            pass
        elif self.a_attack.get_possession(self.ball):
            # Check for clear kick path
            # If clear calc MTV to block
            # Follow path to MTV point
            pass
        else:
            # Try to follow path to ball
            pass

        return ((0,0,0), (0,0,0))


    def update(self, values):
        i = 0
        for item in [self.h_defend, self.h_attack, self.a_defend, self.a_attack, self.ball]:
            item.set_position(values[i][0], values[i][1])
            item.set_orientation(values[i][2])
            item.set_velocity(values[i][3])
            i += 1