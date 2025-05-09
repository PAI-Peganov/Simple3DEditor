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
                                 QPushButton, QMessageBox)
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


PLANE_COLOR = [0.2, 0.8, 0.2, 1.0]
FIGURE2_COLOR = [0.2, 0.2, 0.9, 1.0]
SEGMENT_COLOR = [0.0, 0.8, 0.6, 1.0]
EDGE_COLOR = [0.0, 0.0, 0.0, 1.0]
POINT_COLOR = [1.0, 0.0, 0.0, 1.0]


class GLWidget(QGLWidget):
    def __init__(self, parent=None, scene=None):
        super(GLWidget, self).__init__(parent)
        self.scene = scene

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.3, 0.3, 0.3, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [1.0, 1.0, 1.0, 1])
        # Настройка источника света
        # Направленный свет
        glLightfv(GL_LIGHT0, GL_POSITION, [-100, 100, 100, 0.0])
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
        self.angle = 0
        self.frame_counter = 0

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, self.width() / self.height(), 0.1, 100.0)
        gluLookAt(math.sin(self.angle) * 5, math.cos(self.angle) * 5, 5,
                  0, 0, 0,
                  0, 0, 1)
        self.angle = 4
        self.frame_counter += 1
        if self.frame_counter % 160 == 0:
            if self.frame_counter // 160 % 2 == 1:
                self.scene.load_entities_from_file(Path("test_figure1.pkl"))
            else:
                self.scene.load_entities_from_file(Path("test_figure.pkl"))

        for name, entity in self.scene.entities.items():
            entity.draw_shape()

        self.scene.entities["pnt_upr_five_1"].z += 0.01

        self.update()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = Scene()
        self.init_scene()
        self.openGL_widget = GLWidget(scene=self.scene)
        uic.loadUi("untitled.ui", self)
        self.setWindowTitle("SimpleBlender")
        self.OpenGLContainer.layout().addWidget(self.openGL_widget)

        self.shape_adding_params = self.init_adding_params()


    def init_scene(self):
        self.scene.add_light("main_light", GL_LIGHT0, 100, 100, 100)
        # self.scene.add_prism_n("five", 4, 1, 0.5)
        # self.scene.add_plane_by_points("plane1",
        #                                "pnt_upr_five_1",
        #                                "pnt_upr_five_2",
        #                                "pnt_lwr_five_4")
        # self.scene.add_contur_n_to_plane("plane1", 7, 4)
        # self.scene.save_entities_to_file(Path("test_figure1.pkl"))
        self.scene.load_entities_from_file(Path("test_figure.pkl"))

    def init_adding_params(self):
        return {
            "Point": ""
        }


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
    # sys.exit(app.exec())