from models import *
from collisions import *
from strategies import *
from utilities import *


class Planner:

    def __init__(self, our_side):
        self._world = World(our_side)
        self._world.our_defender.catcher_area = {'width' : 30, 'height' : 15, 'front_offset' : 20}
        self._world.our_attacker.catcher_area = {'width' : 30, 'height' : 25, 'front_offset' : 10}
        self._defender_defence_strat = DefaultDefenderDefence(self._world)
        self._defender_attack_strat = DefaultDefenderAttack(self._world)
        self._attacker_defence_strat = DefaultAttackerDefend(self._world)
        # self._attacker_attack_strat = DefaultAttackerAttack(self._world)
        self._attacker_attack_strat = AttackerScoreDynamic(self._world)
        # self._attacker_attack_strat = AttackerGrabGeneral(self._world)
        self._defender_state = 'defence'
        self._attacker_state = 'defence'

    @property
    def attacker_strat_state(self):
        if self.attacker_state == 'defence':
            return self._attacker_defence_strat.current_state
        else:
            return self._attacker_attack_strat.current_state

    @property
    def defender_strat_state(self):
        if self.defender_state == 'defence':
            return self._defender_defence_strat.current_state
        else:
            return self._defender_attack_strat.current_state

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
                return calculate_motor_speed(0, 0)
