#!/usr/bin/env python2
import serial
import struct
import sys
import signal
import io
import time
import csv
import Queue
import threading

file_name  = "vectorNavData.csv"
write = False

def signal_handler(sig, frame):
    global running
    running = False

class VectorNav():
    def __init__(self, port_name, baud_rate=115200):
        self.port = serial.Serial(port_name, baud_rate, timeout=1.5)
        self.q = Queue.Queue()
        self.running = True

    def flushPort(self):
        self.port.flush()

    def hasData(self):
        return self.port.in_waiting >= 122

    def getData(self):
        datum = self.port.readline().decode("utf-8")
        datum = str(datum[7:-5])
        datum = datum.split(',')
        # datum = datum[:-1]
        if len(datum) == 12:
            try :
                return [float(i) for i in datum]
            except:
                print("VNav Read Error")
        return None

    def start(self):
        t = threading.Thread(target=self.start_stream_to_queue)
        t.start()
    
    def start_stream_to_queue(self):
        while self.running:
            try:
                if self.hasData() :
                    output = self.getData()
                    if output != None:
                        self.q.put(output)
            except Exception as e:
                print("Stopped reading from VNav:")
                print(e)
                self.running = False


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    imu =  VectorNav("COM22")
    print("Running")
    time.sleep(1)
    file = open( file_name, 'w+' )
    file.write("Time,yaw,pitch,roll,magx,magy,magz,accelx,accely,accelz,gyrox,gyroy,gyroz\n")
    imu.start()
    while imu.running:
        if imu.q.qsize() > 0:
            output = imu.q.get()
            while imu.q.qsize() > 0:
                output = imu.q.get()
            print(output)
            if file and write:
                file.write(str(output) + '\n')
    file.close()