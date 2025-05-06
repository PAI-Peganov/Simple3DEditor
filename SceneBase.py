from collections import deque, defaultdict
from BasicShapes import *


class Scene:
    def __init__(self):
        self.path = None
        self.entities = dict()
        self.stack_last_actions = deque()
        self.stack_undo_actions = deque()

    def read_entities_from_file(self, path):
        pass

    def add_point(self, name: str, x: float, y: float, z: float):
        self.entities[name] = Point(x, y, z)

    def add_segment(self, name: str, point_a_name: str, point_b_name: str):
        self.entities[name] = Segment(self.entities[point_a_name],
                                      self.entities[point_b_name])

    def add_figure2(self, name: str, point_names: list[str]):
        self.entities[name] = Figure2([self.entities[el]
                                       for el in point_names])

    def add_plane_3point(self, name:str, point1_name,
                         point2_name, point3_name):
        point1 = self.entities[point1_name]
        point2 = self.entities[point2_name]
        point3 = self.entities[point3_name]
        if is_point_collinear(point1, point2, point3):
            raise ValueError()
        self.entities[name] = PlaneBy3Point(point1, point2, point3)


def is_point_collinear(*args):
    if len(args) < 3:
        return True
    zero_point = args[0]
    direction_vector = np.array([args[1].x - zero_point.x,
                                 args[1].y - zero_point.y,
                                 args[1].z - zero_point.z])
    for arg in args[2:]:
        checked_vector = np.array([arg.x - zero_point.x,
                                   arg.y - zero_point.y,
                                   arg.z - zero_point.z])
        if np.linalg.norm(np.cross(direction_vector, checked_vector)) < 1e-7:
            return True
    return False