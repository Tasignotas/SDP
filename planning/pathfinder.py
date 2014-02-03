# Implements position and orientation control system described at http://www.dca.ufrn.br/~adelardo/artigos/ICINCO04a.pdf


import math


def find_path(tracker, target):
    reference_position = moving_reference_generator(tracker, target)
    path = position_control_system(tracker, reference_position)
    return path


def moving_reference_generator(tracker, target):
    x = tracker.get_position()[0]
    y = tracker.get_position()[1]
    angle = tracker.get_orientation()
    delta_x_d = target.get_position()[0] - x
    delta_y_d = target.get_position()[1] - y
    delta_d = math.sqrt(math.pow(delta_x_d,2) + math.pow(delta_y_d, 2))
    beta = math.atan(delta_y_d / delta_x_d)
    gamma = beta - target.get_orientation()
    x_reference = x + (delta_d * math.cos(beta - gamma))
    y_reference = y + (delta_d * math.sin(beta - gamma))
    return (x_reference, y_reference)


def position_control_system(tracker, reference):
    x = tracker.get_position()[0]
    y = tracker.get_position()[1]
    angle = tracker.get_orientation()
    delta_x_reference = reference[0] - x
    delta_y_reference = reference[1] - y
    delta_phi = math.atan(delta_y_reference / delta_x_reference) - angle
    delta_iota = math.sqrt(math.pow(delta_x_reference, 2) + math.pow(delta_y_reference, 2))
    delta_lambda = delta_iota * math.cos(delta_phi)
    return (delta_lambda, delta_phi)