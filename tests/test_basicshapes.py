import unittest
from src.Simple2DEditorImports import *


class TestBasicShape(unittest.TestCase):
    def test_init(self):
        shape = BasicShape("test")
        self.assertEqual(shape.name, "test")
        self.assertEqual(shape.x, 0.0)
        self.assertEqual(shape.y, 0.0)
        self.assertEqual(shape.z, 0.0)
        self.assertIsNone(shape.child_shapes)

    def test_set_valid_attributes(self):
        shape = BasicShape("test")
        shape.set(x=1.0, y=2.0, z=3.0)
        self.assertEqual(shape.x, 1.0)
        self.assertEqual(shape.y, 2.0)
        self.assertEqual(shape.z, 3.0)

    def test_set_invalid_attribute_type(self):
        shape = BasicShape("test")
        with self.assertRaises(ValueError):
            shape.set(x="string")

    def test_add_children(self):
        shape = BasicShape("parent")
        child1 = BasicShape("child1")
        child2 = BasicShape("child2")
        shape.add_children([child1, child2])
        self.assertEqual(shape.child_shapes, [child1, child2])

    def test_get_edit_params(self):
        shape = BasicShape("test")
        params, set_func = shape.get_edit_params()
        self.assertEqual(params, [("x", "X", float),
                                  ("y", "Y", float),
                                  ("z", "Z", float)])
        self.assertEqual(set_func, shape.set)


class TestPoint(unittest.TestCase):
    def test_init(self):
        point = Point("test_point", 1.0, 2.0, 3.0)
        self.assertEqual(point.name, "test_point")
        self.assertEqual(point.x, 1.0)
        self.assertEqual(point.y, 2.0)
        self.assertEqual(point.z, 3.0)

    def test_np_vector_property(self):
        point = Point("test_point", 1.0, 2.0, 3.0)
        self.assertTrue(np.array_equal(point.np_vector,
                                       np.array([1.0, 2.0, 3.0])))


class TestLightPoint(unittest.TestCase):
    def test_init(self):
        light_gl = object()  # mock object
        light_point = LightPoint("light", light_gl, 1.0, 2.0, 3.0)
        self.assertEqual(light_point.name, "light")
        self.assertEqual(light_point.x, 1.0)
        self.assertEqual(light_point.y, 2.0)
        self.assertEqual(light_point.z, 3.0)
        self.assertIs(light_point.lightGL, light_gl)


class TestSegment(unittest.TestCase):
    def test_init(self):
        point_a = Point("A", 0.0, 0.0, 0.0)
        point_b = Point("B", 1.0, 1.0, 1.0)
        segment = Segment("AB", point_a, point_b)
        self.assertEqual(segment.name, "AB")
        self.assertIs(segment.point_a, point_a)
        self.assertIs(segment.point_b, point_b)

    def test_update_coordinates(self):
        point_a = Point("A", 0.0, 0.0, 0.0)
        point_b = Point("B", 1.0, 1.0, 1.0)
        segment = Segment("AB", point_a, point_b)

        segment.x = 1.0
        segment.y = 2.0
        segment.z = 3.0
        segment.update_coordinates()

        self.assertEqual(point_a.x, 1.0)
        self.assertEqual(point_a.y, 2.0)
        self.assertEqual(point_a.z, 3.0)
        self.assertEqual(point_b.x, 2.0)
        self.assertEqual(point_b.y, 3.0)
        self.assertEqual(point_b.z, 4.0)
        self.assertEqual(segment.x, 0.0)
        self.assertEqual(segment.y, 0.0)
        self.assertEqual(segment.z, 0.0)


class TestFigure2(unittest.TestCase):
    def test_init(self):
        points = [Point("A", 0.0, 0.0, 0.0), Point("B", 1.0, 1.0, 1.0)]
        figure = Figure2("test_fig", points)
        self.assertEqual(figure.name, "test_fig")
        self.assertEqual(figure.points, points)

    def test_update_coordinates(self):
        points = [Point("A", 0.0, 0.0, 0.0), Point("B", 1.0, 1.0, 1.0)]
        figure = Figure2("test_fig", points)

        figure.x = 1.0
        figure.y = 2.0
        figure.z = 3.0
        figure.update_coordinates()

        self.assertEqual(points[0].x, 1.0)
        self.assertEqual(points[0].y, 2.0)
        self.assertEqual(points[0].z, 3.0)
        self.assertEqual(points[1].x, 2.0)
        self.assertEqual(points[1].y, 3.0)
        self.assertEqual(points[1].z, 4.0)
        self.assertEqual(figure.x, 0.0)
        self.assertEqual(figure.y, 0.0)
        self.assertEqual(figure.z, 0.0)


