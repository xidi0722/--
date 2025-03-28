import sys
import os
import json
from PySide6.QtCore import QUrl, QTime, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTimeEdit, QLabel, QMainWindow, QWidget, QListWidget, QFileDialog, QSlider, QMessageBox
)

# 建立 action_json 資料夾（如果不存在的話）
os.makedirs("action_json", exist_ok=True)
ALARM_FILE = os.path.join("action_json", "alarms.json")

def load_alarms():
    if os.path.exists(ALARM_FILE):
        with open(ALARM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def save_alarms(alarms):
    with open(ALARM_FILE, "w", encoding="utf-8") as f:
        json.dump(alarms, f, ensure_ascii=False, indent=4)

class TimePickerDialog(QDialog):
    def __init__(self, initial_time=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("選取時間")
        layout = QVBoxLayout(self)
        
        self.time_edit = QTimeEdit(initial_time if initial_time else QTime.currentTime())
        self.time_edit.setDisplayFormat("hh:mm:ss")
        layout.addWidget(self.time_edit)
        
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("確定")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_time(self):
        return self.time_edit.time()

class AlarmClock(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("鬧鐘設定")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 透過對話框選取新鬧鐘時間
        self.set_time_button = QPushButton("設定新鬧鐘時間")
        main_layout.addWidget(self.set_time_button)
        self.set_time_button.clicked.connect(self.set_new_alarm_time)
        self.current_alarm_time = QTime.currentTime()
        
        # 選取鈴聲按鈕
        self.choose_sound_button = QPushButton("選取鈴聲")
        main_layout.addWidget(self.choose_sound_button)
        self.choose_sound_button.clicked.connect(self.choose_sound)
        self.current_alarm_sound = None  # 暫存目前所選鈴聲完整路徑
        
        # 聲音設定區：檔案名稱、音量滑桿（左右標示在同一行）與試聽按鈕
        sound_layout = QHBoxLayout()
        self.sound_label = QLabel("未選取鈴聲")
        sound_layout.addWidget(self.sound_label)
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("0"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        slider_layout.addWidget(self.volume_slider)
        slider_layout.addWidget(QLabel("100"))
        sound_layout.addLayout(slider_layout)
        
        self.preview_button = QPushButton("試聽")
        sound_layout.addWidget(self.preview_button)
        self.preview_button.clicked.connect(self.preview_sound)
        main_layout.addLayout(sound_layout)
        
        # 功能按鈕：新增、更新、刪除、切換狀態
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("新增鬧鐘")
        self.update_button = QPushButton("更新鬧鐘")
        self.delete_button = QPushButton("刪除鬧鐘")
        self.toggle_button = QPushButton("切換狀態")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.toggle_button)
        main_layout.addLayout(button_layout)
        
        # 鬧鐘列表：顯示時間、鈴聲檔名、音量數值與狀態
        self.alarm_list = QListWidget()
        main_layout.addWidget(self.alarm_list)
        
        # 從檔案載入鬧鐘設定
        self.alarms = load_alarms()  # alarms 為一個列表，每筆資料是一個 dict
        self.refresh_alarm_list()
        
        # 連結按鈕事件
        self.add_button.clicked.connect(self.add_alarm)
        self.update_button.clicked.connect(self.update_alarm)
        self.delete_button.clicked.connect(self.delete_alarm)
        self.toggle_button.clicked.connect(self.toggle_alarm)
        self.alarm_list.itemDoubleClicked.connect(self.edit_alarm_time)
    
    def refresh_alarm_list(self):
        self.alarm_list.clear()
        for alarm in self.alarms:
            status = "啟用" if alarm.get("enabled", True) else "停用"
            self.alarm_list.addItem(f"{alarm['time']} - {os.path.basename(alarm['sound'])} (vol:{alarm['volume']}) [{status}]")
    
    def set_new_alarm_time(self):
        dialog = TimePickerDialog(initial_time=self.current_alarm_time, parent=self)
        if dialog.exec():
            self.current_alarm_time = dialog.get_time()
            self.set_time_button.setText("設定新鬧鐘時間: " + self.current_alarm_time.toString("hh:mm:ss"))
    
    def choose_sound(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選取鈴聲", "", "Audio Files (*.wav *.mp3)")
        if file_path:
            self.current_alarm_sound = file_path
            self.sound_label.setText(os.path.basename(file_path))
    
    def preview_sound(self):
        if self.current_alarm_sound:
            self.play_sound(self.current_alarm_sound, self.volume_slider.value())
    
    def add_alarm(self):
        sound_path = self.current_alarm_sound if self.current_alarm_sound else "default_alarm_sound.wav"
        alarm_time = self.current_alarm_time.toString("hh:mm:ss")
        volume_value = self.volume_slider.value()
        # 檢查是否已有同一時間且啟用的鬧鐘
        for alarm in self.alarms:
            if alarm["time"] == alarm_time and alarm.get("enabled", True):
                QMessageBox.warning(self, "重複鬧鐘", "已經存在一個在相同時間的啟用鬧鐘。")
                return
        # 若沒有重複，則新增鬧鐘，預設為啟用
        alarm = {"time": alarm_time, "sound": sound_path, "volume": volume_value, "enabled": True}
        self.alarms.append(alarm)
        save_alarms(self.alarms)
        self.refresh_alarm_list()
    
    def update_alarm(self):
        row = self.alarm_list.currentRow()
        if row >= 0:
            current_alarm = self.alarms[row]
            dialog = TimePickerDialog(initial_time=QTime.fromString(current_alarm["time"], "hh:mm:ss"), parent=self)
            if dialog.exec():
                new_time = dialog.get_time().toString("hh:mm:ss")
                current_alarm["time"] = new_time
                self.alarms[row] = current_alarm
                save_alarms(self.alarms)
                self.refresh_alarm_list()
    
    def delete_alarm(self):
        row = self.alarm_list.currentRow()
        if row >= 0:
            self.alarm_list.takeItem(row)
            self.alarms.pop(row)
            save_alarms(self.alarms)
    
    def edit_alarm_time(self, item):
        row = self.alarm_list.row(item)
        current_alarm = self.alarms[row]
        dialog = TimePickerDialog(initial_time=QTime.fromString(current_alarm["time"], "hh:mm:ss"), parent=self)
        if dialog.exec():
            new_time = dialog.get_time().toString("hh:mm:ss")
            current_alarm["time"] = new_time
            self.alarms[row] = current_alarm
            save_alarms(self.alarms)
            self.refresh_alarm_list()
    
    def toggle_alarm(self):
        row = self.alarm_list.currentRow()
        if row >= 0:
            alarm = self.alarms[row]
            alarm["enabled"] = not alarm.get("enabled", True)
            self.alarms[row] = alarm
            save_alarms(self.alarms)
            self.refresh_alarm_list()
    
    def play_sound(self, sound_path, volume_value):
        # 如果已存在 preview_player 且正在播放，先停止它
        if hasattr(self, "preview_player") and self.preview_player is not None:
            if self.preview_player.playbackState() == QMediaPlayer.PlayingState:
                self.preview_player.stop()
        self.preview_player = QMediaPlayer()
        self.preview_audio_output = QAudioOutput()
        self.preview_player.setAudioOutput(self.preview_audio_output)
        self.preview_player.setSource(QUrl.fromLocalFile(sound_path))
        self.preview_audio_output.setVolume(volume_value / 100.0)
        self.preview_player.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlarmClock()
    window.show()
    sys.exit(app.exec())
