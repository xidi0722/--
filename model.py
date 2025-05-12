from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout, QGridLayout, QApplication, QWidget, QFileDialog, QLabel, QScrollArea,QToolTip,QPushButton, QSizePolicy,QStackedWidget,QComboBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt, QMimeData
from PySide6.QtGui import QWindow, QDrag, QPixmap, QImage,QCursor
from PySide6 import QtCore
from panda3d.core import WindowProperties, PointLight, AmbientLight, loadPrcFileData, PNMImage, Vec3
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
import os
import sys
import subprocess
import win32gui
import socket
import json
from PySide6.QtWidgets import QDialog, QGridLayout, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from draggablelable import DraggableLabel
from alarm_gui import AlarmClock
from action_editer import CustomDropdown

# Set up shared OpenGL context and Panda3D window properties
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
loadPrcFileData('', 'undecorated 1')
# 設定基底目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 指定存放 JSON 檔案的資料夾，並檢查如果不存在就建立
JSON_DIR = os.path.join(BASE_DIR, "action_json")
if not os.path.exists(JSON_DIR):
    os.makedirs(JSON_DIR)
# 將持久化檔案存放在 action_json 資料夾中
PERSISTENT_FILE = os.path.join(JSON_DIR, "persistent_files.json")
ACTION_FOLDER = os.path.join(BASE_DIR, "action_folder")
if not os.path.exists(ACTION_FOLDER):
    os.makedirs(ACTION_FOLDER)

EXPRESSION_OPTIONS = {
    "開心": "images/happy.png",
    "難過": "images/cry.png",
    "生氣": "images/angry.png",
    "鄙視": "images/disdain.png",
    "愛心": "images/heart.png",
    "星星": "images/star.png",
}
def launch_alarm_bg():
    # 請確認 alarm_bg.py 的完整路徑
    alarm_path = "alarm_bg.py"
    # 使用目前的 Python 執行檔
    python_executable = sys.executable

    # Windows 上設定 DETACHED_PROCESS 標誌
    DETACHED_PROCESS = 0x00000008
    creationflags = DETACHED_PROCESS

    # 啟動 alarm_bg 子程序，並將其脫離主程式關聯
    subprocess.Popen(
        [python_executable, alarm_path],
        creationflags=creationflags,
        close_fds=True,
    )
    print("已啟動 alarm_bg 為獨立子程序。")
class MultiPageContainer(QWidget):
    def __init__(self, ui_list, parent=None):
        """
        ui_list: 一個包含多個 QWidget 頁面的列表
        """
        super().__init__(parent)
        self.ui_list = ui_list

        # 建立主垂直佈局，去除邊距及間距，讓內容貼近左上角
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 建立頂部水平佈局，用於放置頁面切換控件（例如 QComboBox)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        self.pageSwitcher = QComboBox()
        # 根據傳入的 ui 頁面建立選項，這裡可以自定義顯示名稱
        self.pageSwitcher.addItem("動作編輯")
        self.pageSwitcher.addItem("指令編輯")
        self.pageSwitcher.addItem("鬧鐘")

        top_layout.addWidget(self.pageSwitcher, alignment=Qt.AlignLeft | Qt.AlignTop)
        main_layout.addLayout(top_layout)

        # 建立 QStackedWidget 並將各個 ui 頁面加入
        self.pageStack = QStackedWidget()
        self.pageStack.setContentsMargins(0, 0, 0, 0)
        for ui in ui_list:
            self.pageStack.addWidget(ui)
        main_layout.addWidget(self.pageStack)

        # 當切換控件改變時，設定 QStackedWidget 切換到相對應的頁面
        self.pageSwitcher.currentIndexChanged.connect(lambda index: self.pageStack.setCurrentIndex(index))

