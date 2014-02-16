
from math import hypot, atan2, cos, sin


def get_boundary_path(robot, (x, y, displacement, theta), zone):
    # Get closest point on path to zone boundary
    while not zone.isInside(x, y):
        plan_x = robot.x + ((displacement-1) * cos(theta))
        plan_y = robot.y + ((displacement-1) * sin(theta))
        x, y, displacement = plan_x, plan_y, displacement-1
    return x, y, displacement, theta


def get_path_to_point(robot, x, y):
    # Get path for robot to a point (x, y)
    delta_x = x - robot.x
    delta_y = y - robot.y
    displacement = hypot(delta_x, delta_y)
    theta = atan2(delta_y, delta_x) - robot.angle
    return x, y, displacement, theta


def get_interception(path, robot):
    # Get path necessary for robot to intercept ball
    center_path = path.center()
    return get_path_to_point(robot, center_path[0], center_path[1])


def get_avoidance(path, robot, obstacle):
    # Get path necessary for robot to avoid obstacles when kicking the ball
    if path.overlaps(obstacle):
        path_width_x = path[2][0] - path[3][0]
        path_width_y = path[2][1] - path[3][1]
        path_width = hypot(path_width_x, path_width_y)
        robot_width = obstacle.get_dimensions()[0]
        min_distance = (path_width * 0.5) + (robot_width * 0.5)
        center_path = path.center()
        delta_x = center_path[0] - obstacle.x
        delta_y = center_path[1] - obstacle.y
        displacement = hypot(delta_x, delta_y)
        path_distance = min_distance - displacement
        theta = atan2(delta_y, delta_x)
        path_x = robot.x + (path_distance * cos(theta))
        path_y = robot.y + (path_distance * sin(theta))
        return get_path_to_point(robot, path_x, path_y)
    else:
        return None