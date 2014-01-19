from nxt.sensor import *
from nxt.motor import *
from common import Connection


connection = Connection(name='NXT')
BRICK = connection.brick
MOTOR_L = Motor(BRICK, PORT_C)
MOTOR_R = Motor(BRICK, PORT_B)
LIGHT = Light(BRICK, PORT_A)

THRESHOLD_WHITE = 390
SPEED_FACTOR = 7
SPEED = 5 * SPEED_FACTOR


LIGHT.set_illuminated(True)



def stop():
    MOTOR_R.brake()
    MOTOR_L.brake()

def idle():
    MOTOR_R.idle()
    MOTOR_L.idle()

def turn_left(left=15, right=35):
    green_found = False
    while not green_found:
        intensity = LIGHT.get_sample()
        print intensity

        if intensity <   THRESHOLD_WHITE:
            # run(left, right)
            # stop()
            idle()
            green_found = True
            return True
        else:
            run(-left, right)

def turn_right(left=35, right=15):
    MOTOR_L.run(left, True)
    MOTOR_R.run(right, True)

def run(left, right):
    MOTOR_L.run(left, True)
    MOTOR_R.run(right, True)

def reverse():
    MOTOR_R.run(-30, True)
    MOTOR_L.run(-30, True)

def forward(speed=35):
    MOTOR_L.run(speed, True)
    MOTOR_R.run(speed, True)

def follow_border():
    intensity = LIGHT.get_sample()

def is_border(intensity):
    return intensity > THRESHOLD_WHITE

def find_border():
    intensity = LIGHT.get_sample()

    border_found = False
    while not border_found:
        intensity = LIGHT.get_sample()
        print intensity
        if intensity < THRESHOLD_WHITE:
            run(SPEED, SPEED)
        else:
            border_found = True
            # stop()
            idle()
            print 'Border Found!'
            return True

