import RPI.GPIO as GPIO
import time

pin_servo = 5
GPIO.setmode(GPIO.BMC)
GPIO.setup(pin_servo, GPIO.out)
pwm_servo = GPIO.PWM(pin_servo,50)
pwm.start(0)

def destroy():
    pwm_servo.stop()
    GPIO.cleanup()
#0＝停止 2＝0度 7=90度 12=180度
def Direction(angle):
    duty = 2+(angle/18)
    pwm_servo.ChangeDutyCycle(duty)

    #除顫
    time.sleep(0.5)
    pwm_servo.ChangeDutyCycle(duty)
    print("角度=",angle,"duty=",duty)

def run():
    for angle in range(0,180,10):
        Direction(angle)
        time.sleep(1)

if __name__== "__main__":
    try:
        run()
    finally:
        destroy()