class ExpressionSelectionDialog(QDialog):
    def __init__(self, expressions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("選擇表情")
        self.selected_expression = None

        layout = QGridLayout(self)
        row = 0
        col = 0
        # 每個按鈕以縮圖方式顯示
        for name, path in expressions.items():
            btn = QPushButton()
            btn.setIcon(QIcon(path))
            btn.setIconSize(QSize(50, 50))
            btn.setFixedSize(70, 70)
            btn.setToolTip(name)
            btn.clicked.connect(lambda _, p=path: self.expression_selected(p))
            layout.addWidget(btn, row, col)
            col += 1
            if col >= 3:  # 每行顯示三個按鈕
                col = 0
                row += 1

    def expression_selected(self, path):
        self.selected_expression = path
        self.accept()



class PoseWidget(QWidget):
    def __init__(self, pose_data, index):
        super().__init__()
        self.pose_data = pose_data
        DEFAULT_EXPRESSION = "images/deafult.png"
        self.expression_file = DEFAULT_EXPRESSION
        self.data = {}  # 用來儲存資料字典

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        self.expr_button = QPushButton("選擇表情")
        self.expr_button.setFixedHeight(30)
        pixmap = QPixmap(DEFAULT_EXPRESSION)
        thumbnail = pixmap.scaled(30, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.expr_button.setIcon(QIcon(thumbnail))
        self.expr_button.setIconSize(thumbnail.size())
        # 根據文字與縮圖寬度設定按鈕寬度
        text_width = self.expr_button.fontMetrics().horizontalAdvance(self.expr_button.text())
        button_width = thumbnail.width() + text_width + 20
        self.expr_button.setFixedWidth(button_width)
        # ---------------------------------
        button_layout.addWidget(self.expr_button, alignment=Qt.AlignCenter)
        self.expr_button.clicked.connect(self.select_expression)

        self.image_label = DraggableLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setProperty("index", index)
        main_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        self.order_label = QLabel(f"{index + 1}")
        self.order_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.order_label, alignment=Qt.AlignCenter)

    def select_expression(self):
        # 利用自定義對話框顯示固定表情選項
        dialog = ExpressionSelectionDialog(EXPRESSION_OPTIONS, self)
        if dialog.exec() == QDialog.Accepted:
            selected_path = dialog.selected_expression
            if selected_path:
                self.expression_file = selected_path
                self.data["img"] = selected_path

                # 載入圖片並縮放為縮圖
                pixmap = QPixmap(selected_path)
                thumbnail = pixmap.scaled(30, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                base_name = os.path.basename(selected_path)
                self.expr_button.setIcon(QIcon(thumbnail))
                self.expr_button.setText(base_name)
                self.expr_button.setIconSize(thumbnail.size())

                # 根據文字與縮圖寬度設定按鈕大小
                text_width = self.expr_button.fontMetrics().horizontalAdvance(base_name)
                button_width = thumbnail.width() + text_width + 20
                self.expr_button.setFixedWidth(button_width)
                self.expr_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        
    
class Panda3DWidget(QWidget):
    def __init__(self, base, parent=None):
        super().__init__(parent)
        self.base = base
        Wid = win32gui.FindWindowEx(0, 0, None, "Panda")
        if Wid == 0:
            print("Failed to find Panda3D window.")
        else:
            self.sub_window = QWindow.fromWinId(Wid)
            self.displayer = QWidget.createWindowContainer(self.sub_window)
            # 設定自動擴展
            self.displayer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout = QGridLayout(self)
            layout.addWidget(self.displayer)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_panda)
        self.timer.start(16)
        

        # Load model
        # 1) 用 Actor 載入並自動套用 bind pose
        self.actor = Actor("blender/robot.glb")
        if not self.actor:
            print("Actor 載入失敗！")
            return
        self.actor.reparentTo(self.base.render)
        self.actor.setScale(0.1)

        # 3) 重新計算 tight bounds，並把鏡頭擺回去
        # 計算 tight bounds 之後──
        min_pt, max_pt = self.actor.getTightBounds()
        center   = (min_pt + max_pt) * 0.5
        radius   = (max_pt - center).length()

        # 你原本的後退距離
        cam_dist = radius * 3.3

        # 原本的抬高（模型高度 10%）
        vertical_offset = (max_pt.z - min_pt.z) * 0.1

        # 再額外抬高模型 20% 的高度
        extra_height = (max_pt.z - min_pt.z) * 0.5

        # 合併起來
        self.base.cam.setPos(
            center + Vec3(cam_dist, 0, vertical_offset + extra_height)
        )
        self.base.cam.lookAt(center)

   
        # 如果有預設動作，可以先 pose 到第 0 幀，確保 bind-pose 正確
        # self.actor.pose("default", 0)
         # 2) 釋放並取得關節的 NodePath，之後就能像操作普通 NodePath 一樣
        #    注意：第二個參數要填你的 root 骨架名稱，通常是 "modelRoot" 或 "root"
        self.left_arm  = self.actor.controlJoint(None, "modelRoot", "left_hand")
        self.right_arm = self.actor.controlJoint(None, "modelRoot", "right_hand")
        self.body      = self.actor.controlJoint(None, "modelRoot", "root")
        self.head      = self.actor.controlJoint(None, "modelRoot", "head")
        self.bottom    = self.actor.controlJoint(None, "modelRoot", "bottom")
        
        self.base.cam.lookAt(self.actor)

        self.add_lighting()
       

    def add_lighting(self):
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        ambient_light_node = self.base.render.attachNewNode(ambient_light)
        self.base.render.setLight(ambient_light_node)
        point_light = PointLight('point_light')
        point_light.setColor((1, 1, 1, 1))
        point_light_node = self.base.render.attachNewNode(point_light)
        point_light_node.setPos(0, -10, 10)
        self.base.render.setLight(point_light_node)

    def update_panda(self):
        self.base.taskMgr.step()

class Stats:
    def __init__(self):
        # Load UI file
        self.ui = QUiLoader().load('ui/SDK.ui')
        self.get_inponent(self.ui)

        self.default_image_path = "images/deafult.png"  # 請確保這個檔案存在
        pixmap = QPixmap(self.default_image_path)
        # 可依照需要設定縮放尺寸
        self.expressionPreviewLabel.setPixmap(pixmap.scaled(
            self.expressionPreviewLabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

        # Connect slider events
        self.slider1.valueChanged.connect(lambda: self.update_slider_value(self.slider1, self.label1))
        self.slider2.valueChanged.connect(lambda: self.update_slider_value(self.slider2, self.label3))
        self.slider3.valueChanged.connect(lambda: self.update_slider_value(self.slider3, self.label2))
        self.slider4.valueChanged.connect(lambda: self.update_slider_value(self.slider4, self.label4))

        # Initialize Panda3D
        self.base = ShowBase()
        container = self.ui.findChild(QWidget, "Panda3DContainer")
        self.panda_widget = Panda3DWidget(self.base, parent=container)
        self.slider1.valueChanged.connect(lambda:  self.panda_widget.head.setHpr( self.slider1.value(),0, 0))
        self.slider2.valueChanged.connect(lambda:  self.panda_widget.body.setHpr( 0,0,self.slider2.value()))
        self.slider3.valueChanged.connect(lambda: self.panda_widget.left_arm.setHpr(0, 0, self.slider3.value()-180))
        self.slider4.valueChanged.connect(lambda: self.panda_widget.right_arm.setHpr(0, 0 ,-(self.slider4.value()-180)))

        # Connect button events
        self.ui.store_button.clicked.connect(self.store_event)
        self.ui.reset_button.clicked.connect(self.reset_event)
        self.ui.play_button.clicked.connect(self.play_event)
        self.ui.store_file.clicked.connect(self.store_to_file_event)
        self.ui.play_file.clicked.connect(self.play_from_file_event)

        layout = QVBoxLayout(container)
        layout.addWidget(self.panda_widget)

        # Initialize captured images area
        self.captured_images = []  # List to store DraggableLabel widgets
        scroll_area = self.ui.capturedImagesScrollArea
        scroll_widget = self.ui.scrollAreaWidgetContents

        # 檢查 scrollAreaWidgetContents 是否有 layout，若無則新建一個 QHBoxLayout
        layout_container = self.ui.findChild(QWidget, "scrollwidget")  # 找到包含 layout 的 widget
        self.captured_images_layout = layout_container.layout()
        layout_container.reorder_images = self.reorder_images
        layout_container.setAcceptDrops(True)
        if self.captured_images_layout is None:
            print("Layout 未初始化，重新創建 QVBoxLayout")
            self.captured_images_layout = QHBoxLayout(layout_container)
            layout_container.setLayout(self.captured_images_layout)

        scroll_widget.reorder_images = self.reorder_images  # Assign reordering method to the widget
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.scrollwidget.setAcceptDrops(True)
        
        # Pi 的 IP/Port
        self.pi_ip = '100.105.82.116'
        self.pi_port = 54230
        self.current_expression = ""
        self.latest_angle = None
        self.command_timer = QTimer(self.ui)
        self.command_timer.timeout.connect(self.send_latest_command)
        self.command_timer.start(30)

    def get_inponent(self, ui):
        self.store_file = []
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
        self.expressionPreviewLabel=ui.expression_label
    def set_slider(self, slider):
        slider.setMinimum(-90)
        slider.setMaximum(90)
        middle_value = (slider.minimum() + slider.maximum()) // 2
        slider.setValue(middle_value)

    def update_slider_value(self, slider, label):
        slider_value = slider.value()
        label.setText(f" {slider_value}")
        self.updateLabelPosition(slider, label)

    def updateLabelPosition(self, slider, label):
        slider_pos = slider.mapToGlobal(slider.rect().topLeft())
        x = slider_pos.x() + (slider.width() - label.width() / 2.25) * (slider.value() - slider.minimum()) / (slider.maximum() - slider.minimum())
        y = slider_pos.y() - 25
        label.move(self.ui.mapFromGlobal(QtCore.QPoint(x, y)))
        label.raise_()

    def store_event(self):
        """Capture Panda3D rendering and display it in the scroll area."""
        screenshot = self.base.win.getScreenshot()
        if screenshot:
            pnm = PNMImage()
            screenshot.store(pnm)
            qimage = self.pnmimage_to_qimage(pnm)
            thumbnail = qimage.scaled(100, 100, Qt.KeepAspectRatio)
            
            # 建立 PoseWidget
            pose_widget = PoseWidget(
                pose_data=(
                    self.slider1.value(),
                    self.slider2.value(),
                    self.slider3.value(),
                    self.slider4.value()
                ),
                index=len(self.store_file)
            )
            
            # 顯示 Panda3D 擷取的縮圖
            pose_widget.image_label.setPixmap(QPixmap.fromImage(thumbnail))
            
            # 加入到介面佈局與管理陣列
            self.captured_images_layout.addWidget(pose_widget)
            self.captured_images.append(pose_widget)
            
            # 建立一個資料字典，初始時 "expression" 為空字串
            pose_data_dict = {
                "angles": (
                    self.slider1.value(),
                    self.slider2.value(),
                    self.slider3.value(),
                    self.slider4.value()
                ),
                "img": ""
            }
            # 將資料字典存到 PoseWidget 裡，方便後續更新
            pose_widget.data = pose_data_dict
            self.store_file.append(pose_data_dict)
            
            print("Stored poses:", self.store_file)




    def pnmimage_to_qimage(self, pnmimage):
        width = pnmimage.getXSize()
        height = pnmimage.getYSize()
        # 建立一個 bytearray 來儲存 RGB 資料，每個像素 3 個 bytes
        image_data = bytearray(width * height * 3)
        for y in range(height):
            for x in range(width):
                r, g, b = pnmimage.getXel(x, y)
                idx = (y * width + x) * 3
                image_data[idx] = int(r * 255)
                image_data[idx + 1] = int(g * 255)
                image_data[idx + 2] = int(b * 255)
        # QImage 建構子需要指定每行的 byte 數 (bytesPerLine)
        qimage = QImage(image_data, width, height, width * 3, QImage.Format_RGB888)
        return qimage.copy()  # 複製一份，確保 image_data 可以被釋放


    def reorder_images(self, from_index, to_index):
        print(f"呼叫 reorder_images: 從 {from_index} 到 {to_index}")
        if from_index == to_index:
            print("來源與目的相同，不作變更")
            return

        # 移除並重新插入拖曳的 widget
        widget = self.captured_images.pop(from_index)
        self.captured_images.insert(to_index, widget)
        self.captured_images_layout.removeWidget(widget)
        self.captured_images_layout.insertWidget(to_index, widget)

        # 同步調整儲存陣列順序
        pose = self.store_file.pop(from_index)
        self.store_file.insert(to_index, pose)

        # 更新所有 widget 的順序標籤

        for i, pose_widget in enumerate(self.captured_images):
            pose_widget.order_label.setText(str(i + 1))
            pose_widget.image_label.setProperty("index", i)

        # 強制刷新佈局（如有需要）
        self.captured_images_layout.invalidate()
        self.captured_images_layout.activate()
        self.captured_images_layout.update()

        print("更新後儲存陣列順序:", self.store_file)



    def reset_event(self):
            self.store_file.clear()
            for label in self.captured_images:
                self.captured_images_layout.removeWidget(label)
                label.deleteLater()
            self.captured_images.clear()
            print('Reset successful')

    def play_event(self):
        if hasattr(self, 'animation_timer') and self.animation_timer.isActive():
            print("Animation already running.")
            return
        self.ui.play_button.setEnabled(False)
        if self.store_file:
            self.current_index = 0
            self.total_steps = 30
            self.step_counter = 0
            self.animation_timer = QTimer(self.ui)
            self.animation_timer.timeout.connect(self.animate_to_next_pose)
            self.animation_timer.start(16)
            print("Animation started.")
        else:
            print("No saved poses to play.")

    def animate_to_next_pose(self):
        current_pose = self.store_file[self.current_index]
        next_pose = self.store_file[self.current_index + 1] if self.current_index < len(self.store_file) - 1 else current_pose
        
        # 根據 step_counter 計算動作插值
        t = self.step_counter / self.total_steps
        interpolated_pose = [
            current_pose["angles"][i] + (next_pose["angles"][i] - current_pose["angles"][i]) * t
            for i in range(4)
        ]
        self.latest_angle = interpolated_pose

        # step_counter==0：表示剛切到新的動作，可以在這裡更新表情
        if self.step_counter == 0:
            expr = current_pose.get("expression", "")
            print(f"目前動作的表情：{expr}")
            
            if expr:
                pixmap = QPixmap(expr)
                # 將圖片依照 expressionPreviewLabel 的大小縮放
                scaled_pixmap = pixmap.scaled(
                    self.expressionPreviewLabel.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.expressionPreviewLabel.setPixmap(scaled_pixmap)
                self.current_expression = expr
            else:
                # 如果沒有表情，清空顯示 
                pixmap = QPixmap(self.default_image_path)
                # 可依照需要設定縮放尺寸
                self.expressionPreviewLabel.setPixmap(pixmap.scaled(
                    self.expressionPreviewLabel.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                self.current_expression = ""

        # 讓 Panda3D 的手臂隨著 interpolated_pose 做角度插值
        head_angle, body_angle, left_arm_angle, right_arm_angle = interpolated_pose
        self.panda_widget.left_arm.setHpr(0, 0, left_arm_angle)
        self.panda_widget.right_arm.setHpr(0, 0, right_arm_angle)

        self.step_counter += 1
        if self.step_counter > self.total_steps:
            self.step_counter = 0
            if self.current_index < len(self.store_file) - 1:
                self.current_index += 1
            else:
                self.animation_timer.stop()
                self.ui.play_button.setEnabled(True)
                self.latest_angle = None
                print("Animation finished.")
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.pi_ip, self.pi_port))
                    s.send(json.dumps({"reset_background": True}).encode("utf-8"))
                    s.close()
                    print("已送出 reset_background 給 Pi")
                except Exception as e:
                    print("送 reset_background 失敗：", e)

    def store_to_file_event(self):
        if not self.store_file:
            QToolTip.showText(QCursor.pos(),"沒有儲存任何動作無法儲存", self.ui.store_button)
            return

        folder = "action_folder"
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename, _ = QFileDialog.getSaveFileName(self.ui, "儲存動作檔案", folder, "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, "w") as f:
                    json.dump(self.store_file, f, ensure_ascii=False, indent=2)
                QToolTip.showText(QCursor.pos(),f"成功儲存到: {filename}", self.ui.store_button)
                print(f"Stored poses saved to file: {filename}")
            except Exception as e:
                QToolTip.showText(QCursor.pos(),f"儲存檔案失敗: {e}", self.ui.store_button)
                print("Error saving file:", e)


    def play_from_file_event(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "讀取動作檔案", "action_folder", "JSON Files (*.json)")

        if filename:
            try:
                with open(filename, "r") as f:
                    self.store_file = json.load(f)
                
                if self.store_file:
                    print("從檔案讀取成功：")
                    for i, data in enumerate(self.store_file):
                        #表情圖片路徑
                        print(f"動作 {i+1}: angles = {data['angles']}, 表情路徑 = {data['img']}")
                    
                    # 直接播放動作
                    self.play_event()
                else:
                    print("檔案中沒有儲存任何動作。")
            except Exception as e:
                print("讀取檔案時發生錯誤:", e)

    def send_latest_command(self):
        if self.latest_angle is not None:
            self.send_command(self.latest_angle)

    def send_command(self, angle):
        # 把角度跟表情一起打包
        img_name = os.path.basename(self.current_expression) if self.current_expression else None

        payload = {
            "angles": angle
        }
        if img_name:
            payload["image"] = img_name

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.pi_ip, self.pi_port))
            s.send(json.dumps(payload).encode("utf-8"))
            s.close()
            print("已送出命令到 Pi：", payload)
        except Exception as e:
            print("送命令到 Pi 失敗：", e)
    def on_sequence_selected(self, which, filepath):
        """
        which: 'boot' 或 'idle'
        filepath: 使用者在下拉選單裡選到的 JSON 檔案路徑
        """
        # 1) 讀 JSON 檔案內容
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                seq = json.load(f)
        except Exception as e:
            print(f"無法讀取 {filepath}：", e)
            return

        # 2) 封裝成 update_sequence 命令
        payload = {
            'update_sequence': {
                which: seq
            }
        }

        # 3) 連到 Pi，送出 payload
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.pi_ip, self.pi_port))
            s.send(json.dumps(payload).encode('utf-8'))
            s.close()
            print(f"已更新 Pi 上的 {which}.json")
        except Exception as e:
            print("傳送更新到 Pi 失敗：", e)

if __name__ == "__main__":
    launch_alarm_bg()
    app = QApplication(sys.argv)  # 首先建立 QApplication

    # 建立 AlarmClock 物件，若其為 QMainWindow 則取出 centralWidget
    alarm = AlarmClock()
    alarm_widget = alarm.centralWidget() if alarm.centralWidget() is not None else alarm

    # 建立 Stats 物件，假設其主要介面為 stats.ui（透過 QUiLoader 載入）
    stats = Stats()
    window = QWidget()
    window.setWindowTitle("指令編輯")
    instr_layout = QVBoxLayout(window)
    instr_layout.setContentsMargins(20,20,20,20)
    # 建立第三個介面（自訂下拉選單範例）的 widget
    default_options = [
        ("開機預設", r"action_json/boot.json"),
        ("眨眼",r"action_json/idle.json")
        ]
    dropdown_boot = CustomDropdown(
        default_options,
        label_text="開機動作",
        identifier="boot",
        persistent_file=os.path.join(JSON_DIR, "persistent_boot.json")
    )
    dropdown_idle = CustomDropdown(
        default_options,
        label_text="待機動作",
        identifier="idle",
        persistent_file=os.path.join(JSON_DIR, "persistent_idle.json")
    )
    instr_layout.addWidget(dropdown_boot)
    instr_layout.addWidget(dropdown_idle)

    # 4) 當使用者在下拉裡選擇檔案時，把對應的 JSON 發給 Pi
    dropdown_boot.listWidget.itemClicked.connect(
        lambda _: stats.on_sequence_selected("boot", dropdown_boot.current_selection)
    )
    dropdown_idle.listWidget.itemClicked.connect(
        lambda _: stats.on_sequence_selected("idle", dropdown_idle.current_selection)
    )
    
    

    # 將三個介面加入多頁面容器中
    container = MultiPageContainer([ stats.ui, window,alarm_widget])
    #設定視窗標題
    container.setWindowTitle('小機器人')
    #設定視窗大小
    container.resize(800, 600)
    #設定icon
    container.setWindowIcon(QIcon("icon/robot.png"))
    container.show()

    sys.exit(app.exec())
