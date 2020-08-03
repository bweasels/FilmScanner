import RPi.GPIO as GPIO
import time


FAN_PIN = 12
WAIT_TIME = 1
PWM_FREQ = 25000
print("hello")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=40)
fan = GPIO.PWM(FAN_PIN, PWM_FREQ)

print('setup GPIO')

print("pwm range set")
fan.start(40)

print("Min RPM")
time.sleep(5)

fan.start(50)

print("Mid 1 RPM")
time.sleep(5)

fan.start(60)
print("Mid 2 RPM")
time.sleep(5)

fan.start(70)

print("Mid 3 RPM")
time.sleep(5)

fan.start(80)   # mid RPM

print("Mid 4 RPM")
time.sleep(5)

fan.start(90)

print("High RPM")
time.sleep(5)

fan.start(100)
print("Max RPM")
time.sleep(5)

print("done!")
quit()
