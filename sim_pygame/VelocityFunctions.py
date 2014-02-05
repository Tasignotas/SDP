"""
We are taking advantage of chipmunk's allowance for custom velocity functions to add z-axis friction to our objects.
This is getting around the fact that chipmunk is really supposed to be used for side-on 2d simulations, not top-down.
"""
from math import cos, sin

from Funcs import vecMult
from Params import Params
class BallVelocity:
    """ Simulate friction on the ball """
    def __call__(self, body, gravity, damping, dt):
        vel = tuple(body.velocity)
        damping *= Params.ballFriction
        damping *= dt
        damping = 1-damping
        body.velocity = tuple(map(lambda v: v*damping, vel)) 
		

class RobotVelocity:
    """ Simulation friction on the Robots """
    def __init__(self, robot):
        self._robot = robot
    def __call__(self, body, gravity, damping, dt):
        damping *= Params.robotFriction
        damping *= dt
        damping = 1-damping
        body.velocity = vecMult((damping,)*2, body.velocity)

class WheelVelocity:
    """ Simulate wheels turning """
    def __init__(self, parentBody, wheelVelFunction):
        self._wheelVelFunc = wheelVelFunction
        self._parentBody = parentBody
    def __call__(self, body, gravity, damping, dt):
        # Simulate wheels turning
        a = self._parentBody.angle
        wheelSpeed = self._wheelVelFunc()
        vx = wheelSpeed*cos(a)
        vy = wheelSpeed*sin(a)

        body.velocity = (vx, vy)
