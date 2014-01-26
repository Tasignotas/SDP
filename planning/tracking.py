import math
import movement

def Track(tracker, target):
    pr = MRG(tracker, target)
    err = PCS(tracker, pr)
    movement.forward(err[0])
    movement.turn(err[1])

def MRG(self, tracker, target):
    x = tracker.position[0]
    y = tracker.position[1]
    r = tracker.position[2]
    dxd = target.position[0] - x
    dyd = target.position[1] - y
    dd = math.sqrt(math.pow(dxd,2) + math.pow(dyd, 2))
    b = math.atan(dyd / dxd)
    g = b - target.position[2]
    xr = x + (dd * math.cos(b - g))
    yr = y + (dd * math.sin(b - g))
    return (xr, yr)

def PCS(self, tracker, (xr, yr)):
    x = tracker.position[0]
    y = tracker.position[1]
    r = tracker.position[2]
    dyr = yr - y
    dxr = xr - x
    dr = math.atan(dyr / dxr)
    er = dr - r
    dl = math.sqrt(math.pow(dxr, 2) + math.pow(dyr, 2))
    dt = math.atan(dxr / dxr) - r
    es = dl * math.cos(dt)
    return (es, er)