import RPi.GPIO as GPIO
import time
import pigpio as pi

GPIO.setmode(GPIO.BOARD)#以板子接腳編號為主

GPIO.setup(12,GPIO.OUT)#連GPIO
svo1=GPIO.PWM(12,50)#連舵機PWM (11腳，50hz)

svo1.start(0)#開使servo

def set_servo_angle(angle):
             pulsewidth = 500 + (angle + 90) * 2000 / 180
             duty = pulsewidth/20000*100
             svo1.ChangeDutyCycle(duty)
try:
    while True:
        angle=float(input("輸入角度："))
        set_servo_angle(angle)
        time.sleep(0.5)

finally:
    svo1.stop()
    GPIO.cleanup()
    print("good")