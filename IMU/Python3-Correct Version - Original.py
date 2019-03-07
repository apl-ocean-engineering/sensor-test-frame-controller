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

def send_command_bytes_usb(data):
    global port
    checksum = 0
    
    for d in data:
        checksum += ord(d)

    # Construct the packet. NOTE: If you don't want the header use 0xf8 instead of 0xf9
    packet = chr(0xf9)+data+chr(checksum % 256)
    port.write(packet.encode('latin1'))

# Prompt the user for the command port
port_name = input("Please input the com port of the device: ")

# Create the serial port for communication
port = serial.Serial(port_name,115200,timeout=1)

# Set the header to contain the timestamp
send_command_bytes_usb(chr(0xdd)+chr(0x0)+chr(0x0)+chr(0)+chr(2))
port.read(4)

# Set the stream timing
delayTime = chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0)
send_command_bytes_usb(chr(0x52)+chr(0x0)+chr(0x0)+chr(0x3)+chr(0xE8)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+delayTime)
port.read(4)

# Set the streaming slots to stream the tared quaternion
send_command_bytes_usb(chr(0x50)+chr(0x0)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff))
port.read(4)

# Start Streaming
port.reset_input_buffer()
send_command_bytes_usb(chr(0x55))
port.read(4)
# Read 20 packets
for i in range(0,200):
    data = port.read(20)
    print(struct.unpack(">I",data[0:4]))
    print(struct.unpack(">ffff",data[4:20]))

# Stop Streaming
send_command_bytes_usb(chr(0x56))
port.close()
