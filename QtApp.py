#!/usr/bin/env python3

import sys, traceback
from collections import deque, defaultdict
import math
import pickle
from pathlib import Path

ERROR_EXCEPTION = 1
ERROR_WRONG_SETTINGS = 2
ERROR_PYTHON_VERSION = 3
ERROR_MODULES_MISSING = 4
ERROR_QT_VERSION = 5
ERROR_OPENGL_VERSION = 6
ERROR_NUMPY_VERSION = 6

if sys.version_info < (3, 10):
    print('Use python >= 3.10', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

sys.excepthook = lambda x, y, z:(
    print("".join(traceback.format_exception(x, y, z)))
)

try:
    from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL, uic
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                                 QWidget, QDialog, QLabel, QLineEdit,
                                 QPushButton, QMessageBox, QFormLayout,
                                 QDoubleSpinBox, QSpinBox, QHBoxLayout,
                                 QTreeWidgetItem)
    from PyQt5.QtOpenGL import QGLWidget
except Exception as e:
    print('PyQt5 not found: "{}".'.format(e),
          file=sys.stderr)
    sys.exit(ERROR_QT_VERSION)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except Exception as e:
    print('OpenGL not found: "{}".'.format(e),
          file=sys.stderr)
    sys.exit(ERROR_OPENGL_VERSION)

try:
    import numpy as np
except Exception as e:
    print('numpy not found: "{}".'.format(e),
          file=sys.stderr)
    sys.exit(ERROR_NUMPY_VERSION)

try:
    from SceneBase import *
    from AddingWindows import *
except Exception as e:
    print('App modules not found: "{}"'.format(e), file=sys.stderr)
    sys.exit(ERROR_MODULES_MISSING)


PLANE_COLOR = [0.2, 0.7, 0.3, 1.0]
FIGURE2_COLOR = [0.2, 0.2, 0.9, 1.0]
SEGMENT_COLOR = [0.0, 0.9, 0.6, 1.0]
EDGE_COLOR = [0.0, 0.0, 0.0, 1.0]
POINT_COLOR = [1.0, 0.0, 0.0, 1.0]


