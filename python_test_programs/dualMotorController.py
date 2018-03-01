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
freqM1 = 10000
dutyM2 = 0
freqM2 = 10000
directionM1 = True
directionM2 = True
PWM.start(M1_PWM_PIN, dutyM1, freqM1)
PWM.start(M2_PWM_PIN, dutyM2, freqM2)
GPIO.setup(M1_DIRECTION_PIN, GPIO.OUT)
GPIO.setup(M2_DIRECTION_PIN, GPIO.OUT)
os.system('clear')
while 1:
    print("Motor 1")
    print("Duty Cycle: " +  str(dutyM1))
    print("Frequency: " + str(freqM1))
    print("Forward Direction: " + str(directionM1))
    print
    print("Motor 2")
    print("Duty Cycle: " + str(dutyM2))
    print("Frequency: " + str(freqM2))
    print("Forward Direction: " + str(directionM2))
    print("---------------------------------------------------------")
    motor = raw_input("Select a motor or e(x)it (1/2): ")
    if motor == 'x':
	break
    print("Enter a command for Motor " + str(motor))
    cmd = raw_input("Edit (d)uty cycle,(f)requency, d(i)rection, or e(x)it: ")
    if motor == '1' :
        if cmd == 'x' :
	    break
        elif cmd == 'd':
            dutyM1 = input("Enter a duty cycle between 0 and 100: ")
        elif cmd == 'f':
	    freqM1 = input("Enter a desired frequency: ")
        elif cmd == 'i':
	    directionM1 = not directionM1
    elif motor == '2' :
        if cmd == 'x' :
	    break
        elif cmd == 'd':
	    dutyM2 = input("Enter a duty cycle between 0 and 100: ")
        elif cmd == 'f':
	    freqM2 = input("Enter a desired frequency: ")
        elif cmd == 'i':
	    directionM2 = not directionM2
    os.system('clear')
    if dutyM1 >= 0 and dutyM2 >= 0 and dutyM1 <= 100 and dutyM2 <= 100 and freqM1 >= 1 and freqM2 >= 1 : #and (motor == 1 or motor == 2):
        PWM.set_duty_cycle(M1_PWM_PIN, dutyM1)
	PWM.set_frequency(M1_PWM_PIN, freqM1)
        PWM.set_duty_cycle(M2_PWM_PIN, dutyM2)
	PWM.set_frequency(M2_PWM_PIN, freqM2)
	if directionM1 :
	    GPIO.output(M1_DIRECTION_PIN, GPIO.HIGH)
	else :
	    GPIO.output(M1_DIRECTION_PIN, GPIO.LOW)
	if directionM2 :
	    GPIO.output(M2_DIRECTION_PIN, GPIO.HIGH)
	else:
	    GPIO.output(M2_DIRECTION_PIN, GPIO.LOW)
    else :
	print("Non-legal value given.")
	print
GPIO.cleanup()
PWM.stop(M1_PWM_PIN)
PWM.stop(M2_PWM_PIN)
