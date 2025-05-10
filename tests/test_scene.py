import pytest
from pathlib import Path
import pickle
import math
import numpy as np
from BasicShapes import *
from collections import deque
from SceneBase import *


@pytest.fixture
def scene():
    """Фикстура для создания экземпляра Scene для тестов"""

    def mock_update():
        pass

    return Scene(mock_update)


def test_initial_state(scene):
    """Тест начального состояния сцены"""
    assert scene.entities == {}
    assert len(scene.stack_last_actions) == 0
    assert len(scene.stack_undo_actions) == 0
    assert scene.path is None


def test_add_point(scene):
    """Тест добавления точки"""
    scene.add_point("test_point", 1.0, 2.0, 3.0)
    assert "test_point" in scene.entities
    assert isinstance(scene.entities["test_point"], Point)
    assert scene.entities["test_point"].x == 1.0
    assert scene.entities["test_point"].y == 2.0
    assert scene.entities["test_point"].z == 3.0


def test_add_point_duplicate_name(scene):
    """Тест добавления точки с существующим именем"""
    scene.add_point("test_point", 1.0, 2.0, 3.0)
    with pytest.raises(EntityNameAlreadyExistsException):
        scene.add_point("test_point", 4.0, 5.0, 6.0)


def test_add_point_empty_name(scene):
    """Тест добавления точки с пустым именем"""
    with pytest.raises(EmptyFieldException):
        scene.add_point("", 1.0, 2.0, 3.0)


def test_add_segment(scene):
    """Тест добавления отрезка"""
    scene.add_point("A", 0, 0, 0)
    scene.add_point("B", 1, 1, 1)
    scene.add_segment("AB", "A", "B")

    assert "AB" in scene.entities
    assert isinstance(scene.entities["AB"], Segment)
    assert scene.entities["AB"].point_a.name == "A"
    assert scene.entities["AB"].point_b.name == "B"


def test_add_segment_nonexistent_points(scene):
    """Тест добавления отрезка с несуществующими точками"""
    with pytest.raises(EntityNotFoundException):
        scene.add_segment("AB", "A", "B")


def test_add_figure2(scene):
    """Тест добавления 2D фигуры"""
    points = ["A", "B", "C"]
    for i, name in enumerate(points):
        scene.add_point(name, i, i, 0)

    scene.add_figure2("triangle", points)

    assert "triangle" in scene.entities
    assert isinstance(scene.entities["triangle"], Figure2)
    assert len(scene.entities["triangle"].points) == 3


def test_add_figure2_n(scene):
    """Тест добавления правильного n-угольника"""
    n = 5
    radius = 2.0
    scene.add_figure2_n("pentagon", n, radius)

    assert "pentagon" in scene.entities
    assert isinstance(scene.entities["pentagon"], Figure2)
    assert len(scene.entities["pentagon"].points) == n

    # Проверяем, что созданы все необходимые точки
    for i in range(1, n + 1):
        point_name = f"figure2_point_pentagon_{i}"
        assert point_name in scene.entities
        assert isinstance(scene.entities[point_name], Point)


def test_add_plane_by_points(scene):
    """Тест добавления плоскости по трем точкам"""
    scene.add_point("A", 1, 0, 0)
    scene.add_point("B", 0, 1, 0)
    scene.add_point("C", 0, 0, 1)
    scene.add_plane_by_points("plane", "A", "B", "C")

    assert "plane" in scene.entities
    assert isinstance(scene.entities["plane"], PlaneBy3Point)


def test_add_plane_by_points_collinear(scene):
    """Тест добавления плоскости с коллинеарными точками"""
    scene.add_point("A", 0, 0, 0)
    scene.add_point("B", 1, 1, 1)
    scene.add_point("C", 2, 2, 2)

    with pytest.raises(ValueError):
        scene.add_plane_by_points("plane", "A", "B", "C")


def test_add_plane_by_point_and_segment(scene):
    """Тест добавления плоскости по точке и отрезку"""
    scene.add_point("A", 1, 0, 0)
    scene.add_point("B", 0, 1, 0)
    scene.add_point("C", 0, 0, 1)
    scene.add_segment("AB", "A", "B")
    scene.add_plane_by_point_and_segment("plane", "C", "AB")

    assert "plane" in scene.entities
    assert isinstance(scene.entities["plane"], PlaneByPointSegment)


def test_add_contur_to_plane(scene):
    """Тест добавления контура к плоскости"""
    # Создаем плоскость
    scene.add_point("A", 1, 0, 0)
    scene.add_point("B", 0, 1, 0)
    scene.add_point("C", 0, 0, 1)
    scene.add_plane_by_points("plane", "A", "B", "C")

    # Создаем отрезки для контура
    scene.add_point("D", 0.5, 0.5, 0)
    scene.add_segment("AD", "A", "D")
    scene.add_segment("DB", "D", "B")
    scene.add_segment("BC", "B", "C")
    scene.add_segment("CA", "C", "A")
