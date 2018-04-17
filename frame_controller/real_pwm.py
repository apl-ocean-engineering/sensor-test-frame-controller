
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

M1_PWM_PIN = 
M1_DIRECTION_PIN = 
M2_PWM_PIN =
M2_DIRECTION_PIN = 


M3_PWM_PIN =
M3_DIRECTION_PIN = 

M4_PWM_PIN = 
M4_DIRECTION_PIN = 

# One instance of RealPWM handles the two motors running a single axis (pitch or yaw)
class RealPwm:

    def __init__(self, name, logger=None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)

        if name.lower() == "pitch":
            self.dir1 = M1_DIRECTION_PIN
            self.pwm1 = M1_PWM_PIN

            self.dir2 = M2_DIRECTION_PIN
            self.pwm2 = M2_PWM_PIN

        elif name.lower() == "yaw":
            self.dir1 = M3_DIRECTION_PIN
            self.pwm1 = M3_PWM_PIN

            self.dir2 = M4_DIRECTION_PIN
            self.pwm2 = M4_PWM_PIN

        else:
            self.logger.error("Trying to configure with unknown axis \"%s\"" % axis)

    @property
    def logname(self):
        return "Real " + self.name

    def start(self):
        self.logger.info("%s: Starting" % self.logname)

        freq = 10000
        PWM.start(self.pwm1, 0, freq)
        PWM.start(self.pwm2, 0, freq)
        GPIO.setup(self.dir1, GPIO.OUT)
        GPIO.setup(self.dir2, GPIO.OUT)

    def stop(self):
        self.logger.info("%s: Stopping" % self.logname)

        PWM.stop(self.pwm1)
        PWM.stop(self.pwm2)
        GPIO.cleanup()

    def set(self, motors, duty):
        if motors & 1:
            self.logger.info("%s: Set duty %02f pct. on motor 1", self.logname, (duty*100))
            PWM.set_duty_cycle(self.pwm1, float(duty))
            if duty >= 0.0:
                GPIO.output(self.dir1, GPIO.HIGH)
            else:
                GPIO.output(self.dir1, GPIO.LOW)

        if motors & 2:
            self.logger.info("%s: Set duty %02f pct. on motor 2", self.logname, (duty*100))
            PWM.set_duty_cycle(self.pwm2, float(duty))
            if duty >= 0.0:
                GPIO.output(self.dir2, GPIO.HIGH)
            else:
                GPIO.output(self.dir2, GPIO.LOW)
