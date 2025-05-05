from OpenGL.GL import *
from OpenGL.GLU import *


class BasicShape:
    def __init__(self, uniq_name: str):
        self.name = uniq_name
        self.x = 0
        self.y = 0
        self.z = 0
        self.child_shapes = list()

    def set(self, *args, **kwargs):
        for tag, value in kwargs:
            if isinstance(value, type(self.__getattribute__(tag))):
                self.__setattr__(tag, value)
            else:
                raise ValueError()

    def send_init_params(self):
        pass

    def draw_shape(self):
        pass


class Point(BasicShape):
    def __init__(self, uniq_name: str, x: float, y: float, z: float):
        super().__init__(uniq_name)
        self.x = x
        self.y = y
        self.z = z

    def draw_shape(self):
        glBegin(GL_POINT)
        glPointParameterfv([self.x, self.y, self.z])
        glEnd()

    def send_init_params(self):
        return {
            "name": type(str),
            "x": type(float),
            "y": type(float),
            "z": type(float),
        }, self.set


class Segment(BasicShape):
    def __init__(self, uniq_name, a: Point, b: Point):
        super().__init__(uniq_name)
        self.point_a = a
        self.point_b = b

    def draw_shape(self):
        glBegin(GL_LINE)
        glVertex3fv([self.x + self.point_a.x,
                     self.y + self.point_a.y,
                     self.z + self.point_a.z])
        glVertex3fv([self.x + self.point_b.x,
                     self.y + self.point_b.y,
                     self.z + self.point_b.z])
        glEnd()

    def send_init_params(self):
        return {
            "name": type(str),
            "x": type(float),
            "y": type(float),
            "z": type(float)
        }, self.set


class Figure2(BasicShape):
    def __init__(self, uniq_name, points: list[Point]):
        super().__init__(uniq_name)
        self.points = points

    def draw_shape(self):
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_POLYGON)
        for point in self.points:
            glVertex3fv(point.x, point.y, point.z)
        glEnd()
        glDisable(GL_TEXTURE_2D)