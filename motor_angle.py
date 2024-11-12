from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, QTimer, QThread, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtCore import QUrl
import sys


#啟用ui加載
uiLoader = QUiLoader()

class Stats:
    
    def __init__(self):
        #載入UI
        self.ui = uiLoader.load('ui/motor.ui')
        # 取得元件
        self.slider = self.ui.Slider
        self.label = self.ui.angel_num
        #點擊按鈕連接更動的函數
        self.ui.Button1.clicked.connect(self.set_angel)

        # 設定 Slider 的最小值和最大值
        self.slider.setMinimum(30)    
        self.slider.setMaximum(150)
        # 當 Slider 的值改變時連接函數
        self.slider.valueChanged.connect(self.update_slider_value)


    def set_angel(self):
        #填入樹梅派更動
        print(2)
    def update_slider_value(self):
        # 獲取滑動條的值
        slider_value = self.slider.value()
        self.label.setText(f" {slider_value}")
    
        
#開啟Qapp來管理所有視窗
app = QApplication([])
stats = Stats()
stats.ui.show()  # 顯示UI介面
app.exec()
