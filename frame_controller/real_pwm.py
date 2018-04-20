import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

M1_PWM_PIN = "P9_14"
M1_DIRECTION_PIN = "P9_13"

M2_PWM_PIN = "P9_16"
M2_DIRECTION_PIN = "P9_15"

M3_PWM_PIN = "P9_21"
M3_DIRECTION_PIN = "P9_23"

M4_PWM_PIN = "P9_22"
M4_DIRECTION_PIN = "P9_41"

# One instance of RealPWM handles the two motors running a single axis (pitch or yaw)
class RealPwm:

    def __init__(self, name, logger=None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)

        if name.lower() == "yaw":
            self.dir1 = M1_DIRECTION_PIN
            self.pwm1 = M1_PWM_PIN

            self.dir2 = M2_DIRECTION_PIN
            self.pwm2 = M2_PWM_PIN

        elif name.lower() == "pitch":
            self.dir1 = M3_DIRECTION_PIN
            self.pwm1 = M3_PWM_PIN

            self.dir2 = M4_DIRECTION_PIN
            self.pwm2 = M4_PWM_PIN

        else:
            self.logger.error("Trying to configure with unknown axis \"%s\"" % axis)

    @property
    def logname(self):
        return "Real " + self.name

    def setup(self):
        self.logger.info("%s: Initializing" % self.logname)

        freq = 10000
        PWM.start(self.pwm1, 0, freq)
        PWM.start(self.pwm2, 0, freq)
        GPIO.setup(self.dir1, GPIO.OUT)
        GPIO.setup(self.dir2, GPIO.OUT)

    def cleanup(self):
        self.logger.info("%s: Cleaning up" % self.logname)

        PWM.stop(self.pwm1)
        PWM.stop(self.pwm2)
        GPIO.cleanup()

    def set(self, motors, duty):
        duty = int(100*duty)
        if duty > 100:
                duty = 100
        if duty < -100:
                duty = -100

        if motors & 2:
            self.logger.info("%s: Set duty %d pct. on motor 2, pwm %s", self.logname, duty, self.pwm2)
            PWM.set_duty_cycle(self.pwm2, abs(duty))
            if duty >= 0.0:
                GPIO.output(self.dir2, GPIO.HIGH)
            else:
                GPIO.output(self.dir2, GPIO.LOW)

        if motors & 1:
            self.logger.info("%s: Set duty %d pct. on motor 1, pwm %s", self.logname, duty, self.pwm1)
            PWM.set_duty_cycle(self.pwm1, abs(duty))
            if duty >= 0.0:
                GPIO.output(self.dir1, GPIO.HIGH)
            else:
                GPIO.output(self.dir1, GPIO.LOW)


    def stopAll(self):
           PWM.set_duty_cycle(self.pwm1,0)
           PWM.set_duty_cycle(self.pwm2,0)
