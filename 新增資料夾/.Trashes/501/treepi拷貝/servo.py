import pigpio
import time

pin_servo = 5

pwm = pigpio.pi()
pwm.set_mode(pin_servo, pigpio.OUTPUT)
pwm.set_PWM_frequency(pin_servo, 50)  # 50Hz frequency

def destroy():
    pwm.set_PWM_dutycycle(pin_servo, 0)
    pwm.set_PWM_frequency(pin_servo, 0)

# 輸入0 ～ 180度即可
# 別超過180度
def setDirection(angle):
    # 0 = 停止轉動
    # 500 = 0度
    # 1500 = 90度
    # 2500 = 180度
    duty = 500 + (angle / 180) * 2000
    pwm.set_servo_pulsewidth(pin_servo, duty)
    print("角度=", angle, "-> duty=", duty)

def run():
    for angle in range(0, 181, 10):
        setDirection(angle)
        time.sleep(1)


if __name__ == "__main__":
    try:
        run()
    finally:
        destroy()