# Functions for reading data from the Yostlabs IMU
# See docs/3-Space-Sensor-Usermanual-Embedded-LX.pdf
#   starting on pg 23
#

from __future__ import absolute_import

import logging
import time

import serial
import struct
import io

from imu.imu_data import ImuData

# A brief example to stream the tared quaternion
# Other commands can be found at: https://yostlabs.com/wp/wp-content/uploads/pdf/3-Space-Sensor-Family-User-Manual.pdf
# For just command and response use the following code
# send_command_bytes_usb(chr(0x0))
# port.read(20)
# print(struct.unpack(">I",data[0:4]))
# print(struct.unpack(">ffff",data[4:20]))

def send_command_bytes_usb(port, data, response_header = False):
    checksum = 0

    for d in data:
        checksum += ord(d)

    # Construct the packet.
    # NOTE: If you want the response header use 0xf9;  
    #       for no response header (see below) use 0xf7
    packet = chr(0xf7)

    if response_header:
        packet = chr(0xf9)

    packet += data+chr(checksum % 256)
    port.write(packet.encode('latin-1'))


class Imu:

    def __init__(self, name, portname):
        self.name = name
        self.logger = logging.getLogger(name)
        self.callbacks = []
        self.portname = portname

        self.port = None


    def __del__(self):
        if self.port and self.port.is_open:
            # Stop Streaming
            send_command_bytes_usb(self.port,chr(0x56))
            self.port.close()


    def add_callback(self, callback):
        self.callbacks.append(callback)


    def run(self):

        # Prompt the user for the command port
        #port_name = "/dev/ttyS4"
        #input("Please input the com port of the device: ")

        # Create the serial port for communication
        self.port = serial.Serial(self.portname,115200,timeout=1.5)

        ## Try to stop the output before doing any configuration
        #
        send_command_bytes_usb(self.port, chr(0x56))

        # Set the header to contain the timestamp
        # From manual page 47:
        #   0xDD   : Set wired response header, takes 4 data bytes
        #   0x00   : Data byte 4, ignored
        #   0x00   : Data byte 3, ignored
        #   0x00   : Data byte 2, ignored
        #   0x4A   : Data byte 1,
        #                   0x40 == prepend length of packet (1 bytes)
        #                   0x08 == prepend 1-byte checksum
        #                   0x04 == command echo
        #                   0x02 == prepend timestanp in microseconds as 4-byte value
        #                   0x01 == prepend success/failure; non-zero == failure
        send_command_bytes_usb(self.port, chr(0xdd)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x47))

        # Set the stream timing
        # From manual page 39:
        #   0x52   : Set streaming timing, takes 3 x 4-byte unsigned ints, all in microsecond
        #   bytes 1-5   : interval (don't know what these mean, though 0x000003E8 == 1000 us = 1 ms)
        #               :   0x186A0 = 100,000 = 10Hz
        #               :   0xF4240 = 1,000,000 = 1Hz
        #   bytes 6-9   : duration -- how long the streaming will run for (set to 0xFFFFFFFF.  What does it mean?)
        #   bytes 10-13 : delay between start command and streaming data .. insert a short 100ms delay to allow
        #                 other resopnse headers to clear the system
        send_command_bytes_usb(self.port, chr(0x52)+chr(0x0)+chr(0x0f)+chr(0x42)+chr(0x40)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0))

        # Set the streaming slots to stream the tared quaternion
        # From manualpage 39:
        #   0x50   : Set streaming slots, takes 8 bytes, presumably 8 "slots"
        #   0x00   : Read filtered, tared orientation(Quaternion) --> 16 bytes
        #   0x01   : Read filtered, tared orientation(Euler Angles) --> 12 bytes
        #   0xff   : Must mean "don't stream anything"
        send_command_bytes_usb(self.port, chr(0x50)+chr(0x0)+chr(0x01)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff))

        # Start Streaming
        send_command_bytes_usb(self.port, chr(0x55), response_header=True)
        # Drain any residual bytes
        self.port.read(128)





        while True:

            # Read 20 packets
            while True:
                # Header
                data = self.port.read(7)

                # Header fields  are packed lower bit to highest:
                #    success/failure, timestamp (4 bytes), echo, length
                hdr = struct.unpack(">cIcc", data)
                timestamp = hdr[1]

                # Data
                data = self.port.read(28)

                results = struct.unpack(">fffffff",data)

                imu_data = ImuData()

                imu_data.system_timestamp = time.time()
                imu_data.imu_timesstamp   =  timestamp
                imu_data.euler       = results[4:]
                imu_data.quaternions = results[0:3]

                for c in self.callbacks:
                    c(imu_data)



