#!/usr/bin/env python

import nxt.locator
from nxt.sensor import *
from nxt.motor import *

b = nxt.locator.find_one_brick(name="NXT")
m_left = Motor(b, PORT_B)
m_right = Motor(b, PORT_A)
# print 'Touch:', Touch(b, PORT_1).get_sample()
# print 'Sound:', Sound(b, PORT_2).get_sample()
l1 = Light(b, PORT_2)
l2 = Light(b, PORT_3)
l1.set_illuminated(True)
l2.set_illuminated(True)
val_right_light = l1.get_sample()
val_left_light = l2.get_sample()
m_left.run(50,True)
m_right.run(50,True)
while True:
    print "Right value:", val_right_light
    print "Left value: ", val_left_light
    if val_right_light > 390 and val_left_light > 390:
    	m_right.brake()
        m_left.brake()
        m_left.turn(-127,360)
        m_left.run(35,True)
        m_right.run(35,True)
    elif val_right_light > 390:
        m_right.brake()
        m_left.brake()
        m_left.turn(-127,90)
        m_left.run(35,True)
        m_right.run(35,True)
    elif val_left_light > 390:
    	m_right.brake()
        m_left.brake()
        m_right.turn(-127,90)
        m_left.run(35,True)
        m_right.run(35,True)
    val_right_light = l1.get_sample()
    val_left_light = l2.get_sample()
#while True:
#    print 'Light:', l.get_sample()
# print 'Ultrasonic:', Ultrasonic(b, PORT_4).get_sample()
