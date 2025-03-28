import sys
import RPi.GPIO as GPIO
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

class Rpib():
    #初始設定
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT)
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
    #馬達啟動有校準值
    def MotorON(self):
        if self.servopinA is None:
            self.servopinA = GPIO.PWM(12, 50)
        self.servopinA.start(5)
        print("MotorON called, PWM started at 5%")
    #馬達關閉
    def MotorOFF(self):
        if self.servopinA is not None:
            self.servopinA.stop()
            self.servopinA = None
        print("MotorOFF called")
    #輸入角度轉動
    def ServoPosA_angle(self, angle):
        if self.servopinA is None:
            self.MotorON()
        angle = float(max(min(angle, 90), -90))  # 限制角度範圍
        pulsewidth = 500 + (angle + 90) * 2000 / 180
        duty = pulsewidth / 20000 * 100
        print("Setting angle:", angle, "Pulsewidth:", pulsewidth, "Duty:", duty)
        self.servopinA.ChangeDutyCycle(duty)
    #將chanvalue轉成角度
    def map_range(self, value, in_min, in_max, out_min, out_max):
        print('value:', value)
        if in_min == in_max:
            print("in_min == out_max")
            return 0
        result = ((value - in_min) * (out_max - out_min) // (in_max - in_min)) + out_min
        return result
    #初始校準
    def setup(self):
        print("Setup: Starting at 0 degrees")
        self.MotorON()
        self.ServoPosA_angle(0)
        QTimer.singleShot(1000, self.setup_step1)

    def setup_step1(self):
        print("Setup: Moving to -80 degrees")
        self.ServoPosA_angle(self.regulateMin)
        QTimer.singleShot(1000, self.setup_step1_off)

    def setup_step1_off(self):
        QTimer.singleShot(500, self.setup_step2)

    def setup_step2(self):
        self.sensorMinA = self.chan.value >> 6
        print("Setup: Measured sensorMinA:", self.sensorMinA)
        QTimer.singleShot(500, self.setup_step3)

    def setup_step3(self):
        print("Setup: Moving to 80 degrees")
        self.ServoPosA_angle(self.regulateMax)
        QTimer.singleShot(1000, self.setup_step3_off)

    def setup_step3_off(self):
        QTimer.singleShot(500, self.setup_step4)

    def setup_step4(self):
        self.sensorMaxA = self.chan.value >> 6
        print("Setup: Measured sensorMaxA:", self.sensorMaxA)
        print("Setup: Returning to 0 degrees")
        self.ServoPosA_angle(0)
        QTimer.singleShot(1000, self.setup_finish)

    def setup_finish(self):
        self.MotorOFF()
        if self.sensorMinA == self.sensorMaxA:
            self.sensorMaxA += 1
        print("sensormina1:", self.sensorMinA)
        print("sensormina2:", self.sensorMaxA)

