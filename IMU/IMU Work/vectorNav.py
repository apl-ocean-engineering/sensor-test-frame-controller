#!/usr/bin/env python3
import serial
import struct
import sys
import signal
import io
import time

port_name = "COM22"
file_name  = "data.csv"

def signal_handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, signal_handler)
port = serial.Serial(port_name,115200,timeout=1.5)
print("Running")
running = True
time.sleep(1)
file = open( file_name, 'w+' )
file.write("Time,Yaw,Pitch,Roll\n")

while running:
    if port.in_waiting > 0 :
        data = port.readline().decode("utf-8")
        
        output = str(time.time()) + ',' + str(data[7:])
        output = output.strip('\r\n')
        print(output)
        if file:
            file.write(output + '\n')
file.close()
port.close()
print("Exited Gracefully")