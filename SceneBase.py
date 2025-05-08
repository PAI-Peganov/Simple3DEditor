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

    def add_figure2_n(self, name: str, n: int):
        points = [f"figure2_point_{name}_{i}" for i in range(1, n + 1)]
        for i, name in enumerate(points):
            self.entities[name] = Point(math.sin(math.pi * i / n * 2),
                                        math.cos(math.pi * i / n * 2),
                                        0)
        self.add_figure2(name, points)

    def add_plane_by_points(self, name: str, point1_name: str,
                            point2_name: str, point3_name: str):
        point1 = self.entities[point1_name]
        point2 = self.entities[point2_name]
        point3 = self.entities[point3_name]
        if is_point_collinear(point1, point2, point3):
            raise ValueError()
        self.entities[name] = PlaneBy3Point(point1, point2, point3)

    def add_plane_by_point_and_segment(self, name: str, point_name: str,
                                       segment_name: str):
        point1 = self.entities[point_name]
        point2 = self.entities[segment_name].point_a
        point3 = self.entities[segment_name].point_b
        if is_point_collinear(point1, point2,point3):
            raise ValueError()
        self.entities[name] = PlaneBy3Point(point1, point2, point3)

    def add_plane_by_plane(self, name: str, point_name:str,
                           plane_name: str):
        point = self.entities[point_name]
        plane = self.entities[plane_name]
        self.entities[name] = PlaneByPlane(point, plane)

    def add_contur_to_plane(self, plane_name: str,
                            segments_names: list[str]):
        plane = self.entities[plane_name]
        plane.add_contur([self.entities[segment_name]
                          for segment_name in segments_names])

    def add_figure3(self, name: str, faces_names: list[str]):
        self.entities[name] = Figure3([self.entities[face_name]
                                       for face_name in faces_names])

    def add_prism_n(self, name: str, n: int):
        upper_points = [f"pnt_upr_{name}_{i}" for i in range(1, n + 1)]
        lower_points = [f"pnt_lwr_{name}_{i}" for i in range(1, n + 1)]
        for i, (name_u, name_l) in enumerate(zip(upper_points, lower_points)):
            self.entities[name_u] = Point(math.sin(math.pi * i / n * 2),
                                          math.cos(math.pi * i / n * 2),
                                          1)
            self.entities[name_l] = Point(math.sin(math.pi * i / n * 2),
                                          math.cos(math.pi * i / n * 2),
                                          -1)
        faces = [f"face_upper_{name}", f"face_lower_{name}"]
        self.add_figure2(faces[0], upper_points)
        self.add_figure2(faces[1], lower_points)
        for i in range(1, n + 1):
            faces.append(f"face_middle_{name}_{i}")
            self.add_figure2(faces[-1], [upper_points[i - 1],
                                         upper_points[i % n],
                                         lower_points[i % n],
                                         lower_points[i - 1]])
        self.add_figure3(name, faces)


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