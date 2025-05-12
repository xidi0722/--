# app_ui.py
import sys
import os
import json
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox
)
import socket
# 在檔案開頭加上：
CONTROL_HOST   = '100.105.82.116'   # 樹莓派的 IP
CONTROL_PORT   = 54231  
# ─── 將設定與三個函式封裝到這個類別 ──────────────────────────────
class ConfigManager:
    CONFIG_FILE   = 'config.json'
    FINGER_SCRIPT = 'finger_execute.py'

    def __init__(self):
        # 啟動 finger_execute.py 背景程式
        self.launch_finger_execute_bg()
        # 載入或初始化設定
        self.cfg = self.load_config()

    def load_config(self) -> dict:
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        else:
            cfg = {}
        # 確保欄位
        cfg.setdefault('camera_enabled', False)
        cfg.setdefault('mapping', {str(i): "" for i in range(1, 6)})
        for i in range(1, 6):
            cfg['mapping'].setdefault(str(i), "")
        return cfg

    def save_config(self):
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=4)

    def launch_finger_execute_bg(self):
        """一啟動就啟動 finger_execute.py，永不關閉"""
        script = os.path.join(os.path.dirname(__file__), self.FINGER_SCRIPT)
        python_exe = sys.executable
        kwargs = {'close_fds': True}
        if os.name == 'nt':
            kwargs['creationflags'] = 0x00000200
        else:
            kwargs['start_new_session'] = True
        subprocess.Popen([python_exe, script], **kwargs)
# ─────────────────────────────────────────────────────────────────

class ConfigWindow(QWidget, ConfigManager):
      
    def __init__(self):
         # 先呼叫兩個父類別的 __init__
        QWidget.__init__(self)
        ConfigManager.__init__(self)
        self.setWindowTitle("手勢+攝影機設定")

        # 2) 建 UI
        layout = QVBoxLayout()

        # Finger 對應設定
        self.edits = {}
        for i in range(1, 6):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Finger {i}:"))
            edit = QLineEdit(self.cfg['mapping'][str(i)])
            row.addWidget(edit)
            layout.addLayout(row)
            self.edits[str(i)] = edit

        # 攝影機開關
        self.chk_cam = QCheckBox("開啟攝影機")
        self.chk_cam.setChecked(self.cfg['camera_enabled'])
        self.chk_cam.toggled.connect(self.on_toggle_camera)
        layout.addWidget(self.chk_cam)

        # 儲存設定按鈕
        btn_save = QPushButton("儲存 ")
        btn_save.clicked.connect(self.on_save)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def on_toggle_camera(self, checked: bool):
        # 1) 更新本地 config
        self.cfg['camera_enabled'] = checked
        self.save_config()

        # 2) 把控制字串送到 Pi
        cmd = 'camera 1' if checked else 'camera 0'
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # 3 秒逾時
                s.connect((CONTROL_HOST, CONTROL_PORT))
                s.sendall(cmd.encode('utf-8'))
            QMessageBox.information(self, "攝影機", f"已發送指令：{cmd}")
        except Exception as e:
            QMessageBox.critical(self, "攝影機控制失敗", str(e))

        # 3) UI 回饋
        if checked:
            QMessageBox.information(self, "攝影機", "已啟用攝影機")
        else:
            QMessageBox.information(self, "攝影機", "已關閉攝影機")

    def on_save(self):
        for k, edit in self.edits.items():
            self.cfg['mapping'][k] = edit.text().strip()
        self.save_config()
        QMessageBox.information(self, "儲存成功", f"已更新 {self.CONFIG_FILE}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ConfigWindow()
    win.show()
    sys.exit(app.exec())
