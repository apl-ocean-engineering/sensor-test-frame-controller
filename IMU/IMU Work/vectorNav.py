#!/usr/bin/env python3
import serial
import struct
import sys
import signal
import io
import time
import csv

file_name  = "vectorNavData.csv"

def signal_handler(sig, frame):
    global running
    running = False

class VectorNav():
    def __init__(self, port_name, baud_rate=115200):
        self.port = serial.Serial(port_name, baud_rate, timeout=1.5)

    def flushPort(self):
        self.port.flush()

    def hasData(self):
        return self.port.in_waiting > 0

    def getData(self):
        datum = self.port.readline().decode("utf-8")
        datum = str(datum[7:]).strip('\r\n')
        datum = datum.split(',')
        datum = datum[:-1]
        return [float(i) for i in datum]

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    imu =  VectorNav("COM22")
    print("Running")
    running = True
    time.sleep(1)
    file = open( file_name, 'w+' )
    file.write("Time,Yaw,Pitch,Roll\n")

    while running:
        if imu.hasData() :
            output = imu.getData()
            # output = [str(time.time())] + output
            print(output)
            if file:
                file.write(str(output) + '\n')
    file.close()