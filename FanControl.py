import wiringpi
import time

print("hello")

wiringpi.wiringPiSetupGpio()

wiringpi.pwmSetMode(1) # PWM_MODE_MS = 1

print('setupgpIO')

wiringpi.pinMode(18, 2)      # pwm only works on GPIO port 18

print("pwm mode set")

wiringpi.pullUpDnControl(18, 2) # 0=None; 1=Pull Down; 2=Pull Up

print("Pwm pull up active")

wiringpi.pwmSetClock(4)  # this parameters correspond to 25kHz

print("pwm clock set")
wiringpi.pwmSetRange(128)

print("pwm range set")

wiringpi.pwmWrite(18, 76) # minimum RPM

print("Min RPM")
time.sleep(5)

wiringpi.pwmWrite(18, 80)   # mid RPM

print("Mid 1 RPM")
time.sleep(5)

wiringpi.pwmWrite(18, 90)   # mid RPM

print("Mid 2 RPM")
time.sleep(5)

wiringpi.pwmWrite(18, 100)   # mid RPM

print("Mid 3 RPM")
time.sleep(5)

wiringpi.pwmWrite(18, 110)   # mid RPM

print("Mid 4 RPM")
time.sleep(5)

wiringpi.pwmWrite(18, 120)   # mid RPM

print("High RPM")
time.sleep(5)

wiringpi.pwmWrite(18, 128)  # maximum RPM

print("Max RPM")
time.sleep(5)

wiringpi.pwmWrite(18, 0)
wiringpi.pinMode(18, 0)