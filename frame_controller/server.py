#!/usr/bin/env python

# Copyright 2018 UW-APL
# See LICENSE

"""The Python implementation of the GRPC frame.Controller server."""

from __future__ import absolute_import

from concurrent import futures
import time
from datetime import datetime

import grpc

import frame_controller.frame_controller_pb2 as frame_api
import frame_controller.frame_controller_pb2_grpc as frame_grpc

from .fake_pwm import FakePwm
from .real_pwm import RealPwm

import logging
# This is apparently best practice...  define a null logger for myself
# then let the _user_ of the library replace it with a more useful logger
logging.getLogger(__name__).addHandler(logging.NullHandler())

_DT_IN_SECONDS = 0.1

class FrameController(frame_grpc.FrameControllerServicer):

    def __init__(self, logger=None, fake_hardware=False):
        self.logger = logger or logging.getLogger(__name__)

        if fake_hardware:
            self.logger.warn("Using fake hardware")
            self.pitch = FakePwm("Pitch", self.logger)
            self.yaw   = FakePwm("Yaw", self.logger)
        else:
            ## Use real hardware
            self.logger.warn("Using real hardware")
            self.pitch = RealPwm("Pitch", self.logger)
            self.yaw   = RealPwm("Yaw", self.logger)

    def cleanup(self):
        self.pitch.cleanup()
        self.yaw.cleanup()

    # Main control loop
    def controlLoop(self):
        loops = 0

        self.pitch.setup()
        self.yaw.setup()

        startTime = datetime.now()
        while True:
            if loops % 50 == 0:
                self.logger.info("Control loop %d : %.2f" % (loops,(datetime.now()-startTime).total_seconds()))

            loops += 1
            time.sleep(_DT_IN_SECONDS)

    # Respond to gRPC commands
    def StopAll(self, request, context):
        self.logger.warn("Stopping all motors!!")
        self.pitch.stopAll()
        self.yaw.stopAll()
        return frame_api.Status()

    def SetVelocity(self, request, context):
        if request.axes & frame_api.AXIS_PITCH:
            self.pitch.set( request.motors, request.duty_cycle )

        if request.axes & frame_api.AXIS_YAW:
            self.yaw.set( request.motors, request.duty_cycle )

        # else:
        #     self.logger.warn("Didn't understand motor mask %d" % request.motors )

        return frame_api.Status()



# Entrypoint.  Starts gRPC server and launches a FrameController instance...
def serve(use_fake_hardware=False):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    logger = logging.getLogger(__name__)
    controller = FrameController(logger,use_fake_hardware)
    frame_grpc.add_FrameControllerServicer_to_server(controller, server)

    server.add_insecure_port('[::]:50051')
    server.start()

    logger.info("Started server.")

    try:
        controller.controlLoop()
    except KeyboardInterrupt:
        server.stop(0)

    controller.cleanup()
