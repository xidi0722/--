from __future__ import division  # 這行必須是第一行
import time  # 匯入 time 模組
from adafruit_pca9685 import PCA9685
import socket
import threading
import RPi.GPIO as GPIO
from PyQt5.QtCore import QTimer
import busio
import sys
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from PyQt5.QtWidgets import QApplication 
from adafruit_mcp3xxx.analog_in import AnalogIn
import ast
class Rpib():
    def __init__(self):
        # 正確初始化 PCA9685
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pwm = PCA9685(i2c)
        self.pwm.frequency = 60
        
        
        # 其他初始化
        self.servopinA = None
        self.sensorMaxA = 1023
        self.sensorMinA = 0
        
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = digitalio.DigitalInOut(board.D5)
        mcp = MCP.MCP3008(spi, cs)
        self.chan = AnalogIn(mcp, MCP.P0)
        
        print("chan.value", str(self.chan.value))
        
        self.stepTime = 100
        self.sensorpinA = 5
        self.regulateMin = -80
        self.regulateMax = 80
        self.posCount = 100
        self.POS = [[0, 0, 0, 0] for _ in range(self.posCount)]
        self.arrayCount = 0
        self.clearPos = 0
        
        self.setup()
    def MotorOFF(self, channel):
        self.pwm.channels[channel].duty_cycle = 0
        print("MotorOFF called")

    #要改
    def angle_to_pwm(self,angle):
        # 限制角度範圍在 -90 ~ +90
        angle = max(min(angle, 90), -90)

        # 轉換角度成脈衝寬度 (150~600 對應 -90~+90 度)
        pulse = 150 + (angle + 90) * (600 - 150) / 180

        # 將脈衝寬度轉換成 12-bit 整數（0~4095）
        pwm_val = int(pulse)
        return pwm_val

    def set_servo_angle(self, servo_channel, angle):
        pwm_val = self.angle_to_pwm(angle)
        self.pwm.channels[servo_channel].duty_cycle = 0  # 先清空一下再寫入
        self.pwm.channels[servo_channel].duty_cycle  = int(pwm_val / 4096 * 65535)
        
        print(f"設定角度 {angle}° -> Pulse: {pwm_val} ")
    
    
    def setup(self):
        print("Setup: Starting at 0 degrees")
        for i in range(4):
            self.set_servo_angle(i,0)
        QTimer.singleShot(1000, self.setup_step1)
    
    def setup_step1(self):
        print("Setup: Moving to -80 degrees")
        for i in range(4):
            self.set_servo_angle(i,-80)
        QTimer.singleShot(1000, self.setup_step1_off)
    
    def setup_step1_off(self):
        QTimer.singleShot(500, self.setup_step2)
    
    def setup_step2(self):
        self.sensorMinA = self.chan.value >> 6
        print("Setup: Measured sensorMinA:", self.sensorMinA)
        QTimer.singleShot(500, self.setup_step3)
    
    def setup_step3(self):
        print("Setup: Moving to 80 degrees")
        for i in range(4):
            self.set_servo_angle(i,80)
        QTimer.singleShot(1000, self.setup_step3_off)
    
    def setup_step3_off(self):
        QTimer.singleShot(500, self.setup_step4)
    
    def setup_step4(self):
        self.sensorMaxA = self.chan.value >> 6
        print("Setup: Measured sensorMaxA:", self.sensorMaxA)
        print("Setup: Returning to 0 degrees")
        for i in range(4):
            self.set_servo_angle(i,0)
        QTimer.singleShot(1000, self.setup_finish)
    
    def setup_finish(self):
        for i in range (4):
            self.MotorOFF(i)
        if self.sensorMinA == self.sensorMaxA:
            self.sensorMaxA += 1
        print("sensormina1:", self.sensorMinA)
        print("sensormina2:", self.sensorMaxA)
    
    def handle_command(self, command):

        try:
            # 安全地將字符串解析為 Python 列表
            angles = ast.literal_eval(command.strip())
            
            # 檢查 angles 是否為列表且長度為 4（對應 4 個伺服馬達）
            if isinstance(angles, list) and len(angles) == 4:
                print(f"Received angles: {angles}")
                # 為每個伺服馬達設置角度
                for i in range(4):
                    self.set_servo_angle(i, angles[i])
            else:
                print("Invalid angles format. Expected a list of 4 angles.")
        except (ValueError, SyntaxError) as e:
            print("Invalid command received:", command)
            print("Error:", e)

def socket_server(rpib_instance, host='100.105.82.116', port=54230):
    """
    建立一個簡單的 TCP 伺服器，監聽指定的 host 與 port。
    當接收到命令時，將其傳遞給 Rpib 的 handle_command 方法。
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Socket server running on {host}:{port}")
    
    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        data = conn.recv(1024).decode()
        if data:
            rpib_instance.handle_command(data)
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 初始化 Rpib 實例（這裡會執行 setup 程序）
    rpib_instance = Rpib()
    
    # 使用 threading 模組在獨立的執行緒中啟動 socket 伺服器
    server_thread = threading.Thread(target=socket_server, args=(rpib_instance,), daemon=True)
    server_thread.start()
    
    # 如果有其他主程式邏輯，例如 Qt 事件循環或其他處理，
    # 這裡可以讓主線程持續運行，或整合進你的應用程式架構中。
    try:
        print('server')
    except KeyboardInterrupt:
        print("Server terminated.")