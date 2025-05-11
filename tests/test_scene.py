import unittest
from unittest.mock import MagicMock
from src.Simple2DEditorImports import *


class TestScene(unittest.TestCase):
    def setUp(self):
        self.mock_update = MagicMock()
        self.scene = Scene(self.mock_update)

        # Создадим несколько тестовых точек
        self.scene.add_point("A", 0, 0, 0)
        self.scene.add_point("B", 1, 0, 0)
        self.scene.add_point("C", 0, 1, 0)
        self.scene.add_point("D", 0, 0, 1)

    def test_initial_state(self):
        self.assertEqual(len(self.scene.entities), 4)
        self.assertEqual(len(self.scene.stack_last_actions), 0)
        self.assertEqual(len(self.scene.stack_undo_actions), 0)

    def test_add_point(self):
        calls = self.mock_update.call_count
        self.scene.add_point("P1", 1.0, 2.0, 3.0)
        self.assertIn("P1", self.scene.entities)
        self.assertIsInstance(self.scene.entities["P1"], Point)
        self.assertEqual(self.scene.entities["P1"].x, 1.0)
        self.assertEqual(self.scene.entities["P1"].y, 2.0)
        self.assertEqual(self.scene.entities["P1"].z, 3.0)
        self.assertEqual(self.mock_update.call_count, calls + 1)

    def test_add_point_empty_name(self):
        with self.assertRaises(EmptyFieldException):
            self.scene.add_point("", 1, 2, 3)

    def test_add_point_duplicate_name(self):
        self.scene.add_point("P1", 1, 2, 3)
        with self.assertRaises(EntityNameAlreadyExistsException):
            self.scene.add_point("P1", 4, 5, 6)

    def test_add_segment(self):
        self.scene.add_segment("AB", "A", "B")
        self.assertIn("AB", self.scene.entities)
        self.assertIsInstance(self.scene.entities["AB"], Segment)
        self.assertEqual(self.scene.entities["AB"].point_a.name, "A")
        self.assertEqual(self.scene.entities["AB"].point_b.name, "B")

    def test_add_segment_nonexistent_points(self):
        with self.assertRaises(EntityNotFoundException):
            self.scene.add_segment("XY", "X", "Y")

    def test_add_figure2(self):
        self.scene.add_figure2("ABC", ["A", "B", "C"])
        self.assertIn("ABC", self.scene.entities)
        self.assertIsInstance(self.scene.entities["ABC"], Figure2)
        self.assertEqual(len(self.scene.entities["ABC"].points), 3)

    def test_add_figure2_n(self):
        n = 5
        radius = 2.0
        self.scene.add_figure2_n("pentagon", n, radius)

        self.assertIn("pentagon", self.scene.entities)
        self.assertIsInstance(self.scene.entities["pentagon"], Figure2)
        self.assertEqual(len(self.scene.entities["pentagon"].points), n)

        # Проверяем созданные точки
        for i in range(1, n + 1):
            point_name = f"figure2_point_pentagon_{i}"
            self.assertIn(point_name, self.scene.entities)

    def test_add_plane_by_points(self):
        self.scene.add_plane_by_points("plane1", "A", "B", "D")
        self.assertIn("plane1", self.scene.entities)
        self.assertIsInstance(self.scene.entities["plane1"], PlaneBy3Point)

    def test_add_plane_by_points_collinear(self):
        # Создаем коллинеарные точки
        self.scene.add_point("E", 2, 0, 0)
        with self.assertRaises(ValueError):
            self.scene.add_plane_by_points("plane2", "A", "B", "E")

    def test_add_plane_by_point_and_segment(self):
        self.scene.add_segment("AB", "A", "B")
        self.scene.add_plane_by_point_and_segment("plane3", "D", "AB")
        self.assertIn("plane3", self.scene.entities)
        self.assertIsInstance(self.scene.entities["plane3"],
                              PlaneByPointSegment)

    def test_add_plane_by_plane(self):
        self.scene.add_plane_by_points("base_plane", "A", "B", "D")
        self.scene.add_plane_by_plane("new_plane", "C", "base_plane")
        self.assertIn("new_plane", self.scene.entities)
        self.assertIsInstance(self.scene.entities["new_plane"], PlaneByPlane)

    def test_add_contur_to_plane(self):
        self.scene.add_plane_by_points("plane4", "A", "B", "D")
        self.scene.add_segment("AD", "A", "D")
        self.scene.add_segment("DB", "D", "B")
        self.scene.add_segment("BA", "B", "A")

        self.scene.add_contur_to_plane("plane4", ["AD", "DB", "BA"])
        plane = self.scene.entities["plane4"]
        self.assertEqual(len(plane.contur), 1)
        self.assertIsInstance(plane.contur[0], Contur2)

    def test_add_contur_n_to_plane(self):
        self.scene.add_plane_by_points("plane5", "A", "B", "D")
        self.scene.add_contur_n_to_plane("plane5", 4, 1.0)
        plane = self.scene.entities["plane5"]
        self.assertEqual(len(plane.contur), 1)

    def test_add_figure3(self):
        self.scene.add_figure2("face1", ["A", "B", "C"])
        self.scene.add_figure2("face2", ["A", "B", "D"])
        self.scene.add_figure3("figure3", ["face1", "face2"])
        self.assertIn("figure3", self.scene.entities)
        self.assertIsInstance(self.scene.entities["figure3"], Figure3)

    def test_add_prism_n(self):
        n = 4
        radius = 1.0
        height = 2.0
        self.scene.add_prism_n("prism", n, radius, height)

        self.assertIn("prism", self.scene.entities)
        self.assertIsInstance(self.scene.entities["prism"], Figure3)

        # Проверяем количество созданных граней
        self.assertEqual(len(self.scene.entities["prism"].faces), n + 2)

    def test_save_and_load_entities(self):
        # Создаем тестовые данные
        test_file = Path("test_scene.pkl")
        self.scene.add_segment("AB", "A", "B")
        self.scene.add_figure2("ABC", ["A", "B", "C"])

        # Сохраняем
        self.scene.save_entities_to_file(test_file)

        # Создаем новую сцену и загружаем
        new_scene = Scene(self.mock_update)
        new_scene.load_entities_from_file(test_file)

        # Проверяем загруженные данные
        self.assertIn("AB", new_scene.entities)
        self.assertIn("ABC", new_scene.entities)

        # Удаляем тестовый файл
        test_file.unlink()

    def test_is_point_collinear(self):
        p1 = Point("p1", 0, 0, 0)
        p2 = Point("p2", 1, 0, 0)
        p3 = Point("p3", 2, 0, 0)  # коллинеарна
        p4 = Point("p4", 0, 1, 0)  # не коллинеарна

        self.assertTrue(is_point_collinear(p1, p2, p3))
        self.assertFalse(is_point_collinear(p1, p2, p4))


if __name__ == '__main__':
    unittest.main()
