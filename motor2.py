#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import division  # 必須放在最前面
import os
import sys
import time
import threading
import socket
import json

import busio
import board
import digitalio
from digitalio import DigitalInOut
from adafruit_pca9685 import PCA9685
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# 強制使用 XCB 後端，避免 Wayland 警告
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


class Rpib:
    """
    树莓派：伺服馬達 + 靜態圖片 & 視頻全螢幕顯示 (PyQt5 版)
    - 開機校準後，同步執行 boot.json 串行馬達動作，並全螢幕播放 boot.mp4
    - 空閒超時後，同步執行 idle.json 串行馬達動作，並全螢幕播放 idle.mp4
    - 監聽 TCP Socket，可接收 JSON 指令：angles / video / image
    """
    def __init__(self, host='0.0.0.0', port=54230):
        # --- 硬體初始化 ---
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pwm = PCA9685(i2c); self.pwm.frequency = 60
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = DigitalInOut(board.D5)
        mcp = MCP.MCP3008(spi, cs)
        self.chan = AnalogIn(mcp, MCP.P0)

        # --- 資源資料夾 --- 
        base_dir = os.path.dirname(__file__)
        video_dir = os.path.join(base_dir, 'video')     # 放 mp4 的資料夾
        json_dir  = os.path.join(base_dir, 'json')      # 放 json 序列的資料夾
        img_dir   = os.path.join(base_dir, 'images')    # 放 png、jpg 圖片的資料夾

        # --- 動畫 & 序列路徑 ---
        self.boot_video = os.path.join(video_dir, 'boot.mp4')
        self.idle_video = os.path.join(video_dir, 'idle.mp4')
        self.boot_seq   = os.path.join(json_dir,  'boot.json')
        self.idle_seq   = os.path.join(json_dir,  'idle.json')
        self.static_img_path = os.path.join(img_dir, 'static.png')
        # --- Qt & 顯示設定 ---
        self.app = QApplication(sys.argv)

        # 1) 常駐全螢幕背景 (static.png)

        self.static_widget = QLabel()
        self.static_widget.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        screen_size = self.app.primaryScreen().size()
        self.static_widget.setGeometry(
            0, 0, screen_size.width(), screen_size.height()
        )
        pix = QPixmap(self.static_img_path).scaled(
            screen_size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        self.static_widget.setPixmap(pix)
        self.static_widget.showFullScreen()
        self.static_widget.raise_()

        # 2) 覆蓋在背景之上的 VideoWidget
        self.video_widget = QVideoWidget()
        self.video_widget.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.video_widget.hide()

        self.player = QMediaPlayer(self.video_widget)
        self.player.setVideoOutput(self.video_widget)
        self.player.mediaStatusChanged.connect(self.on_media_status)

        # --- Idle 檢測設定 ---
        self.idle_timeout = 5.0
        self.last_active  = time.time()
        self.idle_timer   = QTimer()
        self.idle_timer.timeout.connect(self.check_idle)
        self.idle_timer.start(1000)

        # 啟動校準
        self.setup()

        # 啟動 Socket 監聽
        t = threading.Thread(
            target=self.socket_server,
            args=(host, port),
            daemon=True
        )
        t.start()

        sys.exit(self.app.exec_())


    # --- 伺服 & ADC 輔助函式 ---
    def angle_to_pwm(self, angle):
        a = max(min(angle, 90), -90)
        pulse = 150 + (a + 90) * (600 - 150) / 180
        return int(pulse)

    def set_servo_angle(self, ch, ang):
        pwm_val = self.angle_to_pwm(ang)
        self.pwm.channels[ch].duty_cycle = int(pwm_val / 4096 * 65535)
        self.last_active = time.time()

    def load_sequence(self, path):
        info = { 'video': None, 'image': None, 'sequence': [] }
        if os.path.exists(path):
            raw = json.load(open(path, 'r', encoding='utf-8'))
            if isinstance(raw, dict):
                info['video']    = raw.get('video')
                info['image']    = raw.get('image')
                info['sequence'] = raw.get('sequence', [])
            elif isinstance(raw, list):
                info['sequence'] = raw
        return info

    def run_sequence(self, seq):
        for angles in seq:
            if isinstance(angles, list) and len(angles) == 4:
                for i, a in enumerate(angles):
                    self.set_servo_angle(i, a)
                time.sleep(0.5)

    # --- 校準步驟 ---
    def setup(self):
        for i in range(4):
            self.set_servo_angle(i, 0)
        QTimer.singleShot(1000, self.setup_step1)

    def setup_step1(self):
        for i in range(4):
            self.set_servo_angle(i, -80)
        QTimer.singleShot(1000, self.setup_step2)

    def setup_step2(self):
        self.sensorMinA = self.chan.value >> 6
        QTimer.singleShot(500, self.setup_step3)

    def setup_step3(self):
        for i in range(4):
            self.set_servo_angle(i, 80)
        QTimer.singleShot(1000, self.setup_step4)

    def setup_step4(self):
        self.sensorMaxA = self.chan.value >> 6
        for i in range(4):
            self.set_servo_angle(i, 0)
        QTimer.singleShot(500, self.setup_finish)

    def setup_finish(self):
        # 1) 馬達動作
        info = self.load_sequence(self.boot_seq)
        threading.Thread(
            target=self.run_sequence,
            args=(info['sequence'],),
            daemon=True
        ).start()
        # 2) 影片 or 圖片
        if info['video']:
            self.play_video(os.path.join(self.video_dir, info['video']))
        elif info['image']:
            self.show_static(os.path.join(self.video_dir, info['image']))
        else:
            self.play_video(self.boot_video)

    def run_boot_sequence(self):
        seq = self.load_sequence(self.boot_seq)
        self.run_sequence(seq)

    # --- 空閒邏輯 ---
    def check_idle(self):
        elapsed = time.time() - self.last_active
        if elapsed > self.idle_timeout:
            info = self.load_sequence(self.idle_seq)
            threading.Thread(
                target=self.run_sequence,
                args=(info['sequence'],),
                daemon=True
            ).start()
            if info['video']:
                self.play_video(os.path.join(self.video_dir, info['video']))
            elif info['image']:
                self.show_static(os.path.join(self.video_dir, info['image']))
            else:
                self.play_video(self.idle_video)


    def run_idle_sequence(self):
        seq = self.load_sequence(self.idle_seq)
        self.run_sequence(seq)

    # --- Socket 監聽 ---
    def socket_server(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        print(f"Socket server listening on {host}:{port}")
        while True:
            conn, _ = s.accept()
            data = conn.recv(4096)
            conn.close()
            if not data:
                continue
            try:
                cmd = json.loads(data.decode())
            except:
                continue
            self.handle_command(cmd)

    # --- 處理外部指令 ---
    def handle_command(self, cmd):
        # —— angles 如常 —— 
        angs = cmd.get('angles')
        if isinstance(angs, list) and len(angs)==4:
            for i, a in enumerate(angs):
                self.set_servo_angle(i, a)

        # —— video —— 
        vid = cmd.get('video')
        if vid:
            # 如果收到的是相對路徑，就接到 self.video_dir 底下
            if not os.path.isabs(vid):
                vid = os.path.join(self.video_dir, vid)
            if os.path.exists(vid):
                self.play_video(vid)

        # —— image —— 
        img = cmd.get('image')
        if img:
            # 如果收到的是相對路徑，就接到 self.img_dir 底下
            if not os.path.isabs(img):
                img = os.path.join(self.img_dir, img)
            if os.path.exists(img):
                self.player.stop()
                self.video_widget.hide()
                pix = QPixmap(img).scaled(
                    self.app.primaryScreen().size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                self.static_widget.setPixmap(pix)
        seq_update = cmd.get('update_sequence')
        if isinstance(seq_update, dict):
            # boot.json
            if 'boot' in seq_update:
                try:
                    with open(self.boot_seq, 'w', encoding='utf-8') as f:
                        json.dump(seq_update['boot'], f, ensure_ascii=False, indent=2)
                    print(f"已更新 {self.boot_seq}")
                except Exception as e:
                    print("寫入 boot.json 失敗：", e)
            # idle.json
            if 'idle' in seq_update:
                try:
                    with open(self.idle_seq, 'w', encoding='utf-8') as f:
                        json.dump(seq_update['idle'], f, ensure_ascii=False, indent=2)
                    print(f"已更新 {self.idle_seq}")
                except Exception as e:
                    print("寫入 idle.json 失敗：", e)

    # --- 播放並覆蓋全螢幕 ---
    def play_video(self, path):
        # 隱藏靜態背景
        self.static_widget.hide()
        # 全螢幕顯示 video_widget
        self.video_widget.setFullScreen(True)
        screen = self.app.primaryScreen().size()
        self.video_widget.setGeometry(0, 0,
                                      screen.width(),
                                      screen.height())
        self.video_widget.show()
        self.video_widget.raise_()
        # 播放影片
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.player.play()
    def show_static(self, img_path):
        """把 static_widget 拿出來顯示單張圖片"""
        self.player.stop()
        self.video_widget.hide()
        pix = QPixmap(img_path).scaled(
            self.app.primaryScreen().size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        self.static_widget.setPixmap(pix)
        self.static_widget.showFullScreen()
    # --- 媒體播放狀態偵聽 ---
    def on_media_status(self, status):
        from PyQt5.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia:
            # 結束後退出全螢幕並隱藏影片層
            self.video_widget.setFullScreen(False)
            self.video_widget.hide()
            # 恢復靜態背景
            self.static_widget.showFullScreen()


if __name__ == '__main__':
    Rpib(host='100.105.82.116', port=54230)
