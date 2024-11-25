from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, QTimer, QThread, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtCore import QUrl
from PySide6 import QtCore
import os
import sys

#修改


#啟用ui加載
uiLoader = QUiLoader()

class Stats:
    
    def __init__(self):
        #載入UI
        self.ui = uiLoader.load('ui/SDK.ui')
        # 取得元件
        self.slider1 = self.ui.Slider1
        self.label1 = self.ui.Slider_num1
        #點擊按鈕連接更動的函數


        # 設定 Slider 的最小值和最大值
        self.slider1.setMinimum(0)    
        self.slider1.setMaximum(180)

        middle_value = (self.slider1.minimum() + self.slider1.maximum()) // 2
        self.slider1.setValue(middle_value)
        

        # 當 Slider 的值改變時連接函數
        self.slider1.valueChanged.connect(self.update_slider_value)
        QTimer.singleShot(0, self.updateLabelPosition)

    def set_angel(self):
        #填入樹梅派更動
        
        main = "C:/Users/USER/Desktop/專案/exe/Volume_up.exe"
        f = os.popen(main)    
        f.close()    

    def update_slider_value(self):
        # 獲取滑動條的值
        slider_value = self.slider1.value()
        self.label1.setText(f" {slider_value}")
        self.updateLabelPosition()
    def updateLabelPosition(self):
        
        slider_pos = self.slider1.mapToGlobal(self.slider1.rect().topLeft())
        x =  slider_pos.x() + (self.slider1.width()+8- self.label1.width()/2) * (self.slider1.value() - self.slider1.minimum()) / (self.slider1.maximum() - self.slider1.minimum())
        y = y = slider_pos.y() - self.label1.height() - 5  # 滑塊上方 25 像素的位置
        self.label1.move(self.ui.mapFromGlobal(QtCore.QPoint(x, y)))
        # 圖層上移保證在上面
        self.label1.raise_()  
    
        
#開啟Qapp來管理所有視窗
app = QApplication([])
stats = Stats()
stats.ui.show()  # 顯示UI介面
app.exec()
