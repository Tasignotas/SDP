import vision

def update(ball, robotA, robotB, robotC, robotD):
    ball.position = vision.get_ball()
    robotA.position = vision.get_robotA()
    robotB.position = vision.get_robotB()
    robotC.position = vision.get_robotC()
    robotD.position = vision.get_robotD()
    return (ball, robotA, robotB, robotC, robotD)

