# Functions for reading data from the Yostlabs IMU

import logging
import time
import random

class FakeImu:

    def __init__(self,name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.callbacks = []

    def add_callback(self,callback):
        self.callbacks.append(callback)

    def run(self):
        while True:
            ## New data has arrived!
            euler = { 'roll': random.random(), 'pitch': random.random(), 'yaw': random.random()}

            for c in self.callbacks:
                c(euler)

            time.sleep(1)
