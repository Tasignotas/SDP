# By Ignotas

from nxt.sensor import *
from nxt.motor import *
from common import Connection


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
        self.LIGHT_L = Light(BRICK, PORT_3)
        self.LIGHT_R = Light(BRICK, PORT_2)
        self.LIGHT_L.set_illuminated(True)
        self.LIGHT_R.set_illuminated(True)


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

    def find_border(self):
        intensity_left = self.LIGHT_L.get_sample()
        intensity_right = self.LIGHT_R.get_sample()

        border_found = False
        while not border_found:
            intensity_left = self.LIGHT_L.get_sample()
            intensity_right = self.LIGHT_R.get_sample()

            print 'LIGHT L:', intensity_left, 'LIGHT_R:', intensity_right

            if intensity_left < THRESHOLD_WHITE and intensity_right < THRESHOLD_WHITE:
                self.run(SPEED, SPEED)
            else:
                border_found = True
                self.stop()
                self.idle()
                print 'Border Found!'
                return True

    def align_to_border(self, left=False, right=False):
        if not (left or right):
            return
        self.reverse(10,10)
        self.run()

    def run_boundry(self):
        self.find_border()
        intensity_left = self.LIGHT_L.get_sample()
        intensity_right = self.LIGHT_R.get_sample()        
        while True:
            intensity_left = self.LIGHT_L.get_sample()
            intensity_right = self.LIGHT_R.get_sample()
            print 'LIGHT L:', intensity_left, 'LIGHT_R:', intensity_right
            if intensity_left < THRESHOLD_WHITE and intensity_right < THRESHOLD_WHITE:
                self.turn(-10, 10)
            elif intensity_left > THRESHOLD_WHITE and intensity_right > THRESHOLD_WHITE:
                self.turn(10, -10)
            else:
                self.run(SPEED, SPEED)



# def stop():
#     MOTOR_R.brake()
#     MOTOR_L.brake()

# def idle():
#     MOTOR_R.idle()
#     MOTOR_L.idle()

# def turn_left(left=15, right=35):
#     green_found = False
#     while not green_found:
#         intensity = LIGHT.get_sample()
#         print intensity

#         if intensity <   THRESHOLD_WHITE:
#             # run(left, right)
#             # stop()
#             idle()
#             green_found = True
#             return True
#         else:
#             run(-left, right)


# def run(left, right):
#     MOTOR_L.run(left, True)
#     MOTOR_R.run(right, True)

# def reverse():
#     MOTOR_R.run(-30, True)
#     MOTOR_L.run(-30, True)

# def forward(speed=35):
#     MOTOR_L.run(speed, True)
#     MOTOR_R.run(speed, True)

# def follow_border():
#     intensity = LIGHT.get_sample()
