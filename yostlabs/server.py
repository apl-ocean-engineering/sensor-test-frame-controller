#!/usr/bin/env python
# Copyright 2018 UW-APL
# See LICENSE

import pika
import sys
import logging
import time

import yostlabs.imu_data_pb2 as imu_api

from .base import Base

from .imu import Imu
from .fake_imu import FakeImu


class ImuServer(Base):

    def __init__(self, name, fakehw=False, port=None):
        Base.__init__(self, name)
        self.logger = logging.getLogger(self.full_name())

        if fakehw:
            self.imu = FakeImu(name)
        else:
            self.imu = Imu(name, port)

        credentials = pika.PlainCredentials('guest', 'guest')
        params = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        self.logger.info("Connecting to exchange \"%s\"" % self.full_name())
        self.channel.exchange_declare(exchange='yostlabs',
                                      exchange_type='direct')

        self.sequence = 0

    def close(self):
        self.connection.close()

    def send(self,euler):
        # Make an IMU data packet
        packet = imu_api.EulerAngles()
        packet.timestamp = time.monotonic()
        packet.sequence = self.sequence
        self.sequence += 1

        packet.roll = euler['roll']
        packet.pitch = euler['pitch']
        packet.yaw  = euler['yaw']

        self.channel.basic_publish(exchange='yostlabs',
                                  routing_key=self.full_name(),
                                  body=packet.SerializeToString())
        self.logger.info(" [x] Sent imu message %d" % packet.sequence)

    def run(self):
        self.logger.warning("IMU Server %s running ..." % self.name)

        # def callback(euler):
        #     self.send()

        self.imu.add_callback( self.send )

        self.imu.run()
