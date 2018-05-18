#!/usr/bin/env python
# Copyright 2018 UW-APL
# See LICENSE

import pika
import sys
import logging
import time

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

    def close(self):
        self.connection.close()

    def send(self):
        message = "%s: Hello World!" % self.name
        self.channel.basic_publish(exchange='yostlabs',
                                  routing_key=self.full_name(),
                                  body=message)
        self.logger.info(" [x] Sent %r" % message)

    def run(self):
        self.logger.warning("IMU Server %s running ..." % self.name)
        while True:
            self.send()
            time.sleep(1)
