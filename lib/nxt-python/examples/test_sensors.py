#!/usr/bin/env python

import nxt.locator
from nxt.sensor import *
from nxt.motor import *

b = nxt.locator.find_one_brick(name="NXT")
m_left = Motor(b, PORT_B)
m_right = Motor(b, PORT_A)
# print 'Touch:', Touch(b, PORT_1).get_sample()
# print 'Sound:', Sound(b, PORT_2).get_sample()
l = Light(b, PORT_3)
l.set_illuminated(True)
val = l.get_sample()
m_left.run(50,True)
m_right.run(50,True)
while True:
    print val
    if val > 390:
        m_right.brake()
        m_left.brake()
        m_left.turn(-100,20)
        m_left.run(50,True)
        m_right.run(50,True)
    val = l.get_sample()
#while True:
#    print 'Light:', l.get_sample()
# print 'Ultrasonic:', Ultrasonic(b, PORT_4).get_sample()
