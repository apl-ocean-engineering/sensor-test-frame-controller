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
from pyquaternion import Quaternion

# import matplotlib
# import matplotlib.pyplot as plt

import numpy as np

timer = time.time()

IMUs = []
Threads = []

def signal_handler(sig, frame):
    print("Stopped by Keyboard Interrupt")
    global IMUs
    global Threads
    for i in range(len(IMUs)):
        IMUs[i].running = False
        Threads[i].join
        IMUs[i].stop_streaming()
        print("Streaming stopped and all ports closed")
    sys.exit(0)
    #quit()
    #send_command_bytes_usb(chr(0x56))


def plot_and_log(time_data = [], values1 = [], values2 = [], values3 = [], values4 = []):
    #global timer
    
    # with open("test_data.csv","a") as f:
    #         writer = csv.writer(f,delimiter=",")
    #         writer.writerow([time.time(),values[0]])
    
    # plt.autoscale()

    # plt.scatter(time_data, values1)
    # plt.scatter(time_data, values2)
    # plt.scatter(time_data, values3)
    # plt.scatter(time_data, values4)
    
    if len(values1) > 25:
        values1.pop(0)
        values2.pop(0)
        values3.pop(0)
        values4.pop(0)
        time_data.pop(0)
        #timer = time.time()
    # plt.pause(0.000001)
    # plt.cla()
    
# Potential Better way here: https://pythonprogramming.net/python-matplotlib-live-updating-graphs/

if __name__ == '__main__':
    print("Started")
    signal.signal(signal.SIGINT, signal_handler)
    #IMUs.append(IMU("COM5", frequency=1000))
    IMUs.append(IMU("/dev/ttyS1", frequency=10))
    IMUs.append(IMU("/dev/ttyS4", frequency=10))
    for imu in IMUs:
        Threads.append(threading.Thread(target=imu.start_stream_to_queue, args=(True,)))
    
    for t in Threads:
        t.start()
    
    # Quaternions
    targetQuat = Quaternion()
    referenceQuat = Quaternion()
    relativeQuat = Quaternion()

    # Plotter variables
    plotting = True
    full_data1 = []
    full_data2 = []
    full_data3 = []
    full_data4 = []
    time_data = []

    #numpy.linalg.norm
    while True:
        #TODO: not sure how to turn into for loop. or if even necessary
        headers = []
        data = []
        for i in range(len(IMUs)):
            headers.append
            headers[i], data[i] = IMUs[i].q.get()
        
        print("data1", data[1], " sum: ", np.linalg.norm(data[1]))
        #print("data2", data[2])
        for imu in IMUs: # For when loop is slowed down by anything (like plotting)
            while imu.q.qsize() > 0:
                header1, data1 = imu.q.get()

        populated = [imus.q.empty() for imus in IMUs if True]
        if not all(populated):
            #print("data 1: ", "% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
            print(header1)
            for i in range(4) :
                targetQuat[i] = data1[i]
                #referenceQuat[i] = data2[i]
            relativeQuat = targetQuat / referenceQuat
           
            print(targetQuat)
            print(referenceQuat)
            if plotting:
                full_data1.append(relativeQuat[0])
                full_data2.append(relativeQuat[1])
                full_data3.append(relativeQuat[2])
                full_data4.append(relativeQuat[3])
                time_data.append(time.time())
                plot_and_log(time_data, full_data1, full_data2, full_data3, full_data4)
