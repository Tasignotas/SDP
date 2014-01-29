#By Ignotas

import time

from nxt.sensor import *
from nxt.motor import *

from planning.common import Connection



# Connect to the brick
connection = Connection(name='GRP7D')
BRICK = connection.brick

# Constants
THRESHOLD_WHITE = 325
SPEED_FACTOR = 5
SPEED = 5 * SPEED_FACTOR


def is_border(intensity):
    return intensity > THRESHOLD_WHITE


class Robot:

    def __init__(self):
        self.MOTOR_L = Motor(BRICK, PORT_B)
        self.MOTOR_R = Motor(BRICK, PORT_C)
        self.LIGHT_L = Light(BRICK, PORT_2)
        self.LIGHT_L.set_illuminated(True)


    def stop(self):
        self.MOTOR_R.brake()
        self.MOTOR_L.brake()

    def idle(self):
        self.MOTOR_R.idle()
        self.MOTOR_L.idle()

    def run(self, left=SPEED, right=SPEED):
        self.MOTOR_L.run(left, True)
        self.MOTOR_R.run(right, True)

    def reverse(self, left=SPEED, right=SPEED):
        self.run(-left, -right)

    def rotate_left(left=SPEED, right=SPEED):
        self.run(-left, right)

    def rotate_right(self, left=SPEED, right=SPEED):
        self.run(left, -right)

    def turn(self, left, right):
        self.MOTOR_L.run(left, True)
        self.MOTOR_R.run(right, True)


    def align_for_boundary(self):
        intensity_left = self.LIGHT_L.get_sample()
        while intensity_left < THRESHOLD_WHITE:
            self.run(SPEED, SPEED)
            intensity_left = self.LIGHT_L.get_sample()
        while intensity_left >= THRESHOLD_WHITE:
            self.turn(4, -4)
            intensity_left = self.LIGHT_L.get_sample()
	self.stop()


    def run_boundary(self, time_to_run):
        timeout = time.time() + time_to_run
        while True:
            if time.time() > timeout:
                break
            intensity_left = self.LIGHT_L.get_sample()
            print 'LIGHT L:', intensity_left
            if intensity_left < THRESHOLD_WHITE:
                self.run(SPEED, SPEED + 2)
            else:
                self.turn(4, -4)
        self.stop()

class Attack(Robot):


    def complete_a_lap(self):
        self.align_for_boundary()
        self.run_boundary(46)


class Defence(Robot):


    def complete_a_lap(self):
        self.align_for_boundary()
        self.run_boundary(41.5)
