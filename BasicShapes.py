from QtApp import *
import numpy as np


class BasicShape:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.child_shapes = None

    def set(self, **kwargs):
        for tag, value in kwargs:
            if isinstance(value, type(self.__getattribute__(tag))):
                self.__setattr__(tag, value)
            else:
                raise ValueError()
        self.update_coordinates()

    def update_coordinates(self):
        pass

    def send_init_params(self):
        return {
            "x": type(float),
            "y": type(float),
            "z": type(float)
        }, self.set

    def draw_shape(self):
        pass


class Point(BasicShape):
    def __init__(self, x: float, y: float, z: float):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

    def draw_shape(self):
        glBegin(GL_POINTS)
        glColor3f(1.0, 0, 0)
        glVertex3f(self.x, self.y, self.z)
        glEnd()

    @property
    def np_vector(self):
        return np.array([self.x, self.y, self.z])


class Segment(BasicShape):
    def __init__(self, a: Point, b: Point):
        super().__init__()
        self.point_a = a
        self.point_b = b

    def draw_shape(self):
        glColor3f(0, 0, 0)
        glBegin(GL_LINE)
        glVertex3fv(self.point_a.np_vector)
        glVertex3fv(self.point_b.np_vector)
        glEnd()

    def update_coordinates(self):
        self.point_a.x += self.x
        self.point_a.y += self.y
        self.point_a.z += self.z
        self.point_b.x += self.x
        self.point_b.y += self.y
        self.point_b.z += self.z
        self.x = 0
        self.y = 0
        self.z = 0


class Figure2(BasicShape):
    def __init__(self, points: list[Point]):
        super().__init__()
        self.points = list(points)

    def draw_shape(self):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 0.2, 0.5, 1.0])
        first_point = self.points[0].np_vector
        for i in range(2, len(self.points)):
            glBegin(GL_POLYGON)
            normal_vec = np.cross(self.points[i].np_vector - first_point,
                                  self.points[i - 1].np_vector - first_point)
            glNormal3fv(normal_vec)
            glVertex3fv(first_point)
            glVertex3fv(self.points[i - 1].np_vector)
            glVertex3fv(self.points[i].np_vector)
            glEnd()

    def update_coordinates(self):
        for point in self.points:
            point.x += self.x
            point.y += self.y
            point.z += self.z
        self.x = 0
        self.y = 0
        self.z = 0


class Contur2(BasicShape):
    def __init__(self, segments: list[Segment]):
        super().__init__()
        self.segments = list(segments)


class Plane(BasicShape):
    def __init__(self, point):
        super().__init__()
        self.normal = np.array([0.0, 0.0, 0.0], dtype=float)
        self.point_a = point
        self.redraw = 0
        self.contur = []

    def update_plane(self):
        pass

    def update_contur(self):
        for contur in self.contur:
            for i in range(len(contur.segments)):
                new_z = self.count_new_z(contur.segments[i].point_a.x,
                                         contur.segments[i].point_a.y)
                contur.segments[i].point_a.z = new_z
                contur.segments[i - 1].point_b.z = new_z

    def count_new_z(self, x, y):
        return ((self.point_a.x - x) * self.normal[0] +
                (self.point_a.y - y) * self.normal[1] +
                self.point_a.z * self.normal[2]) / self.normal[2]

    def draw_shape(self):
        if self.redraw > 0:
            self.redraw -= 1
            return
        self.redraw = np.random.randint(10, 20)
        self.update_plane()
        glEnable(GL_TEXTURE_2D)
        glColor3fv(0.7, 0.7, 0.7)
        glBegin(GL_POLYGON)
        if len(self.contur) > 0:
            for segment in self.contur[0]:
                glVertex3fv(segment.point_a.x,
                            segment.point_a.y,
                            segment.point_a.z)
        else:
            glVertex3fv(10000, 10000, self.count_new_z(10000, 10000))
            glVertex3fv(10000, -10000, self.count_new_z(10000, -10000))
            glVertex3fv(-10000, -10000, self.count_new_z(-10000, -10000))
            glVertex3fv(-10000, 10000, self.count_new_z(-10000, 10000))
        glEnd()
        glDisable(GL_TEXTURE_2D)


class PlaneBy3Point(Plane):
    def __init__(self, point_a, point_b, point_c):
        super().__init__(point_a)
        self.point_b = point_b
        self.point_c = point_c
        self.update_plane()

    def update_plane(self):
        self.normal = np.cross(self.point_a.np_vector -
                               self.point_b.np_vector,
                               self.point_c.np_vector -
                               self.point_b.np_vector)
        self.update_contur()


class PlaneByPointSegment(PlaneBy3Point):
    def __init__(self, point: Point, segment: Segment):
        super().__init__(point, segment.point_a, segment.point_b)
        
        
class PlaneByPlane(Plane):
    def __init__(self, point, plane):
        super().__init__(point)
        self.base_plane = plane
        self.update_plane()

    def update_plane(self):
        self.normal = np.array(self.base_plane.normal)
        self.update_contur()