from json import load


class Pitch:


    def __init__(self):
        config_file = open('../vision/calibrate.json', 'r')
        config_json = json.load(config_file)
        config_file.close()
        # Getting the coordinates of the bottom left corner:
        min_x = min([point[0] for point in config_json['outline']])
        min_y = min([point[1] for point in config_json['outline']]) 
        # Getting the zones:       
        self.zones = []
        self.zones.append(Polygon(config_json['Zone_0']))
        self.zones.append(Polygon(config_json['Zone_1']))
        self.zones.append(Polygon(config_json['Zone_2']))
        self.zones.append(Polygon(config_json['Zone_3']))        
        # Making the point coordinates relative to the bottom leftmost point:
        # TODO: figure out why some points become negative!!!
        for zone in self.zones:
            for point in zone.points:
                point.x -= min_x
                point.y -= min_y
    

    def is_within_bounds(self, robot, point):
    # Checks whether the position/point planned for the robot is reachable:
        zone = self.zones[robot.zone]
        return zone.is_point_inside(point)        


class Polygon:

    
    def __init__(self, coord_array):
        self.points = []
        for coords in coord_array:
            self.points.append(Point(*coords))


    def __repr__(self):
        return ''.join([point.__repr__() for point in self.points])


    def is_point_inside(self, point):
        # Method that checks if the point is inside the polygon:    
        n = len(self.points)
        inside = False
        p1x, p1y = self.points[0].x, self.points[0].x 
        for i in range(n + 1):
            p2x, p2y = self.points[i % n].x, self.points[i % n].y
            if point.y > min(p1y, p2y):
                if point.y <= max(p1y, p2y):
                    if point.x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (point.y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or point.x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y
        return inside
        

class Point:

    
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def __repr__(self):
        return 'x: %s, y: %s\n' % (self.x, self.y)
