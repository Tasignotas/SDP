from math import pi, sqrt, fsum, hypot, cos, sin, atan2, degrees
import operator

def vecPlus(a, b):
    return map(operator.add, a, b)

def vecSub(a, b):
    return map(operator.sub, a, b)

def vecMult(a, b):
    return tuple(map(operator.mul, a, b))

def vecNorm(vec):           # warning - works only for two dimensions!
    return hypot(*vec)

def weightNorm(vec):
    """so it sums to 1"""
    S = sum(vec)
    return map(lambda x: float(x)/S, vec)

def vecNormalise(vec):
    return map(lambda x: float(x)/vecNorm(vec), vec)

def vecDist(a, b):
    return vecNorm(vecSub(a, b))
    
def angleDiff(a,b):
    return simpleAngle(a-b)
    
def vecAngle(a, b):
    try:
        v = vecSub(a,b)
        return atan2(v[1], v[0])
    except TypeError:
        return 0

def dotProduct(a, b):
    return fsum(vecMult(a, b))

def get_robot_vertices((x, y), (w, b)):
    hw, hb = w/2, b/2
    return [(x-hb, y-hw), (x-hb, y+hw), (x+hb, y+hw), (x+hb, y-hw)]

def rotate(point, angle):
    (x, y) = point
    sint = sin(angle)
    cost = cos(angle)
    return (cost*x-sint*y, sint*x+cost*y)

def rotateAbout(vector, point, angle):
    return tuple(map(operator.add, point, rotate(map(operator.sub, vector, point), angle)))

def simpleAngle(a):
    while a >= pi:
        a -= 2*pi
    while a <= -pi:
        a += 2*pi
    return a
    
def convert(point,fromUnitLen, toUnitLen, shift=0, offset=None, integer=False): 
    # shift=1 changes for example from (-1,1) to (0,2), shift=-1  changes the other way around.
    if offset:
        point = vecSub(point, offset)
    scale = float(toUnitLen) / fromUnitLen
    try:
        vec = vecPlus(map(lambda x:x*scale, point), map(lambda x: shift*x, (toUnitLen/2,toUnitLen/4)))
        if integer:
            return map(lambda x: int(x), vec)
        return vec
    except TypeError:
        sc= point*scale
        if integer:
            return int(sc)
        return sc
        
        
        
        
def getWheelSpeeds(pos, orient, gpos):

    maxspeed = 127

    alpha = vecAngle(gpos,pos)
    angle = simpleAngle(alpha-orient)   

    angle_to_turn_factor = 100
    if degrees(abs(angle)) < 3:
        return(maxspeed, maxspeed)
    a = abs(angle)
    smaller = max(int(maxspeed-(a*angle_to_turn_factor)), -maxspeed)   
    if angle >= 0:       
        return(maxspeed, smaller)
    elif angle < 0:
        return(smaller, maxspeed)

def computeKickingPosition(ball,goal,dist):
    norm = vecNormalise(vecSub(goal, ball))
    return map(lambda (x,y): y-x*dist,zip(norm,ball))

def getRectangle(pos, orient, width, length):
        
    cornerFL = rotateAbout((pos[0] + length/2, pos[1] + width/2), pos, orient)
    cornerBL = rotateAbout((pos[0] - length/2, pos[1] + width/2), pos, orient)
    cornerBR = rotateAbout((pos[0] - length/2, pos[1] - width/2), pos, orient)
    cornerFR = rotateAbout((pos[0] + length/2, pos[1] - width/2), pos, orient)  
    
    return map(lambda (x,y): (int(x),int(y)), (cornerFL, cornerBL, cornerBR, cornerFR) )
