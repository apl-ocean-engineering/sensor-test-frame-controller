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
import sys
import glob
import time

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def send_command_bytes_usb(data):
    global port
    checksum = 0

    for d in data:
        checksum += ord(d)

    # Construct the packet. NOTE: If you don't want the header use 0xf8 instead of 0xf9
    # > Manual doesn't discuss 0xf9 as a header.
    packet = chr(0xf9)+data+chr(checksum % 256)
    port.write(packet.encode('latin1'))

# Prompt the user for the command port
print(serial_ports())
port_name = input("Please input the com port of the device: ")
# port_name = "/dev/tty.usbmodem1411"

# Create the serial port for communication
port = serial.Serial(port_name,115200,timeout=1)

# Set the header to contain the timestamp
# From manual page 47:
#   0xDD   : Set wired response header, takes 4 data bytes
#   0x00   : Data byte 4, ignored
#   0x00   : Data byte 3, ignored
#   0x00   : Data byte 2, (no values set)
#   0x4A   : Data byte 1,
#                   0x40 == prepend length of packet (1 bytes)
#                   0x08 == prepend 1-byte checksum
#                   0x02 == prepend timestand in microseconds as 4-byte value
send_command_bytes_usb(chr(0xdd)+chr(0x0)+chr(0x0)+chr(0x00)+chr(0x02))
port.read(4)

# Set the stream timing
# From manual page 39:
#   0x52   : Set streaming timing, takes 3 x 4-byte unsigned ints, all in microsecond
#   bytes 1-5   : interval (don't know what these mean, though 0x000003E8 == 1000 us = 1 ms)
#               :   0x186A0 = 100,000 = 10Hz
#   bytes 6-9   : duration (set to 0xFFFFFFFF.  What does it mean?)
#   bytes 10-13 : delay
send_command_bytes_usb(chr(0x52)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0x0)+chr(0x0)+chr(0x0)+chr(0x0))
port.read(4)

# Set the streaming slots to stream the tared quaternion
# From manualpage 39:
#   0x50   : Set streaming slots, takes 8 bytes, presumably 8 "slots"
#   0x00   : Read filtered, tared orientation(Quaternion) --> 16 bytes
#   0x01   : Read filtered, tared orientation(Euler Angles) --> 12 bytes
#   0xff   : Must mean "don't stream anything"
send_command_bytes_usb(chr(0x50)+chr(0x0)+chr(0x01)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff))
port.read(4)

# Setup Output File
startTime = time.time()
f=open("IMUQuaternions.csv", "a+") #append to. create if not already existing
f.write("New Session at Start Time: %d \n" % startTime)

# Start Streaming
send_command_bytes_usb(chr(0x55))
port.read(4)

# Read 20 packets
try:
    while True:
        data = port.read(32)
        results = struct.unpack(">Ifffffff",data)
        f.write(str(time.time()-startTime) + ", ")
        f.write("% 8d, %f, %7f, %7f, %7f,   :   %7f, %7f, %7f,\n" % results)
        print(time.time()-startTime, end =" ")
        print("% 8d %f %7f %7f %7f   :   %7f %7f %7f" % results)
except KeyboardInterrupt:
    send_command_bytes_usb(chr(0x56))
    port.close()
    f.write("\n")
    f.close()
    print()
    print("Ended Streaming")
    #raise
except:
    # report error and proceed
    raise
# Stop Streaming
#send_command_bytes_usb(chr(0x56))
#port.close()
