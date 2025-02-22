import RPi.GPIO as GPIO
import pigpio as pi
import time
import asyncio
'''
import board
import busio
from digitalio import DigitalInOut
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = DigitalInOut(board.D5)  # 選擇片選引腳（CS）

# 初始化 MCP3008
mcp = MCP3008(spi, cs)

# 使用第 1-4 通道讀取模擬值
chan1 = AnalogIn(mcp, MCP3008.P1)
chan2 = AnalogIn(mcp, MCP3008.P2)
chan3 = AnalogIn(mcp, MCP3008.P3)
chan4 = AnalogIn(mcp, MCP3008.P4)

# 顯示數據
print(f"原始值: {chan1.value}")#0-1023
print(f"原始值: {chan2.value}")
print(f"原始值: {chan3.value}")
print(f"原始值: {chan4.value}")
'''
GPIO.setmode(GPIO.BOARD)
GPIO.setup(1,GPIO.OUT)
GPIO.setup(2,GPIO.OUT)
GPIO.setup(3,GPIO.OUT)
GPIO.setup(4,GPIO.OUT)
# 伺服馬達腳位
servopinA=GPIO.PWM(1,50)
servopinB=GPIO.PWM(2,50)
servopinC=GPIO.PWM(3,50)
servopinD=GPIO.PWM(4,50)

moveSmooth = 25; #兩個動作之間的平滑參數
stepTime = 100;   #到定點之後停留的時間
# 訊號回傳腳位
sensorpinA = 5
sensorpinB = 6
sensorpinC = 7
sensorpinD = 8

# 按鈕腳位
ButtonA = 9
ButtonB = 10

# 馬達校正基準點
regulateMin = -60
regulateMax = 60

# 記錄位置
posCount = 100
POS = [[0, 0, 0, 0] for _ in range(posCount)]  # 初始化角度為90度
arrayCount = 0
clearPos = 0

# 初始化伺服馬達位置
global ServoPosA ,ServoPosB ,ServoPosC ,ServoPosD 

sensorMaxA, sensorMaxB, sensorMaxC, sensorMaxD = 0, 0, 0, 0  # 紀錄可變電阻最大值
sensorMinA, sensorMinB, sensorMinC, sensorMinD = 0, 0, 0, 0  # 紀錄可變電阻最小值

# 初始化 GPIO 模式
GPIO.setup(ButtonA, GPIO.IN, pull_up_down=GPIO.PUD_UP) #默認為高電位
GPIO.setup(ButtonB, GPIO.IN, pull_up_down=GPIO.PUD_UP) #默認為低電位

# 初始化 pigpio 伺服控制
def MotorON():
    servopinA.start(0)
    servopinB.start(0)
    servopinC.start(0)
    servopinD.start(0)
def MotorOFF():
    servopinA.stop()
    servopinB.stop()
    servopinC.stop()
    servopinD.stop()


#舵機角度從duty轉-90~90
def ServoPosA_angle(angle):
             pulsewidth = 500 + (angle + 90) * 2000 / 180
             duty = pulsewidth/20000*100
             servopinA.ChangeDutyCycle(duty)
def ServoPosB_angle(angle):
             pulsewidth = 500 + (angle + 90) * 2000 / 180
             duty = pulsewidth/20000*100
             servopinB.ChangeDutyCycle(duty)
def ServoPosC_angle(angle):
             pulsewidth = 500 + (angle + 90) * 2000 / 180
             duty = pulsewidth/20000*100
             servopinC.ChangeDutyCycle(duty)
def ServoPosD_angle(angle):
             pulsewidth = 500 + (angle + 90) * 2000 / 180
             duty = pulsewidth/20000*100
             servopinD.ChangeDutyCycle(duty)

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

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def loop():
    # 紀錄按鈕
    if GPIO.input(ButtonA) == GPIO.LOW:
        global clearPos
        #清零arraycount
        if clearPos == 1:
            arrayCount = 0
            clearPos = 0

        MotorOFF()
        time.sleep(0.1)

        # 轉換感測值到伺服馬達角度
        ServoPosA = map_range(chan1.value, sensorMinA, sensorMaxA, regulateMin, regulateMax)
        ServoPosB = map_range(chan2.value, sensorMinB, sensorMaxB, regulateMin, regulateMax)
        ServoPosC = map_range(chan3.value, sensorMinC, sensorMaxC, regulateMin, regulateMax)
        ServoPosD = map_range(chan4.value, sensorMinD, sensorMaxD, regulateMin, regulateMax)
        
        if arrayCount < posCount:
            POS[arrayCount][0] = ServoPosA
            POS[arrayCount][1] = ServoPosB
            POS[arrayCount][2] = ServoPosC
            POS[arrayCount][3] = ServoPosD
            arrayCount=arrayCount+1
        
        time.sleep(0.2)
        

    # 播放按鈕
    if GPIO.input(ButtonB) == GPIO.LOW:
        MotorON()
        ServoPosA_angle(POS[0][0])
        ServoPosB_angle(POS[0][1])
        ServoPosC_angle(POS[0][2])
        ServoPosD_angle(POS[0][3])
        time.sleep(1)

        for i in range(arrayCount-1):#如果用arraycount不-1pos[i+1]會爆掉
            nowA = POS[i][0]
            nowB= POS[i][1]
            nowC = POS[i][2]
            nowD = POS[i][3]
            endA = POS[i+1][0]
            endB = POS[i+1][1]
            endC = POS[i+1][2]
            endD = POS[i+1][3]
            for j in range(moveSmooth):
                ServoPosA_angle(map_range(j,0,moveSmooth,nowA,endA))
                ServoPosB_angle(map_range(j,0,moveSmooth,nowB,endB))
                ServoPosC_angle(map_range(j,0,moveSmooth,nowC,endC))
                ServoPosD_angle(map_range(j,0,moveSmooth,nowD,endD))
                time.sleep(0.01)
            time.sleep(0.1)

        time.sleep(0.5)
        clearPos = 1
        MotorOFF()

try:
    setup()
    while True:
        loop()
except KeyboardInterrupt:
    GPIO.cleanup()
    pi.stop()
