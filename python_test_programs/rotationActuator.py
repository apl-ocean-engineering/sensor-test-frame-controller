import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import time
import os
#PWM.start(channel, duty, freq=2000, polarity=0)
M1_PWM_PIN = "P9_14"
M2_PWM_PIN = "P9_16"
M1_DIRECTION_PIN = "P9_13"
M2_DIRECTION_PIN = "P9_15"
dutyM1 = 0
dutyM2 = 0
freq = 10000
# Note that boolean toggles for direction were removed. Adjusting physical wires is MUCH simpler.
PWM.start(M1_PWM_PIN, dutyM1, freq)
PWM.start(M2_PWM_PIN, dutyM2, freq)
GPIO.setup(M1_DIRECTION_PIN, GPIO.OUT)
GPIO.setup(M2_DIRECTION_PIN, GPIO.OUT)
os.system('clear')
while 1:
    print("Single Axis Rotation Actuator")
    print("PWM Frequency: " + str(freq))
    print("---------------------------------------------------------")
    direction = raw_input("Enter Direction (+/-) or e(x)it: ")
    if direction == 'x':
	break
    speed = raw_input("Enter % Speed of Motion (0-100) or e(x)it: ")
    if speed == 'x':
        break
    duration = raw_input("Enter Duration of Movement in seconds or e(x)it: ")
    if duration == 'x':
        break
    os.system('clear')
    if int(speed) >= 0 and int(speed) <= 100 and int(duration) >= 0 and (direction == '+' or direction == '-'):
        confirmation = raw_input("Execute Rotation in " + str(direction) + " Direction at " + str(speed) + "% Speed for " + str(duration) + " seconds? (y/n)")
        if confirmation == 'y' :
            PWM.set_duty_cycle(M1_PWM_PIN, float(speed))
            PWM.set_duty_cycle(M2_PWM_PIN, float(speed))
	    if direction == '+' :
                GPIO.output(M1_DIRECTION_PIN, GPIO.HIGH)
                GPIO.output(M2_DIRECTION_PIN, GPIO.LOW)
            else :
                GPIO.output(M1_DIRECTION_PIN, GPIO.LOW)
                GPIO.output(M2_DIRECTION_PIN, GPIO.HIGH)
            print("Executing...")
            time.sleep(float(duration))
            PWM.set_duty_cycle(M1_PWM_PIN, 0.0)
            PWM.set_duty_cycle(M2_PWM_PIN, 0.0)
    else :
	print("Non-legal value(s) given.")
        print
GPIO.cleanup()
PWM.stop(M1_PWM_PIN)
PWM.stop(M2_PWM_PIN)
