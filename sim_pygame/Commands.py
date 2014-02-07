""" Command objects to be put on a multiprocess queue and executed at the other side. """
from math import radians
from Funcs import simpleAngle

class Kick:
    """ Kick the ball """
    def __call__(self, robot):
        # TODO: implement me
        robot.kick()

class Move:
    """ Set motor speeds """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, robot):
        robot.move(self.left, self.right)

class Turn:
    """ Turn by angle """
    def __init__(self, angle):
        self.angle = simpleAngle(radians(angle))
    def __call__(self, robot):
        robot.turn(self.angle)

class Stop:
    """ Cease all motion """
    def __call__(self, robot):
        robot.move(0,0)

