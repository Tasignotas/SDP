#By Ignotas

from nxt.sensor import *
from nxt.motor import *
from common import Connection


# Connect to the brick
connection = Connection(name='GRP7D')
BRICK = connection.brick

# Constants
THRESHOLD_WHITE = 325
SPEED_FACTOR = 6
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
        

class Attack(Robot):


    def run_boundry(self):        
        while True:
            intensity_left = self.LIGHT_L.get_sample()
            print 'LIGHT L:', intensity_left
            if intensity_left < THRESHOLD_WHITE:
                self.run(SPEED, SPEED + 1)    
            else:
                self.turn(5, -5)
