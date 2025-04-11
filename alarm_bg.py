import sys
import os
import json
import signal
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer, QTime, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

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

# AlarmDialog：鬧鐘響起時的提示小視窗
class AlarmDialog(QDialog):
    def __init__(self, stop_callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle("鬧鐘響起")
        layout = QVBoxLayout(self)
        label = QLabel("鬧鐘！")
        layout.addWidget(label)
        stop_button = QPushButton("中止")
        layout.addWidget(stop_button)
        # 當按下中止時，先呼叫回調函數停止音效，再關閉視窗
        stop_button.clicked.connect(stop_callback)
        stop_button.clicked.connect(self.accept)

class AlarmBackground:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alarms)
        self.timer.start(1000)  # 每秒檢查一次

    def check_alarms(self):
        alarms = load_alarms()
        current_time = QTime.currentTime().toString("hh:mm:ss")
        remaining_alarms = []
        for alarm in alarms:
            # 只觸發啟用的鬧鐘，這裡簡單設計：觸發後移除避免重複
            if alarm.get("enabled", True) and alarm["time"] == current_time:
                self.play_alarm(alarm["sound"], alarm["volume"])
            else:
                remaining_alarms.append(alarm)
        if len(alarms) != len(remaining_alarms):
            save_alarms(remaining_alarms)

    def play_alarm(self, sound_path, volume_value):
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(sound_path))
        volume = volume_value / 100.0
        self.audio_output.setVolume(volume)
        self.player.play()
        print("背景播放：", sound_path, "音量:", volume)
        # 改用 show() 以非模態方式顯示
        self.current_dialog = AlarmDialog(stop_callback=self.player.stop)
        self.current_dialog.show()


    def run(self):
        sys.exit(self.app.exec())

def signal_handler(sig, frame):
    print("收到中斷訊號，背景程式正在退出...")
    sys.exit(0)

if __name__ == "__main__":
    # 在啟動背景程式前註冊 signal 處理器，方便 Ctrl+C 中斷
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    bg = AlarmBackground()
    bg.run()
