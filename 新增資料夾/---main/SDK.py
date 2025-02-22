from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt
from panda3d.core import WindowProperties, AmbientLight, loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import sys
import win32gui
from PySide6.QtGui import QWindow

QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
#隱藏panda3d的邊框和選擇欄
loadPrcFileData('', 'undecorated 1')  
class Panda3DWidget(QWidget):
    def __init__(self, base, parent=None):
        super().__init__(parent)
        self.base = base
        #獲得panda3d的句柄(像索引的東西)
        Wid = win32gui.FindWindowEx(0, 0, None, "Panda")
        if Wid == 0:
            print("Failed to find Panda3D window.")
        else:
            #將panda3d變成Qwindow(類型)
            self.sub_window = QWindow.fromWinId(Wid)
            #將Qwindow從類型變成物件供Qt操作
            self.displayer = QWidget.createWindowContainer(self.sub_window)
            layout = QGridLayout(self)
            #加入布局(建立視窗但尚未加入容器)
            layout.addWidget(self.displayer)
        

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

        # 設置相機
        self.base.cam.setPos(0, -15, 10)
        self.base.cam.lookAt(self.model)

        # 添加光源
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        ambient_node = self.base.render.attachNewNode(ambient_light)
        self.base.render.setLight(ambient_node)

    def update_panda(self):
        """更新 Panda3D 的渲染任務"""
        self.base.taskMgr.step()

class Stats:
    def __init__(self):
        # 加載 UI 文件
        self.ui = QUiLoader().load('ui/SDK.ui')

        # 初始化 Panda3D 基礎類
        self.base = ShowBase()

        # 查找 UI 中的容器部件
        container = self.ui.findChild(QWidget, "Panda3DContainer")
        # 創建 Panda3DWidget嵌入到容器中(parent=父控件)
        self.panda_widget = Panda3DWidget(self.base, parent=container)

        # 創建佈局
        layout = QVBoxLayout(container)
        #將 Panda3D 渲染窗口添加到 UI 中
        layout.addWidget(self.panda_widget)

app = QApplication(sys.argv)
stats = Stats()
stats.ui.show()
app.exec()
