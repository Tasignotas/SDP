import unittest
from planning.models import World
from planning.strategies import AttackerScoreDynamic


class AttackerScoreDynamicTestCase(unittest.TestCase):

    def setUp(self):
        self.world = World('left')
        self.strategy = AttackerScoreDynamic(self.world)

    def test_strategy_initializes(self):
        self.assertFalse(None, self.strategy)
