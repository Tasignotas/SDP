from nxt.sensor import *
from nxt.motor import *
import sys
import os
sys.path.append(os.path.abspath('../vision'))
from planning.common import Connection
from vision import Vision

import math

# Connect to the brick
connection = Connection(name='GRP7D')
BRICK = connection.brick

# Constants
THRESHOLD_WHITE = 325
SPEED_FACTOR = 5
SPEED = 5 * SPEED_FACTOR

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

#Very likely to be extremely buggy, more work to be done.
#Also no idea what the angle is relative to.
class Move(Robot):

    def correct_trajectory(self, needed_angle):
        if needed_angle < 0:
	    self.run(SPEED+5,SPEED)
        else:
	    self.run(SPEED,SPEED+5)
		
    def go_to_location(self, location):
        while(1):
	    result = Vision().locate()	#super laggy without threading lololol :1
	    ball_location = result[4][0]	#location of the ball
	    robot_location = result[0][0]	#robot 1?
	    angle = result[0][1]	#is this in radians?

	    distance = math.sqrt((ball_location[1]-robot_location[1])^2 + (ball_location[0]-robot_location[0])^2) #distance between robot and ball

	    needed_angle = math.atan((ball_location[1]-robot_location[1])/(ball_location[0]-robot_location[0])) - angle #in RADIANS

	    if distance >30:
	        if abs(needed_angle) > 0.09:
		    correct_trajectory(needed_angle)
	        else: 
		    self.run(SPEED,SPEED)
	    else: #if closer than 30 pixels to target
	        break
        self.stop()
	

