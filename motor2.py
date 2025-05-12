#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import division  # 必須放在最前面
import os
import sys
import time
import threading
import socket
import json
import adafruit_dht
import busio
import board
import digitalio
from digitalio import DigitalInOut
from adafruit_pca9685 import PCA9685
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from gpiozero import Button
from signal import pause
# 強制使用 XCB 後端，避免 Wayland 警告
os.environ["QT_QPA_PLATFORM"] = "xcb"
import RPi.GPIO as GPIO
from PyQt5.QtCore import Qt, QTimer, QUrl,QThread, pyqtSignal,pyqtSlot,QObject
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
class SocketWorker(QObject):
    newCommand = pyqtSignal(dict)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    @pyqtSlot()
    def run(self):
        """在這個方法裡啟動 socket 監聽迴圈"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(1)
        print(f"Socket server listening on {self.host}:{self.port}")
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
            # 將指令透過 signal 傳回主執行緒
            self.newCommand.emit(cmd)

class Rpib(QObject):
    """
    树莓派：伺服馬達 + 靜態圖片 & 視頻全螢幕顯示 (PyQt5 版)
    - 開機校準後，同步執行 boot.json 串行馬達動作，並全螢幕播放 boot.mp4
    - 空閒超時後，同步執行 idle.json 串行馬達動作，並全螢幕播放 idle.mp4
    - 監聽 TCP Socket，可接收 JSON 指令：angles / video / image
    """
    vib_signal = pyqtSignal()
    touch_signal=pyqtSignal()
    def __init__(self, host='0.0.0.0', port=54230):
        super().__init__()
         # --- 正在播放／執行動畫的旗標 ---
        self._playing_event = False
        # 用來保存所有活躍的 SequenceRunner，初始化一次就好
        # --- 睡眠模式設定 ---
        self.sleep_threshold = 10       # 10 秒没动就进入睡眠动画
         # --- 触摸冷却设置（和振动类似） ---
        self.touch_cooldown = 10    # 10 秒内只响应一次触摸
        self._last_touch    = 0
        self._sleeping = False           # 当前是否已进入睡眠
        self._idling   = False  
        self.runners = []
        # --- 硬體初始化 ---
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pwm = PCA9685(i2c); self.pwm.frequency = 60
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = DigitalInOut(board.D5)
        mcp = MCP.MCP3008(spi, cs)
        self.chan = AnalogIn(mcp, MCP.P0)
        self.touch = Button(18)
        # 降低 CPU 優先度
        os.nice(10)

        # 使用 DHT22，資料腳接在 GPIO 17（可自行改腳位）
        self.dhtDevice = adafruit_dht.DHT22(board.D17, use_pulseio=False)
        
        self.touch_signal.connect(self.on_touched)

        # 把 gpiozero callback 改成只 emit Qt 訊號
        self.touch.when_pressed = lambda: self.touch_signal.emit()
        self.touch.when_released=self.on_released
        
        # --- Vibration Sensor 設定 ---
        self.vib_pin       = 6        # BCM5，你也可以換別的純 GPIO
        self.vib_cooldown  = 10       # 冷卻時間：10 秒內只響應一次
        self._last_vib     = 0        # 上次觸發的時間戳

        # 建立 gpiozero Button 物件，pull_up=False 視你的接線而定
        self.vib_sensor = Button(self.vib_pin, pull_up=False)
        # 當偵測到按下（震動）時，呼叫 on_vibration
        
        # ② 把這個訊號接到主執行緒裡的 _on_vibration_slot
        self.vib_signal.connect(self._on_vibration_slot)

        # 把 gpiozero callback 改成只 emit Qt 訊號
        self.vib_sensor.when_pressed = lambda: self.vib_signal.emit()
        
        

        # --- 雨天觸發門檻與冷卻設定 ---
        self.rain_humidity_threshold = 80     # 濕度大於 80% 就觸發
        self.rain_cooldown = 30
        self._last_rain=0              # 30 秒內只觸發一次雨天動畫
        # --- 資源資料夾 --- 
        base_dir = os.path.dirname(__file__)
        self.video_dir = os.path.join(base_dir, 'video')     # 放 mp4 的資料夾
        self.json_dir  = os.path.join(base_dir, 'json')      # 放 json 序列的資料夾S
        self.img_dir   = os.path.join(base_dir, 'images')    # 放 png、jpg 圖片的資料夾
        # --- 在 __init__ 的動畫 & 序列路徑區塊，加入 rain.mp4 / rain.json ---
        self.rain_video = os.path.join(self.video_dir, 'rain.mp4')
        self.rain_seq   = os.path.join(self.json_dir,  'rain.json')
        # --- 動畫 & 序列路徑 ---
        self.touch_video = os.path.join(self.video_dir, 'touch.mp4')
        self.touch_seq   = os.path.join(self.json_dir,  'touch.json')
        self.sleep_path = os.path.join(self.video_dir, 'sleep.mp4')
        self.boot_video = os.path.join(self.video_dir, 'boot.mp4')
        self.idle_video = os.path.join(self.video_dir, 'idle.mp4')
        self.boot_seq   = os.path.join(self.json_dir,  'boot.json')
        self.idle_seq   = os.path.join(self.json_dir,  'idle.json')
        # spin 動作
        self.spin_video = os.path.join(self.video_dir, 'spin.mp4')
        self.spin_seq   = os.path.join(self.json_dir,  'spin.json')
        self.static_img_path = os.path.join(self.img_dir, 'deafult.png')
        
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
        
        self.deafult_pixmap = QPixmap(self.static_img_path).scaled(
            screen_size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        pix=self.deafult_pixmap
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
         # --- DHT22 定時讀取設定（每 5 秒呼叫一次） ---
        self.dht_timer = QTimer()
        # 直接把你的讀取函式連到 timeout
        self.dht_timer.timeout.connect(self.dht22_detected)
        # 5000 毫秒 = 5 秒
        self.dht_timer.start(5000)
            # 啟動校準
        self.setup()
        
        self.socket_thread = QThread()
        self.socket_worker = SocketWorker(host, port)
        self.socket_worker.moveToThread(self.socket_thread)

        # 當 QThread 啟動，就呼叫 worker.run()
        self.socket_thread.started.connect(self.socket_worker.run)

        # 當 worker 收到 cmd，就在主執行緒呼叫 handle_command
        self.socket_worker.newCommand.connect(self.handle_command)

        # 啟動 QThread
        self.socket_thread.start()
        try:
            sys.exit(self.app.exec_())
        finally:
            # ⚙️ 清理 GPIO
            GPIO.cleanup()
    @pyqtSlot()        
    def on_touched(self):
        # 如果已經在播，就先跳過
        if self._playing_event and not (self._sleeping or self._idling):
            
            return
        now = time.time()
        if now - self._last_touch < self.touch_cooldown:
            return
        print('touch trigged')
        self._last_touch = now
        self._sleeping = False
        self._idling   = False
        self._playing_event = False
        
        info = self.load_sequence(self.touch_seq)
        print(info['sequence'])

        # ——— 播放媒体 ———
        if info['video']:
            vid = info['video']
            vid_path = vid if os.path.isabs(vid) else os.path.join(self.video_dir, vid)
            if os.path.exists(vid_path):
                self.play_video(vid_path)
        elif info['img']:
            img_path = info['img'] if os.path.isabs(info['img']) else os.path.join(self.img_dir, info['img'])
            if os.path.exists(img_path):
                self.show_static(img_path)
        else:
            # fallback 播 touch.mp4
            if os.path.exists(self.touch_video):
                self.play_video(self.touch_video)

        # ——— 排程马达 ———
        if info['sequence']:
            self.schedule_sequence(info['sequence'], interval_ms=500)


    def on_released(self):
        print('放開了')
    @pyqtSlot()
    def _on_vibration_slot(self):
        
        # 如果已經在播，就先跳過
        if self._playing_event and not (self._sleeping or self._idling):
            
            return
        now = time.time()
        if now - self._last_vib < self.vib_cooldown:
            return
        print('vibration trigged')
        self._last_vib = now
        self._sleeping = False
        self._idling   = False
        self._playing_event = False
        info = self.load_sequence(self.spin_seq)

        # ——— 媒體播放（不跳過伺服） ———
        if info['video']:
            vid = info['video']
            vid = vid if os.path.isabs(vid) else os.path.join(self.video_dir, vid)
            if os.path.exists(vid):
                self.play_video(vid)
        elif info['img']:
            img_path = info['img'] if os.path.isabs(info['img']) else os.path.join(self.img_dir, info['img'])
            if os.path.exists(img_path):
                self.show_static(img_path)
        else:
            # 沒指定就播預設 spin.mp4
            if os.path.exists(self.spin_video):
                self.play_video(self.spin_video)

        # ——— 無論是否有媒體，都一併排程馬達動作 ———
        if info['sequence']:
            self.schedule_sequence(info['sequence'], interval_ms=300)
    def schedule_sequence(self, seq, interval_ms):
        """
        seq: list of steps, each step 可以是：
        - list of 4 angles: [a0, a1, a2, a3]
        - dict with keys "video", "image", "angles"
        interval_ms: 每步之間的間隔毫秒數
        """
        for idx, step in enumerate(seq):
            delay = idx * interval_ms

            # 用 default arg 捕捉當前 step
            def action(s=step):
                # 1) 如果是 dict，先播 media
                if isinstance(s, dict):
                    # video 優先
                    vid = s.get("video")
                    if vid:
                        vid_path = vid if os.path.isabs(vid) else os.path.join(self.video_dir, vid)
                        if os.path.exists(vid_path):
                            self.play_video(vid_path)
                            

                    # image 次之
                    img = s.get("img")
                    if img:
                        img_path = img if os.path.isabs(img) else os.path.join(self.img_dir, img)
                        if os.path.exists(img_path):
                            self.show_static(img_path)

                    # 最後取 angles
                    angles = s.get("angles", [])
                else:
                    # 若 step 本身就是 list，就當成 angles
                    angles = s

                # 2) 執行伺服馬達動作
                for ch, a in enumerate(angles):
                    self.set_servo_angle(ch, a)

            QTimer.singleShot(delay, action)
        total = len(seq) * interval_ms
        QTimer.singleShot(total, lambda: setattr(self, '_playing_event', False))
    def dht22_detected(self):
        # 如果已經在播，就先跳過
        
        try:
            temperature_c = self.dhtDevice.temperature
            humidity = self.dhtDevice.humidity
        except RuntimeError:
            return
        
        now = time.time()
        if humidity and humidity > self.rain_humidity_threshold \
        and now - self._last_rain > self.rain_cooldown:
            if self._playing_event and not (self._sleeping or self._idling):
                return
            print('humidity too high!')
            self._last_rain = now
            self._sleeping = False
            self._idling   = False
            self._playing_event = False
            info = self.load_sequence(self.rain_seq)

            # ——— 播放媒体 ———
            if info['video']:
                vid = info['video']
                vid_path = vid if os.path.isabs(vid) else os.path.join(self.video_dir, vid)
                if os.path.exists(vid_path):
                    self.play_video(vid_path)
            elif info['img']:
                img_path = info['img'] if os.path.isabs(info['img']) else os.path.join(self.img_dir, info['img'])
                if os.path.exists(img_path):
                    self.show_static(img_path)
            else:
                if os.path.exists(self.rain_video):
                    self.play_video(self.rain_video)

            # ——— 排程马达 ———
            if info['sequence']:
                self.schedule_sequence(info['sequence'], interval_ms=300)

            return



        # 下面保留原有溫溼度正常處理
        if 0 < temperature_c < 100 and 0 < humidity < 100:
            temperature_f = temperature_c * 9 / 5 + 32
            print(f" Temp: {temperature_f:.1f} F / {temperature_c:.1f} C    Humidity: {humidity:.1f}%")
            return temperature_c, humidity
        else:
            print(" 讀取異常，數值不合常理")
            return 0

    # --- 伺服 & ADC 輔助函式 ---
    def angle_to_pwm(self, angle):
        a = max(min(angle, 90), -90)
        pulse = 150 + (a + 90) * (600 - 150) / 180
        return int(pulse)

    def set_servo_angle(self, ch, ang):
        pwm_val = self.angle_to_pwm(ang)
        self.pwm.channels[ch].duty_cycle = int(pwm_val / 4096 * 65535)
        print(f"[Servo] channel={ch}, angle={ang}, pwm_pulse={pwm_val}")
        # 每次马达动作也算一次“活动”，刷新 last_active
        self.last_active = time.time()
        # 并且退出睡眠状态
        self._sleeping = False
        self._idling   = False

    def load_sequence(self, path):
        info = { 'video': None, 'img': None, 'sequence': [] }
        if os.path.exists(path):
            raw = json.load(open(path, 'r', encoding='utf-8'))
            if isinstance(raw, dict):
                info['video']    = raw.get('video')
                info['img']    = raw.get('img')
                info['sequence'] = raw.get('sequence', [])
            elif isinstance(raw, list):
                info['sequence'] = raw
        return info

    def run_sequence(self, seq):
        for angles in seq:
            print("→ Setting angles:", angles) 
            if isinstance(angles, list) and len(angles) == 4:
                for i, a in enumerate(angles):
                    self.set_servo_angle(i, a)

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
        info = self.load_sequence(self.boot_seq)

        # ——— 1) 播放開機媒體 ———
        if info['video']:
            vid  = info['video']
            vid_path = vid if os.path.isabs(vid) else os.path.join(self.video_dir, vid)
            if os.path.exists(vid_path):
                self.play_video(vid_path)

        elif info['img']:
            img_path = info['img'] if os.path.isabs(info['img']) else os.path.join(self.img_dir, info['img'])
            if os.path.exists(img_path):
                self.show_static(img_path)
        else:
            # fallback: 播 boot.mp4
            if os.path.exists(self.boot_video):
                self.play_video(self.boot_video)

        # ——— 2) 同步排程所有伺服馬達動作 ———
        if info['sequence']:
            self.schedule_sequence(info['sequence'], interval_ms=200)

    def run_boot_sequence(self):
        seq = self.load_sequence(self.boot_seq)
        self.run_sequence(seq)
        
    # --- 空閒邏輯 ---
    def check_idle(self):
         # 只要有 event 在播放，就不觸發 idle/sleep
        if self._playing_event:
            return
        if self.player.state() == QMediaPlayer.PlayingState:
            return

        elapsed = time.time() - self.last_active
        if self.player.state() == QMediaPlayer.PlayingState:
            return
        # 1) 先到睡眠門檻
        if elapsed > self.sleep_threshold and not self._sleeping:
            self._sleeping = True
            # 播睡眠動畫
            if os.path.exists(self.sleep_path):
                self.play_video(self.sleep_path)
            return

        # 2) 到 idle 門檻（但還沒到 sleep），且還沒播過 idle
        if elapsed > self.idle_timeout and not self._sleeping and not self._idling:
            self._idling = True
            # 只播 idle 影片，不動馬達
            if os.path.exists(self.idle_video):
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
            print('raw data',data)
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
        if self._playing_event and not (self._sleeping or self._idling):
            return
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
        img = cmd.get('img')
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
                self.static_widget.raise_()
                self.static_widget.showFullScreen()
            QTimer.singleShot(100, lambda: setattr(self, '_playing_event', False))
        if cmd.get("reset_background"):
            print("recover deafult background")
            self.static_widget.setPixmap(self.deafult_pixmap)
            self.video_widget.hide()
            self.static_widget.raise_()
            self.static_widget.showFullScreen()
                
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
        if self._playing_event and not (self._sleeping or self._idling):
            return
        self._playing_event = True
        
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
        if self._playing_event and not (self._sleeping or self._idling):
            return
        # 把旗標打開（代表正在「播」靜態事件）
        self._playing_event = True
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
        QTimer.singleShot(100, lambda: setattr(self, '_playing_event', False))
    # --- 媒體播放狀態偵聽 ---
    def on_media_status(self, status):
        from PyQt5.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia:
            # 動畫播完，清旗標
            self._playing_event = False
            # 如果是在睡眠狀態，影片播完就再播一次
            if self._sleeping and os.path.exists(self.sleep_path):
                # 直接重新播放 sleep.mp4
                self.play_video(self.sleep_path)
            else:
                # 正常結束，恢復靜態背景
                self.video_widget.setFullScreen(False)
                self.video_widget.hide()
                self.static_widget.showFullScreen()


if __name__ == '__main__':
    Rpib(host='100.105.82.116', port=54230)
