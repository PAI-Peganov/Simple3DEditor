#!/usr/bin/env python3

import sys
import os
import traceback
from collections import deque, defaultdict
import math
import pickle
from pathlib import Path
from PIL import Image

ERROR_EXCEPTION = 1
ERROR_WRONG_SETTINGS = 2
ERROR_PYTHON_VERSION = 3
ERROR_MODULES_MISSING = 4
ERROR_QT_VERSION = 5
ERROR_OPENGL_VERSION = 6
ERROR_NUMPY_VERSION = 6

PLANE_COLOR = [0.2, 0.7, 0.3, 1.0]
FIGURE2_COLOR = [0.2, 0.2, 0.9, 1.0]
SEGMENT_COLOR = [0.0, 0.9, 0.6, 1.0]
EDGE_COLOR = [0.0, 0.0, 0.0, 1.0]
POINT_COLOR = [1.0, 0.0, 0.0, 1.0]

if sys.version_info < (3, 10):
    print('Use python >= 3.10', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

sys.excepthook = lambda x, y, z: (
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
    from src.ShapeOpenGLDrawers import *
    from src.BasicShapes import *
    from src.SceneBase import *
    from src.AddingWindows import *
    from src.QtApp import *
except Exception as e:
    print('App modules not found: "{}"'.format(e), file=sys.stderr)
    sys.exit(ERROR_MODULES_MISSING)
