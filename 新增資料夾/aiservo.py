import sys
import time
import RPi.GPIO as GPIO
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

# 初始化 GPIO
if GPIO.getmode() is None:  
    GPIO.setmode(GPIO.BCM)  

servo_pin = 12  
GPIO.setup(servo_pin, GPIO.OUT)
servo = GPIO.PWM(servo_pin, 50)
servo.start(0)

# 初始化 MCP3008
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P1)  

# 角度範圍
regulateMin, regulateMax = -60, 60
sensorMinA, sensorMaxA = 0, 1  
positions = []  


def map_range(value, in_min, in_max, out_min, out_max):
    """數值映射，確保不發生 ZeroDivisionError"""
    if in_max - in_min == 0:
        return out_min  
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def set_servo_angle(angle):
    """設定伺服馬達角度"""
    pulsewidth = 500 + (angle + 90) * 2000 / 180
    duty = pulsewidth / 20000 * 100
    servo.ChangeDutyCycle(duty)


def setup():
    """初始化伺服馬達與感測數值"""
    global sensorMinA, sensorMaxA

    set_servo_angle(regulateMin)
    time.sleep(1)
    sensorMinA = chan.value
    print(f"sensorMinA = {sensorMinA}")  

    set_servo_angle(regulateMax)
    time.sleep(1)
    sensorMaxA = chan.value
    print(f"sensorMaxA = {sensorMaxA}")  

    if sensorMaxA == sensorMinA:
        sensorMaxA += 1  

    set_servo_angle(0)
    time.sleep(1)


class ServoThread(QThread):
    """播放伺服馬達記錄"""
    update_signal = pyqtSignal(str)

    def __init__(self, positions):
        super().__init__()
        self.positions = positions
        self.running = True  

    def run(self):
        """執行播放"""
        if not self.positions:
            self.update_signal.emit("⚠️ 無記錄動作！")
            return

        set_servo_angle(self.positions[0])
        time.sleep(1)

        for i in range(len(self.positions) - 1):
            if not self.running:
                break

            now_angle = self.positions[i]
            next_angle = self.positions[i + 1]

            for j in range(25):
                if not self.running:
                    break
                angle = map_range(j, 0, 25, now_angle, next_angle)
                set_servo_angle(angle)
                time.sleep(0.01)
            time.sleep(0.1)

        time.sleep(0.5)
        self.update_signal.emit("✅ 播放完成！")

    def stop(self):
        """停止播放"""
        self.running = False


class ServoControlUI(QMainWindow):
    """伺服馬達控制 UI"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Servo Motor Control")
        self.setGeometry(100, 100, 300, 200)

        self.save_button = QPushButton("Save", self)
        self.play_button = QPushButton("Play", self)

        self.save_button.clicked.connect(self.save_action)
        self.play_button.clicked.connect(self.play_action)

        layout = QVBoxLayout()
        layout.addWidget(self.save_button)
        layout.addWidget(self.play_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.play_thread = None  

    def save_action(self):
        """記錄當前角度"""
        global positions
        angle = map_range(chan.value, sensorMinA, sensorMaxA, regulateMin, regulateMax)
        positions.append(angle)
        print(f"🎯 已儲存角度：{angle}")

    def play_action(self):
        """播放記錄的角度變化"""
        if self.play_thread and self.play_thread.isRunning():
            print("⏳ 播放中，請稍候...")
            return

        print("▶ 開始播放...")
        self.play_thread = ServoThread(positions)
        self.play_thread.update_signal.connect(self.show_message)
        self.play_thread.start()

    def show_message(self, message):
        """顯示狀態訊息"""
        print(message)


if __name__ == "__main__":
    try:
        setup()  
        app = QApplication(sys.argv)
        window = ServoControlUI()
        window.show()
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        GPIO.cleanup()
        servo.stop()