class TestPlane(unittest.TestCase):
    def test_init(self):
        point = Point("A", 0.0, 0.0, 0.0)
        plane = Plane("test_plane", point)
        self.assertEqual(plane.name, "test_plane")
        self.assertIs(plane.point_a, point)
        self.assertTrue(np.array_equal(plane.normal,
                                       np.array([0.0, 0.0, 0.0])))
        self.assertEqual(plane.redraw, 0)
        self.assertEqual(plane.contur, [])

    def test_count_new_z(self):
        point = Point("A", 1.0, 1.0, 1.0)
        plane = Plane("test_plane", point)
        plane.normal = np.array([1.0, 1.0, 1.0])

        z = plane.count_new_z(2.0, 2.0)
        expected_z = ((1.0 - 2.0) * 1.0 + (1.0 - 2.0) * 1.0 + 1.0 * 1.0)
        self.assertEqual(z, expected_z)

    def test_add_contur(self):
        point = Point("A", 0.0, 0.0, 0.0)
        plane = Plane("test_plane", point)
        plane.normal = np.array([0.0, 0.0, 1.0])

        segment = Segment("AB", Point("A", 1.0, 1.0, 0.0),
                          Point("B", 2.0, 2.0, 0.0))
        contur = Contur2("contur", [segment])
        plane.add_contur(contur)

        self.assertEqual(plane.contur, [contur])
        self.assertEqual(segment.point_a.z, 0.0)


class TestPlaneBy3Point(unittest.TestCase):
    def test_init(self):
        point_a = Point("A", 1.0, 0.0, 0.0)
        point_b = Point("B", 0.0, 1.0, 0.0)
        point_c = Point("C", 0.0, 0.0, 1.0)
        plane = PlaneBy3Point("test_plane", point_a, point_b, point_c)

        expected_normal = np.cross(
            point_a.np_vector - point_b.np_vector,
            point_c.np_vector - point_b.np_vector
        )
        self.assertTrue(np.array_equal(plane.normal, expected_normal))

    def test_update_plane(self):
        point_a = Point("A", 1.0, 0.0, 0.0)
        point_b = Point("B", 0.0, 1.0, 0.0)
        point_c = Point("C", 0.0, 0.0, 1.0)
        plane = PlaneBy3Point("test_plane", point_a, point_b, point_c)

        point_a.x = 2.0
        plane.update_plane()

        new_normal = np.cross(
            point_a.np_vector - point_b.np_vector,
            point_c.np_vector - point_b.np_vector
        )
        self.assertTrue(np.array_equal(plane.normal, new_normal))


class TestPlaneByPointSegment(unittest.TestCase):
    def test_init(self):
        point = Point("P", 1.0, 1.0, 1.0)
        segment = Segment("AB", Point("A", 0.0, 0.0, 0.0),
                          Point("B", 0.0, 0.0, 1.0))
        plane = PlaneByPointSegment("test_plane", point, segment)

        expected_normal = np.cross(
            point.np_vector - segment.point_a.np_vector,
            segment.point_b.np_vector - segment.point_a.np_vector
        )
        self.assertTrue(np.array_equal(plane.normal, expected_normal))


class TestPlaneByPlane(unittest.TestCase):
    def test_init(self):
        base_point = Point("A", 0.0, 0.0, 0.0)
        base_plane = Plane("base", base_point)
        base_plane.normal = np.array([1.0, 0.0, 0.0])

        new_point = Point("P", 1.0, 1.0, 1.0)
        plane = PlaneByPlane("test_plane", new_point, base_plane)

        self.assertTrue(np.array_equal(plane.normal, base_plane.normal))
        self.assertIs(plane.base_plane, base_plane)


class TestFigure3(unittest.TestCase):
    def test_init(self):
        face1 = Figure2("face1", [Point("A", 0.0, 0.0, 0.0)])
        face2 = Figure2("face2", [Point("B", 1.0, 1.0, 1.0)])
        figure = Figure3("test_figure", [face1, face2])

        self.assertEqual(figure.name, "test_figure")
        self.assertEqual(figure.faces, [face1, face2])

    def test_update_coordinates(self):
        point_a = Point("A", 0.0, 0.0, 0.0)
        point_b = Point("B", 1.0, 1.0, 1.0)
        face1 = Figure2("face1", [point_a])
        face2 = Figure2("face2", [point_b])
        figure = Figure3("test_figure", [face1, face2])

        figure.x = 1.0
        figure.y = 2.0
        figure.z = 3.0
        figure.update_coordinates()

        self.assertEqual(point_a.x, 1.0)
        self.assertEqual(point_a.y, 2.0)
        self.assertEqual(point_a.z, 3.0)
        self.assertEqual(point_b.x, 2.0)
        self.assertEqual(point_b.y, 3.0)
        self.assertEqual(point_b.z, 4.0)
        self.assertEqual(figure.x, 0.0)
        self.assertEqual(figure.y, 0.0)
        self.assertEqual(figure.z, 0.0)


if __name__ == '__main__':
    unittest.main()
