#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 10:42:15 2019

@author: mitchell
"""

from IMU_module import IMU
import time

imu1 = IMU("COM5", frequency=10)
#imu2 = IMU(2)
while True:
    header1, data1 = imu1.get_IMU_data()
    timestamp = header1[1]
    #data2 = imu2.get_IMU_data()
    """
    DO STUFF
    """
    print("imu data: ", data1)
    #print("%f,%d,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
    print("% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
    #time.sleep()