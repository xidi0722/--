import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
    #初始化 OpenGL 狀態
    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
    #調整視窗用
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / float(height or 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        #相機角度((相機位置),(往哪個點看),(相機的旋轉角度))
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 1, 0)

        #繪畫的程式區間
        glBegin(GL_QUADS)
        # 正面
        glColor3f(1, 0, 0)
        glVertex3f(-1, -1,  1)
        glVertex3f( 1, -1,  1)
        glVertex3f( 1,  1,  1)
        glVertex3f(-1,  1,  1)

        # 背面
        glColor3f(1, 0, 0)
        glVertex3f(-1, -1, -1)
        glVertex3f(-1,  1, -1)
        glVertex3f( 1,  1, -1)
        glVertex3f( 1, -1, -1)

        # 左面
        glColor3f(0, 1, 0)
        glVertex3f(-1, -1, -1)
        glVertex3f(-1, -1,  1)
        glVertex3f(-1,  1,  1)
        glVertex3f(-1,  1, -1)

        # 右面
        glColor3f(0, 1, 0)
        glVertex3f( 1, -1, -1)
        glVertex3f( 1,  1, -1)
        glVertex3f( 1,  1,  1)
        glVertex3f( 1, -1,  1)

        # 上面
        glColor3f(0, 0, 1)
        glVertex3f(-1,  1, -1)
        glVertex3f(-1,  1,  1)
        glVertex3f( 1,  1,  1)
        glVertex3f( 1,  1, -1)

        # 下面
        glColor3f(0, 1, 0)
        glVertex3f(-1, -1, -1)
        glVertex3f( 1, -1, -1)
        glVertex3f( 1, -1,  1)
        glVertex3f(-1, -1,  1)

        glEnd()

            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('3D 動作編輯器')
        self.setGeometry(200, 200, 800, 600)
        #啟用和設定openGL物件
        self.opengl_widget = OpenGLWidget(self)
        #放入中間
        self.setCentralWidget(self.opengl_widget)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())