

class BaseImu:

    def __init__(self, name):
        self.name = name

    def full_name(self):
        return "imu_%s" % self.name
