from models import World
from collisions import *


class Planner:


    def __init__(self, our_side):
        self._world = World(our_side)


    def plan(self, position_dictionary):

        self._world.update_positions(position_dictionary)
        our_attacker = self._world.get_our_attacker()
        our_defender = self._world.get_our_defender()
        our_goal = self._world.get_our_goal()
        their_attacker = self._world.get_their_attacker()
        their_defender = self._world.get_their_defender()
        their_goal = self._world.get_their_goal()
        ball = self._world.get_ball()
        '''
        if our_defender.get_possession(ball):
            pass_path = our_defender.get_pass_path(our_attacker)
            avoid_plan = get_avoidance(pass_path, our_defender, their_attacker)
            if avoid_plan == None:
                return (0, 0, 0, our_defender.get_path_alignment(pass_path))
            else:
                return (avoid_plan)

        elif our_attacker.get_possession(ball):
            shoot_path = our_defender.get_shoot_path(their_goal)
            avoid_plan = get_avoidance(shoot_path, our_attacker, their_defender)
            if avoid_plan == None:
                return (0, 0, 0, our_defender.get_path_alignment(shoot_path))
            else:
                return (avoid_plan)

        elif their_defender.get_possession(ball):
            pass_path = their_defender.get_pass_path(their_attacker)
            intercept_plan = get_interception(pass_path, our_attacker)
            return (intercept_plan)

        if their_attacker.get_ball_possession(ball):
            print 'Yes!!!'
            shoot_path = their_attacker.get_shoot_path(our_goal)
            for point in shoot_path:
               print point
            raise Exception()
            intercept_plan = get_interception(shoot_path, our_defender)
            return (intercept_plan)
        else:
            print 'NO!!!'
            if our_attacker.get_ball_proximity(ball):
                our_attacker.get_robot_aligment(ball)
            elif our_defender.get_ball_proximity(ball):
                our_defender.get_robot_alignment(ball)
            '''
        if ball.get_velocity() < 3:
            # print our_attacker.get_stationary_ball(ball)
            pass
            #our_defender.get_stationary_ball(ball)
            '''
            else:
                our_attacker.get_moving_ball(ball)
                our_defender.get_moving_ball(ball)
            '''