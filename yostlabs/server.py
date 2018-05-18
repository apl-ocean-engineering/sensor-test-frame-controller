#!/usr/bin/env python
# Copyright 2018 UW-APL
# See LICENSE

import pika
import sys
import logging
import time

class ImuServer:

    def __init__(self, name, fakehw):
        self.name = name
        self.full_name = "imu_%s" % name
        self.logger = logging.getLogger(self.full_name)

        credentials = pika.PlainCredentials('user', 'bitnami')
        params = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        self.logger.info("Connecting to exchange \"%s\"" % self.full_name)
        self.channel.exchange_declare(exchange=self.full_name,
                                      exchange_type='fanout')

    def send(self):
        message = "info: Hello World!"
        self.channel.basic_publish(exchange=self.full_name,
                                  routing_key='',
                                  body=message)
        print(" [x] Sent %r" % message)

        #connection.close()

    def run(self):
        self.logger.warning("IMU Server %s running ..." % self.name)
        while True:
            self.send()
            time.sleep(1)