class GLWidget(QGLWidget):
    def __init__(self, parent=None, scene=None):
        super(GLWidget, self).__init__(parent)
        self.scene = scene
        self.camera_rotation_angle = 0
        self.camera_lifting_angle = 0
        self.camera_distance = 1
        self.frame_counter = 0
        self.basis_p_0 = Point("", 0, 0, 0)
        self.basis_p_x = Point("", 1, 0, 0)
        self.basis_p_y = Point("", 0, 1, 0)
        self.basis_p_z = Point("", 0, 0, 1)
        self.basis_x = Segment("", self.basis_p_x, self.basis_p_0)
        self.basis_y = Segment("", self.basis_p_y, self.basis_p_0)
        self.basis_z = Segment("", self.basis_p_z, self.basis_p_0)
        self.basis_render_size = 0.3

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.3, 0.3, 0.3, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [1.0, 1.0, 1.0, 1])
        # Настройка источника света
        # Направленный свет
        glLightfv(GL_LIGHT0, GL_POSITION, [-100.0, 100.0, 100.0, 0.0])
        # Цвет рассеянного света
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        # Цвет зеркального отражения
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        # включение нормалей
        glEnable(GL_NORMALIZE)
        glLineWidth(2.0)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glPointSize(4.0)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, self.width() / self.height(), 0.1, 100.0)
        gluLookAt(math.cos(self.camera_rotation_angle) *
                  math.cos(self.camera_lifting_angle) * self.camera_distance,
                  math.sin(self.camera_rotation_angle) *
                  math.cos(self.camera_lifting_angle) * self.camera_distance,
                  math.sin(self.camera_lifting_angle) * self.camera_distance,
                  0, 0, 0,
                  0, 0, 1)
        self.frame_counter += 1

        self.draw_basis()
        for name, entity in self.scene.entities.items():
            entity.draw_shape()

        self.update()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def draw_basis(self):
        new_value = self.camera_distance * self.basis_render_size
        self.basis_p_x.x = new_value
        self.basis_p_y.y = new_value
        self.basis_p_z.z = new_value
        draw_segment(self.basis_x, color=[1.0, 0.0, 0.0])
        draw_segment(self.basis_y, color=[0.0, 1.0, 0.0])
        draw_segment(self.basis_z, color=[0.0, 0.0, 1.0])



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = Scene(self.scene_update)

        self.openGL_widget = GLWidget(scene=self.scene)
        uic.loadUi("untitled.ui", self)
        self.setWindowTitle("SimpleBlender")
        self.OpenGLContainer.layout().addWidget(self.openGL_widget)

        self.adding_page.layout().addWidget(
            AddingOptionsWidget("", self.init_adding_params(),
                                is_destroyable=False)
        )
        self.entity_tree.setColumnCount(2)
        self.entity_tree.setHeaderLabels(["Имя", "Тип"])
        self.init_tree_interaction()
        self.init_saving_field()
        self.init_scroll()
        self.init_scene()

    def scene_update(self):
        self.update_entity_tree()

    def update_entity_tree(self):
        self.entity_tree.clear()
        for el in self.scene.entities:
            self.update_entity_tree_node(self.entity_tree, el)

    def update_entity_tree_node(self, node, entity_name):
        new_node = QTreeWidgetItem(node)
        new_node.setText(0, entity_name)
        new_node.setText(1, type(self.scene.entities[entity_name]).__name__)
        children = self.scene.entities[entity_name].child_shapes
        if children is not None:
            for child_name in children:
                self.update_entity_tree_node(new_node, child_name)

    def init_tree_interaction(self):
        def tree_clicked(item, column):
            entity = self.scene.entities[item.text(0)]
            options = entity.get_edit_params()
            self.label_name_view.setText(entity.name)
            self.double_edit_x.setValue(entity.x)
            self.double_edit_y.setValue(entity.y)
            self.double_edit_z.setValue(entity.z)

            def apply_clicked():
                values = {
                    "x": float(self.double_edit_x.value()),
                    "y": float(self.double_edit_y.value()),
                    "z": float(self.double_edit_z.value())
                }
                options[1](**values)
                self.double_edit_x.setValue(entity.x)
                self.double_edit_y.setValue(entity.y)
                self.double_edit_z.setValue(entity.z)

            self.button_edit_apply.clicked.connect(apply_clicked)

        self.entity_tree.itemClicked.connect(tree_clicked)

    def init_saving_field(self):
        layout = QHBoxLayout()
        path_line = QLineEdit()

        def save_click():
            self.scene.save_entities_to_file(Path(path_line.text().strip()))
        save_button = QPushButton(text="Save")
        save_button.clicked.connect(save_click)

        def load_click():
            self.scene.load_entities_from_file(Path(path_line.text().strip()))
        load_button = QPushButton(text="Load")
        load_button.clicked.connect(load_click)
        layout.addWidget(load_button)
        layout.addWidget(path_line)
        layout.addWidget(save_button)
        self.widget.layout().addLayout(layout)

    def init_scroll(self):
        self.scroll_rotation.setRange(0, 360)
        self.scroll_rotation.setValue(0)
        self.scroll_rotation.valueChanged.connect(self.set_camera_rotation)
        self.scroll_lifting.setRange(-90, 90)
        self.scroll_lifting.setValue(0)
        self.scroll_lifting.valueChanged.connect(self.set_camera_lifting)
        self.scroll_zooming.setRange(1, 30)
        self.scroll_zooming.setValue(5)
        self.scroll_zooming.valueChanged.connect(self.set_camera_distance)

    def set_camera_rotation(self, angle):
        self.openGL_widget.camera_rotation_angle = math.pi * angle / 180

    def set_camera_lifting(self, angle):
        self.openGL_widget.camera_lifting_angle = -math.pi * angle / 180

    def set_camera_distance(self, distance):
        self.openGL_widget.camera_distance = distance

    def init_scene(self):
        # self.scene.add_prism_n("five", 4, 1, 0.5)
        # self.scene.add_plane_by_points("plane1",
        #                                "pnt_upr_five_1",
        #                                "pnt_upr_five_2",
        #                                "pnt_lwr_five_4")
        # self.scene.add_contur_n_to_plane("plane1", 7, 4)
        # self.scene.save_entities_to_file(Path("test_figure1.pkl"))
        # self.scene.load_entities_from_file(Path("test_figure.pkl"))
        self.scene.add_light("main_light", GL_LIGHT0, 100.0, 100.0, 100.0)
        self.scene_update()

    def init_adding_params(self):
        return {
            "Точка": ([
                ("name", "Имя точки", str),
                ("x", "X", float),
                ("y", "Y", float),
                ("z", "Z", float),
            ], self.scene.add_point),
            "Отрезок": ([
                ("name", "Имя отрезка", str),
                ("point_a_name", "Точка A", str),
                ("point_b_name", "Точка B", str)
            ], self.scene.add_segment),
            "Плоскость": {
                "По трем точкам": ([
                    ("name", "Имя плоскости", str),
                    ("point1_name", "", str),
                    ("point2_name", "", str),
                    ("point3_name", "", str)
                ], self.scene.add_plane_by_points),
                "По точке и отрезку": ([
                    ("name", "Имя плоскости", str),
                    ("point_name", "Точка", str),
                    ("segment_name", "Отрезок", str)
                ], self.scene.add_plane_by_point_and_segment),
                "Параллельно плоскости": ([
                    ("name", "Имя плоскости", str),
                    ("point_name", "Точка в плоскости", str),
                    ("plane_name", "Параллельна плоскость", str)
                ], self.scene.add_plane_by_plane)
            },
            "Контур 2D": {
                "По отрезкам зацикленной ломаной": ([
                    ("plane_name", "Плоскость", str),
                    ("segments_names", "Отрезки (по порядку в ломаной)",
                     list[str], 3, True)
                ], self.scene.add_contur_to_plane),
                "Сгенерировать N Отрезков": ([
                    ("plane_name", "Плоскость", str),
                    ("n", "Кол-во точек", int),
                    ("radius", "Радиус", float)
                ], self.scene.add_contur_n_to_plane)
            },
            "Фигура 2D": {
                "По точкам": ([
                    ("name", "Имя фигуры", str),
                    ("points_names", "Точки (порядок по ходу окружности)",
                     list[str], 3, True)
                ], self.scene.add_figure2),
                "Сгенерировать N Точек": ([
                    ("name", "Имя фигуры", str),
                    ("n", "Кол-во точек", int),
                    ("radius", "Радиус", float)
                ], self.scene.add_figure2_n)
            },
            "Фигура 3D": {
                "Объединить грани": ([
                    ("name", "Имя фигуры", str),
                    ("faces_names", "Грани", list[str], 1, True)
                ], self.scene.add_figure3),
                "Призма": ([
                    ("name", "Имя фигуры", str),
                    ("n", "Кол-во боковых граней", int),
                    ("radius", "Радиус", float),
                    ("height", "Высота", float)
                ], self.scene.add_prism_n)
            }
        }


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
    # sys.exit(app.exec())
