import sys
import time
import RPi.GPIO as GPIO
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# 設置 GPIO
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

# 伺服馬達腳位
servopinA = GPIO.PWM(12, 50)

# ADC 設定
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P1)

# 伺服馬達參數
moveSmooth = 25  # 平滑移動
stepTime = 100  # 到定點後的停留時間
sensorpinA = 5  # 訊號回傳腳位
regulateMin = -60
regulateMax = 60
posCount = 100
POS = [[0] for _ in range(posCount)]
arrayCount = 0
clearPos = 0

sensorMaxA = chan.value>>6
sensorMinA = chan.value>>6


# 初始化伺服馬達
def MotorON():
    servopinA.start(0)


def MotorOFF():
    servopinA.stop()


def ServoPosA_angle(angle):
    pulsewidth = 500 + (angle + 90) * 2000 / 180
    duty = pulsewidth / 20000 * 100
    servopinA.ChangeDutyCycle(duty)


def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.bta = QPushButton("Save", self)
        self.bta.clicked.connect(self.save_action)

        self.btb = QPushButton("Play", self)
        self.btb.clicked.connect(self.play_action)

        layout.addWidget(self.bta)
        layout.addWidget(self.btb)

        self.setLayout(layout)
        self.setWindowTitle("Servo Motor Control")
        self.setGeometry(100, 100, 300, 200)
    def setup():
        # 移動伺服馬達至初始位置
        MotorON()
        ServoPosA_angle(0)#90度
        ServoPosB_angle(0)
        ServoPosC_angle(0)
        ServoPosD_angle(0)
        time.sleep(1)

        #偵測小角度基準數值
        ServoPosA_angle(regulateMin)
        ServoPosB_angle(regulateMin)
        ServoPosC_angle(regulateMin)
        ServoPosD_angle(regulateMin)
        time.sleep(1)
        MotorOFF()
        time.sleep(1)
        sensorMinA=chan1.value
        sensorMinB=chan2.value
        sensorMinC=chan3.value
        sensorMinD=chan4.value

        #偵測大角度基準數值
        MotorON()
        ServoPosA_angle(regulateMax)
        ServoPosB_angle(regulateMax)
        ServoPosC_angle(regulateMax)
        ServoPosD_angle(regulateMax)
        time.sleep(1)
        MotorOFF()
        time.sleep(1)
        sensorMaxA=chan1.value
        sensorMaxB=chan2.value
        sensorMaxC=chan3.value
        sensorMaxD=chan4.value

        # 移動伺服馬達回初始位置
        MotorON()
        ServoPosA_angle(0)#90度
        ServoPosB_angle(0)
        ServoPosC_angle(0)
        ServoPosD_angle(0)
        time.sleep(1)
        MotorOFF()

    def save_action(self):
        global arrayCount, clearPos
        if clearPos == 1:
            arrayCount = 0
            clearPos = 0

        MotorOFF()
        time.sleep(0.1)

        # 轉換感測值到伺服馬達角度
        ServoPosA = map_range(chan.value >> 6, sensorMinA, sensorMaxA, regulateMin, regulateMax)

        if arrayCount < posCount:
            POS[arrayCount][0] = ServoPosA
            arrayCount += 1

        time.sleep(0.2)
        print("Saved Position:", POS[:arrayCount])

    def play_action(self):
        global clearPos, arrayCount
        if arrayCount == 0:
            print("No recorded positions to play.")
            return

        MotorON()
        ServoPosA_angle(POS[0][0])
        time.sleep(1)

        for i in range(arrayCount - 1):
            nowA = POS[i][0]
            endA = POS[i + 1][0]

            for j in range(moveSmooth):
                ServoPosA_angle(map_range(j, 0, moveSmooth, nowA, endA))
                time.sleep(0.01)

            time.sleep(0.1)

        time.sleep(0.5)
        clearPos = 1
        MotorOFF()
        print("Playback completed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
