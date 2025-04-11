from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout, QGridLayout, QApplication, QWidget, QFileDialog, QLabel, QScrollArea,QToolTip,QPushButton, QSizePolicy
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt, QMimeData
from PySide6.QtGui import QWindow, QDrag, QPixmap, QImage,QCursor
from PySide6 import QtCore
from panda3d.core import WindowProperties, NodePath, PointLight, AmbientLight, loadPrcFileData, PNMImage
from direct.showbase.ShowBase import ShowBase
import os
import sys
import win32gui
import socket
import json
from PySide6.QtWidgets import QDialog, QGridLayout, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from draggablelable import DraggableLabel
# Set up shared OpenGL context and Panda3D window properties
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
loadPrcFileData('', 'undecorated 1')


EXPRESSION_OPTIONS = {
    "開心": "images/happy.png",
    "難過": "images/cry.png",
    "生氣": "images/angry.png",
    "鄙視": "images/disdain.png",
    "愛心": "images/heart.png",
    "星星": "images/star.png",
}
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
        self.expression_file = None
        self.data = {}  # 用來儲存資料字典

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        self.expr_button = QPushButton("選擇表情")
        self.expr_button.setFixedHeight(30)
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
                self.data["expression"] = selected_path

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
        # Get Panda3D window handle
        Wid = win32gui.FindWindowEx(0, 0, None, "Panda")
        if Wid == 0:
            print("Failed to find Panda3D window.")
        else:
            self.sub_window = QWindow.fromWinId(Wid)
            self.displayer = QWidget.createWindowContainer(self.sub_window)
            layout = QGridLayout(self)
            layout.addWidget(self.displayer)

        # Update Panda3D rendering
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_panda)
        self.timer.start(16)  # 60 FPS

        # Load model
        self.model = self.base.loader.loadModel("blender/robo1.glb")
        if self.model:
            self.model.reparentTo(self.base.render)
        else:
            print("Model failed to load.")
        self.left_arm = self.model.find("**/left_arm")
        self.right_arm = self.model.find("**/right_arm")
        self.base.cam.setPos(8, 3, 3)
        self.base.cam.lookAt(self.model)
        self.add_lighting()

    def add_lighting(self):
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        ambient_light_node = self.base.render.attachNewNode(ambient_light)
        self.base.render.setLight(ambient_light_node)
        point_light = PointLight('point_light')
        point_light.setColor((1, 1, 1, 1))
        point_light_node = self.base.render.attachNewNode(point_light)
        point_light_node.setPos(10, -10, 10)
        self.base.render.setLight(point_light_node)

    def update_panda(self):
        self.base.taskMgr.step()

class Stats:
    def __init__(self):
        # Load UI file
        self.ui = QUiLoader().load('ui/SDK.ui')
        self.get_inponent(self.ui)

        # Connect slider events
        self.slider1.valueChanged.connect(lambda: self.update_slider_value(self.slider1, self.label1))
        self.slider2.valueChanged.connect(lambda: self.update_slider_value(self.slider2, self.label2))
        self.slider3.valueChanged.connect(lambda: self.update_slider_value(self.slider3, self.label3))
        self.slider4.valueChanged.connect(lambda: self.update_slider_value(self.slider4, self.label4))

        # Initialize Panda3D
        self.base = ShowBase()
        container = self.ui.findChild(QWidget, "Panda3DContainer")
        self.panda_widget = Panda3DWidget(self.base, parent=container)
        self.slider3.valueChanged.connect(lambda: self.panda_widget.left_arm.setHpr(0, 0, self.slider3.value()))
        self.slider4.valueChanged.connect(lambda: self.panda_widget.right_arm.setHpr(0, 0, self.slider4.value()))

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
        # Raspberry Pi settings
        self.pi_ip = '100.105.82.116'
        self.pi_port = 54230
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
                "expression": ""
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
            else:
                # 如果沒有表情，清空顯示
                self.expressionPreviewLabel.clear()

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
                        print(f"動作 {i+1}: angles = {data['angles']}, 表情路徑 = {data['expression']}")
                    
                    # 直接播放動作
                    self.play_event()
                else:
                    print("檔案中沒有儲存任何動作。")
            except Exception as e:
                print("讀取檔案時發生錯誤:", e)

    def send_latest_command(self):
        if self.latest_angle is not None:
            self.send_command_to_pi(self.latest_angle)

    def send_command_to_pi(self, angle):
        command = str(angle)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.pi_ip, self.pi_port))
                sock.sendall(command.encode())
                print(f"Sent command '{command}' to Pi at {self.pi_ip}:{self.pi_port}")
        except Exception as e:
            print("Failed to send command:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stats = Stats()
    stats.ui.show()
    app.exec()