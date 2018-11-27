#!/usr/bin/env python3
# A brief example to stream the tared quaternion
# Other commands can be found at: https://yostlabs.com/wp/wp-content/uploads/pdf/3-Space-Sensor-Family-User-Manual.pdf
# For just command and response use the following code
# send_command_bytes_usb(chr(0x0))
# port.read(20)
# print(struct.unpack(">I",data[0:4]))
# print(struct.unpack(">ffff",data[4:20]))
import serial
import struct
import io
import time

import argparse

def send_command_bytes_usb(data, response_header = False):
    global port
    checksum = 0

    for d in data:
        checksum += ord(d)

    # Construct the packet.
    # NOTE: If you want the response header use 0xf9;  
    #       for no response header (see below) use 0xf7
    packet = b''

    if response_header:
        packet = chr(0xf9)
    else:
        packet = chr(0xf7)

    packet += data+chr(checksum % 256)
    port.write(packet.encode('latin-1'))

parser = argparse.ArgumentParser(description='Read data from Yostlabs IMU')
parser.add_argument('port_name',
                    help='Device file for serial port (e.g., /dev/ttyUSBS0)')

parser.add_argument('--output',
                    help='Save output to file')

parser.add_argument('--output-raw',
                    help='Save raw output to file')


args = parser.parse_args()

# Prompt the user for the command port
#port_name = "/dev/ttyS4"
#input("Please input the com port of the device: ")

# Create the serial port for communication
port = serial.Serial(args.port_name,115200,timeout=1.5)

## Try to stop the output before doing any configuration
#
send_command_bytes_usb(chr(0x56))
# send_command_bytes_usb(chr(0x56))
# send_command_bytes_usb(chr(0x56))

## Drain any remaining input

# Set the header to contain the timestamp
# From manual page 47:
#   0xDD   : Set wired response header, takes 4 data bytes
#   0x00   : Data byte 4, ignored
#   0x00   : Data byte 3, ignored
#   0x00   : Data byte 2, (no values set)
#   0x4A   : Data byte 1,
#                   0x40 == prepend length of packet (1 bytes)
#                   0x08 == prepend 1-byte checksum
#                   0x04 == command echo
#                   0x02 == prepend timestanp in microseconds as 4-byte value
#                   0x01 == prepend success/failure; non-zero == failure
send_command_bytes_usb(chr(0xdd)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x47))

# Set the stream timing
# From manual page 39:
#   0x52   : Set streaming timing, takes 3 x 4-byte unsigned ints, all in microsecond
#   bytes 1-5   : interval (don't know what these mean, though 0x000003E8 == 1000 us = 1 ms)
#               :   0x186A0 = 100,000 = 10Hz
#               :   0xF4240 = 1,000,000 = 1Hz
#   bytes 6-9   : duration -- how long the streaming will run for (set to 0xFFFFFFFF.  What does it mean?)
#   bytes 10-13 : delay between start command and streaming data .. insert a short 100ms delay to allow
#                 other resopnse headers to clear the system
#send_command_bytes_usb(chr(0x52)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0x0)+chr(0x0)+chr(0x0)+chr(0x0))
send_command_bytes_usb(chr(0x52)+chr(0x0)+chr(0x0f)+chr(0x42)+chr(0x40)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0))

# Set the streaming slots to stream the tared quaternion
# From manualpage 39:
#   0x50   : Set streaming slots, takes 8 bytes, presumably 8 "slots"
#   0x00   : Read filtered, tared orientation(Quaternion) --> 16 bytes
#   0x01   : Read filtered, tared orientation(Euler Angles) --> 12 bytes
#   0xff   : Must mean "don't stream anything"
send_command_bytes_usb(chr(0x50)+chr(0x0)+chr(0x01)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff))

outfile = None
rawfile = None

if args.output:
    outfile = open( args.output, 'w' )
    outfile.write("#system_time_sec,imu_time_usec,quat1,quat2,quat3,quat4,euler1,euler2,euler3\n")

if args.output_raw:
    rawfile = open( args.output_raw, 'wb' )

# Start Streaming
send_command_bytes_usb(chr(0x55), response_header=True)
# Drain any residual bytes
port.read(128)

# Read 20 packets
while True:
    now = time.time()

    # Header
    data = port.read(7)
    if rawfile:
        rawfile.write(data)

    # Header bytes are packed in reverse order from lower bit to highest:
    #    success/failure, timestamp (4 bytes), echo, length
    hdr = struct.unpack(">cIcc", data)
    timestamp = hdr[1]

    # Data
    data = port.read(28)
    if rawfile:
        rawfile.write(data)

    results = struct.unpack(">fffffff",data)
    results = [now,timestamp] + list(results)

    #print(results)

    print("%f,%d,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(results) )

    if outfile:
        outfile.write("%f,%d,%f,%f,%f,%f,%f,%f,%f\n" % tuple(results) )


# Stop Streaming
send_command_bytes_usb(chr(0x56))
port.close()
