#!/usr/bin/env python
# Copyright 2018 UW-APL
# See LICENSE

import pika
import sys
import logging
import time

import imu.imu_data_pb2 as imu_api

from .base import Base

class ImuClient(Base):

    def __init__(self, name, credentials=None):
        Base.__init__(self,name)
        self.logger = logging.getLogger(self.full_name())

        if not credentials:
            credentials = pika.PlainCredentials('guest', 'guest')
        params = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        # self.logger.info("Connecting to exchange \"%s\"" % self.full_name)
        # self.channel.exchange_declare(exchange=self.full_name,
        #                          exchange_type='fanout')

        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange='yostlabs',
                                queue=self.queue_name,
                                routing_key=self.full_name())


    def run(self):
        self.logger.warning(' [*] Waiting for logs. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            packet = imu_api.EulerAngles()
            packet.ParseFromString(body)
            self.logger.info(" [x] Got packet %d:   R %6.2f    P %6.2f    Y%6.2f"
                        % (packet.sequence, packet.roll, packet.pitch, packet.yaw) )

        self.channel.basic_consume(callback,
                              queue=self.queue_name,
                              no_ack=True)

        self.channel.start_consuming()
