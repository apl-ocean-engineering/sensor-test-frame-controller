

class ImuData:

    def __init__(self):
        self.system_timestamp = 0;
        self.imu_timestamp = 0;

        self.euler = None;
        self.quaternions = None;


#    @property
#    def system_timestamp(self): return self.system_timestamp

#    @property
#    def imu_timestamp(self): return self.imu_timestamp

#    @property
#    def euler(self): return self.euler

#    @property
#    def quaternions(self): return self.quaternions

