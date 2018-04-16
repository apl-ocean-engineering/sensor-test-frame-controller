
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

class RealPwm:

    def __init__(self,name,logger=None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
	
    @property
    def logname(self):
        return "Real " + self.name

    def start(self):
        self.logger.info("%s: Starting" % self.logname)

    def stop(self):
        self.logger.info("%s: Stopping" % self.logname)

    def setMotor(self, motors, duty, forward): # forward is a boolean. True: forward, False: reverse
        motorstr = "(unknown %d)" % motors
        if motors == 1:
            motorstr = "MOTOR1"
			PWM.set_duty_cycle(M1_PWM_PIN, float(duty))
			if forward:
				GPIO.output(M1_DIRECTION_PIN, GPIO.HIGH)
			else:
				GPIO.output(M1_DIRECTION_PIN, GPIO.LOW)
        
		elif motors == 2:
            motorstr = "MOTOR2"
			PWM.set_duty_cycle(M2_PWM_PIN, float(duty))
			if forward:
				GPIO.output(M2_DIRECTION_PIN, GPIO.HIGH)
			else:
				GPIO.output(M2_DIRECTION_PIN, GPIO.LOW)
				
        elif motors == 3:
            motorstr = "MOTOR3"
			PWM.set_duty_cycle(M3_PWM_PIN, float(duty))
			if forward:
				GPIO.output(M3_DIRECTION_PIN, GPIO.HIGH)
			else:
				GPIO.output(M3_DIRECTION_PIN, GPIO.LOW)
			
		elif motors == 4:
			motorstr = "MOTOR4"
			PWM.set_duty_cycle(M4_PWM_PIN, float(duty))
			if forward:
				GPIO.output(M4_DIRECTION_PIN, GPIO.HIGH)
			else:
				GPIO.output(M4_DIRECTION_PIN, GPIO.LOW)			

        self.logger.info("%s: Set duty %02f pct. on motors %s with forward = %s", self.logname, (duty*100), motorstr, str(forward))

	def setAxis(self, axis, duty, positive): # allows simultaneous control of two motors. direction is boolean (positive being clockwise from top, or pitching up).
		axisStr = "(unknown %d)" %axis
		if axis == 1: 
			axisStr = "YAW"
			if positive :
				setMotor(self, 1, duty, true)
				setMotor(self, 2, duty, false)
			else:
				setMotor(self, 1, duty, false)
				setMotor(self, 2, duty, true)
		elif axis == 2:
			axisStr = "PITCH"
			if positive :
				setMotor(self, 3, duty, true)
				setMotor(self, 4, duty, false)
			else:
				setMotor(self, 3, duty, false)
				setMotor(self, 4, duty, true)
		
		self.logger.info("%s: Set duty %02f pct. on axis %s with positive direction = %s", self.logname, (duty*100), motorstr, str(positive))
		
	def stopAxis(self, axis): #stops axis
		setAxis(self, axis, 0, false)