#!/usr/bin/env python

# Copyright 2018 UW-APL
# See LICENSE

"""The Python implementation of the GRPC frame.Controller server."""

from __future__ import absolute_import

from concurrent import futures
import time

import grpc

import frame_controller.frame_controller_pb2 as frame_api
import frame_controller.frame_controller_pb2_grpc as frame_grpc


import logging
# This is apparently best practice...
logging.getLogger(__name__).addHandler(logging.NullHandler())

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class FrameController(frame_grpc.FrameControllerServicer):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def StopAll(self, request, context):
        self.logger.warn("Stopping all motors!!")
        return frame_api.Status()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frame_grpc.add_FrameControllerServicer_to_server(FrameController(), server)

    server.add_insecure_port('[::]:50051')
    server.start()

    logging.getLogger(__name__).info("Started server.")

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
