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
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

timer = time.time()

# def run(name,q):
#     while True:
#         header, data = imu.get_IMU_data()
#         timestamp = header[1]
#         #data2 = imu2.get_IMU_data()
#         """
#         DO STUFF
#         """
#         print("imu data: ", data)
#         #print("%f,%d,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
#         #print("% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data) )
#         q.put((header, data))
#         #time.sleep()


def signal_handler(sig, frame):
    print("Keyboard Interrupt")
    for imu in IMUs:
        imu.stop_streaming()
    quit()
    #send_command_bytes_usb(chr(0x56))


def plot_and_log(values = []):
    global timer
    with open("test_data.csv","a") as f:
            writer = csv.writer(f,delimiter=",")
            writer.writerow([time.time(),values[0]])
    
    #plt.axis([0, 10, 0, 1])
    plt.autoscale()
    plt.scatter(time.time(), values[0])
    if time.time() - timer > 20 :
        print("clearing")
        plt.cla()
        timer = time.time()
    plt.pause(0.0001)
#    plt.show()
# Potential Better way here: https://pythonprogramming.net/python-matplotlib-live-updating-graphs/

IMUs = []

if __name__ == '__main__':
    q1 = queue.Queue()
    print("Started")
    # global IMUs
    IMUs.append(IMU("COM5", frequency=10))
    t1 = threading.Thread(target=IMUs[0].start_stream_to_queue, args=(q1,))
    t1.start()
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        header1, data1 = q1.get()
        #TODO: Exit gracefully 
        if q1.not_empty:
            #print("% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
            #print(data1)
            plot_and_log(data1)
        #print("finishedPrinting")
    '''
    q2 = queue.Queue()
    t2 = threading.Thread(target=run, args = ("COM4", q2,))
    '''
