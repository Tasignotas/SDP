""" pygame drawing functions for various objects """
from math import cos, sin, pi

from Funcs import get_robot_vertices, rotateAbout
from Params import Params

import pygame
# Some colours
red    = (239,  39,  19)
green  = ( 70, 111,  32)
blue   = ( 12, 170, 205)
yellow = (234, 234,  45)
white  = (255, 255, 255)

def drawPitch(screen, w, h):
    """ Draw the pitch """
    centrewidth = w/2
    rightwidth = (w/4)*3
    leftwidth = w/4

    z = -2

    print(centrewidth)
    print(rightwidth)
    pygame.draw.line(screen, white, (centrewidth, 0), (centrewidth, h), 25)
    pygame.draw.line(screen, white, (leftwidth, 0), (leftwidth, h), 25)
    pygame.draw.line(screen, white, (rightwidth, 0), (rightwidth, h), 25) 
    pygame.draw.line(screen, white, (45, 0), (0, h/8), 10)  # Tuples are of form start(x,y), stop(x,y)
    pygame.draw.line(screen, white, (w-100, -45), (w, h/8), 10)
    pygame.draw.line(screen, white, (w, h-45), (w-45, h), 10)
    pygame.draw.line(screen, white, (45, h), (0, h-45), 10)


def drawRobot(screen, colour, (x, y), (w, b), a, (kx, ky), ka):
    """ Draw a robot and its kicker """
    x2 = x+((b/2)*cos(float(a)))
    y2 = y+((b/2)*sin(float(a)))
    middle = (x, y)

    points = map( lambda point: rotateAbout(point, middle, a)
                , get_robot_vertices((x, y), (w, b))
                )

    kickerPoints = map( lambda point: rotateAbout(point, (kx, ky), ka)
                      , get_robot_vertices((kx, ky), Params.kickerDims)
                      )

    pygame.draw.polygon(screen, darken(colour), kickerPoints)
    pygame.draw.polygon(screen, colour, points)
    pygame.draw.line(screen, white, middle, (x2, y2), 2)
    pygame.draw.circle(screen, darken(colour), middle, 10, 0)

def drawBall(screen, (x, y), radius):
    """ Draw the ball """
    pygame.draw.circle(screen, red, (x, y), radius, 0)

def darken((R, G, B)):
    """ Make a colour a little darker """
    return (R/4, G/4, B/4)
