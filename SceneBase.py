from BasicShapes import *


class EntityNotFoundException(Exception):
    def __init__(self, name):
        super().__init__("Указана несуществующая сущьность {}".format(name))


class EmptyFieldException(Exception):
    def __init__(self):
        super().__init__("В поле ничего не указано")


class EntityNameAlreadyExistsException(Exception):
    def __init__(self):
        super().__init__("Сущьность с таким именем уже существует")


class Scene:
    def __init__(self, app_update: callable):
        self.path = None
        self.app_update = app_update
        self.entities = dict()
        self.stack_last_actions = deque()
        self.stack_undo_actions = deque()

    def load_entities_from_file(self, filepath: Path):
        if filepath.suffix != ".pkl":
            raise TypeError("file is not .pkl")
        with open(filepath, 'rb') as f:
            self.entities = pickle.load(f)
        self.app_update()

    def save_entities_to_file(self, filepath: Path):
        if filepath.suffix != ".pkl":
            raise TypeError("file is not .pkl")
        with open(filepath, 'wb') as f:
            pickle.dump(self.entities, f)

    def check_contains_errors(self, *args, new_entity=None):
        for el in args:
            if len(el) == 0:
                raise EmptyFieldException()
            if self.entities.get(el) is None:
                raise EntityNotFoundException(el)
        if new_entity is not None:
            if len(new_entity) == 0:
                raise EmptyFieldException()
            if self.entities.get(new_entity) is not None:
                raise EntityNameAlreadyExistsException()

    def add_point(self, name: str, x: float, y: float, z: float):
        self.check_contains_errors(new_entity=name)
        self.entities[name] = Point(name, x, y, z)
        self.app_update()

    def add_light(self, name: str, lightGL, x: float, y: float, z: float):
        self.entities[name] = LightPoint(name, lightGL, x, y, z)
        self.app_update()

    def add_segment(self, name: str, point_a_name: str, point_b_name: str):
        self.check_contains_errors(point_a_name, point_b_name,
                                   new_entity=name)
        self.entities[name] = Segment(name,
                                      self.entities[point_a_name],
                                      self.entities[point_b_name])
        self.entities[name].add_children([point_a_name, point_b_name])
        self.app_update()

    def add_figure2(self, name: str, points_names: list[str]):
        self.check_contains_errors(*points_names,
                                   new_entity=name)
        self.entities[name] = Figure2(name,
                                      [self.entities[el]
                                       for el in points_names])
        self.entities[name].add_children(points_names)
        self.app_update()

    def add_figure2_n(self, name: str, n: int, radius: float):
        self.check_contains_errors(new_entity=name)
        points = [f"figure2_point_{name}_{i}" for i in range(1, n + 1)]
        arc = 2 * math.pi / n
        for i, point_name in enumerate(points):
            self.add_point(point_name,
                           math.sin(arc * i) * radius,
                           math.cos(arc * i) * radius,
                           0)
        self.add_figure2(name, points)
        self.app_update()

    def add_plane_by_points(self, name: str, point1_name: str,
                            point2_name: str, point3_name: str):
        self.check_contains_errors(point1_name, point2_name, point3_name,
                                   new_entity=name)
        point1 = self.entities[point1_name]
        point2 = self.entities[point2_name]
        point3 = self.entities[point3_name]
        if is_point_collinear(point1, point2, point3):
            raise ValueError()
        self.entities[name] = PlaneBy3Point(name, point1, point2, point3)
        self.entities[name].add_children([point1_name,
                                          point2_name,
                                          point3_name])
        self.app_update()

    def add_plane_by_point_and_segment(self, name: str, point_name: str,
                                       segment_name: str):
        self.check_contains_errors(point_name, segment_name,
                                   new_entity=name)
        point = self.entities[point_name]
        segment = self.entities[segment_name]
        if is_point_collinear(point, segment.point_a, segment.point_b):
            raise ValueError()
        self.entities[name] = PlaneByPointSegment(name,
                                                  segment.point_a,
                                                  segment.point_b)
        self.entities[name].add_children([point_name,
                                          segment_name])
        self.app_update()

    def add_plane_by_plane(self, name: str, point_name: str,
                           plane_name: str):
        self.check_contains_errors(point_name, plane_name,
                                   new_entity=name)
        point = self.entities[point_name]
        plane = self.entities[plane_name]
        self.entities[name] = PlaneByPlane(name, point, plane)
        self.entities[name].add_children([point_name, plane_name])
        self.app_update()

    def add_contur_to_plane(self, plane_name: str,
                            segments_names: list[str]):
        self.check_contains_errors(plane_name, *segments_names)
        plane = self.entities[plane_name]
        contur_name = f"contur_{plane_name}_{len(plane.contur)}"
        plane.add_contur(Contur2(contur_name,
                                 [self.entities[segment_name]
                                  for segment_name in segments_names]))
        plane.contur[-1].add_children(segments_names)
        self.app_update()

    def add_contur_n_to_plane(self, plane_name: str, n: int, radius: float):
        points = [f"contur_point_{plane_name}_{i}" for i in range(1, n + 1)]
        arc = 2 * math.pi / n
        for i, point_name in enumerate(points):
            self.add_point(point_name,
                           math.sin(arc * i) * radius,
                           math.cos(arc * i) * radius,
                           0)
        segments = []
        for i in range(1, n + 1):
            segments.append(f"segment_{plane_name}_{i}")
            self.add_segment(segments[-1], points[i - 1], points[i % n])
        self.add_contur_to_plane(plane_name, segments)
        self.app_update()

    def add_figure3(self, name: str, faces_names: list[str]):
        self.check_contains_errors(*faces_names,
                                   new_entity=name)
        self.entities[name] = Figure3(name,
                                      [self.entities[face_name]
                                       for face_name in faces_names])
        self.entities[name].add_children(faces_names)
        self.app_update()

    def add_prism_n(self, name: str, n: int, radius: float, height: float):
        self.check_contains_errors(new_entity=name)
        upper_points = [f"pnt_upr_{name}_{i}" for i in range(1, n + 1)]
        lower_points = [f"pnt_lwr_{name}_{i}" for i in range(1, n + 1)]
        arc = 2 * math.pi / n
        for i, (name_u, name_l) in enumerate(zip(upper_points, lower_points)):
            self.add_point(name_u,
                           math.sin(arc * i) * radius,
                           math.cos(arc * i) * radius,
                           height)
            self.add_point(name_l,
                           math.sin(arc * i) * radius,
                           math.cos(arc * i) * radius,
                           0)
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
        self.app_update()


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
