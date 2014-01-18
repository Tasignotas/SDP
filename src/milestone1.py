from nxt.sensor import *
from nxt.motor import *
from common import Connection


connection = Connection(name='NXT')
BRICK = connection.brick
MOTOR_L = Motor(BRICK, PORT_C)
MOTOR_R = Motor(BRICK, PORT_B)
LIGHT = Light(BRICK, PORT_4)

THRESHOLD_WHITE = 390

def stop():
    MOTOR_R.idle()
    MOTOR_L.idle()

def turn_left(left=15, right=35):
    green_found = False
    while not green_found:
        MOTOR_L.run(left, True)
        MOTOR_R.run(right, True)
        intensity = LIGHT.get_sample()

        if intensity > THRESHOLD_WHITE:
            # run(left, right)
            stop()

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

def find_border():
    intensity = LIGHT.get_sample()

    border_found = False
    while not border_found:
        intensity = LIGHT.get_sample()

        if intensity < THRESHOLD_WHITE:
            forward()
        else:
            border_found = True
            # turn_right(70, -15)
            turn_left()
            # stop()
            print 'Border Found!'