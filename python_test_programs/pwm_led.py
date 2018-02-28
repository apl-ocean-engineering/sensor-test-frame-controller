import Adafruit_BBIO.PWM as PWM
#PWM.start(channel, duty, freq=2000, polarity=0)
PWM.start("P9_14", 50, frequency=1)

while True:
    duty = input("Enter a duty cycle between 0 and 100 or -1 to quit")

    if duty == -1:
        break;
    elif duty >= 0 and duty <= 100:
        PWM.set_duty_cycle( "P9_14", duty )
    

PWM.stop("P9_14")
PWM.cleanup()
