from src.Simple2DEditorImports import *


def set_material(color, shininess=100.0,
                 ambient=0.2, diffuse=0.9, specular=0.001):
    color = np.array(color)
    ambient_val = color * ambient
    ambient_val[3] = color[3]
    diffuse_val = color * diffuse
    diffuse_val[3] = color[3]
    specular_val = np.ones(shape=(4,), dtype=float) * specular
    specular_val[3] = color[3]
    # Настройка материала
    glEnable(GL_LIGHTING)
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient_val)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse_val)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular_val)
    glMaterialfv(GL_FRONT, GL_SHININESS, shininess)


def find_normal_figure2(self):
    points = self.points
    A = np.zeros(shape=(len(points), 3), dtype=float)
    b = np.ones(shape=(len(points),), dtype=float)
    alpha = 1000
    delta = alpha * 1000
    for i, point in enumerate(points):
        A[i, :] = [point.x + np.random.randint(-alpha, alpha) / delta,
                   point.y + np.random.randint(-alpha, alpha) / delta,
                   point.z + np.random.randint(-alpha, alpha) / delta]
    x = np.linalg.solve(A.T @ A, A.T @ b)
    return [x[0], x[1], x[2]]


def out_light(func):
    def result(*args, **kwargs):
        glDisable(GL_LIGHTING)
        func(*args, **kwargs)
        glEnable(GL_LIGHTING)
    return result


@out_light
def draw_point(self):
    glBegin(GL_POINTS)
    glColor3fv(POINT_COLOR[:3])
    glVertex3f(self.x, self.y, self.z)
    glEnd()


@out_light
def draw_segment(self, color=SEGMENT_COLOR):
    glBegin(GL_LINES)
    glColor3fv(color[:3])
    glVertex3fv(self.point_a.np_vector)
    glVertex3fv(self.point_b.np_vector)
    glEnd()


@out_light
def draw_contur2(points, color=SEGMENT_COLOR):
    glBegin(GL_LINE_LOOP)
    glColor3fv(color[:3])
    for point in points:
        glVertex3fv(point.np_vector)
    glEnd()


def draw_figure2(self):
    set_material(FIGURE2_COLOR)
    first_point = self.points[0].np_vector
    # normal_vec = find_normal_figure2(self)
    for i in range(2, len(self.points)):
        normal_vec = np.cross(self.points[i].np_vector - first_point,
                              self.points[i - 1].np_vector - first_point)
        glBegin(GL_POLYGON)
        glNormal3fv(normal_vec)
        glVertex3fv(first_point)
        glVertex3fv(self.points[i - 1].np_vector)
        glVertex3fv(self.points[i].np_vector)
        glEnd()
    draw_contur2(self.points, color=EDGE_COLOR)


def draw_plane(self):
    set_material(PLANE_COLOR)
    glBegin(GL_POLYGON)
    glNormal3fv(self.normal)
    if len(self.contur) > 0:
        for segment in self.contur[0].segments:
            glVertex3fv(segment.point_a.np_vector)
        glEnd()
        draw_contur2([el.point_a for el in self.contur[0].segments])
    else:
        # не забыть: size меньше 2000,
        size = 1000
        glVertex3f(size, size, self.count_new_z(size, size))
        glVertex3f(size, -size, self.count_new_z(size, -size))
        glVertex3f(-size, -size, self.count_new_z(-size, -size))
        glVertex3f(-size, size, self.count_new_z(-size, size))
        glEnd()


def draw_figure3(self):
    for face in self.faces:
        draw_figure2(face)


def draw_light(self):
    glLightfv(self.lightGL, GL_POSITION, [self.x, self.y, self.z, 0.0])
