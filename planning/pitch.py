from json import load
from numpy import array
from cv2 import pointPolygonTest


class Pitch:


    def __init__(self):
        config_file = open('../vision/calibrate.json', 'r')
        config_json = load(config_file)
        config_file.close()
        # Getting the zones:
        self.zones = []
        self.zones.append(Polygon(config_json['Zone_0']))
        self.zones.append(Polygon(config_json['Zone_1']))
        self.zones.append(Polygon(config_json['Zone_2']))
        self.zones.append(Polygon(config_json['Zone_3']))


    def is_within_bounds(self, robot, point):
    # Checks whether the position/point planned for the robot is reachable:
        zone = self.zones[robot.zone]
        zone_coords = array([[point.x, point.y] for point in zone.points])
        return pointPolygonTest(zone_coords, (point.x, point.y), False)


class Polygon:


    def __init__(self, coord_array):
        self.points = []
        for coords in coord_array:
            self.points.append(Point(*coords))


    def __repr__(self):
        return ''.join([point.__repr__() for point in self.points])


class Point:


    def __init__(self, x, y):
        self.x = x
        self.y = y


    def __repr__(self):
        return 'x: %s, y: %s\n' % (self.x, self.y)
