from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, QTimer, QThread, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtCore import QUrl
import sys
from face_function import face_rec

#啟用ui加載
uiLoader = QUiLoader()

class Stats:
    def __init__(self):
        #載入UI
        self.ui = uiLoader.load('ui/Button.ui')
        #點擊按鈕連接face的函數
        self.ui.Button_A.clicked.connect(self.printA)
        self.ui.Button_B.clicked.connect(self.printb)
    def printA(self):
        print('a')
    def printb(self):
        print('b')
   
    
#開啟Qapp來管理所有視窗
app = QApplication([])
stats = Stats()
stats.ui.show()  # 顯示UI介面
app.exec()
