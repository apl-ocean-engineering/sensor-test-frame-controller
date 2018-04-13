
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

class FakePwm:

    def __init__(self,name,logger=None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)

    @property
    def logname(self):
        return "Fake " + self.name

    def start(self):
        self.logger.info("%s: Starting" % self.logname)

    def stop(self):
        self.logger.info("%s: Stopping" % self.logname)

    def set(self, motors, duty):
        motorstr = "(unknown %d)" % motors
        if motors == 1:
            motorstr = "MOTOR1"
        elif motors == 2:
            motorstr = "MOTOR2"
        elif motors == 4:
            motorstr = "BOTH"

        self.logger.info("%s: Set duty %02f pct. on motors %s", self.logname, (duty*100), motorstr)
