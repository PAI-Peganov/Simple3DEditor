#!/usr/bin/env python3

import sys

ERROR_EXCEPTION = 1
ERROR_WRONG_SETTINGS = 2
ERROR_PYTHON_VERSION = 3
ERROR_MODULES_MISSING = 4
ERROR_QT_VERSION = 5
ERROR_OPENGL_VERSION = 6

if sys.version_info < (3, 4):
    print('Use python >= 3.4', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

sys.excepthook = lambda x, y, z: print(y)

try:
    from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL, uic
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                                 QWidget)
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
    from SceneBase import *
except Exception as e:
    print('App modules not found: "{}"'.format(e), file=sys.stderr)
    sys.exit(ERROR_MODULES_MISSING)


class GLWidget(QGLWidget):
    def __init__(self, parent=None, scene=None):
        super(GLWidget, self).__init__(parent)
        self.scene = scene

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [1.0, 1.0, 1.0, 1])

        # Настройка источника света
        # Направленный свет
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        # Цвет рассеянного света
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        # Цвет зеркального отражения
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

        # Настройка материала
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SHININESS, 1.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.width() / self.height(), 0.1, 100.0)
        gluLookAt(-10, -10, 10,
                  0, 0, 0,
                  0, 0, 1)

        for name, entity in self.scene.entities.items():
            entity.draw_shape()

        self.scene.entities["1"].x -= 0.01
        self.scene.entities["1"].y -= 0.01

        self.update()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = Scene()
        self.openGL_widget = GLWidget(scene=self.scene)

        uic.loadUi("untitled.ui", self)
        self.setWindowTitle("SimpleBlender")
        self.OpenGLContainer.layout().addWidget(self.openGL_widget)
        self.upd()

    def upd(self):
        self.scene.add_point("1", 1, 10, 0)
        self.scene.add_point("2", 1, -10, 0)
        self.scene.add_point("3", -1, -10, 0)
        self.scene.add_point("4", -1, 10, 0)
        self.scene.add_point("5", 0, 10, 0)
        self.scene.add_figure2("fig", ["1", "2", "3", "4", "5"])


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
    #sys.exit(app.exec())