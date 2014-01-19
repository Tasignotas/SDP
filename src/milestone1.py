from nxt.sensor import *
from nxt.motor import *
from common import Connection


# Connect to the brick
connection = Connection(name='GRP7D')
BRICK = connection.brick

# Constants
THRESHOLD_WHITE = 390
SPEED_FACTOR = 5
SPEED = 5 * SPEED_FACTOR


def is_border(intensity):
    return intensity > THRESHOLD_WHITE


class Robot:

    MOTOR_L = Motor(BRICK, PORT_B)
    MOTOR_R = Motor(BRICK, PORT_C)
    LIGHT_L = Light(BRICK, PORT_3)
    LIGHT_R = Light(BRICK, PORT_2)

    def stop(self):
        MOTOR_R.brake()
        MOTOR_L.brake()

    def idle(self):
        MOTOR_R.idle()
        MOTOR_L.idle()

    def run(self, left=SPEED, right=SPEED):
        MOTOR_L.run(left, True)
        MOTOR_R.run(right, True)

    def reverse(self, left=SPEED, right=SPEED):
        self.run(-left, -right)



class Attack(Robot):

    def __init__(self):
        LIGHT_L.set_illuminated(True)
        LIGHT_R.set_illuminated(True)

    def find_border(self):
        intenstiy_left = LIGHT_L.get_sample()
        intensity_right = LIGHT_R.get_sample()

        border_found = False
        while not border_found:
            intenstiy_left = LIGHT_L.get_sample()
            intensity_right = LIGHT_R.get_sample()

            print 'LIGHT L:', intenstiy_left, 'LIGHT_R:', intensity_right

            if intensity_left < THRESHOLD_WHITE and intensity_right < THRESHOLD_WHITE:
                run(SPEED, SPEED)
            else:
                border_found = True
                # stop()
                idle()
                print 'Border Found!'
                return True




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

# def turn_right(left=35, right=15):
#     MOTOR_L.run(left, True)
#     MOTOR_R.run(right, True)

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





