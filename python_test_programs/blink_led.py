## Taken from https://learn.adafruit.com/blinking-an-led-with-beaglebone-black/writing-a-program
## Assumes an LED between P8 pin 10 and P8 pin 1/2 (ground)


import Adafruit_BBIO.GPIO as GPIO
import time
 
GPIO.setup("P8_10", GPIO.OUT)
 
while True:
    GPIO.output("P8_10", GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output("P8_10", GPIO.LOW)
    time.sleep(0.5)
