# Implements position and orientation control system described at http://www.dca.ufrn.br/~adelardo/artigos/ICINCO04a.pdf


from math import sqrt, pow, cos, sin, atan


def find_path(tracker, target):
    reference_position = moving_reference_generator(tracker, target)
    path = position_control_system(tracker, reference_position)
    return path


def moving_reference_generator(tracker, target):
    x = tracker.get_x()
    y = tracker.get_y()
    angle = tracker.get_angle()
    delta_x_d = target.get_x() - x
    delta_y_d = target.get_y() - y
    delta_d = sqrt(pow(delta_x_d,2) + pow(delta_y_d, 2))
    beta = atan(delta_y_d / delta_x_d)
    gamma = beta - target.get_angle()
    x_reference = x + (delta_d * cos(beta - gamma))
    y_reference = y + (delta_d * sin(beta - gamma))
    return (x_reference, y_reference)


def position_control_system(tracker, reference):
    x = tracker.get_x()
    y = tracker.get_y()
    angle = tracker.get_angle()
    delta_x_reference = reference[0] - x
    delta_y_reference = reference[1] - y
    delta_phi = atan(delta_y_reference / delta_x_reference) - angle
    delta_iota = sqrt(pow(delta_x_reference, 2) + pow(delta_y_reference, 2))
    delta_lambda = delta_iota * cos(delta_phi)
    return (delta_lambda, delta_phi)
