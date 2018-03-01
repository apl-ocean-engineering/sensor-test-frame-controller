import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import time
import os
#PWM.start(channel, duty, freq=2000, polarity=0)
M1_PWM_PIN = "P9_14"
M2_PWM_PIN = "P9_16"
M1_DIRECTION_PIN = "P9_13"
M2_DIRECTION_PIN = "P9_15"
duty = 0
freq = 10000
direction = True
PWM.start(PWM_PIN_1, duty, freq)
GPIO.setup(GPIO_PIN_1, GPIO.OUT)
os.system('clear')
while 1:
    print("Duty Cycle: " +  str(duty))
    print("Frequency: " + str(freq))
    print("Forward Direction: " + str(direction))
    print("---------------------------------------------------------")
    print("Enter a command")
    cmd = raw_input("Edit (d)uty cycle,(f)requency, d(i)rection, or e(x)it: ")
    if cmd == 'x':
	break;
    elif cmd == 'd':
        duty = input("Enter a duty cycle between 0 and 100: ")
    elif cmd == 'f':
	freq = input("Enter a desired frequency: ")
    elif cmd == 'i':
	direction = not direction
    os.system('clear')
    if duty >= 0 and duty <= 100 and freq >= 1:
        PWM.set_duty_cycle(PWM_PIN_1, duty)
	PWM.set_frequency(PWM_PIN_1, freq)
	if direction :
	    GPIO.output(GPIO_PIN_1, GPIO.HIGH)
	else :
	    GPIO.output(GPIO_PIN_1, GPIO.LOW)
    else :
	print("Non-legal value given.")
	print
GPIO.cleanup()
PWM.stop(PWM_PIN_1)
