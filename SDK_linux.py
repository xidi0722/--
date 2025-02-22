from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt
from PySide6 import QtCore
from PySide6.QtGui import QWindow

from panda3d.core import WindowProperties, NodePath, PointLight, AmbientLight, loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import sys


QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
# 隱藏panda3d的邊框和選擇欄
loadPrcFileData('', 'undecorated 1')  

class Panda3DWidget(QWidget):
    def __init__(self, base, parent=None):
        super().__init__(parent)
        self.base = base

        # 設置 Panda3D 渲染窗口
        self.base.win.setSize(800, 600)  # 設置窗口大小
        self.base.win.setTitle("Panda3D")  # 設置窗口標題

        # 使用 createWindowContainer 直接將 Panda3D 渲染窗口嵌入到 QWidget 中
        self.container = QWidget.createWindowContainer(self.base.win.getWinHandler())
        layout = QVBoxLayout(self)
        layout.addWidget(self.container)

        # 定期更新 Panda3D 渲染
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_panda)
        self.timer.start(16)  # 每秒 60 幀 (16 毫秒刷新)

        # 加載模型
        self.model = self.base.loader.loadModel("blender/robo1.glb")
        if self.model:
            self.model.reparentTo(self.base.render)
        else:
            print("Model failed to load.")
        self.left_arm = self.model.find("**/left_arm")  
        self.right_arm = self.model.find("**/right_arm") 
        # 設置相機
        self.base.cam.setPos(8, 3, 3)
        self.base.cam.lookAt(self.model)

        self.add_lighting()

    def add_lighting(self):
        # 創建環境光源
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.5, 0.5, 0.5, 1))  # 設置輕微的環境光
        ambient_light_node = self.base.render.attachNewNode(ambient_light)
        self.base.render.setLight(ambient_light_node)

        # 創建點光源
        point_light = PointLight('point_light')
        point_light.setColor((1, 1, 1, 1))  # 設置白色光源
        point_light_node = self.base.render.attachNewNode(point_light)
        point_light_node.setPos(10, -10, 10)  # 設置光源位置
        self.base.render.setLight(point_light_node)

    def update_panda(self):
        """更新 Panda3D 渲染任務"""
        self.base.taskMgr.step()


class Stats:
    def __init__(self):
        # 加載 UI 文件
        self.ui = QUiLoader().load('ui/SDK.ui')

        # 取得元件
        self.get_inponent(self.ui)

        # 當 Slider 的值改變時連接函數
        self.slider1.valueChanged.connect(lambda:self.update_slider_value(self.slider1, self.label1))
        self.slider2.valueChanged.connect(lambda:self.update_slider_value(self.slider2, self.label2))
        self.slider3.valueChanged.connect(lambda:self.update_slider_value(self.slider3, self.label3))
        self.slider4.valueChanged.connect(lambda:self.update_slider_value(self.slider4, self.label4))

        # 初始化 Panda3D 基礎類
        self.base = ShowBase()

        # 查找 UI 中的容器部件
        container = self.ui.findChild(QWidget, "Panda3DContainer")

        # 創建 Panda3DWidget並嵌入到容器中(parent=父控件)
        self.panda_widget = Panda3DWidget(self.base, parent=container)
        self.slider3.valueChanged.connect(lambda:self.panda_widget.left_arm.setHpr(0, 0, self.slider3.value()))
        self.slider4.valueChanged.connect(lambda:self.panda_widget.right_arm.setHpr(0, 0, self.slider4.value()))

        # 創建佈局
        layout = QVBoxLayout(container)

        # 將 Panda3D 渲染窗口添加到 UI 中
        layout.addWidget(self.panda_widget)

    def get_inponent(self, ui):
        self.slider1 = ui.Slider1
        self.slider2 = ui.Slider2
        self.slider3 = ui.Slider3
        self.slider4 = ui.Slider4
        self.set_slider(self.slider1)
        self.set_slider(self.slider2)
        self.set_slider(self.slider3)
        self.set_slider(self.slider4)
        self.label1 = ui.Slider_num1
        self.label2 = ui.Slider_num2
        self.label3 = ui.Slider_num3
        self.label4 = ui.Slider_num4

    def set_slider(self, slider):
        slider.setMinimum(0)
        slider.setMaximum(180)
        middle_value = (slider.minimum() + slider.maximum()) // 2
        slider.setValue(middle_value)

    def update_slider_value(self, slider, label):
        # 獲取滑動條的值
        slider_value = slider.value()
        label.setText(f" {slider_value}")
        self.updateLabelPosition(slider, label)

    def updateLabelPosition(self, slider, label):
        # 計算label的x來置中
        slider_pos = slider.mapToGlobal(slider.rect().topLeft())
        x = slider_pos.x() + (slider.width() - label.width() / 2.25) * (slider.value() - slider.minimum()) / (slider.maximum() - slider.minimum())
        y = slider_pos.y() - 25  # 滑塊上方 25 像素的位置
        label.move(self.ui.mapFromGlobal(QtCore.QPoint(x, y)))
        # 圖層上移保證在上面
        label.raise_()


app = QApplication(sys.argv)
stats = Stats()
stats.ui.show()
app.exec()
