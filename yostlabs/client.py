#!/usr/bin/env python
# Copyright 2018 UW-APL
# See LICENSE

import pika
import sys
import logging
import time

from .base import BaseImu

class ImuClient(BaseImu):

    def __init__(self, name):
        BaseImu.__init__(self,name)
        self.logger = logging.getLogger(self.full_name())

        credentials = pika.PlainCredentials('user', 'bitnami')
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
            self.logger.info(" [x] %r" % body)

        self.channel.basic_consume(callback,
                              queue=self.queue_name,
                              no_ack=True)

        self.channel.start_consuming()
