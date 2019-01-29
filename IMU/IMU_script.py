#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 10:42:15 2019

@author: mitchell & stefan
"""
from IMU_module import IMU
import queue
import threading
import time
import sys
import signal

def run(name,q):
    imu = IMU(name, frequency=10)
    while True:
        header, data = imu.get_IMU_data()
        timestamp = header[1]
        #data2 = imu2.get_IMU_data()
        """
        DO STUFF
        """
        print("imu data: ", data)
        #print("%f,%d,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
        #print("% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data) )
        q.put((header, data))
        #time.sleep()


def signal_handler(sig, frame):
    print("Cntrl C")
    #imu.stop_streaming()
    #send_command_bytes_usb(chr(0x56))
    

if __name__ == '__main__':
    q1 = queue.Queue()
    t1 = threading.Thread(target=run, args = ("COM5", q1))
    t1.start()
    signal.signal(signal.SIGINT, signal_handler)
 
    while True:
        header1, data1 = q1.get()
        #TODO: Exit gracefully 
        print("% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
        time.sleep(0.5)
    '''
    q2 = queue.Queue()
    t2 = threading.Thread(target=run, args = ("COM4", q2,))
    '''
