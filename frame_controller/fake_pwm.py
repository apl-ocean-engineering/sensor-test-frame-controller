
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

        if motors & 1:
            self.logger.info("%s: Set duty %02f pct. on motor 1", self.logname, (duty*100))

        if motors & 2:
            self.logger.info("%s: Set duty %02f pct. on motor 2", self.logname, (duty*100))
