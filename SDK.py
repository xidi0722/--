from PyQt5.QtWidgets import QVBoxLayout, QGridLayout, QApplication, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtCore
from panda3d.core import WindowProperties, NodePath, PointLight, AmbientLight, loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import sys
from Xlib import display as xdisplay  # 用於 X11 操作

QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
# 隱藏 Panda3D 的邊框和標題欄
loadPrcFileData('', 'undecorated 1')

class Panda3DWidget(QWidget):
    def __init__(self, base, parent=None):
        super().__init__(parent)
        self.base = base

        # 在 Linux 上獲取 Panda3D 視窗的 X11 ID
        self.wid = None
        self.find_panda_window()

        if self.wid:
            # 將 Panda3D 視窗設為子視窗
            self.setMinimumSize(400, 400)  # 設置最小尺寸
            disp = xdisplay.Display()
            panda_window = disp.create_resource_object('window', self.wid)
            qt_window = disp.create_resource_object('window', int(self.winId()))
            panda_window.reparent_window(qt_window)  # 將 Panda3D 視窗設為 Qt 的子視窗
            disp.sync()
        else:
            print("無法找到 Panda3D 視窗。")

        # 定時更新 Panda3D 渲染
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_panda)
        self.timer.start(16)  # 每秒 60 幀 (16 毫秒刷新一次)

        # 載入模型
        self.model = self.base.loader.loadModel("blender/robo1.glb")
        if self.model:
            self.model.reparentTo(self.base.render)
        else:
            print("模型載入失敗。")
        self.left_arm = self.model.find("**/left_arm")
        self.right_arm = self.model.find("**/right_arm")
        # 設置攝影機位置
        self.base.cam.setPos(8, 3, 3)
        self.base.cam.lookAt(self.model)

        self.add_lighting()

    def find_panda_window(self):
        """查找 Panda3D 視窗的 X11 ID"""
        disp = xdisplay.Display()
        root = disp.screen().root
        window_ids = root.get_full_property(disp.intern_atom('_NET_CLIENT_LIST'), 0).value
        for wid in window_ids:
            window = disp.create_resource_object('window', wid)
            name = window.get_wm_name()
            if name == "Panda":  # Panda3D 視窗的標題
                self.wid = wid
                break
        disp.close()

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
        """更新 Panda3D 的渲染任務"""
        self.base.taskMgr.step()

class Stats:
    def __init__(self):
       
        # 加載 UI 文件
        self.ui = loadUi('ui/SDK.ui')

        # 取得元件
        self.get_inponent(self.ui)

        # 當 Slider 的值改變時連接函數
        self.slider1.valueChanged.connect(lambda:self.update_slider_value(self.slider1,self.label1))
        self.slider2.valueChanged.connect(lambda:self.update_slider_value(self.slider2,self.label2))
        self.slider3.valueChanged.connect(lambda:self.update_slider_value(self.slider3,self.label3))
        self.slider4.valueChanged.connect(lambda:self.update_slider_value(self.slider4,self.label4))

        # 初始化 Panda3D 基礎類
        self.base = ShowBase()
        
        # 查找 UI 中的容器部件
        container = self.ui.findChild(QWidget, "Panda3DContainer")

        # 創建 Panda3DWidget嵌入到容器中(parent=父控件)
        self.panda_widget = Panda3DWidget(self.base, parent=container)
        self.slider3.valueChanged.connect(lambda:self.panda_widget.left_arm.setHpr(0, 0,self.slider3.value()))
        self.slider4.valueChanged.connect(lambda:self.panda_widget.right_arm.setHpr(0, 0,self.slider4.value()))
        self.ui.store_button.clicked.connect(self.store_event)
        self.ui.reset_button.clicked.connect(self.reset_event)
        self.ui.play_button.clicked.connect(self.play_event)
        # 創建佈局
        layout = QVBoxLayout(container)

        #將 Panda3D 渲染窗口添加到 UI 中
        layout.addWidget(self.panda_widget)

    def get_inponent(self,ui):
        self.store_file=[]
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

    def set_slider(self,slider):
        slider.setMinimum(0)
        slider.setMaximum(180)
        middle_value = (slider.minimum() + slider.maximum()) // 2
        slider.setValue(middle_value)

    def update_slider_value(self,slider,label):
        # 獲取滑動條的值
        slider_value = slider.value()
        label.setText(f" {slider_value}")
        self.updateLabelPosition(slider,label)
        
    def updateLabelPosition(self,slider,label):
        # 計算label的x來置中
        slider_pos = slider.mapToGlobal(slider.rect().topLeft())
        x =  slider_pos.x() + (slider.width() - label.width()/2.25) * (slider.value() - slider.minimum()) / (slider.maximum() - slider.minimum())
        y = slider_pos.y() - 25  # 滑塊上方 25 像素的位置
        label.move(self.ui.mapFromGlobal(QtCore.QPoint(x, y)))
        # 圖層上移保證在上面
        label.raise_()
    #儲存按鈕的事件
    def store_event(self):
        self.store_file.append((self.slider1.value(),self.slider2.value(),self.slider3.value(),self.slider4.value()))
        print(self.store_file)
    #重製按鈕的事件
    def reset_event(self):
        self.store_file=[]
        print('reset sucessful')
    def play_event(self):
        if self.store_file:
            # 定義播放參數
            self.current_index = 0
            self.total_steps = 30  # 每次過渡的總步數
            self.step_counter = 0

            # 設置定時器，用於逐步更新模型
            self.animation_timer = QTimer(self.ui)
            self.animation_timer.timeout.connect(self.animate_to_next_pose)
            self.animation_timer.start(16)  # 每 16 毫秒觸發一次 (60 FPS)

            print("Animation started.")
        else:
            print("No saved poses to play.")

    def animate_to_next_pose(self):
        # 獲取當前和下一個目標數據
        current_pose = self.store_file[self.current_index]
        next_index = (self.current_index + 1) % len(self.store_file)
        next_pose = self.store_file[next_index]

        # 計算插值過渡
        t = self.step_counter / self.total_steps 
        #獲取四個橫條的數據
        interpolated_pose = [
            current_pose[i] + (next_pose[i] - current_pose[i]) * t for i in range(4)
        ]
        print(interpolated_pose)
        # 更新模型的角度
        head_angle, body_angle, left_arm_angle, right_arm_angle = interpolated_pose
        self.panda_widget.left_arm.setHpr(0, 0, left_arm_angle)
        self.panda_widget.right_arm.setHpr(0, 0, right_arm_angle)
       

        self.step_counter += 1

        # 判斷是否完成當前過渡
        if self.step_counter > self.total_steps:
            self.step_counter = 0
            self.current_index = next_index
            # 完成所有動作
            if self.current_index == 0:  
                self.animation_timer.stop()
                print("Animation finished.")


app = QApplication(sys.argv)
stats = Stats()
stats.ui.show()
app.exec()
