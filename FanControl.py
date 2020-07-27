import RPi.GPIO as GPIO
import time


FAN_PIN = 18
WAIT_TIME = 1
PWM_FREQ = 25000
print("hello")

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)
fan = GPIO.PWM(FAN_PIN, PWM_FREQ)

print('setupgpIO')

print("pwm range set")

fan.start(40)

print("Min RPM")
time.sleep(5)

fan.start(70)

print("Mid 1 RPM")
time.sleep(5)

fan.start(80)
print("Mid 2 RPM")
time.sleep(5)

fan.start(90)

print("Mid 3 RPM")
time.sleep(5)

fan.start(100)   # mid RPM

print("Mid 4 RPM")
time.sleep(5)

fan.start(110)

print("High RPM")
time.sleep(5)

fan.start(128)
print("Max RPM")
time.sleep(5)

print("done!")
quit()