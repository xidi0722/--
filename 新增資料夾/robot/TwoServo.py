import RPi.GPIO as GPIO
import time
import pigpio as pi

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(35,GPIO.OUT)

servo1=GPIO.PWM(12,50)
servo2=GPIO.PWM(35,50)

servo1.start(0)
servo2.start(0)

#angle
def servo1_angle(angle):
             pulsewidth = 500 + (angle + 90) * 2000 / 180
             duty = pulsewidth/20000*100
             servo1.ChangeDutyCycle(duty)
def servo2_angle(angle):
             pulsewidth = 500 + (angle + 90) * 2000 / 180
             duty = pulsewidth/20000*100
             servo2.ChangeDutyCycle(duty)

#1 90,2 0
servo1_angle(-90)
time.sleep(1)
#servo1.ChangeDutyCycle(0)  測試有加沒加是否停止

#1 0,2 90
servo1_angle(0)
servo2_angle(-90)
#servo1.ChangeDutyCycle(0)
#servo2.ChangeDutyCycle(0)
time.sleep(1)

#1 90,2 180
servo1_angle(90)
servo2_angle(0)
#servo1.ChangeDutyCycle(0)
#servo2.ChangeDutyCycle(0)
time.sleep(1)

#1 0,2 0
servo1_angle(0)
servo2_angle(90)
#servo1.ChangeDutyCycle(0)
#servo2.ChangeDutyCycle(0)
time.sleep(1)

servo1_angle(-90)
servo2_angle(0)
time.sleep(1)

servo1_angle(90)
servo2_angle(90)
time.sleep(1)
servo2_angle(-90)

GPIO.cleanup()