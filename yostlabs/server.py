#!/usr/bin/env python
# Copyright 2018 UW-APL
# See LICENSE

import pika
import sys
import logging
import time

import yostlabs.imu_data_pb2 as imu_api

from .base import BaseImu

class ImuServer(BaseImu):

    def __init__(self, name, fakehw):
        BaseImu.__init__(self, name)
        self.logger = logging.getLogger(self.full_name())

        credentials = pika.PlainCredentials('user', 'bitnami')
        params = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        self.logger.info("Connecting to exchange \"%s\"" % self.full_name())
        self.channel.exchange_declare(exchange='yostlabs',
                                      exchange_type='direct')

        self.sequence = 0

    def close(self):
        self.connection.close()

    def send(self):
        # Make an IMU data packet
        packet = imu_api.Quaternions()
        packet.timestamp = time.monotonic()
        packet.sequence = self.sequence
        self.sequence += 1

        self.channel.basic_publish(exchange='yostlabs',
                                  routing_key=self.full_name(),
                                  body=packet.SerializeToString())
        self.logger.info(" [x] Sent imu message %d" % packet.sequence)

    def run(self):
        self.logger.warning("IMU Server %s running ..." % self.name)
        while True:
            self.send()
            time.sleep(1)
