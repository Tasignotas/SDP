from models import *
from collisions import *
from strategies import *
from utilities import *


class Planner:

    def __init__(self, our_side, pitch_num):
        self._world = World(our_side, pitch_num)
        self._world.our_defender.catcher_area = {'width' : 30, 'height' : 30, 'front_offset' : 10}
        self._world.our_attacker.catcher_area = {'width' : 30, 'height' : 30, 'front_offset' : 10}

        self._defender_defence_strat = DefaultDefenderDefence(self._world)
        self._defender_attack_strat = DefaultDefenderAttack(self._world)

        self._attacker_strategies = {'defence' : [DefaultAttackerDefend],
                                     'grab' : [AttackerGrab],
                                     'score' : [AttackerDriveBy, AttackerScoreDynamic],
                                     'catch' : [AttackerCatchStrategy]}

        self._defender_strategies = {'defence' : [DefaultDefenderDefence],
                                     'grab' : [DefenderGrab],
                                     'pass' : [DefenderBouncePass]}

        self._defender_state = 'defence'
        start_strategy = self.choose_defender_strategy()
        self._defender_current_strategy = start_strategy(self._world)

        self._attacker_state = 'defence'
        start_strategy = self.choose_attacker_strategy()
        self._attacker_current_strategy = start_strategy(self._world)

    # Provisional. Choose the first strategy in the applicable list.
    def choose_attacker_strategy(self):
        return self._attacker_strategies[self._attacker_state][0]

    # Provisional. Choose the first strategy in the applicable list.
    def choose_defender_strategy(self):
        return self._defender_strategies[self._defender_state][0]

    @property
    def attacker_strat_state(self):
        return self._attacker_current_strategy.current_state

    @property
    def defender_strat_state(self):
        return self._defender_current_strategy.current_state

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
        their_attacker = self._world.their_attacker
        ball = self._world.ball
        if robot == 'defender':
            # If the ball is in not in our defender zone, we defend:
            if not (self._world.pitch.zones[our_defender.zone].isInside(ball.x, ball.y)):
                # If we need to switch from defending to attacking:
                if self._defender_state == 'pass' and self._defender_current_strategy.current_state == 'SHOOT':
                    self._attacker_state = 'catch'
                    next_strategy = self.choose_defender_strategy()
                    self._defender_current_strategy = next_strategy(self._world)

                elif not self._defender_state == 'defence':
                    # self._defender_defence_strat.reset_current_state()
                    self._defender_state = 'defence'
                    next_strategy = self.choose_defender_strategy()
                    self._defender_current_strategy = next_strategy(self._world)
                return self._defender_current_strategy.generate()

            # We have the ball in our zone, so we grab and pass:
            else:
                # Check if we should switch from a grabbing to a scoring strategy.
                if  self._defender_state == 'grab' and self._defender_current_strategy.current_state == 'GRABBED':
                    self._defender_state = 'pass'
                    next_strategy = self.choose_defender_strategy()
                    self._defender_current_strategy = next_strategy(self._world)

                # Check if we should switch from a defence to a grabbing strategy.
                elif self._defender_state == 'defence':
                    self._defender_state = 'grab'
                    next_strategy = self.choose_defender_strategy()
                    self._defender_current_strategy = next_strategy(self._world)

                return self._defender_current_strategy.generate()

        else:
            # If ball is not in our defender or attacker zones, defend:
            if self._world.pitch.zones[their_defender.zone].isInside(ball.x, ball.y):
                if not self._attacker_state == 'defence':
                    self._attacker_state = 'defence'
                    next_strategy = self.choose_attacker_strategy()
                    self._attacker_current_strategy = next_strategy(self._world)
                return self._attacker_current_strategy.generate()

            # If ball is in our attacker zone, then grab the ball and score:
            elif self._world.pitch.zones[our_attacker.zone].isInside(ball.x, ball.y):

                # Check if we should switch from a grabbing to a scoring strategy.
                if  self._attacker_state == 'grab' and self._attacker_current_strategy.current_state == 'GRABBED':
                    self._attacker_state = 'score'
                    next_strategy = self.choose_attacker_strategy()
                    self._attacker_current_strategy = next_strategy(self._world)

                # Check if we should switch from a defence to a grabbing strategy.
                elif self._attacker_state in ['defence', 'catch'] :
                    self._attacker_state = 'grab'
                    next_strategy = self.choose_attacker_strategy()
                    self._attacker_current_strategy = next_strategy(self._world)

                return self._attacker_current_strategy.generate()
            else:
                if self._attacker_state == 'catch':
                    next_strategy = self.choose_attacker_strategy()
                    self._attacker_current_strategy = next_strategy(self._world)
                    return self._attacker_current_strategy.generate()
                return calculate_motor_speed(0, 0)
