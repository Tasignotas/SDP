import vision

def update_pitch(pitch):
    pitch.robotA.position = vision.get_robotA()
    pitch.robotB.position = vision.get_robotB()
    pitch.robotC.position = vision.get_robotC()
    pitch.robotD.position = vision.get_robotD()
    pitch.ball.position = vision.get_ball()

    return pitch